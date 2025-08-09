<template>
  <!-- 使用 Teleport 将粒子渲染到 body，突破容器限制 -->
  <Teleport to="body">
    <div class="global-particles" :class="{
      'particles-active': isActive,
      'particles-paused': isPaused || !isVisible
    }">
      <!-- 全局背景粒子 - 稀疏分布 -->
      <div
        v-for="i in globalParticleCount"
        :key="`global-${i}`"
        class="global-particle"
        :style="getGlobalParticleStyle(i)"
      ></div>

      <!-- 中心区域增强粒子 - 围绕星际门位置 -->
      <div
        v-for="i in centerParticleCount"
        :key="`center-${i}`"
        class="center-particle"
        :style="getCenterParticleStyle(i)"
      ></div>

      <!-- 深空星云粒子 - 为MembersCircle区域提供深空效果 -->
      <div
        v-for="i in deepSpaceParticleCount"
        :key="`deepspace-${i}`"
        class="deepspace-particle"
        :style="getDeepSpaceParticleStyle(i)"
      ></div>

      <!-- 流动星尘粒子 - 快速移动的小粒子 -->
      <div
        v-for="i in stardustParticleCount"
        :key="`stardust-${i}`"
        class="stardust-particle"
        :style="getStardustParticleStyle(i)"
      ></div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useThemeStore } from '../stores/theme'

// Props
interface Props {
  intensity?: number // 粒子强度 0-1
  centerX?: number   // 星际门中心X位置 (视口百分比)
  centerY?: number   // 星际门中心Y位置 (视口百分比)
  enableDeepSpace?: boolean // 是否启用深空效果
}

const props = withDefaults(defineProps<Props>(), {
  intensity: 0.8,
  centerX: 25,  // 左侧25%位置
  centerY: 50,  // 垂直居中
  enableDeepSpace: true
})

// 主题store
const themeStore = useThemeStore()

// 监听主题变化，重新计算粒子样式
watch(() => themeStore.currentTheme, () => {
  // 主题切换时，强制重新渲染粒子
  isActive.value = false
  setTimeout(() => {
    isActive.value = true
  }, 100)
})

// 响应式状态
const isActive = ref(false)
const isVisible = ref(true)
const isPaused = ref(false)

// 计算粒子数量 - 大幅减少以提升性能
const globalParticleCount = computed(() => Math.floor(30 * props.intensity))
const centerParticleCount = computed(() => Math.floor(15 * props.intensity))
const deepSpaceParticleCount = computed(() =>
  props.enableDeepSpace ? Math.floor(15 * props.intensity) : 0
)
const stardustParticleCount = computed(() =>
  props.enableDeepSpace ? Math.floor(10 * props.intensity) : 0
)

// 生成全局粒子样式
const getGlobalParticleStyle = (index: number) => {
  const seed = index * 0.618033988749895

  // 随机分布在整个视口
  const x = (Math.sin(seed * 17) * 0.5 + 0.5) * 100
  const y = (Math.sin(seed * 19) * 0.5 + 0.5) * 100

  // 计算距离中心的距离，用于调整透明度和大小
  const distanceFromCenter = Math.sqrt(
    Math.pow(x - props.centerX, 2) + Math.pow(y - props.centerY, 2)
  ) / 70 // 归一化距离

  // 距离中心越远，粒子越小越透明
  const size = Math.max(1, 4 - distanceFromCenter * 2)
  const opacity = Math.max(0.1, 0.6 - distanceFromCenter * 0.3)

  // 动画参数
  const delay = (Math.sin(seed * 23) * 0.5 + 0.5) * 15
  const duration = (Math.sin(seed * 29) * 0.5 + 0.5) * 20 + 15
  const driftX = (Math.sin(seed * 31) * 0.5 + 0.5) * 6 - 3
  const driftY = (Math.sin(seed * 37) * 0.5 + 0.5) * 6 - 3

  return {
    left: `${x}%`,
    top: `${y}%`,
    width: `${size}px`,
    height: `${size}px`,
    opacity: opacity,
    animationDelay: `${delay}s`,
    animationDuration: `${duration}s`,
    '--drift-x': `${driftX}px`,
    '--drift-y': `${driftY}px`,
    '--particle-color': distanceFromCenter > 0.5 ? 'var(--particle-primary)' : 'var(--particle-secondary)'
  }
}

