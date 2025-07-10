<template>
  <section id="hero" class="hero-section">

    <div class="container">
      <div class="hero-content">
        <!-- 环形粒子Canvas - 覆盖整个hero-content区域 -->
        <canvas ref="ringParticlesCanvas" class="ring-particles-canvas"></canvas>

        <!-- 2D 星环容器 -->
        <div class="ring-container" ref="ringContainer">
          <Ring2D
            ref="ring2d"
            :size="ringSize"
            :enable-parallax="!isMobile"
            :enable-breathing="true"
            :enable-pulse="true"
          />
        </div>

        <!-- 文本内容 -->
        <div class="hero-text">
          <h1 class="hero-title">
            <span class="title-line title-line--1">欢迎来到</span>
            <span class="title-line title-line--2">VRC Division</span>
          </h1>

          <p class="hero-subtitle">
            愿大家在VRC Division中收获自己的快乐
          </p>

          <!-- CTA 按钮 -->
          <div class="hero-actions">
            <button
              class="cta-button interactive"
              @click="scrollToMembers"
              aria-label="探索成员星云"
            >
              <span class="cta-text">探索成员星云</span>
              <div class="cta-ripple"></div>
              <svg class="cta-icon" width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M10 3L10 17M3 10L17 10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </button>

            <button class="secondary-button interactive">
              <span>了解更多</span>
            </button>
          </div>
        </div>
      </div>
    </div>





    <!-- 滚动指示器 -->
    <div class="scroll-indicator">
      <div class="scroll-mouse">
        <div class="scroll-wheel"></div>
      </div>
      <span class="scroll-text">向下滚动探索</span>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { performanceOptimizer } from '../utils/performanceOptimizer'
import Ring2D from './Ring2D.vue'

const ringContainer = ref<HTMLElement>()
const ring2d = ref<{ getCenter: () => { x: number; y: number } }>()
const ringParticlesCanvas = ref<HTMLCanvasElement>()

// 响应式计算
const isMobile = computed(() => {
  if (typeof window === 'undefined') return false
  return window.innerWidth <= 768
})

const ringSize = computed(() => {
  if (isMobile.value) return 320
  return 520
})

// 同步粒子中心位置
const syncParticleCenter = () => {
  if (!ring2d.value || !ringParticlesCanvas.value) return

  // 获取星环的绝对坐标
  const ringCenter = ring2d.value.getCenter()

  // 获取粒子Canvas的位置，转换为相对于Canvas的坐标
  const canvasRect = ringParticlesCanvas.value.getBoundingClientRect()
  const relativeX = ringCenter.x - canvasRect.left
  const relativeY = ringCenter.y - canvasRect.top

  // 发送相对坐标给Worker
  if (particleWorker) {
    particleWorker.postMessage({
      type: 'updateCenter',
      x: relativeX,
      y: relativeY
    })
  }
}

let particleWorker: Worker | null = null

// 检测浏览器兼容性
const checkBrowserCompatibility = () => {
  const features = {
    offscreenCanvas: typeof OffscreenCanvas !== 'undefined',
    transferControlToOffscreen: HTMLCanvasElement.prototype.transferControlToOffscreen !== undefined,
    webWorkers: typeof Worker !== 'undefined',
    webWorkerModules: false
  }

  // 检测 Web Worker 模块支持
  try {
    new Worker('data:text/javascript,', { type: 'module' })
    features.webWorkerModules = true
  } catch (e) {
    features.webWorkerModules = false
  }

  console.log('Browser compatibility check:', features)
  return features
}

