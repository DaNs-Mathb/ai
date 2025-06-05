import { defineStore } from 'pinia';

export const useWebRTCStore = defineStore('webrtc', {
  state: () => ({
    pc: null as RTCPeerConnection | null,
    isActive: false,
    stream: null as MediaStream | null
  }),
  actions: {
    createPeerConnection() {
      const config = { sdpSemantics: 'unified-plan' };
      this.pc = new RTCPeerConnection(config);

      this.pc.addEventListener('track', (evt) => {
        const element = document.getElementById(evt.track.kind) as HTMLMediaElement;
        if (element) element.srcObject = evt.streams[0];
      });
    },

    async negotiate() {
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

        const response = await fetch('http://127.0.0.1:8000/offer', {
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
        if (startButton) startButton.style.display = 'none';
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
      if (stopButton) stopButton.style.display = 'none';
      const startButton = document.getElementById('start') as HTMLElement;
      if (startButton) startButton.style.display = 'inline-block';
      const videoElement = document.getElementById('video') as HTMLVideoElement;
      if (videoElement) videoElement.srcObject = null;
      this.isActive = false;
    }
  }
});