// 生成中心区域粒子样式
const getCenterParticleStyle = (index: number) => {
  const seed = (index + 1000) * 0.618033988749895

  // 围绕星际门中心的极坐标分布
  const angle = (Math.sin(seed * 13) * 0.5 + 0.5) * 360
  const radius = (Math.sin(seed * 17) * 0.5 + 0.5) * 25 + 5 // 5-30的半径范围

  const x = props.centerX + Math.cos(angle * Math.PI / 180) * radius
  const y = props.centerY + Math.sin(angle * Math.PI / 180) * radius

  // 确保粒子在视口内
  const clampedX = Math.max(2, Math.min(98, x))
  const clampedY = Math.max(2, Math.min(98, y))

  const size = (Math.sin(seed * 19) * 0.5 + 0.5) * 3 + 2
  const delay = (Math.sin(seed * 23) * 0.5 + 0.5) * 10
  const duration = (Math.sin(seed * 29) * 0.5 + 0.5) * 8 + 6

  // 轨道运动参数
  const orbitRadius = radius * 0.3
  const orbitSpeed = (Math.sin(seed * 31) * 0.5 + 0.5) * 2 + 1

  return {
    left: `${clampedX}%`,
    top: `${clampedY}%`,
    width: `${size}px`,
    height: `${size}px`,
    animationDelay: `${delay}s`,
    animationDuration: `${duration}s`,
    '--orbit-radius': `${orbitRadius}px`,
    '--orbit-speed': `${orbitSpeed}s`
  }
}

// 生成深空星云粒子样式
const getDeepSpaceParticleStyle = (index: number) => {
  const seed = index * 0.618033988749895

  // 在整个视口范围内分布，但在下半部分（MembersCircle区域）密度更高
  const x = (Math.sin(seed * 23) * 0.5 + 0.5) * 100
  const yBias = Math.sin(seed * 29) * 0.3 + 0.7 // 偏向下半部分
  const y = yBias * 100

  // 大小和颜色变化
  const size = (Math.sin(seed * 37) * 0.5 + 0.5) * 4 + 2
  const hue = Math.floor((Math.sin(seed * 41) * 0.5 + 0.5) * 60 + 240) // 蓝紫色调
  const saturation = Math.floor((Math.sin(seed * 43) * 0.5 + 0.5) * 40 + 60)
  const lightness = Math.floor((Math.sin(seed * 47) * 0.5 + 0.5) * 30 + 50)

  // 动画参数
  const duration = (Math.sin(seed * 53) * 0.5 + 0.5) * 8 + 12
  const delay = (Math.sin(seed * 59) * 0.5 + 0.5) * 5

  return {
    left: `${x}%`,
    top: `${y}%`,
    width: `${size}px`,
    height: `${size}px`,
    background: `hsl(${hue}, ${saturation}%, ${lightness}%)`,
    animationDelay: `${delay}s`,
    animationDuration: `${duration}s`
  }
}

// 生成星尘粒子样式
const getStardustParticleStyle = (index: number) => {
  const seed = index * 0.618033988749895

  // 随机分布
  const x = (Math.sin(seed * 61) * 0.5 + 0.5) * 100
  const y = (Math.sin(seed * 67) * 0.5 + 0.5) * 100

  // 小尺寸粒子
  const size = (Math.sin(seed * 71) * 0.5 + 0.5) * 2 + 1

  // 快速移动
  const duration = (Math.sin(seed * 73) * 0.5 + 0.5) * 3 + 2
  const delay = (Math.sin(seed * 79) * 0.5 + 0.5) * 3

  // 移动距离
  const driftX = (Math.sin(seed * 83) * 0.5 + 0.5) * 200 - 100
  const driftY = (Math.sin(seed * 89) * 0.5 + 0.5) * 200 - 100

  return {
    left: `${x}%`,
    top: `${y}%`,
    width: `${size}px`,
    height: `${size}px`,
    animationDelay: `${delay}s`,
    animationDuration: `${duration}s`,
    '--drift-x': `${driftX}px`,
    '--drift-y': `${driftY}px`
  }
}

// 性能优化：页面可见性检测
const handleVisibilityChange = () => {
  isVisible.value = !document.hidden
  if (document.hidden) {
    isPaused.value = true
  } else {
    // 页面重新可见时延迟恢复动画
    setTimeout(() => {
      isPaused.value = false
    }, 100)
  }
}

// 全局动画暂停控制（用于滑动时暂停）
const handleAnimationPause = (event: CustomEvent) => {
  isPaused.value = event.detail.pause
}

// 生命周期
onMounted(() => {
  // 延迟激活以确保平滑过渡
  setTimeout(() => {
    isActive.value = true
  }, 500)

  // 监听页面可见性变化
  document.addEventListener('visibilitychange', handleVisibilityChange)

  // 监听全局动画暂停事件
  window.addEventListener('particles-pause', handleAnimationPause as EventListener)
})

onUnmounted(() => {
  isActive.value = false

  // 清理事件监听器
  document.removeEventListener('visibilitychange', handleVisibilityChange)
  window.removeEventListener('particles-pause', handleAnimationPause as EventListener)
})
</script>

<style scoped lang="scss">
.global-particles {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  pointer-events: none;
  z-index: 1;
  opacity: 0;
  transition: opacity 2s ease-in-out;

  &.particles-active {
    opacity: 1;
  }

  &.particles-paused {
    .global-particle,
    .center-particle,
    .deepspace-particle,
    .stardust-particle {
      animation-play-state: paused;
    }
  }
}

