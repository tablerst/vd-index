<template>
  <div class="ring-wrapper" ref="wrapper">
    <svg
      :width="actualSize"
      :height="actualSize"
      :viewBox="viewBox"
      class="ring-svg"
      aria-hidden="true"
    >
      <!-- 定义滤镜和渐变 -->
      <defs>
        <!-- 外发光滤镜 -->
        <filter id="outerGlow" x="-100%" y="-100%" width="300%" height="300%">
          <feGaussianBlur in="SourceGraphic" stdDeviation="8" result="blur"/>
          <feColorMatrix in="blur" type="matrix" 
            values="1 0 1 0 0  0 0.5 1 0 0  1 0 1 0 0  0 0 0 1 0"/>
          <feMerge>
            <feMergeNode in="blur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>

        <!-- 内发光滤镜 -->
        <filter id="innerGlow" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur in="SourceGraphic" stdDeviation="4" result="blur"/>
          <feMerge>
            <feMergeNode in="blur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>

        <!-- 核心光晕滤镜 -->
        <filter id="coreGlow" x="-200%" y="-200%" width="500%" height="500%">
          <feGaussianBlur in="SourceGraphic" stdDeviation="12" result="blur"/>
          <feColorMatrix in="blur" type="matrix" 
            values="0.7 0 1 0 0  0 0.3 0.8 0 0  1 0 0.7 0 0  0 0 0 0.8 0"/>
          <feMerge>
            <feMergeNode in="blur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>

        <!-- 径向渐变 -->
        <radialGradient id="ringGradient1" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#AA83FF" stop-opacity="0.9"/>
          <stop offset="70%" stop-color="#AA83FF" stop-opacity="0.6"/>
          <stop offset="100%" stop-color="#AA83FF" stop-opacity="0.3"/>
        </radialGradient>

        <radialGradient id="ringGradient2" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#D4DEC7" stop-opacity="0.8"/>
          <stop offset="70%" stop-color="#D4DEC7" stop-opacity="0.5"/>
          <stop offset="100%" stop-color="#D4DEC7" stop-opacity="0.2"/>
        </radialGradient>

        <radialGradient id="ringGradient3" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#3F7DFB" stop-opacity="0.7"/>
          <stop offset="70%" stop-color="#3F7DFB" stop-opacity="0.4"/>
          <stop offset="100%" stop-color="#3F7DFB" stop-opacity="0.1"/>
        </radialGradient>

        <radialGradient id="coreGradient" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#FFFFFF" stop-opacity="1"/>
          <stop offset="30%" stop-color="#AA83FF" stop-opacity="0.9"/>
          <stop offset="100%" stop-color="#AA83FF" stop-opacity="0.6"/>
        </radialGradient>
      </defs>

      <!-- 外环 - 最大 -->
      <circle 
        :r="r(0.45)" 
        :cx="c" 
        :cy="c" 
        fill="none"
        stroke="url(#ringGradient1)" 
        stroke-width="4" 
        filter="url(#outerGlow)"
        ref="ring1"
        class="ring-outer"
      />

      <!-- 中环 -->
      <circle 
        :r="r(0.30)" 
        :cx="c" 
        :cy="c" 
        fill="none"
        stroke="url(#ringGradient2)" 
        stroke-width="3" 
        filter="url(#innerGlow)"
        ref="ring2"
        class="ring-middle"
      />

      <!-- 内环 -->
      <circle 
        :r="r(0.15)" 
        :cx="c" 
        :cy="c" 
        fill="none"
        stroke="url(#ringGradient3)" 
        stroke-width="2" 
        ref="ring3"
        class="ring-inner"
      />

      <!-- 核心圆点 -->
      <circle 
        :r="r(0.06)" 
        :cx="c" 
        :cy="c" 
        fill="url(#coreGradient)"
        filter="url(#coreGlow)"
        ref="core"
        class="ring-core"
      />

      <!-- 能量脉冲环 -->
      <circle 
        v-for="(pulse, index) in pulseRings"
        :key="`pulse-${index}`"
        :r="r(pulse.radius)" 
        :cx="c" 
        :cy="c" 
        fill="none"
        :stroke="pulse.color"
        :stroke-width="pulse.width"
        :opacity="pulse.opacity"
        :ref="el => setPulseRef(el, index)"
        class="pulse-ring"
      />
    </svg>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, defineExpose, computed, nextTick } from 'vue'
