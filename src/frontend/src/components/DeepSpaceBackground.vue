<template>
  <div class="deep-space-background">
    <!-- 深空渐变背景 -->
    <div class="space-gradient"></div>
    
    <!-- 星空粒子层 -->
    <canvas 
      ref="starsCanvas"
      class="stars-canvas"
      :width="canvasSize.width"
      :height="canvasSize.height"
    ></canvas>
    
    <!-- 星云粒子层 -->
    <canvas 
      ref="nebulaCanvas"
      class="nebula-canvas"
      :width="canvasSize.width"
      :height="canvasSize.height"
    ></canvas>
    
    <!-- 流动粒子层 -->
    <canvas 
      ref="flowingCanvas"
      class="flowing-canvas"
      :width="canvasSize.width"
      :height="canvasSize.height"
    ></canvas>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useThemeStore } from '../stores/theme'

const starsCanvas = ref<HTMLCanvasElement>()
const nebulaCanvas = ref<HTMLCanvasElement>()
const flowingCanvas = ref<HTMLCanvasElement>()

// Canvas尺寸
const canvasSize = computed(() => ({
  width: window.innerWidth,
  height: window.innerHeight
}))

// 粒子类型定义
interface Star {
  x: number
  y: number
  size: number
  opacity: number
  twinkleSpeed: number
  twinklePhase: number
}

interface NebulaParticle {
  x: number
  y: number
  size: number
  opacity: number
  color: string
  driftX: number
  driftY: number
  speed: number
}

interface FlowingParticle {
  x: number
  y: number
  vx: number
  vy: number
  size: number
  opacity: number
  life: number
  maxLife: number
}

// 粒子数组
const stars = ref<Star[]>([])
const nebulaParticles = ref<NebulaParticle[]>([])
const flowingParticles = ref<FlowingParticle[]>([])

// 动画控制
let animationId: number
let isVisible = true

// 主题store
const themeStore = useThemeStore()

// 监听主题变化
watch(() => themeStore.currentTheme, () => {
  // 主题切换时重新初始化粒子
  initStars()
  initNebula()
  initFlowingParticles()
})

// 初始化星空粒子
const initStars = () => {
  const canvas = starsCanvas.value
  if (!canvas) return

  stars.value = []
  const starCount = Math.floor((canvas.width * canvas.height) / 8000) // 根据屏幕大小调整密度

  for (let i = 0; i < starCount; i++) {
    stars.value.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      size: Math.random() * 2 + 0.5,
      opacity: Math.random() * 0.8 + 0.2,
      twinkleSpeed: Math.random() * 0.02 + 0.01,
      twinklePhase: Math.random() * Math.PI * 2
    })
  }
}

// 初始化星云粒子
const initNebula = () => {
  const canvas = nebulaCanvas.value
  if (!canvas) return

  nebulaParticles.value = []
  const nebulaCount = Math.floor((canvas.width * canvas.height) / 15000)

  const colors = [
    'rgba(170, 131, 255, 0.1)', // 紫色
    'rgba(212, 222, 199, 0.08)', // 绿色
    'rgba(100, 150, 255, 0.06)', // 蓝色
    'rgba(255, 180, 120, 0.05)'  // 橙色
  ]

  for (let i = 0; i < nebulaCount; i++) {
    nebulaParticles.value.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      size: Math.random() * 40 + 20,
      opacity: Math.random() * 0.3 + 0.1,
      color: colors[Math.floor(Math.random() * colors.length)],
      driftX: (Math.random() - 0.5) * 0.5,
      driftY: (Math.random() - 0.5) * 0.5,
      speed: Math.random() * 0.2 + 0.1
    })
  }
}

// 初始化流动粒子
const initFlowingParticles = () => {
  const canvas = flowingCanvas.value
  if (!canvas) return

  flowingParticles.value = []
  // 流动粒子会在动画中动态生成
}

// 绘制星空
const drawStars = () => {
  const canvas = starsCanvas.value
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  ctx.clearRect(0, 0, canvas.width, canvas.height)

  stars.value.forEach(star => {
    // 闪烁效果
    star.twinklePhase += star.twinkleSpeed
    const twinkle = Math.sin(star.twinklePhase) * 0.3 + 0.7

    ctx.beginPath()
    ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2)
    // 使用CSS变量获取星星颜色
    const starColor = getComputedStyle(document.documentElement).getPropertyValue('--star-color').trim()
    const starRgba = starColor.replace('rgba(', '').replace(')', '').split(',')
    ctx.fillStyle = `rgba(${starRgba[0]}, ${starRgba[1]}, ${starRgba[2]}, ${star.opacity * twinkle})`
    ctx.fill()

    // 添加光晕效果
    if (star.size > 1.5) {
      ctx.beginPath()
      ctx.arc(star.x, star.y, star.size * 2, 0, Math.PI * 2)
      ctx.fillStyle = `rgba(${starRgba[0]}, ${starRgba[1]}, ${starRgba[2]}, ${star.opacity * twinkle * 0.1})`
      ctx.fill()
    }
  })
}

