// import 'primeflex/primeflex.css';
import "primeicons/primeicons.css";
import './assets/main.css'
// import "primevue/resources/primevue.css";
import { createApp } from 'vue'
import { createPinia } from 'pinia'

import PrimeVue from 'primevue/config';
import ConfirmationService from 'primevue/confirmationservice'
import DialogService from 'primevue/dialogservice'
import ToastService from 'primevue/toastservice';

import Aura from '@primeuix/themes/aura';

import App from './App.vue'
import router from './router'



const app = createApp(App)

app.use(createPinia())
app.use(ConfirmationService);
app.use(ToastService);
app.use(DialogService);

app.use(router)

app.use(PrimeVue, {
    theme: {
        preset: Aura,
        options: {
            prefix: 'p',
            darkModeSelector: '.my-app-dark',
            cssLayer: false
        }
    }
});

app.mount('#app')