import gsap from 'gsap'

// Props
interface Props {
  size?: number
  enableParallax?: boolean
  enableBreathing?: boolean
  enablePulse?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  size: 520,
  enableParallax: true,
  enableBreathing: true,
  enablePulse: true
})

// 响应式尺寸
const actualSize = computed(() => {
  if (typeof window === 'undefined') return props.size
  return window.innerWidth <= 768 ? 320 : props.size
})

// 计算属性
const c = computed(() => actualSize.value / 2)
const r = (ratio: number) => c.value * ratio
const viewBox = computed(() => `0 0 ${actualSize.value} ${actualSize.value}`)

// 模板引用
const wrapper = ref<HTMLElement>()
const ring1 = ref<SVGCircleElement>()
const ring2 = ref<SVGCircleElement>()
const ring3 = ref<SVGCircleElement>()
const core = ref<SVGCircleElement>()

// 脉冲环数据
const pulseRings = ref([
  { radius: 0.55, color: '#AA83FF', width: 2, opacity: 0 },
  { radius: 0.65, color: '#D4DEC7', width: 2, opacity: 0 },
  { radius: 0.75, color: '#3F7DFB', width: 2, opacity: 0 }
])

const pulseRefs = ref<(SVGCircleElement | null)[]>([])
const setPulseRef = (el: any, index: number) => {
  if (el && el instanceof SVGCircleElement) {
    pulseRefs.value[index] = el
  } else {
    pulseRefs.value[index] = null
  }
}

// 动画时间线
let breathingTl: gsap.core.Timeline
let pulseTl: gsap.core.Timeline
let rotationTl: gsap.core.Timeline

