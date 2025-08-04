<template>
  <div class="custom-pointer" ref="pointerRef">
    <!-- 主光标圆点 -->
    <div class="pointer-dot" :class="{ 'pointer-dot--pressed': isPressed }"></div>
    
    <!-- 漫射渐变光晕 -->
    <div class="pointer-glow" :class="{ 'pointer-glow--pressed': isPressed }"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, inject, watch } from 'vue'
import { useThemeStore } from '../stores/theme'
import { performanceProfiler } from '../utils/performanceProfiler'

const pointerRef = ref<HTMLElement>()
const isPressed = ref(false)
const isVisible = ref(true)
const isMouseInWindow = ref(true)
const isPaused = ref(false) // 新增：暂停状态

let mouseX = 0
let mouseY = 0
let currentX = 0
let currentY = 0
let animationId: number | null = null
let isAnimating = false
let isInitialized = false

// 简化的性能配置
const EASE_NORMAL = 0.25
const EASE_FAST = 0.4
const SPEED_THRESHOLD = 50

// 模态框状态监听
const modalState = inject('modalState', ref(false))

// 主题store
const themeStore = useThemeStore()

// 监听模态框状态变化
watch(modalState, (isOpen: boolean) => {
  if (isOpen) {
    pauseAnimation()
  } else {
    resumeAnimation()
  }
}, { immediate: false })

// 简化的ease计算
const calculateEase = () => {
  const dx = mouseX - currentX
  const dy = mouseY - currentY
  const distance = Math.sqrt(dx * dx + dy * dy)

  return distance > SPEED_THRESHOLD ? EASE_FAST : EASE_NORMAL
}

// 优化的平滑跟随动画
const animatePointer = () => {
  if (!isAnimating || !isVisible.value || !isMouseInWindow.value || !isInitialized || isPaused.value) {
    animationId = null
    return
  }

  // 性能标记开始
  performanceProfiler.mark('pointer-animation-frame')

  const ease = calculateEase()
  currentX += (mouseX - currentX) * ease
  currentY += (mouseY - currentY) * ease

  if (pointerRef.value) {
    // 使用transform3d确保硬件加速
    pointerRef.value.style.transform = `translate3d(${currentX}px, ${currentY}px, 0)`
  }

  // 性能标记结束
  performanceProfiler.measure('pointer-animation-frame')

  animationId = requestAnimationFrame(animatePointer)
}

// 启动动画
const startAnimation = () => {
  if (!isInitialized || isPaused.value) return

  if (!isAnimating && isVisible.value && isMouseInWindow.value) {
    isAnimating = true
    performanceProfiler.mark('pointer-animation-start')
    animatePointer()
  }
}

// 停止动画
const stopAnimation = () => {
  isAnimating = false
  if (animationId) {
    cancelAnimationFrame(animationId)
    animationId = null
    performanceProfiler.measure('pointer-animation-start')
  }
}

// 暂停/恢复动画
const pauseAnimation = () => {
  isPaused.value = true
  stopAnimation()
}

const resumeAnimation = () => {
  isPaused.value = false
  if (isVisible.value && isMouseInWindow.value && isInitialized) {
    startAnimation()
  }
}

// 重置光标状态
const resetPointer = () => {
  if (pointerRef.value) {
    currentX = mouseX
    currentY = mouseY
    pointerRef.value.style.transform = `translate3d(${currentX}px, ${currentY}px, 0)`
    pointerRef.value.style.opacity = '1'
  }
}

// 暴露控制方法给父组件
defineExpose({
  pause: pauseAnimation,
  resume: resumeAnimation,
  reset: resetPointer,
  isAnimating: () => isAnimating,
  isPaused: () => isPaused.value
})

// 鼠标移动事件
const handleMouseMove = (e: MouseEvent) => {
  mouseX = e.clientX
  mouseY = e.clientY

  // 确保鼠标在窗口内
  if (!isMouseInWindow.value) {
    isMouseInWindow.value = true
  }

  // 如果动画未运行且页面可见，启动动画
  if (!isAnimating && isVisible.value && isInitialized) {
    startAnimation()
  }
}

