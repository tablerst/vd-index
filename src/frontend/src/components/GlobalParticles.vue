<template>
  <!-- 使用 Teleport 将粒子渲染到 body，突破容器限制 -->
  <Teleport to="body">
    <div class="global-particles" :class="{ 'particles-active': isActive }">
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
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'

// Props
interface Props {
  intensity?: number // 粒子强度 0-1
  centerX?: number   // 星际门中心X位置 (视口百分比)
  centerY?: number   // 星际门中心Y位置 (视口百分比)
}

const props = withDefaults(defineProps<Props>(), {
  intensity: 0.8,
  centerX: 25,  // 左侧25%位置
  centerY: 50   // 垂直居中
})

// 响应式状态
const isActive = ref(false)

// 计算粒子数量
const globalParticleCount = computed(() => Math.floor(80 * props.intensity))
const centerParticleCount = computed(() => Math.floor(40 * props.intensity))

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
    '--particle-color': distanceFromCenter > 0.5 ? 'var(--primary)' : 'var(--secondary)'
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

// 生命周期
onMounted(() => {
  // 延迟激活以确保平滑过渡
  setTimeout(() => {
    isActive.value = true
  }, 500)
})

onUnmounted(() => {
  isActive.value = false
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
}

.global-particle {
  position: absolute;
  border-radius: 50%;
  background: var(--particle-color, var(--primary));
  filter: blur(0.5px);
  will-change: transform, opacity;
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
    opacity: 0.3;
  }
}

.center-particle {
  position: absolute;
  border-radius: 50%;
  background: var(--secondary);
  box-shadow: 0 0 8px var(--secondary);
  filter: blur(0.3px);
  will-change: transform;
  animation: centerOrbit linear infinite;
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
  }
}

@media (prefers-reduced-motion: reduce) {
  .global-particle,
  .center-particle {
    animation: none;
  }
}
</style>