// 检测动画偏好
const prefersReducedMotion = () => {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

// 初始化呼吸动画
const initBreathingAnimation = () => {
  if (!props.enableBreathing || prefersReducedMotion()) return

  breathingTl = gsap.timeline({ 
    repeat: -1, 
    yoyo: true, 
    defaults: { 
      ease: 'sine.inOut', 
      duration: 3 
    } 
  })

  // 环的呼吸效果
  const rings = [ring1.value, ring2.value, ring3.value].filter(Boolean)
  if (rings.length > 0) {
    breathingTl.to(rings, {
      scale: 1.08,
      opacity: 1,
      transformOrigin: 'center'
    }, 0)
  }

  if (core.value) {
    breathingTl.to(core.value, {
      scale: 1.15,
      opacity: 1,
      transformOrigin: 'center'
    }, 0)
  }
}

// 初始化脉冲动画
const initPulseAnimation = () => {
  if (!props.enablePulse || prefersReducedMotion()) return

  // 确保有脉冲环元素
  const validPulseRefs = pulseRefs.value.filter(Boolean)
  if (validPulseRefs.length === 0) {
    return
  }

  pulseTl = gsap.timeline({ repeat: -1 })

  validPulseRefs.forEach((pulseEl, index) => {
    const delay = index * 1.2 // 增加延迟间隔
    pulseTl
      .fromTo(pulseEl,
        {
          scale: 0.8,
          opacity: 0,
          transformOrigin: 'center'
        },
        {
          scale: 1.2,
          opacity: 0.8, // 增加可见度
          duration: 0.6,
          ease: 'power2.out'
        }, delay)
      .to(pulseEl, {
        scale: 2.0, // 增加扩散范围
        opacity: 0,
        duration: 1.8,
        ease: 'power2.out'
      }, delay + 0.6)
  })


}

// 初始化旋转动画
const initRotationAnimation = () => {
  if (prefersReducedMotion()) return

  rotationTl = gsap.timeline({ repeat: -1 })

  // 不同环以不同速度旋转
  if (ring1.value) {
    gsap.to(ring1.value, { 
      rotation: 360, 
      duration: 20, 
      ease: 'none', 
      repeat: -1,
      transformOrigin: 'center'
    })
  }

  if (ring2.value) {
    gsap.to(ring2.value, { 
      rotation: -360, 
      duration: 15, 
      ease: 'none', 
      repeat: -1,
      transformOrigin: 'center'
    })
  }

  if (ring3.value) {
    gsap.to(ring3.value, { 
      rotation: 360, 
      duration: 10, 
      ease: 'none', 
      repeat: -1,
      transformOrigin: 'center'
    })
  }
}

// 视差效果
const initParallaxEffect = () => {
  if (!props.enableParallax || prefersReducedMotion()) return

  const handleMouseMove = (e: MouseEvent) => {
    if (!wrapper.value) return

    const { clientX, clientY } = e
    const { innerWidth, innerHeight } = window

    const rx = (clientY / innerHeight - 0.5) * 8
    const ry = (clientX / innerWidth - 0.5) * -8

    gsap.to(wrapper.value, {
      rotationX: rx,
      rotationY: ry,
      duration: 0.6,
      ease: 'power3.out',
      transformPerspective: 1000,
      transformOrigin: 'center'
    })
  }

  window.addEventListener('mousemove', handleMouseMove)
  
  return () => {
    window.removeEventListener('mousemove', handleMouseMove)
  }
}

let parallaxCleanup: (() => void) | undefined

// 获取中心坐标
const getCenter = () => {
  if (!wrapper.value) return { x: 0, y: 0 }
  
  const rect = wrapper.value.getBoundingClientRect()
  return { 
    x: rect.left + rect.width / 2, 
    y: rect.top + rect.height / 2 
  }
}

// 暴露方法
defineExpose({
  getCenter
})

onMounted(async () => {
  await nextTick()

  // 初始化动画
  initBreathingAnimation()
  initRotationAnimation()

  // 延迟初始化脉冲动画，确保refs已设置
  setTimeout(() => {
    // 再次确保DOM已完全渲染
    nextTick().then(() => {
      initPulseAnimation()
    })
  }, 200) // 增加延迟时间

  // 初始化视差效果
  parallaxCleanup = initParallaxEffect()

  // 监听窗口大小变化
  const handleResize = () => {
    // 触发响应式更新
    nextTick()
  }
  window.addEventListener('resize', handleResize)

  // 清理函数中移除监听器
  const originalCleanup = parallaxCleanup
  parallaxCleanup = () => {
    originalCleanup?.()
    window.removeEventListener('resize', handleResize)
  }
})

onUnmounted(() => {
  // 清理动画
  breathingTl?.kill()
  pulseTl?.kill()
  rotationTl?.kill()
  
  // 清理视差效果
  parallaxCleanup?.()
})
</script>

<style scoped lang="scss">
.ring-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  will-change: transform;
  transform-style: preserve-3d;
  perspective: 1000px;
}

.ring-svg {
  overflow: visible;
  shape-rendering: geometricPrecision;
  max-width: 100%;
  max-height: 100%;
  
  // 确保在移动设备上的性能
  @media (max-width: 768px) {
    will-change: auto;
  }
}

// 环的基础样式
.ring-outer,
.ring-middle,
.ring-inner {
  will-change: transform, opacity;
  transform-origin: center;
}

.ring-core {
  will-change: transform, opacity;
  transform-origin: center;
}

.pulse-ring {
  will-change: transform, opacity;
  transform-origin: center;
  pointer-events: none;
}

// 减少动画偏好支持
@media (prefers-reduced-motion: reduce) {
  .ring-wrapper {
    transform: none !important;
  }
  
  .ring-outer,
  .ring-middle,
  .ring-inner,
  .ring-core,
  .pulse-ring {
    animation: none !important;
    transform: none !important;
  }
}

// 移动端优化
@media (max-width: 768px) {
  .ring-wrapper {
    perspective: 500px;
  }
}
</style>
