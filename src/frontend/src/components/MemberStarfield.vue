<template>
  <canvas 
    ref="canvasRef" 
    class="starfield-canvas"
    :width="canvasSize.width"
    :height="canvasSize.height"
  />
</template>

<script setup lang="ts">
import { onMounted, ref, onUnmounted, computed } from 'vue'
import * as THREE from 'three'
import { useDeviceDetection } from '../composables/useDeviceDetection'

const canvasRef = ref<HTMLCanvasElement>()
const { deviceInfo } = useDeviceDetection()

// 响应式画布尺寸
const canvasSize = computed(() => ({
  width: 400,
  height: 500
}))

// Three.js 相关变量
let renderer: THREE.WebGLRenderer | null = null
let scene: THREE.Scene | null = null
let camera: THREE.PerspectiveCamera | null = null
let stars: THREE.Points | null = null
let animationId: number | null = null

// 性能优化参数
const particleCount = computed(() => {
  if (deviceInfo.value.isMobile) return 150
  if (deviceInfo.value.isTablet) return 200
  return 300
})

const initThreeJS = () => {
  if (!canvasRef.value) return

  const width = canvasSize.value.width
  const height = canvasSize.value.height

  // 创建渲染器
  renderer = new THREE.WebGLRenderer({ 
    canvas: canvasRef.value, 
    alpha: true,
    antialias: false, // 移动端关闭抗锯齿提升性能
    powerPreference: 'high-performance'
  })
  renderer.setSize(width, height)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2)) // 限制像素比

  // 创建场景
  scene = new THREE.Scene()

  // 创建相机
  camera = new THREE.PerspectiveCamera(60, width / height, 1, 1000)
  camera.position.z = 200

  // 创建星粒子
  createStarfield()

  // 开始动画循环
  animate()
}

const createStarfield = () => {
  if (!scene) return

  const geometry = new THREE.BufferGeometry()
  const vertices = []
  const colors = []
  const sizes = []

  // 主题色彩
  const starColors = [
    new THREE.Color(0xAA83FF), // 主紫色
    new THREE.Color(0xD4DEC7), // 浅绿色
    new THREE.Color(0x3F7DFB), // 蓝色
    new THREE.Color(0xFFFFFF)  // 白色
  ]

  for (let i = 0; i < particleCount.value; i++) {
    // 位置 - 在模态框范围内分布
    vertices.push(
      (Math.random() - 0.5) * 400,
      (Math.random() - 0.5) * 500,
      (Math.random() - 0.5) * 300
    )

    // 颜色 - 随机选择主题色
    const color = starColors[Math.floor(Math.random() * starColors.length)]
    colors.push(color.r, color.g, color.b)

    // 大小 - 随机变化
    sizes.push(Math.random() * 2 + 0.5)
  }

  geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3))
  geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3))
  geometry.setAttribute('size', new THREE.Float32BufferAttribute(sizes, 1))

  // 创建材质
  const material = new THREE.PointsMaterial({
    size: 1.5,
    transparent: true,
    opacity: 0.6,
    vertexColors: true,
    blending: THREE.AdditiveBlending,
    sizeAttenuation: true
  })

  // 创建粒子系统
  stars = new THREE.Points(geometry, material)
  scene!.add(stars)
}

const animate = () => {
  if (!renderer || !scene || !camera || !stars) return

  // 缓慢旋转
  stars.rotation.y += 0.0008
  stars.rotation.x += 0.0005

  // 轻微的上下浮动
  stars.position.y = Math.sin(Date.now() * 0.001) * 2

  // 渲染场景
  renderer.render(scene, camera)

  // 继续动画循环
  animationId = requestAnimationFrame(animate)
}

const cleanup = () => {
  if (animationId) {
    cancelAnimationFrame(animationId)
    animationId = null
  }

  if (stars) {
    stars.geometry.dispose()
    if (Array.isArray(stars.material)) {
      stars.material.forEach(material => material.dispose())
    } else {
      stars.material.dispose()
    }
    scene?.remove(stars)
    stars = null
  }

  if (renderer) {
    renderer.dispose()
    renderer = null
  }

  scene = null
  camera = null
}

onMounted(() => {
  // 延迟初始化，确保DOM已渲染
  setTimeout(initThreeJS, 100)
})

onUnmounted(() => {
  cleanup()
})
</script>

<style scoped>
.starfield-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
  pointer-events: none;
  opacity: 0.8;
}
</style>
