<template>
  <div class="progress-bar" :class="{ 'progress-bar--visible': visible }">
    <div class="progress-track">
      <div 
        class="progress-fill" 
        :style="{ width: `${progressPercentage}%` }"
      ></div>
    </div>
    <div class="progress-info">
      <span class="current-page">{{ current }}</span>
      <span class="separator">/</span>
      <span class="total-pages">{{ total }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  current: number
  total: number
  visible?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  visible: true
})

const progressPercentage = computed(() => {
  if (props.total === 0) return 0
  return (props.current / props.total) * 100
})
</script>

<style scoped lang="scss">
@use '../styles/variables.scss' as *;

.progress-bar {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 100;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  box-shadow: var(--shadow-soft);
  opacity: 0;
  transform: translateY(-10px);
  transition: all var(--transition-base) var(--ease-hover);

  &--visible {
    opacity: 1;
    transform: translateY(0);
  }

  @include media-down(md) {
    top: 10px;
    right: 10px;
    padding: 6px 12px;
    gap: 8px;
  }
}

.progress-track {
  width: 80px;
  height: 4px;
  background: var(--primary-light);
  border-radius: 2px;
  overflow: hidden;

  @include media-down(md) {
    width: 60px;
    height: 3px;
  }
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--secondary), var(--primary));
  border-radius: 2px;
  transition: width 0.6s var(--ease-hover);
  position: relative;

  &::after {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 20px;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3));
    animation: shimmer 2s infinite;
  }
}

.progress-info {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);

  @include media-down(md) {
    font-size: 11px;
  }
}

.current-page {
  color: var(--secondary);
  font-weight: 600;
}

.separator {
  opacity: 0.6;
  margin: 0 2px;
}

.total-pages {
  opacity: 0.8;
}

@keyframes shimmer {
  0% {
    transform: translateX(-20px);
    opacity: 0;
  }
  50% {
    opacity: 1;
  }
  100% {
    transform: translateX(20px);
    opacity: 0;
  }
}
</style>