// 绘制星云
const drawNebula = () => {
  const canvas = nebulaCanvas.value
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  ctx.clearRect(0, 0, canvas.width, canvas.height)

  nebulaParticles.value.forEach(particle => {
    // 缓慢漂移
    particle.x += particle.driftX * particle.speed
    particle.y += particle.driftY * particle.speed

    // 边界处理
    if (particle.x < -particle.size) particle.x = canvas.width + particle.size
    if (particle.x > canvas.width + particle.size) particle.x = -particle.size
    if (particle.y < -particle.size) particle.y = canvas.height + particle.size
    if (particle.y > canvas.height + particle.size) particle.y = -particle.size

    // 绘制星云粒子
    const gradient = ctx.createRadialGradient(
      particle.x, particle.y, 0,
      particle.x, particle.y, particle.size
    )
    gradient.addColorStop(0, particle.color)
    gradient.addColorStop(1, 'rgba(0, 0, 0, 0)')

    ctx.beginPath()
    ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2)
    ctx.fillStyle = gradient
    ctx.fill()
  })
}

// 绘制流动粒子
const drawFlowingParticles = () => {
  const canvas = flowingCanvas.value
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  ctx.clearRect(0, 0, canvas.width, canvas.height)

  // 随机生成新粒子
  if (Math.random() < 0.1) {
    const side = Math.floor(Math.random() * 4)
    let x, y, vx, vy

    switch (side) {
      case 0: // 从左边进入
        x = -10
        y = Math.random() * canvas.height
        vx = Math.random() * 2 + 0.5
        vy = (Math.random() - 0.5) * 1
        break
      case 1: // 从右边进入
        x = canvas.width + 10
        y = Math.random() * canvas.height
        vx = -(Math.random() * 2 + 0.5)
        vy = (Math.random() - 0.5) * 1
        break
      case 2: // 从上边进入
        x = Math.random() * canvas.width
        y = -10
        vx = (Math.random() - 0.5) * 1
        vy = Math.random() * 2 + 0.5
        break
      default: // 从下边进入
        x = Math.random() * canvas.width
        y = canvas.height + 10
        vx = (Math.random() - 0.5) * 1
        vy = -(Math.random() * 2 + 0.5)
        break
    }

    flowingParticles.value.push({
      x, y, vx, vy,
      size: Math.random() * 3 + 1,
      opacity: Math.random() * 0.6 + 0.2,
      life: 0,
      maxLife: Math.random() * 300 + 200
    })
  }

  // 更新和绘制流动粒子
  flowingParticles.value = flowingParticles.value.filter(particle => {
    particle.x += particle.vx
    particle.y += particle.vy
    particle.life++

    // 生命周期透明度变化
    const lifeRatio = particle.life / particle.maxLife
    const alpha = particle.opacity * (1 - lifeRatio)

    if (alpha > 0.01) {
      ctx.beginPath()
      ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2)
      ctx.fillStyle = `rgba(170, 131, 255, ${alpha})`
      ctx.fill()

      // 添加轨迹效果
      ctx.beginPath()
      ctx.arc(particle.x - particle.vx * 3, particle.y - particle.vy * 3, particle.size * 0.5, 0, Math.PI * 2)
      ctx.fillStyle = `rgba(170, 131, 255, ${alpha * 0.3})`
      ctx.fill()

      return true
    }

    return false
  })
}

// 主动画循环
const animate = () => {
  if (!isVisible) return

  drawStars()
  drawNebula()
  drawFlowingParticles()

  animationId = requestAnimationFrame(animate)
}

// 窗口大小变化处理
const handleResize = () => {
  initStars()
  initNebula()
  initFlowingParticles()
}

// 页面可见性变化处理
const handleVisibilityChange = () => {
  isVisible = !document.hidden
  if (isVisible) {
    animate()
  } else {
    cancelAnimationFrame(animationId)
  }
}

onMounted(() => {
  initStars()
  initNebula()
  initFlowingParticles()
  animate()

  window.addEventListener('resize', handleResize)
  document.addEventListener('visibilitychange', handleVisibilityChange)
})

onUnmounted(() => {
  cancelAnimationFrame(animationId)
  window.removeEventListener('resize', handleResize)
  document.removeEventListener('visibilitychange', handleVisibilityChange)
})
</script>

<style scoped lang="scss">
@use '../styles/variables.scss' as *;
@use '../styles/theme-utils.scss' as *;

.deep-space-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
  overflow: hidden;
}

.space-gradient {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  @include gradient-bg('space');
}

.stars-canvas,
.nebula-canvas,
.flowing-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.stars-canvas {
  z-index: 1;
}

.nebula-canvas {
  z-index: 2;
  mix-blend-mode: screen;
}

.flowing-canvas {
  z-index: 3;
  mix-blend-mode: screen;
}
</style>
