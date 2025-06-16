import asyncio
import logging
import os
from collections import defaultdict, deque
from concurrent.futures import ProcessPoolExecutor
import fractions
from aiortc import MediaStreamError, MediaStreamTrack, VideoStreamTrack
import cv2
import numpy as np
import torch
from ultralytics import YOLO
from av import VideoFrame
import psutil
import gc

# Настройка логирования


class FrameProcessor:
    def __init__(self, model_path, device="cuda"):
        self._model_path = model_path
        self._device = device
        self._ready_event = asyncio.Event()
        self._input_queue = asyncio.Queue()
        self._output_queue = asyncio.Queue()
        self._task = asyncio.create_task(self._run())

        # Статистика
        self.fps = 30
        self.frame_count = 0
        self.AVG_CAR_LENGTH_M = 4.5
        self.MIN_CONFIDENCE = 0.6
        self.MIN_BOX_AREA = 1000
        self.MIN_SPEED_KMH = 5
        self.PARKED_FRAMES_THRESH = 30
        self.MAX_TRACK_MEMORY = 10

        self.stats = {
            'unique_cars': set(),
            'unique_motorcycles': set(),
            'unique_trucks': set(),
            'total_vehicles': 0,
            'moving_vehicles': 0,
            'speeds': [],
            'max_speed': 0,
        }
        self.car_tracks = defaultdict(lambda: deque(maxlen=self.MAX_TRACK_MEMORY))
        self.car_dimensions = {}
        self.parked_frames = defaultdict(int)
        self.car_lifetime = defaultdict(int)

    async def _run(self):
        try:
            print("[MODEL] Загрузка модели...")
            self._model = YOLO(self._model_path).to(self._device)
            self._model.fuse()
            dummy = torch.zeros((1, 3, 640, 640)).to(self._device)
            self._model(dummy)
            print("[MODEL] Модель готова.")
            self._ready_event.set()

            while True:
                img = await self._input_queue.get()
                if img is None:
                    break

                self.frame_count += 1

                results = self._model.track(img, persist=True, classes=[2, 3, 7], device=self._device, verbose=False)
                annotated = results[0].plot()

                if results[0].boxes.id is not None:
                    boxes = results[0].boxes.xyxy.cpu().numpy()
                    ids = results[0].boxes.id.int().tolist()
                    confs = results[0].boxes.conf.tolist()
                    class_ids = results[0].boxes.cls.int().tolist()

                    for box, track_id, conf, cls in zip(boxes, ids, confs, class_ids):
                        if conf < self.MIN_CONFIDENCE or (box[2]-box[0])*(box[3]-box[1]) < self.MIN_BOX_AREA:
                            continue

                        self.car_lifetime[track_id] += 1

                        if cls == 2:
                            self.stats['unique_cars'].add(track_id)
                        elif cls == 3:
                            self.stats['unique_motorcycles'].add(track_id)
                        elif cls == 7:
                            self.stats['unique_trucks'].add(track_id)

                        x_center = (box[0] + box[2]) / 2
                        y_center = (box[1] + box[3]) / 2
                        self.car_tracks[track_id].append((x_center, y_center))

                        if track_id not in self.car_dimensions:
                            self.car_dimensions[track_id] = box[2] - box[0]

                        if len(self.car_tracks[track_id]) < 10 or self.car_lifetime[track_id] <= 20:
                            continue

                        prev_x, prev_y = self.car_tracks[track_id][0]
                        curr_x, curr_y = self.car_tracks[track_id][-1]
                        dist = ((curr_x - prev_x)**2 + (curr_y - prev_y)**2)**0.5
                        speed_px_per_sec = dist * self.fps / len(self.car_tracks[track_id])

                        pixels_per_meter = self.car_dimensions[track_id] / self.AVG_CAR_LENGTH_M
                        speed_kmh = (speed_px_per_sec / pixels_per_meter) * 3.6

                        if speed_kmh >= self.MIN_SPEED_KMH:
                            self.stats['speeds'].append(speed_kmh)
                            self.stats['max_speed'] = max(self.stats['max_speed'], speed_kmh)
                            self.parked_frames[track_id] = 0
                        else:
                            self.parked_frames[track_id] += 1

                current_time = self.frame_count / self.fps
                self.stats['total_vehicles'] = len(self.stats['unique_cars'] | self.stats['unique_motorcycles'] | self.stats['unique_trucks'])
                self.stats['moving_vehicles'] = len([v for v in self.parked_frames.values() if v < self.PARKED_FRAMES_THRESH])
                avg_speed = sum(self.stats['speeds']) / len(self.stats['speeds']) if self.stats['speeds'] else 0
                vehicles_per_min = (self.stats['total_vehicles'] / current_time) * 60 if current_time > 0 else 0

                stats_text = [
                    f"Cars: {len(self.stats['unique_cars'])}",
                    f"Motorcycles: {len(self.stats['unique_motorcycles'])}",
                    f"Trucks: {len(self.stats['unique_trucks'])}",
                    f"Total vehicles: {self.stats['total_vehicles']}",
                    f"Moving vehicles: {self.stats['moving_vehicles']}",
                    f"Flow rate: {vehicles_per_min:.1f}/min",
                    f"Avg speed: {avg_speed:.1f} km/h",
                    f"Max speed: {self.stats['max_speed']:.1f} km/h",
                    f"Time: {current_time:.1f}s"
                ]

                for i, text in enumerate(stats_text):
                    cv2.putText(annotated, text, (10, 30 + i * 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

                await self._output_queue.put(annotated)

        except asyncio.CancelledError:
            print("[FrameProcessor] Завершено корректно")
        finally:
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

    async def wait_ready(self, timeout=10):
        try:
            await asyncio.wait_for(self._ready_event.wait(), timeout)
            return True
        except asyncio.TimeoutError:
            return False

    async def process(self, img):
        await self._input_queue.put(img)
        return await self._output_queue.get()

    async def close(self):
        await self._input_queue.put(None)
        await self._task
        print("[FrameProcessor] Shutdown complete")

class VideoTransformTrack(MediaStreamTrack):
    kind = "video"

    # ProcessPoolExecutor(max_workers=1)  # 1 процесс на GPU
    def __init__(self, video_capture, processor: FrameProcessor):
        super().__init__()
        self.track = video_capture
        self.processor = processor
  



    async def recv(self):
        try:
            frame = await self.track.recv()
            
            # Конвертируем кадр в numpy массив
            img = frame.to_ndarray(format="bgr24")
            
            if not await self.processor.wait_ready(timeout=0.1):
                return frame
                
            # Обрабатываем изображение
            processed_img = await self.processor.process(img)
            
            # Освобождаем исходный массив
          
            
            # Создаем новый кадр, используя тот же формат и параметры
            new_frame = VideoFrame.from_ndarray(processed_img, format="bgr24")
            new_frame.pts = frame.pts
            new_frame.time_base = frame.time_base
            
            # Освобождаем обработанное изображение
           
            
            # Принудительно вызываем сборщик мусора
            
            
            return new_frame
            
        except Exception as e:
            print(f"Error in recv: {str(e)}")
            raise MediaStreamError(str(e))
        
        