// 初始化环形粒子Canvas
const initRingParticles = (): (() => void) => {
  const canvas = ringParticlesCanvas.value
  if (!canvas) {
    console.warn('Ring particles canvas not found')
    return () => {}
  }

  // 检测浏览器兼容性
  const compatibility = checkBrowserCompatibility()

  if (!compatibility.offscreenCanvas || !compatibility.transferControlToOffscreen || !compatibility.webWorkers) {
    console.warn('Browser does not support required features for OffscreenCanvas, using fallback')
    return initRingParticlesFallback()
  }

  try {

    // 转换为离屏 Canvas
    const offscreen = canvas.transferControlToOffscreen()

    // 创建 Worker
    particleWorker = new Worker(new URL('../utils/ringParticlesWorker.ts', import.meta.url), { type: 'module' })

    // Worker 错误处理
    particleWorker.onerror = (error) => {
      console.error('Ring particles worker error:', error)
      // 尝试降级方案
      if (particleWorker) {
        particleWorker.terminate()
        particleWorker = null
      }
      return initRingParticlesFallback()
    }

    // Worker 消息监听
    particleWorker.onmessage = (e) => {
      const { type, error } = e.data
      if (type === 'error') {
        console.error('Ring particles worker reported error:', error)
        // 切换到降级方案
        if (particleWorker) {
          particleWorker.terminate()
          particleWorker = null
        }
        return initRingParticlesFallback()
      } else if (type === 'initialized') {
        console.log('Ring particles worker initialized successfully')
      }
    }

    // 检测性能设置
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

  // 初始化并同步尺寸
  const resizeCanvas = () => {
    const rect = (canvas.parentElement as HTMLElement).getBoundingClientRect()
    offscreen.width = rect.width
    offscreen.height = rect.height
    // 只有在 worker 已初始化后才发送 resize 消息
    if (particleWorker) {
      particleWorker.postMessage({ type: 'resize', width: rect.width, height: rect.height })
    }

    // 尺寸变化时同步粒子中心
    setTimeout(syncParticleCenter, 50)
  }

  // 获取初始尺寸
  const rect = (canvas.parentElement as HTMLElement).getBoundingClientRect()
  offscreen.width = rect.width
  offscreen.height = rect.height

  // 发送初始化消息
  particleWorker.postMessage(
    { type: 'init', canvas: offscreen, width: offscreen.width, height: offscreen.height },
    [offscreen]
  )

  // 发送性能设置
  particleWorker.postMessage({
    type: 'setPerformance',
    options: {
      reducedMotion: prefersReducedMotion,
      isMobile: isMobile.value,
      performanceLevel: performanceOptimizer.getCurrentLevel(),
      adaptiveQuality: true
    }
  })

  // 窗口尺寸变化
  window.addEventListener('resize', resizeCanvas)

  // 页面可见性切换
  const handleVisibility = () => {
    particleWorker!.postMessage({ type: document.hidden ? 'pause' : 'resume' })
  }
  document.addEventListener('visibilitychange', handleVisibility)

  // 监听动画偏好变化
  const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
  const handleMotionChange = () => {
    if (particleWorker) {
      particleWorker.postMessage({
        type: 'setPerformance',
        options: { reducedMotion: motionQuery.matches }
      })
    }
  }
  motionQuery.addEventListener('change', handleMotionChange)

    // 返回清理函数
    return () => {
      window.removeEventListener('resize', resizeCanvas)
      document.removeEventListener('visibilitychange', handleVisibility)
      motionQuery.removeEventListener('change', handleMotionChange)
      if (particleWorker) {
        particleWorker.postMessage({ type: 'dispose' })
        particleWorker.terminate()
        particleWorker = null
      }
    }
  } catch (error) {
    console.error('Failed to initialize ring particles with OffscreenCanvas:', error)
    return initRingParticlesFallback()
  }
}