// 鼠标按下事件
const handleMouseDown = () => {
  isPressed.value = true
}

// 鼠标释放事件
const handleMouseUp = () => {
  isPressed.value = false
}

// 鼠标进入窗口
const handleMouseEnterWindow = () => {
  isMouseInWindow.value = true

  if (isVisible.value && isInitialized) {
    resetPointer()
    startAnimation()
  }
}

// 鼠标离开窗口 - 改进事件处理逻辑
const handleMouseLeaveWindow = (e: MouseEvent) => {
  // 只有真正离开浏览器窗口时才停止动画
  if (e.clientX <= 0 || e.clientX >= window.innerWidth ||
      e.clientY <= 0 || e.clientY >= window.innerHeight) {
    isMouseInWindow.value = false
    stopAnimation()

    // 隐藏光标但不移除
    if (pointerRef.value) {
      pointerRef.value.style.opacity = '0'
    }
  }
}

// 页面可见性变化
const handleVisibilityChange = () => {
  const wasVisible = isVisible.value
  isVisible.value = !document.hidden

  if (isVisible.value && isMouseInWindow.value && isInitialized) {
    if (!wasVisible) {
      resetPointer()
    }
    setTimeout(() => {
      startAnimation()
    }, 100)
  } else {
    stopAnimation()
  }
}

// 窗口焦点变化
const handleWindowFocus = () => {
  isVisible.value = true

  if (isMouseInWindow.value && isInitialized) {
    resetPointer()
    startAnimation()
  }
}

const handleWindowBlur = () => {
  isVisible.value = false
  stopAnimation()
}

// 鼠标进入可交互元素
const handleMouseEnter = (e: MouseEvent) => {
  const target = e.target as HTMLElement
  // 检查 target 是否是 HTMLElement 并且有 matches 方法
  if (target && typeof target.matches === 'function' &&
      target.matches('button, a, [role="button"], .interactive, input, textarea, select')) {
    pointerRef.value?.classList.add('pointer--interactive')
  }
}

// 鼠标离开可交互元素
const handleMouseLeave = (e: MouseEvent) => {
  const target = e.target as HTMLElement
  // 检查 target 是否是 HTMLElement 并且有 matches 方法
  if (target && typeof target.matches === 'function' &&
      target.matches('button, a, [role="button"], .interactive, input, textarea, select')) {
    pointerRef.value?.classList.remove('pointer--interactive')
  }
}

onMounted(() => {
  // 强制隐藏默认光标
  document.documentElement.style.cursor = 'none'
  document.body.style.cursor = 'none'

  // 添加全局样式确保所有元素都不显示光标
  const style = document.createElement('style')
  style.textContent = `
    *, *::before, *::after {
      cursor: none !important;
    }
  `
  document.head.appendChild(style)

  // 初始化鼠标位置
  const initMousePosition = (e: MouseEvent) => {
    mouseX = e.clientX
    mouseY = e.clientY
    currentX = mouseX
    currentY = mouseY

    if (pointerRef.value) {
      pointerRef.value.style.transform = `translate3d(${currentX}px, ${currentY}px, 0)`
      pointerRef.value.style.opacity = '1'
    }

    isInitialized = true
    document.removeEventListener('mousemove', initMousePosition)
  }

  // 添加事件监听器
  document.addEventListener('mousemove', initMousePosition, { once: true, passive: true })
  document.addEventListener('mousemove', handleMouseMove, { passive: true })
  document.addEventListener('mousedown', handleMouseDown)
  document.addEventListener('mouseup', handleMouseUp)
  document.addEventListener('mouseenter', handleMouseEnter, true)
  document.addEventListener('mouseleave', handleMouseLeave, true)

  // 页面可见性和焦点事件
  document.addEventListener('visibilitychange', handleVisibilityChange)
  window.addEventListener('focus', handleWindowFocus)
  window.addEventListener('blur', handleWindowBlur)

  // 使用window来监听鼠标进入/离开，提高稳定性
  window.addEventListener('mouseenter', handleMouseEnterWindow)
  window.addEventListener('mouseleave', handleMouseLeaveWindow)

  // 延迟启动动画，确保初始化完成
  setTimeout(() => {
    if (isInitialized) {
      startAnimation()
    }
  }, 100)
})

