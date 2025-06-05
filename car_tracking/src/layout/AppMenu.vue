<script setup>
import { ref } from 'vue';

import AppMenuItem from './AppMenuItem.vue';

const model = ref([
    {
        label: 'Главное',
        items: [{ label: 'Загрузки', icon: 'pi pi-fw pi-download', to: '/' },
                { label: 'Трансляции', icon: 'pi pi-fw pi-play', to: '/broadcast' }
        ]
        
    },
    {
        label: 'Дополнительно',
                items: [{ label: 'Настройки', icon: 'pi pi-fw pi-cog', to: '/settings' },
                        { label: 'Информация', icon: 'pi pi-fw pi-info-circle', to: '/about' },
                        { label: 'Источнки', icon: 'pi pi-fw pi-github', to: '/ауау' }
        ]
    },
    
]);
</script>

<template>
    <ul class="layout-menu">
        <template v-for="(item, i) in model" :key="item">
            <app-menu-item v-if="!item.separator" :item="item" :index="i"></app-menu-item>
            <li v-if="item.separator" class="menu-separator"></li>
        </template>
    </ul>
</template>

<style lang="scss" scoped></style>