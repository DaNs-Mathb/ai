<script setup lang="ts">
import { RouterLink } from 'vue-router'
// import IconDownload from '@/components/icons/IconDownload.vue'
// import IconSettings from '@/components/icons/IconSettings.vue'
// import IconRepeat from '@/components/icons/IconRepeat.vue'
// import IconHeart from '@/components/icons/IconHeart.vue'
// import IconInfo from '@/components/icons/IconInfo.vue'
</script>

<template>
  <aside class="sidebar">
    <div class="logo">Ремукс</div>
    
    <nav>
      <ul>
        <li>
          <RouterLink to="/">
            <IconDownload class="icon" />
            <span class="text">Главная</span>
          </RouterLink>
        </li>
        <!-- Остальные пункты меню -->
         <li>
          <RouterLink to="/remux">
            <IconRepeat class="icon" />
            <span>Ремукс</span>
          </RouterLink>
        </li>
        <li>
          <RouterLink to="/settings">
            <IconSettings class="icon" />
            <span>Настройки</span>
          </RouterLink>
        </li>
        <li>
          <RouterLink to="/donate">
            <IconHeart class="icon" />
            <span>Донаты</span>
          </RouterLink>
        </li>
        <li>
          <RouterLink to="/info">
            <IconInfo class="icon" />
            <span>Информация</span>
          </RouterLink>
        </li>
      </ul>
    </nav>
  </aside>
</template>

<style scoped>
.sidebar {
  --sidebar-width: 250px;
  --mobile-height: 70px;
  
  background: black;
  color: white;
  height: 100vh;
  width: var(--sidebar-width);
  position: fixed;
  left: 0;
  top: 0;
  padding: 1rem;
  z-index: 100;
}

nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

nav a {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: white;
  text-decoration: none;
  padding: 0.75rem;
  border-radius: 4px;
}

/* Десктопная версия (по умолчанию) */
@media (min-width: 769px) {
  .sidebar {
    height: 100vh;
    width: var(--sidebar-width);
    top: 0;
    bottom: auto;
  }
  
  nav a {
    flex-direction: row;
  }
}

/* Мобильная версия */
@media (max-width: 768px) {
  .sidebar {
    width: 100%;
    height: var(--mobile-height);
    bottom: 0;
    top: auto;
    padding: 0;
  }
  
  .logo {
    display: none;
  }
  
  nav ul {
    display: flex;
    height: 100%;
  }
  
  nav li {
    flex: 1;
    display: flex;
  margin: 0;
  }
  
  nav a {
    flex-direction: column;
    justify-content: center;
    font-size: 0.75rem;
    padding: 0.5rem;
    width: 100%;
  }
  
  .icon {
    width: 20px;
    height: 20px;
  }
}
</style>