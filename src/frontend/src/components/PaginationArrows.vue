<template>
  <div class="pagination-arrows">
    <!-- 左箭头 -->
    <button
      ref="prevBtnRef"
      class="arrow-btn arrow-btn--prev"
      :class="{ 'arrow-btn--disabled': currentPage <= 1 }"
      :disabled="currentPage <= 1"
      @click="goToPrevPage"
      @mouseenter="handleMouseEnter('prev')"
      @mouseleave="handleMouseLeave('prev')"
      aria-label="上一页"
    >
      <div class="arrow-bg"></div>
      <div class="arrow-icon">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
          <path 
            d="M15 18L9 12L15 6" 
            stroke="currentColor" 
            stroke-width="2" 
            stroke-linecap="round" 
            stroke-linejoin="round"
          />
        </svg>
      </div>
      <div class="arrow-glow"></div>
      <div class="arrow-particles">
        <div v-for="i in 6" :key="i" class="particle" :style="getParticleStyle(i, 'prev')"></div>
      </div>
    </button>

    <!-- 右箭头 -->
    <button
      ref="nextBtnRef"
      class="arrow-btn arrow-btn--next"
      :class="{ 'arrow-btn--disabled': currentPage >= totalPages }"
      :disabled="currentPage >= totalPages"
      @click="goToNextPage"
      @mouseenter="handleMouseEnter('next')"
      @mouseleave="handleMouseLeave('next')"
      aria-label="下一页"
    >
      <div class="arrow-bg"></div>
      <div class="arrow-icon">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
          <path 
            d="M9 18L15 12L9 6" 
            stroke="currentColor" 
            stroke-width="2" 
            stroke-linecap="round" 
            stroke-linejoin="round"
          />
        </svg>
      </div>
      <div class="arrow-glow"></div>
      <div class="arrow-particles">
        <div v-for="i in 6" :key="i" class="particle" :style="getParticleStyle(i, 'next')"></div>
      </div>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Props {
  currentPage: number
  totalPages: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'prev-page': []
  'next-page': []
}>()

const prevBtnRef = ref<HTMLButtonElement>()
const nextBtnRef = ref<HTMLButtonElement>()

const isHovering = ref<{ prev: boolean; next: boolean }>({
  prev: false,
  next: false
})

// 分页控制
const goToPrevPage = () => {
  if (props.currentPage > 1) {
    emit('prev-page')
  }
}

const goToNextPage = () => {
  if (props.currentPage < props.totalPages) {
    emit('next-page')
  }
}

// 鼠标悬停处理
const handleMouseEnter = (direction: 'prev' | 'next') => {
  isHovering.value[direction] = true
}

const handleMouseLeave = (direction: 'prev' | 'next') => {
  isHovering.value[direction] = false
}



// 粒子样式生成
const getParticleStyle = (index: number, direction: 'prev' | 'next') => {
  const angle = (index * 60) + (direction === 'prev' ? 180 : 0) // 每个粒子间隔60度
  const distance = 20 + (index % 3) * 5 // 不同距离
  
  return {
    '--angle': `${angle}deg`,
    '--distance': `${distance}px`,
    '--delay': `${index * 0.1}s`
  }
}
</script>

<style scoped lang="scss">
@use '../styles/variables.scss' as *;

.pagination-arrows {
  position: fixed;
  top: 50%;
  left: 0;
  right: 0;
  transform: translateY(-50%);
  display: flex;
  justify-content: space-between;
  pointer-events: none;
  z-index: 50;
  padding: 0 30px;

  @include media-down(md) {
    padding: 0 20px;
  }
}

.arrow-btn {
  position: relative;
  width: 60px;
  height: 60px;
  border: none;
  background: none;
  cursor: pointer;
  pointer-events: all;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-base);
  overflow: hidden;

  &:focus {
    outline: none;
  }

  &--disabled {
    opacity: 0.3;
    cursor: not-allowed;
    pointer-events: none;
  }

  @include media-down(md) {
    width: 50px;
    height: 50px;
  }
}

.arrow-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  border: 1px solid var(--primary-light);
  border-radius: 50%;
  transition: all var(--transition-base);
}

.arrow-icon {
  position: relative;
  z-index: 2;
  color: var(--secondary);
  transition: all var(--transition-base);

  svg {
    width: 24px;
    height: 24px;

    @include media-down(md) {
      width: 20px;
      height: 20px;
    }
  }
}

.arrow-glow {
  position: absolute;
  top: -10px;
  left: -10px;
  right: -10px;
  bottom: -10px;
  background: radial-gradient(circle, var(--primary-light) 0%, transparent 70%);
  border-radius: 50%;
  opacity: 0;
  scale: 1;
  transition: all var(--transition-base);
}

.arrow-particles {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.particle {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 4px;
  height: 4px;
  background: var(--secondary);
  border-radius: 50%;
  opacity: 0;
  scale: 0;
  transform: translate(-50%, -50%) 
            rotate(var(--angle)) 
            translateY(calc(-1 * var(--distance)));
  animation: particleFloat 2s infinite ease-in-out;
  animation-delay: var(--delay);

  &::after {
    content: '';
    position: absolute;
    top: -1px;
    left: -1px;
    right: -1px;
    bottom: -1px;
    background: var(--primary);
    border-radius: 50%;
    filter: blur(2px);
  }
}

// 冲击波效果
:global(.shockwave) {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 20px;
  height: 20px;
  border: 2px solid var(--secondary);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  pointer-events: none;
}

// 悬停效果
.arrow-btn:hover:not(.arrow-btn--disabled) {
  .arrow-bg {
    border-color: var(--secondary);
    box-shadow: var(--shadow-glow);
  }

  .arrow-icon {
    color: var(--primary);
  }
}

// 激活效果
.arrow-btn:active:not(.arrow-btn--disabled) {
  transform: scale(0.95);
}

@keyframes particleFloat {
  0%, 100% {
    transform: translate(-50%, -50%) 
               rotate(var(--angle)) 
               translateY(calc(-1 * var(--distance)));
  }
  50% {
    transform: translate(-50%, -50%) 
               rotate(var(--angle)) 
               translateY(calc(-1 * var(--distance) - 5px));
  }
}
</style>
