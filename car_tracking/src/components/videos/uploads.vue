

<template>
  <div class="upload-container">
    <Toast />
    
    <div class="upload-content">
      <ProgressBar class="p-progressbar" :value="progressValue" />

      <FileUpload
        ref="fileupload"
        mode="basic"
        name="video"
        accept="video/*"
        :maxFileSize="100000000"
        @select="onSelect"
      />
      <Button id="fetch_button" label="Upload" @click="upload" severity="secondary" :disabled="isUploading" />
      
    </div>
    <div class="trafficContainer">
    <!-- Первая секция -->
    <div class="sectionBlock">
      <div class="iconWrapper">
        <i class="pi pi-fw pi-download"></i>
      </div>
      <div class="contentWrapper">
        <div class="sectionTitle">Что делает обработка?</div>
        <div class="sectionText">
          Обработка видео с камер дорожного движения преобразует сырые записи в структурированные данные, пригодные для анализа нейронными сетями. Это включает:
          Детекцию и классификацию транспортных средств (автомобили, грузовики, мотоциклы).
          Отслеживание максимальной и средней скорости транспорта.
          Подсчёт интенсивности потока и загруженности дорог.
        </div>
      </div>
    </div>

    <!-- Вторая секция -->
    <div class="sectionBlock">
      <div class="iconWrapper">
        <i class="pi pi-fw pi-cog"></i> <!-- Другая иконка -->
      </div>
      <div class="contentWrapper">
        <div class="sectionTitle">Как это работает?</div>
        <div class="sectionText">
          Анализ нейросетью – выделение объектов, определение их скорости и типа.
          Сохранение данных – статистика в формате CSV, визуализация на видео.
        </div>
      </div>
    </div>

    <!-- Третья секция -->
    <div class="sectionBlock">
      <div class="iconWrapper">
        <i class="pi pi-fw pi-chart-bar"></i> <!-- Другая иконка -->
      </div>
      <div class="contentWrapper">
        <div class="sectionTitle">Результаты</div>
        <div class="sectionText">
          После обработки вы получаете:
          Отчёты о загруженности дорог в реальном времени.
          Предупреждения о нарушениях ПДД (превышение скорости, проезд на красный).
          Данные для оптимизации дорожной инфраструктуры.
          Обработка видео с камер позволяет автоматизировать мониторинг трафика и повысить безопасность на дорогах.
        </div>
      </div>
    </div>
  </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Toast from 'primevue/toast'
import FileUpload from 'primevue/fileupload'
import Button from 'primevue/button';
import { useToast } from 'primevue/usetoast'
import {ChildService} from "../../servise/api/videos"
import { ProgressBar } from 'primevue';
import { progressbar } from '@primeuix/themes/aura/fileupload';


const childService = new ChildService();

const isUploading = ref(true)

const progressValue = ref(0);
let socket:WebSocket
const toast = useToast();
const fileupload = ref();
const selectedFile = ref<File | null>(null)


const onSelect = (event: { files: File[] }) => {
  const file = event.files[0]
  if (file) {
    selectedFile.value = file
    isUploading.value = false
  }
}

const upload = async () => {
  if (!selectedFile.value) return

  const formData = new FormData()
  formData.append('video', selectedFile.value)

  try {
    const response = await childService.UploadVideo(formData)
    toast.add({
      severity: 'success',
      summary: 'В очерди',
      detail: 'Файл в очерди на обработку',
      life: 3000
    })
    isUploading.value = true
    selectedFile.value = null
    fileupload.value.clear()
    
    await progress(response.task_id)

  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: 'Не удалось загрузить файл',
      life: 3000
    })
  }
}

const progress =async (task:string)=>{
   const taskId = task; 
  
  if (!taskId) {
    console.error('Task ID is required');
    return;
  }

  // Формируем URL подключения
  const protocol ='ws:';
  const connection = `${protocol}//127.0.0.1:8000/ws/tasks/${taskId}`;
  
  console.log('Connecting to:', connection);
  
  // Создаем новое подключение
  socket = new WebSocket(connection);

  socket.onopen = () => {
    console.log('WebSocket connection established');
  };

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Update received:', data);
    
    // Обновляем прогресс
    if (data.progress !== undefined) {
      progressValue.value = data.progress;
      console.log(`Progress: ${data.progress}% (${data.current || 0}/${data.total || 1} frames)`);
    }

    if (data.status === 'PENDING') {
      console.log('Task is waiting in queue');
      progressValue.value = 0;
      
      if (data.position) {
        console.log(`Position in queue: ${data.position}`);
      }
    }
    
    if (data.status === 'RECEIVED') {
      console.log('Task received and queued for processing');
      progressValue.value = 0;
    }
    else if (data.status === 'PROGRESS') {
      console.log(`Progress: ${data.progress}% (${data.current || 0}/${data.total || 1} frames)`);
    }
    else if (data.status === 'SUCCESS') {
      console.log('Processing complete!', data.result);
      progressValue.value = 0;

      const downloadLink = document.createElement('a');
      downloadLink.href = data.result.url;
      downloadLink.download = data.processed_file; // Имя файла для сохранения
      downloadLink.style.display = 'none';
      
      document.body.appendChild(downloadLink);
      downloadLink.click();
      document.body.removeChild(downloadLink);
      toast.add({
      severity: 'success',
      summary: 'Успех',
      detail: 'Файл успешно обработан',
      life: 3000
      })
      socket.close();
    }
    else if (data.status === 'FAILURE') {
      console.error('Error:', data.error || 'Unknown error');
      socket.close();
    }
  };

  
  socket.onclose = (event) => {
    if (event.wasClean) {
      console.log(`Connection closed cleanly, code=${event.code}, reason=${event.reason}`);
    } else {
      console.error('Connection interrupted');
    }
  };

  socket.onerror = (error) => {
    console.error('WebSocket error:', error);
  };
}




</script>

<style scoped>
.upload-container {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh; /* центрирование по всей высоте экрана */
  flex-direction: row;
  gap: 48px;
  text-align: center;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem; /* отступ между загрузкой и кнопкой */
}
.upload-content .p-progressbar {
  visibility: visible;
  width: 100%;
  /* Увеличьте высоту для лучшей видимости */
  
}

@media (max-width: 991px) {
  .upload-container{
    flex-direction: column;
  }
}
</style>

