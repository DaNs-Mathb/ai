<template>
<div class="broadcast-container">
    <div>
        
        <audio id="audio" autoplay="true"></audio>
        <video id="video" autoplay="true"  playsinline="true"></video>
    </div>
    <div>
        <Button id="start" label="Запустить" @click="startStream"  />
        <Button id="stop" label="Стоп" style="display: none" @click="stopStream"></Button>
    </div>
    <div>
        <Checkbox inputId="useaudio" value="Cheese" v-model="audio_checked" binary  />
        <label for="useaudio"> Микрофон </label>
    </div>
    
    
    
</div>
</template>
<script setup lang="js">
import { ref } from "vue";
import Checkbox from 'primevue/checkbox';
import Button from 'primevue/button';
import { useWebRTCStore } from './connection.ts'
import { onBeforeUnmount } from 'vue'

var audio_checked=ref(false)

var pc = null;

// data channel
var dc = null, dcInterval = null;
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

    flex-direction: column;
    gap: 5px;
}


</style>