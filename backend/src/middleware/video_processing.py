from datetime import timedelta
import glob
import cv2 
from ultralytics import YOLO
import torch
from celery import Celery
from minio import Minio
from minio.lifecycleconfig import LifecycleConfig, Expiration, Rule
from minio.commonconfig import ENABLED, Filter
import os
from dotenv import load_dotenv
from collections import defaultdict, deque
import csv

load_dotenv() 

celery_app = Celery("tasks", broker=os.getenv("REDIS_URL"))
celery_app.conf.result_backend = os.getenv("REDIS_URL")


client = Minio(
    os.getenv("MINIO_ENDPOINT"),
    access_key=os.getenv("MINIO_ACCESS_KEY"),
    secret_key=os.getenv("MINIO_SECRET_KEY"),
    secure=False  # True для HTTPS
)

@celery_app.task(bind=True,name="src.middleware.video_processing.processing_video")
def processing_video(self,input_video: str ,classe:int=2):
    try:
        
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        # print(f"Using device: {device}")
        model = YOLO("backend/src/middleware/yolo11m.pt").to(device)  # Замените "yolov8n.pt" на путь к вашей модели
        # Открываем видео через OpenCV
        cap = cv2.VideoCapture(f"backend/src/uploads/{input_video}")
    
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        

        # Проверка, что видеофайл открылся
        if not cap.isOpened():
            print("Ошибка: не удалось открыть видеофайл")
            exit()

        
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        output_name=f'output_{input_video}'
        # Создаем VideoWriter для сохранения видео
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        out = cv2.VideoWriter(f'backend/src/uploads/{output_name}', fourcc, fps, (frame_width, frame_height))
        
        #подсчет количества
        all_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = all_frames/fps
        MIN_CONFIDENCE = 0.6
        MIN_BOX_AREA = 1000
        MIN_SPEED_KMH = 5
        PARKED_FRAMES_THRESH = 30
        AVG_CAR_LENGTH_M = 4.5
        MAX_TRACK_MEMORY = 10

        stats = {
            'total_vehicles': 0,
            'moving_vehicles': 0,
            'speeds': [],
            'max_speed': 0,
            'frame_count': 0,
            'unique_cars': set(),
            'unique_motorcycles': set(),
            'unique_trucks': set()
        }

        car_tracks = defaultdict(lambda: deque(maxlen=MAX_TRACK_MEMORY))
        car_dimensions = {}
        parked_frames = defaultdict(int)
        car_lifetime = defaultdict(int)
        
        frame_count = 0
        skip_frames = 2
        last_processed_frame = None

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break  # Выход из цикла, если видео закончилось

            frame_count += 1
            # if frame_count % (skip_frames + 1) == 0:
                # Обрабатываем каждый (skip_frames+1)-й кадр
            results = model.track(frame, classes=[classe], persist=True, device=device, imgsz=640,conf=0.4)
            
            
            if results[0].boxes.id is not None:
                boxes = results[0].boxes.xyxy.cpu().numpy()
                track_ids = results[0].boxes.id.int().tolist()
                confidences = results[0].boxes.conf.tolist()

                class_ids = results[0].boxes.cls.int().tolist()

                for box, track_id, conf, cls in zip(boxes, track_ids, confidences,class_ids):
                    if conf >= MIN_CONFIDENCE and (box[2]-box[0])*(box[3]-box[1]) >= MIN_BOX_AREA:
                        car_lifetime[track_id] += 1
                        if cls == 2:
                            stats['unique_cars'].add(track_id)
                        elif cls == 3:
                            stats['unique_motorcycles'].add(track_id)
                        elif cls == 7:
                            stats['unique_trucks'].add(track_id)

                        x_center = (box[0] + box[2]) / 2
                        y_center = (box[1] + box[3]) / 2
                        car_tracks[track_id].append((x_center, y_center))
                        
                        
                        
                        if track_id not in car_dimensions:
                            car_width_px = box[2] - box[0]
                            car_dimensions[track_id] = car_width_px

                        if len(car_tracks[track_id]) < 10 or car_lifetime[track_id] <= 20:
                            continue

                        

                        prev_x, prev_y = car_tracks[track_id][0]
                        curr_x, curr_y = car_tracks[track_id][-1]
                        distance_px = ((curr_x - prev_x)**2 + (curr_y - prev_y)**2)**0.5
                        speed_px_per_sec = distance_px * fps / len(car_tracks[track_id])

                        if track_id in car_dimensions:
                            pixels_per_meter = car_dimensions[track_id] / AVG_CAR_LENGTH_M
                            speed_kmh = (speed_px_per_sec / pixels_per_meter) * 3.6

                            if speed_kmh >= MIN_SPEED_KMH:
                                stats['speeds'].append(speed_kmh)
                                stats['max_speed'] = max(stats['max_speed'], speed_kmh)
                                parked_frames[track_id] = 0
                            else:
                                parked_frames[track_id] += 1
                
                
            stats['total_vehicles'] = len(stats['unique_cars'] | stats['unique_motorcycles'] | stats['unique_trucks'])
            current_time = frame_count / fps
            vehicles_per_min = (stats['total_vehicles'] / current_time) * 60 if current_time > 0 else 0
            avg_speed = sum(stats['speeds']) / len(stats['speeds']) if stats['speeds'] else 0
            stats['moving_vehicles'] = len([v for v in parked_frames.values() if v < PARKED_FRAMES_THRESH])

            stats_text = [
                f"Cars: {len(stats['unique_cars'])}",
                f"Motorcycles: {len(stats['unique_motorcycles'])}",
                f"Trucks: {len(stats['unique_trucks'])}",
                f"Total vehicles: {stats['total_vehicles']}",
                f"Moving vehicles: {stats['moving_vehicles']}",
                f"Flow rate: {vehicles_per_min:.1f}/min",
                f"Avg speed: {avg_speed:.1f} km/h",
                f"Max speed: {stats['max_speed']:.1f} km/h",
                f"Time: {current_time:.1f}s / {duration:.1f}s"
            ]
            # Сохраняем обработанный кадр
            last_processed_frame = results[0].plot()
            y_offset = 30
            for i, text in enumerate(stats_text):
                cv2.putText(last_processed_frame, text, (10, y_offset + i * 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
       
            progress = int((frame_count / total_frames) * 100)
            if progress % 5 == 0:
                
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'progress': progress,
                        'current': frame_count,
                        'total': total_frames
                    }
                )
            
            # Записываем последний обработанный кадр для всех кадров
            if last_processed_frame is not None:
                out.write(last_processed_frame)

        # Освобождение ресурсов
        cap.release()
        out.release()
        
        
        client.fput_object(
            "processed-videos",  # Бакет
            output_name,      # Имя файла в MinIO
            f"backend/src/uploads/{output_name}"    # Локальный путь
        )
        stats_csv_rows = [line.split(":", 1) for line in stats_text]
        # Удалим лишние пробелы у метрик и значений
        stats_csv_rows = [[key.strip(), value.strip()] for key, value in stats_csv_rows]
        csv_filename = f"{output_name[:-4]}.csv"
        with open(f"backend/src/uploads/{output_name[:-4]}.csv", mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Metric", "Value"])
            writer.writerows(stats_csv_rows)
        
        client.fput_object(
            "processed-csv",
            csv_filename,
            f"backend/src/uploads/{output_name[:-4]}.csv"
        )
        
        csv_url = client.presigned_get_object(
            "processed-csv",
            csv_filename,
            expires=timedelta(hours=1)
        )
        
        video_url = client.presigned_get_object(
        "processed-videos",
        output_name,
        expires=timedelta(hours=1)
        )
        
        # uploads_dir = "backend/src/uploads"

        # Получаем все файлы в директории
        for file_path in [f'backend/src/uploads/{output_name}',f"backend/src/uploads/{input_video}",f'backend/src/uploads/{output_name[:-4]}.csv']:
            if os.path.exists(file_path):
                os.remove(file_path)
        
        return {
            "status": "success",
            "original_task_id": self.request.id,  # Настоящий task_id из Celery
            "processed_file": output_name,
            "video_url":video_url,
            "csv_url": csv_url,
            
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "original_task_id": self.request.id,  # Даже при ошибке возвращаем task_id
        }
# print(torch.cuda.is_available())
# processing_video(input_video="cars.mp4")

# print(f"PyTorch version: {torch.__version__}")
# print(f"CUDA available: {torch.cuda.is_available()}")
# print(f"GPU device: {torch.cuda.get_device_name(0)}")
# print(torch.backends.cudnn.enabled)  # Должно быть True
# docker run -p 9000:9000 -p 9001:9001 --name minio -v D:\programm\minio_storage:/data -e "MINIO_ROOT_USER=minioadmin" -e "MINIO_ROOT_PASSWORD=minioadmin" minio/minio server /data --console-address ":9001"