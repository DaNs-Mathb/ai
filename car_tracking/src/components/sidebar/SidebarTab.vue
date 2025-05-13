<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const props = defineProps({
  name: { type: String, required: true },
  path: { type: String, required: true },
  beta: { type: Boolean, default: false }
})

const route = useRoute()
const isTabActive = computed(() => route.path.startsWith(props.path))
</script>

<template>
  <RouterLink
    :to="path"
    class="sidebar-tab"
    :class="{ active: isTabActive }"
    role="tab"
    :aria-selected="isTabActive"
  >
    <span v-if="beta" class="beta-sign" aria-label="Beta">β</span>
    <slot name="icon"></slot>
    <span class="text"><slot></slot></span>
  </RouterLink>
</template>

<style scoped>
.sidebar-tab {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 3px;
  padding: var(--padding) 3px;
  color: var(--sidebar-highlight);
  font-size: var(--sidebar-font-size);
  opacity: 0.75;
  height: fit-content;
  border-radius: var(--border-radius);
  transition: transform 0.2s;
  text-decoration: none;
  position: relative;
  cursor: pointer;
}

.sidebar-tab :deep(svg) {
  stroke-width: 1.2px;
  height: 22px;
  width: 22px;
}

.sidebar-tab.active {
  color: var(--sidebar-bg);
  background: var(--sidebar-highlight);
  opacity: 1;
  transform: none;
  transition: none;
  animation: pressButton 0.3s;
  cursor: default;
}

.sidebar-tab:not(.active):active {
  transform: scale(0.95);
}

.beta-sign {
  position: absolute;
  transform: translateX(16px) translateY(-6px);
  opacity: 0.7;
}

@keyframes pressButton {
  0% { transform: scale(0.9); }
  50% { transform: scale(1.015); }
  100% { transform: scale(1); }
}

@media (hover: hover) {
  .sidebar-tab:active:not(.active) {
    opacity: 1;
    background-color: var(--sidebar-hover);
  }
  
  .sidebar-tab:hover:not(.active) {
    opacity: 1;
    background-color: var(--sidebar-hover);
  }
}

@media screen and (max-width: 535px) {
  .sidebar-tab {
    padding: 5px var(--padding);
    min-width: calc(var(--sidebar-width) / 2);
  }
  
  .sidebar-tab.active {
    z-index: 2;
  }
  
  .sidebar-tab:active:not(.active) {
    transform: scale(0.9);
  }
  
  @keyframes pressButton {
    0% { transform: scale(0.8); }
    50% { transform: scale(1.02); }
    100% { transform: scale(1); }
  }
}
</style>