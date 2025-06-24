import { defineStore } from 'pinia';
import {baseUrl} from "../env"

export const useWebRTCStore = defineStore('webrtc', {
  state: () => ({
    pc: null as RTCPeerConnection | null,
    isActive: false,
    stream: null as MediaStream | null
  }),
  actions: {
    createPeerConnection() {
      const config: RTCConfiguration = {
        iceServers: [
          { urls: 'stun:stun.l.google.com:19302' }
        ]
      }; //так правильно но меделнно
      // const config = { sdpSemantics: 'unified-plan' };
      this.pc = new RTCPeerConnection(config);

      this.pc.addEventListener('track', (evt) => {
        const element = document.getElementById(evt.track.kind) as HTMLMediaElement;
        if (element) {
          element.srcObject = evt.streams[0];
          // Показываем видео только когда начали приходить кадры
          const videoCont = document.getElementById('video-cont') as HTMLElement;
          if (videoCont) {
            videoCont.classList.add('video');
          }
          // Скрываем спиннер
          const spinner = document.getElementById('loading-spinner') as HTMLElement;
          if (spinner) {
            spinner.classList.remove('active');
          }
        }
      });
    },

    

    async negotiate() {
      const Url:string=baseUrl
      if (!this.pc) throw new Error('PeerConnection не инициализирован');

      try {
        const offer = await this.pc.createOffer();
        await this.pc.setLocalDescription(offer);

        await new Promise<void>((resolve) => {
          if (this.pc!.iceGatheringState === 'complete') {
            resolve();
          } else {
            const handler = () => {
              if (this.pc!.iceGatheringState === 'complete') {
                this.pc!.removeEventListener('icegatheringstatechange', handler);
                resolve();
              }
            };
            this.pc!.addEventListener('icegatheringstatechange', handler);
          }
        });

        const response = await fetch(`${Url}/offer`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            sdp: this.pc.localDescription!.sdp,
            type: this.pc.localDescription!.type
          })
        });

        const answer = await response.json();
        await this.pc.setRemoteDescription(answer);
      } catch (e) {
        console.error('Ошибка согласования:', e);
        this.stop();
        throw e;
      }
    },

    async start() {
      try {
        const startButton = document.getElementById('start') as HTMLElement;
        const video = document.getElementById('video-cont') as HTMLElement;
        const trafficContainer = document.querySelector('.trafficContainer') as HTMLElement;
        const spinner = document.getElementById('loading-spinner') as HTMLElement;
        
        if (startButton){ 
          startButton.style.display = 'none';
        }
        if (trafficContainer) {
          trafficContainer.classList.add('hidden');
        }
        if (spinner) {
          spinner.classList.add('active');
        }
        
        this.createPeerConnection();

        const constraints = { audio: false, video: true };
        this.stream = await navigator.mediaDevices.getUserMedia(constraints);

        this.stream.getTracks().forEach(track => {
          this.pc!.addTrack(track, this.stream!);
        });

        await this.negotiate();
        const stopButton = document.getElementById('stop') as HTMLElement;
        if (stopButton) stopButton.style.display = 'inline-block';
        this.isActive = true;
      } catch (err) {
        console.error('Ошибка запуска:', err);
        this.stop();
      }
    },

    stop() {
      if (this.stream) {
        this.stream.getTracks().forEach(track => track.stop());
        this.stream = null;
      }

      if (this.pc) {
        this.pc.getSenders().forEach(sender => sender.track?.stop());
        setTimeout(() => {
          this.pc!.close();
          this.pc = null;
        }, 500);
      }

      const stopButton = document.getElementById('stop') as HTMLElement;
      const video = document.getElementById('video-cont') as HTMLElement;
      const trafficContainer = document.querySelector('.trafficContainer') as HTMLElement;
      const spinner = document.getElementById('loading-spinner') as HTMLElement;
      
      if (stopButton) stopButton.style.display = 'none';
      const startButton = document.getElementById('start') as HTMLElement;
      if (startButton) {
        startButton.style.display = 'inline-block';
        video.classList.remove('video');
      }
      if (trafficContainer) {
        trafficContainer.classList.remove('hidden');
      }
      if (spinner) {
        spinner.classList.remove('active');
      }
      
      const videoElement = document.getElementById('video') as HTMLVideoElement;
      if (videoElement) videoElement.srcObject = null;
      this.isActive = false;
    }
  }
});
