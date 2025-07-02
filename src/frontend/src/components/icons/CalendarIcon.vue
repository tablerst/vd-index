<template>
  <svg 
    width="20" 
    height="20" 
    viewBox="0 0 24 24" 
    fill="none"
    class="calendar-icon"
    :class="{ 'calendar-icon--hover': isHovered }"
    @mouseenter="isHovered = true"
    @mouseleave="isHovered = false"
  >
    <rect 
      x="3" 
      y="4" 
      width="18" 
      height="18" 
      rx="3" 
      stroke="currentColor" 
      stroke-width="2"
    />
    <path 
      d="M16 2V6" 
      stroke="currentColor" 
      stroke-width="2" 
      stroke-linecap="round"
    />
    <path 
      d="M8 2V6"  
      stroke="currentColor" 
      stroke-width="2" 
      stroke-linecap="round"
    />
    <path 
      d="M3 10H21" 
      stroke="currentColor" 
      stroke-width="2" 
      stroke-linecap="round"
    />
    <!-- 日期点 -->
    <circle cx="8" cy="15" r="1" fill="currentColor" />
    <circle cx="12" cy="15" r="1" fill="currentColor" />
    <circle cx="16" cy="15" r="1" fill="currentColor" />
  </svg>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const isHovered = ref(false)
</script>

<style scoped>
.calendar-icon {
  color: var(--text-secondary);
  transition: all 0.4s var(--ease-hover);
  transform-origin: center;
}

.calendar-icon--hover {
  color: var(--primary);
  transform: rotateY(180deg) scale(1.1);
}

.calendar-icon:hover {
  filter: drop-shadow(0 0 8px rgba(170, 131, 255, 0.4));
}
</style>
