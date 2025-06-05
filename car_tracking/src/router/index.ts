import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '@/layout/AppLayout.vue';


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: AppLayout,
      children: [
          {
            path: '/',
            name: 'home',
            component: () => import('@/views/HomeView.vue')
          },
          {
            path: '/broadcast',
            name: 'translations',
            component: ()=> import('../views/BroadcastView.vue')
          },
          {
            path: '/settings',
            name: 'settings',
            component:  ()=>import('../views/SettingsView.vue')
          },
          {
            path: '/about',
            name: 'about',
            component: () => import('../views/AboutView.vue'),
          },
      ]
    },
    
  ],
})

export default router