.global-particle {
  position: absolute;
  border-radius: 50%;
  background: var(--particle-color, var(--particle-primary));
  box-shadow: 0 0 4px var(--particle-color, var(--particle-primary));
  will-change: transform, opacity;
  transform: translate3d(0, 0, 0); // 强制GPU加速
  animation: globalFloat linear infinite;

  &::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, currentColor 0%, transparent 70%);
    border-radius: 50%;
    opacity: 0.15; // 减少透明度以降低渲染负载
  }
}

.center-particle {
  position: absolute;
  border-radius: 50%;
  background: var(--particle-secondary);
  box-shadow: 0 0 6px var(--particle-secondary);
  will-change: transform;
  transform: translate3d(0, 0, 0); // 强制GPU加速
  animation: centerOrbit linear infinite;
}

.deepspace-particle {
  position: absolute;
  border-radius: 50%;
  background: var(--particle-accent);
  box-shadow: 0 0 3px var(--particle-accent);
  will-change: transform, opacity;
  transform: translate3d(0, 0, 0); // 强制GPU加速
  animation: deepSpaceFloat linear infinite;
  opacity: 0.5; // 降低透明度减少渲染负载

  &::before {
    content: '';
    position: absolute;
    top: -100%;
    left: -100%;
    width: 300%;
    height: 300%;
    background: radial-gradient(circle, currentColor 0%, transparent 60%);
    border-radius: 50%;
    opacity: 0.2; // 降低透明度
  }
}

.stardust-particle {
  position: absolute;
  border-radius: 50%;
  background: var(--particle-primary);
  box-shadow: 0 0 2px var(--particle-primary);
  will-change: transform;
  transform: translate3d(0, 0, 0); // 强制GPU加速
  animation: stardustFlow linear infinite;
  opacity: 0.6; // 降低透明度
}

// 全局粒子漂浮动画
@keyframes globalFloat {
  0% {
    transform: translate(0, 0) scale(0.8);
    opacity: 0.3;
  }
  25% {
    transform: translate(var(--drift-x), calc(var(--drift-y) * 0.5)) scale(1.1);
    opacity: 0.8;
  }
  50% {
    transform: translate(calc(var(--drift-x) * 1.5), var(--drift-y)) scale(1);
    opacity: 0.6;
  }
  75% {
    transform: translate(var(--drift-x), calc(var(--drift-y) * 1.5)) scale(1.2);
    opacity: 0.9;
  }
  100% {
    transform: translate(0, 0) scale(0.8);
    opacity: 0.3;
  }
}

// 中心粒子轨道动画
@keyframes centerOrbit {
  0% {
    transform: rotate(0deg) translateX(var(--orbit-radius)) rotate(0deg) scale(0.9);
    opacity: 0.6;
  }
  25% {
    opacity: 1;
    transform: rotate(90deg) translateX(var(--orbit-radius)) rotate(-90deg) scale(1.2);
  }
  50% {
    opacity: 0.8;
    transform: rotate(180deg) translateX(var(--orbit-radius)) rotate(-180deg) scale(1);
  }
  75% {
    opacity: 1;
    transform: rotate(270deg) translateX(var(--orbit-radius)) rotate(-270deg) scale(1.1);
  }
  100% {
    transform: rotate(360deg) translateX(var(--orbit-radius)) rotate(-360deg) scale(0.9);
    opacity: 0.6;
  }
}

// 深空粒子漂浮动画
@keyframes deepSpaceFloat {
  0% {
    transform: translate(0, 0) scale(0.9);
    opacity: 0.4;
  }
  33% {
    transform: translate(20px, -30px) scale(1.1);
    opacity: 0.7;
  }
  66% {
    transform: translate(-15px, 25px) scale(1);
    opacity: 0.5;
  }
  100% {
    transform: translate(0, 0) scale(0.9);
    opacity: 0.4;
  }
}

// 星尘流动动画
@keyframes stardustFlow {
  0% {
    transform: translate(0, 0) scale(1);
    opacity: 0.8;
  }
  50% {
    transform: translate(var(--drift-x), var(--drift-y)) scale(0.5);
    opacity: 0.3;
  }
  100% {
    transform: translate(calc(var(--drift-x) * 2), calc(var(--drift-y) * 2)) scale(0);
    opacity: 0;
  }
}

// 响应式优化
@media (max-width: 768px) {
  .global-particles {
    // 移动设备减少粒子数量以提升性能
    .global-particle:nth-child(n+41) {
      display: none;
    }
    .center-particle:nth-child(n+21) {
      display: none;
    }
    .deepspace-particle:nth-child(n+31) {
      display: none;
    }
    .stardust-particle:nth-child(n+16) {
      display: none;
    }
  }
}

@media (prefers-reduced-motion: reduce) {
  .global-particle,
  .center-particle,
  .deepspace-particle,
  .stardust-particle {
    animation: none;
  }
}
</style>