// 降级方案：使用传统 Canvas 渲染
const initRingParticlesFallback = (): (() => void) => {
  const canvas = ringParticlesCanvas.value
  if (!canvas) return () => {}

  console.log('Using fallback canvas rendering for ring particles')

  const ctx = canvas.getContext('2d')
  if (!ctx) {
    console.error('Failed to get 2D context for fallback canvas')
    return () => {}
  }

  // 简化的粒子系统（不使用 Worker）
  let animationId: number
  let particles: Array<{
    x: number; y: number; angle: number; radius: number;
    size: number; opacity: number; color: string; speed: number;
  }> = []

  const createFallbackParticles = () => {
    particles = []
    const centerX = canvas.width / 2
    const centerY = canvas.height / 2
    const baseRadius = Math.min(canvas.width, canvas.height) * 0.35

    for (let i = 0; i < 60; i++) {
      particles.push({
        x: centerX,
        y: centerY,
        angle: (i / 60) * Math.PI * 2,
        radius: baseRadius + Math.random() * 50,
        size: 1 + Math.random() * 2,
        opacity: 0.3 + Math.random() * 0.4,
        color: ['#AA83FF', '#D4DEC7', '#3F7DFB'][Math.floor(Math.random() * 3)],
        speed: 0.005 + Math.random() * 0.01
      })
    }
  }

  const animateFallback = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    particles.forEach(p => {
      p.angle += p.speed
      const x = canvas.width / 2 + Math.cos(p.angle) * p.radius
      const y = canvas.height / 2 + Math.sin(p.angle) * p.radius

      ctx.globalAlpha = p.opacity
      ctx.fillStyle = p.color
      ctx.beginPath()
      ctx.arc(x, y, p.size, 0, Math.PI * 2)
      ctx.fill()
    })

    animationId = requestAnimationFrame(animateFallback)
  }

  const resizeFallback = () => {
    const rect = (canvas.parentElement as HTMLElement).getBoundingClientRect()
    canvas.width = rect.width
    canvas.height = rect.height
    createFallbackParticles()
  }

  resizeFallback()
  createFallbackParticles()
  animateFallback()

  window.addEventListener('resize', resizeFallback)

  return () => {
    window.removeEventListener('resize', resizeFallback)
    if (animationId) {
      cancelAnimationFrame(animationId)
    }
  }
}

let particleCleanup: (() => void) | null = null

// 滚动到成员区域
const scrollToMembers = () => {
  const membersSection = document.getElementById('members')
  if (membersSection) {
    membersSection.scrollIntoView({ 
      behavior: 'smooth',
      block: 'start'
    })
  }
}

onMounted(() => {
  // 添加调试信息
  console.log('HeroSection mounted, initializing ring particles...')

  // 延迟初始化以确保 DOM 完全加载
  setTimeout(() => {
    // 初始化粒子系统
    particleCleanup = initRingParticles()

    // 初始化完成后同步粒子中心
    setTimeout(syncParticleCenter, 100)
  }, 100)
})

onUnmounted(() => {
  // 清理粒子系统
  if (particleCleanup) particleCleanup()
})
</script>

<style scoped lang="scss">
@use '../styles/variables.scss' as *;

.hero-section {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: var(--base-dark);
  
  // 渐变背景
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(
      ellipse at center,
      rgba(170, 131, 255, 0.1) 0%,
      rgba(14, 16, 22, 0.8) 50%,
      var(--base-dark) 100%
    );
    z-index: 1;
  }
}

.hero-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-3xl);
  align-items: center;
  position: relative;
  z-index: 2;

  @include media-down(lg) {
    grid-template-columns: 1fr;
    gap: var(--spacing-2xl);
    text-align: center;
  }
}

/* 环形粒子Canvas样式 - 覆盖整个hero-content区域 */
.ring-particles-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1; /* 在文本内容之下，但在背景之上 */
}

.ring-container {
  position: relative;
  width: 100%;
  height: 600px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: visible;
  pointer-events: none;
  z-index: 2;

  @include media-down(md) {
    height: 400px;
  }

  @include media-down(sm) {
    height: 300px;
  }
}



