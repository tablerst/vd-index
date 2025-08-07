<template>
  <div class="scroll-indicator" :class="{ 'scroll-indicator--visible': visible }">
    <!-- 进度条 -->
    <div class="progress-track">
      <div 
        class="progress-fill" 
        :style="{ transform: `scaleY(${progress})` }"
      ></div>
    </div>
    
    <!-- 分屏指示点 -->
    <div class="section-dots">
      <button
        v-for="(section, index) in sections"
        :key="section.id"
        class="section-dot"
        :class="{
          'section-dot--active': index === currentSection,
          'section-dot--completed': index < currentSection,
          'section-dot--disabled': isMobileProgressBarDisabled
        }"
        @click="!isMobileProgressBarDisabled && $emit('goToSection', index)"
        :aria-label="`跳转到第${index + 1}屏`"
        :disabled="isMobileProgressBarDisabled"
      >
        <span class="dot-inner"></span>
        <span class="dot-label">{{ getSectionLabel(index) }}</span>
      </button>
    </div>
    
    <!-- 滚动提示 -->
    <div class="scroll-hint" v-if="showHint">
      <div class="hint-icon">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <path 
            d="M10 3V17M3 10L17 10" 
            stroke="currentColor" 
            stroke-width="2" 
            stroke-linecap="round"
          />
        </svg>
      </div>
      <span class="hint-text">滚动探索</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { SnapScrollSection } from '@/composables/useSnapScroll'

interface Props {
  currentSection: number
  sections: SnapScrollSection[]
  progress: number
  visible?: boolean
  showHint?: boolean
  isMobileProgressBarDisabled?: boolean
}

interface Emits {
  (e: 'goToSection', index: number): void
}

const props = withDefaults(defineProps<Props>(), {
  visible: true,
  showHint: false,
  isMobileProgressBarDisabled: false
})

defineEmits<Emits>()

// 获取section标签
const getSectionLabel = (index: number) => {
  const labels = ['首页', '成员', '活动']
  return labels[index] || `第${index + 1}屏`
}
</script>

<style scoped lang="scss">
@use '../styles/variables.scss' as *;

.scroll-indicator {
  position: fixed !important;
  right: 32px !important;
  top: 50% !important;
  transform: translateY(-50%) !important;
  z-index: 9999 !important;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-lg);
  opacity: 0;
  visibility: hidden;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(8px);
  padding: var(--spacing-md);
  border-radius: var(--radius-lg);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  
  &--visible {
    opacity: 1;
    visibility: visible;
    transform: translateY(-50%) translateX(0);
  }
  
  @include media-down(md) {
    right: var(--spacing-lg);
    gap: var(--spacing-md);
    padding: var(--spacing-sm);
  }
}

.progress-track {
  width: 3px;
  height: 140px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: var(--radius-full);
  position: relative;
  overflow: hidden;
  box-shadow: inset 0 0 4px rgba(0, 0, 0, 0.2);
  
  @include media-down(md) {
    height: 100px;
    width: 2px;
  }
}

.progress-fill {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(180deg, var(--primary), var(--primary-variant));
  border-radius: var(--radius-full);
  transform-origin: top;
  transition: transform 0.8s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 0 8px rgba(var(--primary-rgb), 0.5);
}

.section-dots {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  align-items: center;
}

.section-dot {
  position: relative;
  width: 16px;
  height: 16px;
  border: none;
  background: transparent;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  
  &:hover {
    transform: scale(1.3);
    
    .dot-inner {
      box-shadow: 0 0 16px rgba(255, 255, 255, 0.4);
    }
    
    .dot-label {
      opacity: 1;
      transform: translateX(-100%) scale(1);
    }
  }
  
  &--active {
    .dot-inner {
      background: var(--primary);
      box-shadow: 0 0 16px rgba(var(--primary-rgb), 0.8), 0 0 32px rgba(var(--primary-rgb), 0.4);
      transform: scale(1.4);
      border: 2px solid rgba(255, 255, 255, 0.3);
    }
  }
  
  &--completed {
    .dot-inner {
      background: var(--primary);
      opacity: 0.8;
      transform: scale(1.1);
    }
  }

  &--disabled {
    pointer-events: none;
    opacity: 0.4;
    cursor: default;

    .dot-inner {
      background: rgba(255, 255, 255, 0.2);
      border-color: rgba(255, 255, 255, 0.2);
    }

    .dot-label {
      color: rgba(255, 255, 255, 0.3);
      background: rgba(0, 0, 0, 0.4);
    }

    &:hover {
      transform: none;

      .dot-inner {
        transform: none;
        border: 1px solid rgba(255, 255, 255, 0.2);
      }
    }
  }

  @include media-down(md) {
    width: 12px;
    height: 12px;
  }
}

.dot-inner {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.5);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  
  @include media-down(md) {
    width: 8px;
    height: 8px;
  }
}

.dot-label {
  position: absolute;
  right: 100%;
  top: 50%;
  transform: translateY(-50%) translateX(-8px) scale(0.8);
  background: rgba(0, 0, 0, 0.8);
  color: var(--text-primary);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
  font-weight: 500;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(8px);
  
  &::after {
    content: '';
    position: absolute;
    left: 100%;
    top: 50%;
    transform: translateY(-50%);
    border: 4px solid transparent;
    border-left-color: rgba(0, 0, 0, 0.8);
  }
  
  @include media-down(md) {
    display: none;
  }
}

.scroll-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-xs);
  margin-top: var(--spacing-md);
  color: rgba(255, 255, 255, 0.6);
  animation: pulse 2s ease-in-out infinite;
  
  @include media-down(md) {
    margin-top: var(--spacing-sm);
  }
}

.hint-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  
  svg {
    width: 100%;
    height: 100%;
  }
  
  @include media-down(md) {
    width: 16px;
    height: 16px;
  }
}

.hint-text {
  font-size: var(--font-size-xs);
  font-weight: 400;
  writing-mode: vertical-rl;
  text-orientation: mixed;
  
  @include media-down(md) {
    font-size: 10px;
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 0.6;
    transform: translateY(0);
  }
  50% {
    opacity: 1;
    transform: translateY(-2px);
  }
}

// 主题适配
:root[data-theme="light"] {
  .scroll-indicator {
    .progress-track {
      background: rgba(0, 0, 0, 0.1);
    }
    
    .dot-inner {
      background: rgba(0, 0, 0, 0.3);
    }
    
    .dot-label {
      background: rgba(255, 255, 255, 0.95);
      color: var(--text-primary);
      
      &::after {
        border-left-color: rgba(255, 255, 255, 0.95);
      }
    }
    
    .scroll-hint {
      color: rgba(0, 0, 0, 0.6);
    }
  }
}

// 性能优化
.scroll-indicator {
  will-change: opacity, visibility;
  
  .progress-fill {
    will-change: transform;
  }
  
  .section-dot {
    will-change: transform;
  }
}

// 可访问性
@media (prefers-reduced-motion: reduce) {
  .scroll-indicator {
    .progress-fill,
    .section-dot,
    .dot-label {
      transition-duration: 0.1s;
    }
    
    .scroll-hint {
      animation: none;
    }
  }
}
</style>
