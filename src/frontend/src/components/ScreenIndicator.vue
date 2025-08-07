<template>
  <div class="screen-indicator" :class="{ 'is-visible': isVisible }">
    <div class="indicator-container">
      <div 
        v-for="(screen, index) in screens" 
        :key="index"
        class="indicator-dot"
        :class="{ 
          'is-active': index === activeIndex,
          'is-passed': index < activeIndex 
        }"
        @click="onDotClick(index)"
        :title="screen.title"
      >
        <div class="dot-inner"></div>
        <div class="dot-ripple"></div>
      </div>
    </div>
    
    <!-- 进度条 -->
    <div class="progress-bar">
      <div 
        class="progress-fill" 
        :style="{ transform: `scaleX(${progress})` }"
      ></div>
    </div>
    
    <!-- 屏幕标题 -->
    <div class="screen-title" v-if="currentScreen">
      {{ currentScreen.title }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import gsap from 'gsap'

interface Screen {
  title: string
  section: string
}

interface Props {
  screens: Screen[]
  activeIndex: number
  isVisible?: boolean
}

interface Emits {
  (e: 'goto', index: number): void
}

const props = withDefaults(defineProps<Props>(), {
  isVisible: true
})

const emit = defineEmits<Emits>()

const progress = computed(() => {
  if (props.screens.length <= 1) return 1
  return (props.activeIndex + 1) / props.screens.length
})

const currentScreen = computed(() => {
  return props.screens[props.activeIndex] || null
})

const onDotClick = (index: number) => {
  if (index === props.activeIndex) return
  
  // 添加点击动画
  const dot = document.querySelectorAll('.indicator-dot')[index]
  if (dot) {
    gsap.fromTo(dot.querySelector('.dot-ripple'), 
      { scale: 0, opacity: 0.8 },
      { scale: 2, opacity: 0, duration: 0.6, ease: 'power2.out' }
    )
  }
  
  emit('goto', index)
}

// 监听活跃索引变化，添加切换动画
watch(() => props.activeIndex, (newIndex, oldIndex) => {
  if (newIndex !== oldIndex) {
    // 标题切换动画
    const titleEl = document.querySelector('.screen-title')
    if (titleEl) {
      gsap.fromTo(titleEl, 
        { y: 20, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.5, ease: 'power2.out' }
      )
    }
  }
})
</script>

<style scoped>
.screen-indicator {
  position: fixed;
  right: 2rem;
  top: 50%;
  transform: translateY(-50%);
  z-index: 100;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
}

.screen-indicator.is-visible {
  opacity: 1;
  visibility: visible;
}

.indicator-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  align-items: center;
  margin-bottom: 1rem;
}

.indicator-dot {
  position: relative;
  width: 12px;
  height: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.indicator-dot:hover {
  transform: scale(1.2);
}

.dot-inner {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  border: 2px solid rgba(255, 255, 255, 0.5);
  transition: all 0.3s ease;
  position: relative;
  z-index: 2;
}

.indicator-dot.is-active .dot-inner {
  background: var(--primary-color, #00d4ff);
  border-color: var(--primary-color, #00d4ff);
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.6);
}

.indicator-dot.is-passed .dot-inner {
  background: rgba(0, 212, 255, 0.6);
  border-color: rgba(0, 212, 255, 0.8);
}

.dot-ripple {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: var(--primary-color, #00d4ff);
  transform: translate(-50%, -50%) scale(0);
  opacity: 0;
  pointer-events: none;
}

.progress-bar {
  width: 2px;
  height: 60px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 1px;
  overflow: hidden;
  margin: 0 auto 1rem;
}

.progress-fill {
  width: 100%;
  height: 100%;
  background: linear-gradient(
    to bottom,
    var(--primary-color, #00d4ff),
    var(--secondary-color, #ff6b9d)
  );
  transform-origin: top;
  transition: transform 0.6s ease;
}

.screen-title {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.8);
  text-align: center;
  writing-mode: vertical-rl;
  text-orientation: mixed;
  max-width: 100px;
  line-height: 1.2;
  font-weight: 500;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .screen-indicator {
    right: 1rem;
    transform: translateY(-50%) scale(0.8);
  }
  
  .indicator-container {
    gap: 0.8rem;
  }
  
  .indicator-dot {
    width: 10px;
    height: 10px;
  }
  
  .progress-bar {
    height: 40px;
  }
  
  .screen-title {
    font-size: 0.7rem;
  }
}

/* 横屏模式 */
@media (orientation: landscape) and (max-height: 600px) {
  .screen-indicator {
    right: 1rem;
    transform: translateY(-50%) scale(0.7);
  }
  
  .progress-bar {
    height: 30px;
  }
}

/* 高对比度模式 */
@media (prefers-contrast: high) {
  .dot-inner {
    border-width: 3px;
  }
  
  .indicator-dot.is-active .dot-inner {
    background: #ffffff;
    border-color: #ffffff;
  }
}

/* 减少动画模式 */
@media (prefers-reduced-motion: reduce) {
  .screen-indicator,
  .indicator-dot,
  .dot-inner,
  .progress-fill {
    transition: none !important;
  }
}
</style>