.hero-text {
  position: relative;
  z-index: 3; /* 确保文本在粒子之上 */
  
  .hero-title {
    font-size: var(--font-size-5xl);
    font-weight: var(--font-weight-bold);
    line-height: var(--line-height-tight);
    margin-bottom: var(--spacing-lg);
    
    @include media-down(md) {
      font-size: var(--font-size-4xl);
    }
    
    .title-line {
      display: block;
      opacity: 0;
      transform: translateY(30px);
      animation: titleSlideIn 0.8s ease-out forwards;
      
      &--1 {
        color: var(--text-secondary);
        animation-delay: 0.2s;
      }
      
      &--2 {
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation-delay: 0.4s;
      }
    }
  }
  
  .hero-subtitle {
    font-size: var(--font-size-xl);
    color: var(--text-secondary);
    margin-bottom: var(--spacing-2xl);
    opacity: 0;
    transform: translateY(20px);
    animation: titleSlideIn 0.8s ease-out 0.6s forwards;
    
    @include media-down(md) {
      font-size: var(--font-size-lg);
    }
  }
}

.hero-actions {
  display: flex;
  gap: var(--spacing-lg);
  opacity: 0;
  transform: translateY(20px);
  animation: titleSlideIn 0.8s ease-out 0.8s forwards;
  
  @include media-down(sm) {
    flex-direction: column;
    align-items: center;
  }
}

.cta-button {
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md) var(--spacing-xl);
  background: var(--secondary-gradient);
  color: var(--base-dark);
  border-radius: var(--radius-lg);
  font-weight: var(--font-weight-semibold);
  font-size: var(--font-size-lg);
  box-shadow: var(--shadow-green-glow);
  transition: all var(--transition-base) var(--ease-hover);
  overflow: hidden;

  &:hover {
    transform: translateY(-4px);
    background: var(--mixed-gradient);
    color: white;
    box-shadow: var(--shadow-mixed-glow);

    .cta-icon {
      transform: rotate(45deg);
    }
  }
  
  &:active {
    transform: translateY(-2px);
    
    .cta-ripple {
      animation: rippleEffect 1s ease-out;
    }
  }
  
  .cta-icon {
    transition: transform var(--transition-base);
  }
  
  .cta-ripple {
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    background: rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    transform: translate(-50%, -50%);
  }
}

.secondary-button {
  padding: var(--spacing-md) var(--spacing-xl);
  background: transparent;
  border: var(--border-secondary);
  color: var(--secondary);
  border-radius: var(--radius-lg);
  font-weight: var(--font-weight-medium);
  font-size: var(--font-size-lg);
  transition: all var(--transition-base) var(--ease-hover);

  &:hover {
    @include magnetic-hover(4px);
    background: var(--secondary);
    color: var(--base-dark);
    box-shadow: var(--shadow-green-glow);
  }
}





.scroll-indicator {
  position: absolute;
  bottom: var(--spacing-2xl);
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-sm);
  color: var(--text-muted);
  animation: scrollBounce 2s ease-in-out infinite;
  
  .scroll-mouse {
    width: 24px;
    height: 40px;
    border: 2px solid var(--text-muted);
    border-radius: 12px;
    position: relative;
    
    .scroll-wheel {
      width: 4px;
      height: 8px;
      background: var(--text-muted);
      border-radius: 2px;
      position: absolute;
      top: 6px;
      left: 50%;
      transform: translateX(-50%);
      animation: scrollWheel 2s ease-in-out infinite;
    }
  }
  
  .scroll-text {
    font-size: var(--font-size-xs);
    text-transform: uppercase;
    letter-spacing: 1px;
  }
}

// 动画定义
@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes portalRotate {
  to { transform: rotate(360deg); }
}

@keyframes portalPulse {
  0%, 100% { opacity: 0.8; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.1); }
}

@keyframes titleSlideIn {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes rippleEffect {
  to {
    width: 300px;
    height: 300px;
    opacity: 0;
  }
}





@keyframes scrollBounce {
  0%, 100% { transform: translateX(-50%) translateY(0); }
  50% { transform: translateX(-50%) translateY(-10px); }
}

@keyframes scrollWheel {
  0% { top: 6px; opacity: 1; }
  50% { top: 16px; opacity: 0.5; }
  100% { top: 6px; opacity: 1; }
}


</style>
