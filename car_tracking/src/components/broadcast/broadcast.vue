<template>
<div class="broadcast-container">
    <div class="video-container">
        <div id="video-cont">
            <audio id="audio" autoplay></audio>
            <video class="container" id="video" autoplay playsinline muted controls></video>
        </div>
        <div id="loading-spinner" class="loading-spinner">
          <ProgressSpinner id="loading-spinner" />
        </div>
      
    
        <div>
            <Button id="start" label="Запустить" @click="startStream"  />
            <Button id="stop" label="Стоп" style="display: none" @click="stopStream"></Button>
        </div>
        <!-- <div>
            <Checkbox inputId="useaudio" value="Cheese" v-model="audio_checked" binary  />
            <label for="useaudio"> Микрофон </label>
        </div> -->
    </div>    
    <div class="trafficContainer">
    <!-- Первая секция -->
    <div class="sectionBlock">
      <div class="iconWrapper">
        <i class="pi pi-fw pi-eye"></i> <!-- Иконка "глаз" для визуализации -->
      </div>
      <div class="contentWrapper">
        <div class="sectionTitle">Что показывает трансляция?</div>
        <div class="sectionText">
          Прямая трансляция с камер дорожного движения анализируется нейросетью в реальном времени, преобразуя видеопоток в интерактивную аналитическую панель. Это включает:
          Мгновенную детекцию транспорта с цветными метками (автомобили, грузовики, мотоциклы).
          Отображение текущей средней скорости транспорта прямо на видео.
          Визуализацию плотности потока и загруженности дорог.
        </div>
      </div>
    </div>

    <!-- Вторая секция -->
    <div class="sectionBlock">
      <div class="iconWrapper">
        <i class="pi pi-fw pi-bolt"></i> <!-- Иконка "молния" для скорости -->
      </div>
      <div class="contentWrapper">
        <div class="sectionTitle">Как работает в реальном времени?</div>
        <div class="sectionText">
          Мгновенный анализ - каждый кадр обрабатывается за 20-50 мс без задержек.
          Интерактивная визуализация - результаты детекции и статистика отображаются поверх видеопотока.
          Адаптивная обработка - система автоматически подстраивается под изменения освещения и погодных условий.
        </div>
      </div>
    </div>
    </div>
    
</div>

</template>
<script setup lang="js">
import { ref } from "vue";
import Checkbox from 'primevue/checkbox';
import Button from 'primevue/button';
import { useWebRTCStore } from './connection.ts'
import { onBeforeUnmount } from 'vue'
import ProgressSpinner from 'primevue/progressspinner';

var audio_checked=ref(false)



// data channel

const webrtcStore = useWebRTCStore()

// Эти функции будут доступны в шаблоне автоматически
const startStream = () => webrtcStore.start()
const stopStream = () => webrtcStore.stop()



// Очистка при размонтировании компонента

onBeforeUnmount(() => {
  if (webrtcStore.isActive) {
    webrtcStore.stop()
  }
})

</script>

<style>
.broadcast-container{
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100vh; /* центрирование по всей высоте экрана */
    flex-direction: row;
    gap: 48px;
    
}

.video-container{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
}

#video-cont {
    display: none;
    width: 640px;
    height: 480px;
    background: #000;
    position: relative;
}

#video-cont.video {
    display: block;
}

#video-cont video {
    width: 100%;
    height: 100%;
    object-fit: contain;
}

.loading-spinner {
    display: none;
    margin: 20px auto;
}

.loading-spinner.active {
    display: block;
}

.trafficContainer {
    transition: opacity 0.3s ease;
}

.trafficContainer.hidden {
    display: none;
}

@media (max-width: 991px) {
  .broadcast-container{
    flex-direction: column;
  }
  
  .video-container {
    width: 100%;
    max-width: 640px;
  }
  
  #video-cont {
    width: 100%;
    height: auto;
    aspect-ratio: 4/3;
  }
}


</style>