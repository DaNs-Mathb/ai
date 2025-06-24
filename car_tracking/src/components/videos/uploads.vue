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
        chooseLabel="Выбрать файл"
        uploadLabel="Загрузить"
        cancelLabel="Отмена"
        
        @select="onSelect"
      />
      <Button id="fetch_button" label="Загрузить" @click="upload" severity="secondary" :disabled="isUploading" />
      
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
        <i class="pi pi-fw pi-question-circle"></i> <!-- Другая иконка -->
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
          Предупреждения о нарушениях ПДД (превышение скорости).
          Данные для оптимизации дорожной инфраструктуры.
          Обработка видео с камер позволяет автоматизировать мониторинг трафика и повысить безопасность на дорогах.
        </div>
      </div>
    </div>
  </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import Toast from 'primevue/toast'
import FileUpload from 'primevue/fileupload'
import Button from 'primevue/button';
import { useToast } from 'primevue/usetoast'
import {ChildService} from "../../servise/api/videos"
import { ProgressBar } from 'primevue';
import { onMounted } from 'vue';
import { onBeforeUnmount } from 'vue';
import { useWebSocketStore } from '../../servise/api/websocket';


const childService = new ChildService();

const isUploading = ref(true)
const websocketStore = useWebSocketStore();

const progressValue = ref(0);
progressValue.value=websocketStore.progressValue;

const toast = useToast();
const fileupload = ref();
const selectedFile = ref<File | null>(null)


onMounted(() => {
  const savedTaskId = localStorage.getItem('video_task_id');
  if (savedTaskId) {
    websocketStore.connect(savedTaskId)
  }
});

watch(
  () => websocketStore.progressValue,
  (newVal) => {
    progressValue.value = newVal;
  },
  { immediate: true }
);

// Отслеживаем завершение задачи для автоскачивания



const onSelect = (event: { files: File[] }) => {
  const file = event.files[0]
  if (file) {
    selectedFile.value = file
    isUploading.value = false
  }
}

const upload = async () => {
  if (!selectedFile.value) return

  // Проверка на активную задачу
  if (localStorage.getItem('video_task_id')) {
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: 'Дождитесь завершения текущей обработки перед загрузкой нового файла',
      life: 3000
    });
    return;
  }

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
    
    
    websocketStore.connect(response.task_id);
    // await progress(response.task_id)

  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: 'Не удалось загрузить файл',
      life: 3000
    })
  }
}


</script>

<style lang="scss">

</style>