onUnmounted(() => {
  // 停止动画
  stopAnimation()

  // 恢复默认光标
  document.documentElement.style.cursor = ''
  document.body.style.cursor = ''

  // 移除添加的样式
  const customStyles = document.head.querySelectorAll('style')
  customStyles.forEach(style => {
    if (style.textContent?.includes('cursor: none !important')) {
      style.remove()
    }
  })

  // 移除事件监听器
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mousedown', handleMouseDown)
  document.removeEventListener('mouseup', handleMouseUp)
  document.removeEventListener('mouseenter', handleMouseEnter, true)
  document.removeEventListener('mouseleave', handleMouseLeave, true)
  document.removeEventListener('visibilitychange', handleVisibilityChange)
  window.removeEventListener('focus', handleWindowFocus)
  window.removeEventListener('blur', handleWindowBlur)
  window.removeEventListener('mouseenter', handleMouseEnterWindow)
  window.removeEventListener('mouseleave', handleMouseLeaveWindow)
})
</script>

<style scoped lang="scss">
@use '../styles/variables.scss' as *;
@use '../styles/theme-utils.scss' as *;

.custom-pointer {
  position: fixed;
  top: 0;
  left: 0;
  width: 20px;
  height: 20px;
  pointer-events: none;
  z-index: 9999;
  // 移除 mix-blend-mode，改用主题感知的颜色
  opacity: 1;
  transition: opacity 0.2s ease;
  will-change: transform, opacity;

  // 在移动设备上隐藏
  @media (hover: none) and (pointer: coarse) {
    display: none;
  }
}

.pointer-dot {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 8px;
  height: 8px;
  background: var(--particle-secondary);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  transition: all 0.86s var(--ease-pointer);
  animation: breathe 3s ease-in-out infinite;
  box-shadow: 0 0 8px var(--particle-secondary);

  // 按下状态
  &--pressed {
    transform: translate(-50%, -50%) scale(0.75);
    background: var(--particle-primary);
    box-shadow: 0 0 20px var(--particle-primary);
  }
}

.pointer-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 40px;
  height: 40px;
  background: radial-gradient(
    circle,
    var(--secondary-light) 0%,
    var(--secondary-lighter) 50%,
    transparent 100%
  );
  border-radius: 50%;
  transform: translate(-50%, -50%);
  transition: all 0.86s var(--ease-pointer);
  animation: breathe 3s ease-in-out infinite reverse;

  // 按下状态
  &--pressed {
    width: 60px;
    height: 60px;
    background: radial-gradient(
      circle,
      var(--primary-light) 0%,
      var(--primary-lighter) 50%,
      transparent 100%
    );
  }
}

// 交互状态样式
.custom-pointer.pointer--interactive {
  .pointer-dot {
    width: 12px;
    height: 12px;
    background: var(--particle-primary);
    box-shadow: 0 0 15px var(--particle-primary);
  }

  .pointer-glow {
    width: 50px;
    height: 50px;
    background: radial-gradient(
      circle,
      var(--primary-light) 0%,
      var(--primary-lighter) 50%,
      transparent 100%
    );
  }
}

// 呼吸动画
@keyframes breathe {
  0%, 100% {
    opacity: 0.7;
    transform: translate(-50%, -50%) scale(1);
  }
  50% {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1.1);
  }
}

// 在不支持自定义光标的设备上隐藏
@media (pointer: coarse) {
  .custom-pointer {
    display: none !important;
  }
}
</style>
