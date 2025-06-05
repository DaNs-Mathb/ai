// import 'primeflex/primeflex.css';

// import './assets/main.css'
// import "primevue/resources/primevue.css";
import './assets/styles.scss'
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { definePreset } from '@primeuix/themes';
import PrimeVue from 'primevue/config';
import ConfirmationService from 'primevue/confirmationservice'
import DialogService from 'primevue/dialogservice'
import ToastService from 'primevue/toastservice';

import Aura from '@primeuix/themes/aura';
import Lara from '@primeuix/themes/lara';

import App from './App.vue'
import router from './router'



const app = createApp(App)

app.use(createPinia())
app.use(ConfirmationService);
app.use(ToastService);
app.use(DialogService);

app.use(router)

const Noir = definePreset(Aura, {
    semantic: {
        primary: {
            50: '{zinc.50}',
            100: '{zinc.100}',
            200: '{zinc.200}',
            300: '{zinc.300}',
            400: '{zinc.400}',
            500: '{zinc.500}',
            600: '{zinc.600}',
            700: '{zinc.700}',
            800: '{zinc.800}',
            900: '{zinc.900}',
            950: '{zinc.950}'
        },
        colorScheme: {
            light: {
                primary: {
                    color: '{zinc.950}',
                    inverseColor: '#ffffff',
                    hoverColor: '{zinc.900}',
                    activeColor: '{zinc.800}'
                },
                highlight: {
                    background: '{zinc.950}',
                    focusBackground: '{zinc.700}',
                    color: '#ffffff',
                    focusColor: '#ffffff'
                }
            },
            dark: {
                primary: {
                    color: '{zinc.50}',
                    inverseColor: '{zinc.950}',
                    hoverColor: '{zinc.100}',
                    activeColor: '{zinc.200}'
                },
                highlight: {
                    background: 'rgba(250, 250, 250, .16)',
                    focusBackground: 'rgba(250, 250, 250, .24)',
                    color: 'rgba(255,255,255,.87)',
                    focusColor: 'rgba(255,255,255,.87)'
                }
            }
        }
    }
});


app.use(PrimeVue, {
    theme: {
        preset: Noir,
        options: {
            darkModeSelector: '.app-dark',
        }
    }
});

app.mount('#app')
