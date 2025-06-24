// stores/websocket.ts
import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useToast } from 'primevue/usetoast';
import {websocketUrl} from "../env"


interface WebSocketMessage {
  status: string;
  progress?: number;
  current?: number;
  total?: number;
  position?: number;
  task_id?: string;
  result?: {
    video_url: string;
    csv_url:string
  };
  processed_file?: string;
  error?: string;
}

export const useWebSocketStore = defineStore('websocket', () => {
  const socket = ref<WebSocket | null>(null);
  const progressValue = ref(0);
  const toast = useToast(); 
  const downloadUrl = ref('');
  const processedFileName = ref('');
  const Url:string = websocketUrl

  const connect = (taskId: string) => {
    if (!taskId) {
      
      return;
    }

    const connection = `${Url}/${taskId}`;

    socket.value = new WebSocket(connection);

    socket.value.onmessage = (event: MessageEvent) => {
      const data: WebSocketMessage = JSON.parse(event.data);
    //   console.log('Update received:', data);

      if (!localStorage.getItem('video_task_id') && data.task_id) {
        localStorage.setItem('video_task_id', data.task_id);
        
      }

      if (data.progress !== undefined) {
        progressValue.value = data.progress;
      }

      switch (data.status) {
        case 'PENDING':
          // console.log('Task is waiting in queue');
          progressValue.value = 0;
          if (data.position) {
            // console.log(`Position in queue: ${data.position}`);
          }
          break;
        case 'RECEIVED':
          // console.log('Task received and queued for processing');
          progressValue.value = 0;
          break;
        case 'PROGRESS':
          // console.log(`Progress: ${data.progress}% (${data.current || 0}/${data.total || 1} frames)`);
          break;
        case 'SUCCESS':
          localStorage.removeItem('video_task_id');
          progressValue.value = 0;

          if (data.result?.video_url) {
            const downloadLink = document.createElement('a');
            downloadLink.href = data.result.video_url;
            downloadLink.style.display = 'none';
            document.body.appendChild(downloadLink);
            downloadLink.click();
            document.body.removeChild(downloadLink);
          }
          setTimeout(() => {
            if (data.result?.csv_url) {
                const link = document.createElement('a');
                link.href = data.result.csv_url;
                link.style.display = 'none';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }
            }, 1000); // Задержка 1 секунда
          toast.add({
            severity: 'success',
            summary: 'Успех',
            detail: 'Файл успешно обработан',
            life: 3000,
          });
          disconnect();
          break;
        case 'FAILURE':
          localStorage.removeItem('video_task_id');
          // console.error('Error:', data.error || 'Unknown error');
          disconnect();
          break;
      }
    };

    socket.value.onclose = (event) => {
      
      if (event.wasClean) {
        // console.log(`Connection closed cleanly, code=${event.code}, reason=${event.reason}`);
      } else {
        // console.error('Connection interrupted');
        toast.add({
          severity: 'error',
          summary: 'Ошибка соединения',
          detail: 'Соединение с сервером было прервано',
          life: 4000,
        });
      }
    };

    socket.value.onerror = (error) => {
      // console.error('WebSocket error:', error);
      toast.add({
        severity: 'error',
        summary: 'Ошибка WebSocket',
        detail: 'Произошла ошибка WebSocket соединения',
        life: 4000,
      });
    };
  };

  const disconnect = () => {
    if (socket.value) {
      socket.value.close();
      socket.value = null;
    }
  };

  return {
    socket,
    progressValue,
    downloadUrl,
    processedFileName,
    connect,
    disconnect,
  };
});
