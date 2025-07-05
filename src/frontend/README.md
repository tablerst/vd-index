# VD群成员管理系统 - 前端技术文档

## 📋 目录

- [技术栈与架构](#技术栈与架构)
- [整体功能与展示效果](#整体功能与展示效果)
- [目录结构说明](#目录结构说明)
- [核心功能实现](#核心功能实现)
- [视觉效果系统](#视觉效果系统)
- [组件架构](#组件架构)
- [性能优化](#性能优化)
- [构建与部署](#构建与部署)

## 🛠️ 技术栈与架构

### 核心技术栈

- **前端框架**: Vue 3.5+ (Composition API + TypeScript)
- **状态管理**: Pinia 3.0+ (现代化状态管理)
- **3D图形**: Three.js 0.177+ (WebGL 3D渲染)
- **动画引擎**: GSAP 3.13+ (高性能动画库)
- **滑动组件**: Swiper 11.2+ (触摸滑动支持)
- **构建工具**: Vite 6.3+ (现代化构建工具)
- **样式预处理**: Sass/SCSS (模块化样式)
- **类型检查**: TypeScript 5.8+ (类型安全)
- **依赖管理**: pnpm 8.18+ (高性能包管理器)

### 架构设计

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Vue 3 组件    │◄──►│   Pinia Store   │◄──►│   API Service   │
│                 │    │                 │    │                 │
│ • 响应式UI      │    │ • 状态管理      │    │ • 后端通信      │
│ • 组合式API     │    │ • 数据缓存      │    │ • 错误处理      │
│ • TypeScript    │    │ • 计算属性      │    │ • 重试机制      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   视觉效果层    │    │   工具函数层    │    │   样式系统      │
│                 │    │                 │    │                 │
│ • Three.js 3D   │    │ • 数学计算      │    │ • SCSS变量      │
│ • GSAP动画      │    │ • 设备检测      │    │ • 响应式设计    │
│ • Canvas粒子    │    │ • 性能监控      │    │ • 主题系统      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 设计原则

1. **组件化设计**: 高度模块化的组件架构，便于维护和复用
2. **性能优先**: Web Workers、离屏Canvas、动画优化
3. **响应式体验**: 移动端适配、触摸交互、设备检测
4. **视觉震撼**: 3D效果、粒子系统、流畅动画

## 🎨 整体功能与展示效果

### 主要功能模块

#### 1. Hero首屏区域 (HeroSection)
**功能特性:**
- 2D星际跃迁门效果 (Ring2D组件)
- 环形粒子系统 (Web Workers + Canvas)
- 鼠标视差交互 (2.5D效果)
- 呼吸脉冲动画 (GSAP Timeline)

**展示效果:**
- 中央星际门随鼠标移动产生3D视差
- 围绕星际门的粒子轨道运动
- 三层同心圆环的呼吸和脉冲效果
- 渐变背景与粒子的深度层次感

#### 2. 成员星云展示 (MembersCircle)
**功能特性:**
- 水平全屏分页 (Swiper集成)
- 力导向连接系统 (D3-force算法)
- 成员头像星球化展示
- 实时连接线动画

**展示效果:**
- 每页40-50个成员头像呈星云分布
- 成员间动态连接线，随机高亮呼吸
- 左右箭头导航 + 滑动手势支持
- 页面切换时的3D翻转过渡动画

#### 3. 深空背景系统 (DeepSpaceBackground)
**功能特性:**
- Three.js星空场景渲染
- 300+随机分布星点
- 视差滚动效果
- 性能自适应调节

**展示效果:**
- 深邃的宇宙星空背景
- 星点闪烁和深度模糊效果
- 滚动时的视差层次感

#### 4. 全局粒子系统 (GlobalParticles)
**功能特性:**
- Teleport突破容器限制
- 全屏粒子分布算法
- 中心区域密度梯度
- 性能优化渲染

**展示效果:**
- 全屏稀疏粒子背景
- 星际门周围粒子密度增强
- 粒子的浮动和闪烁动画

### 核心交互体验

```
用户交互流程:
页面加载 → 星际门呼吸动画 → 鼠标视差跟随 → 滚动到成员区域 → 
星云展示 → 左右滑动分页 → 成员连接动画 → 头像悬停效果
```

## 📁 目录结构说明

```
src/frontend/
├── public/                     # 静态资源
│   ├── avatars/mems/          # 成员头像文件
│   └── favicon.ico            # 网站图标
├── src/
│   ├── components/            # Vue组件
│   │   ├── icons/            # 图标组件
│   │   ├── App.vue           # 根组件
│   │   ├── HeroSection.vue   # 首屏区域
│   │   ├── Ring2D.vue        # 2D星际门
│   │   ├── MembersCircle.vue # 成员星云
│   │   ├── GalaxySlide.vue   # 星云页面
│   │   ├── GlobalParticles.vue # 全局粒子
│   │   ├── DeepSpaceBackground.vue # 深空背景
│   │   ├── CustomPointer.vue # 自定义光标
│   │   ├── GlassNavigation.vue # 玻璃导航
│   │   ├── ProgressBar.vue   # 进度条
│   │   ├── PaginationArrows.vue # 分页箭头
│   │   └── StarCalendar.vue  # 星历日历
│   ├── composables/          # 组合式API
│   │   ├── useDeviceDetection.ts # 设备检测
│   │   ├── usePerformanceMonitor.ts # 性能监控
│   │   ├── useForceDirectedConnections.ts # 力导向连接
│   │   └── useThreeScene.ts  # Three.js场景管理
│   ├── stores/               # Pinia状态管理
│   │   └── members.ts        # 成员数据状态
│   ├── services/             # API服务
│   │   └── api.ts            # 后端API客户端
│   ├── utils/                # 工具函数
│   │   ├── stargate3d.ts     # 3D星际门工具
│   │   ├── gravityScatter3d.ts # 3D重力散布
│   │   ├── ringParticlesWorker.ts # 粒子Worker
│   │   ├── mathUtils.ts      # 数学工具
│   │   └── performanceUtils.ts # 性能工具
│   ├── styles/               # 样式文件
│   │   ├── main.scss         # 主样式入口
│   │   ├── variables.scss    # SCSS变量
│   │   ├── mixins.scss       # SCSS混入
│   │   └── components/       # 组件样式
│   ├── types/                # TypeScript类型
│   │   └── index.ts          # 类型定义
│   ├── main.ts               # 应用入口
│   └── env.d.ts              # 环境类型声明
├── package.json              # 项目配置
├── vite.config.ts            # Vite配置
├── tsconfig.json             # TypeScript配置
└── README.md                 # 本文档
```

### 关键文件说明

- **App.vue**: 应用根组件，定义整体布局和组件层次
- **HeroSection.vue**: 首屏核心组件，集成星际门和粒子效果
- **MembersCircle.vue**: 成员展示核心，集成Swiper和力导向算法
- **stores/members.ts**: 成员数据管理，API调用和状态缓存
- **utils/**: 核心工具函数，Three.js、数学计算、性能优化
- **vite.config.ts**: 构建配置，代理设置、优化配置

## 🔧 核心功能实现

### 1. 星际跃迁门系统

#### 2D星际门实现 (Ring2D.vue)

```vue
<template>
  <div class="ring-2d" ref="ringContainer">
    <!-- 三层同心圆环 -->
    <div class="ring ring--outer" ref="outerRing"></div>
    <div class="ring ring--middle" ref="middleRing"></div>
    <div class="ring ring--inner" ref="innerRing"></div>

    <!-- 脉冲效果层 -->
    <div class="pulse-ring" v-for="i in 3" :key="i" ref="pulseRefs"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { gsap } from 'gsap'

// 呼吸动画实现
const initBreathingAnimation = () => {
  const tl = gsap.timeline({ repeat: -1, yoyo: true })

  tl.to([outerRing.value, middleRing.value, innerRing.value], {
    scale: 1.08,
    opacity: 0.9,
    duration: 3,
    ease: "power2.inOut",
    stagger: 0.2
  })
}

// 鼠标视差效果
const handleMouseMove = (event: MouseEvent) => {
  if (!enableParallax) return

  const rect = ringContainer.value?.getBoundingClientRect()
  const centerX = rect.left + rect.width / 2
  const centerY = rect.top + rect.height / 2

  const deltaX = (event.clientX - centerX) / rect.width
  const deltaY = (event.clientY - centerY) / rect.height

  gsap.to(ringContainer.value, {
    rotationY: deltaX * 15,
    rotationX: -deltaY * 15,
    duration: 0.3,
    ease: "power2.out"
  })
}
</script>
```

#### 环形粒子系统 (Web Workers)

```typescript
// ringParticlesWorker.ts
class RingParticleSystem {
  private particles: Particle[] = []
  private canvas: OffscreenCanvas
  private ctx: OffscreenCanvasRenderingContext2D

  constructor(canvas: OffscreenCanvas) {
    this.canvas = canvas
    this.ctx = canvas.getContext('2d')!
    this.initParticles()
  }

  private initParticles() {
    const particleCount = 120

    for (let i = 0; i < particleCount; i++) {
      this.particles.push({
        angle: (i / particleCount) * Math.PI * 2,
        radius: 200 + Math.random() * 100,
        speed: 0.002 + Math.random() * 0.001,
        size: 1 + Math.random() * 2,
        opacity: 0.3 + Math.random() * 0.7,
        trail: []
      })
    }
  }

  private updateParticles() {
    this.particles.forEach(particle => {
      particle.angle += particle.speed

      const x = this.canvas.width / 2 + Math.cos(particle.angle) * particle.radius
      const y = this.canvas.height / 2 + Math.sin(particle.angle) * particle.radius

      // 添加轨迹点
      particle.trail.push({ x, y, opacity: particle.opacity })
      if (particle.trail.length > 10) {
        particle.trail.shift()
      }
    })
  }

  private render() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height)

    this.particles.forEach(particle => {
      // 绘制轨迹
      particle.trail.forEach((point, index) => {
        const alpha = (index / particle.trail.length) * point.opacity
        this.ctx.fillStyle = `rgba(170, 131, 255, ${alpha})`
        this.ctx.beginPath()
        this.ctx.arc(point.x, point.y, particle.size * (index / particle.trail.length), 0, Math.PI * 2)
        this.ctx.fill()
      })
    })
  }
}
```

### 2. 成员星云系统

#### Swiper集成与分页

```vue
<template>
  <div class="members-galaxy">
    <Swiper
      :modules="[Navigation, Mousewheel]"
      :slides-per-view="1"
      :space-between="0"
      :mousewheel="{ forceToAxis: true }"
      @slide-change="onSlideChange"
      @swiper="onSwiperInit"
    >
      <SwiperSlide v-for="(pageMembers, index) in memberPages" :key="index">
        <GalaxySlide :members="pageMembers" :slide-index="index" />
      </SwiperSlide>
    </Swiper>
  </div>
</template>

<script setup lang="ts">
import { Swiper, SwiperSlide } from 'swiper/vue'
import { Navigation, Mousewheel } from 'swiper/modules'

// 分页逻辑
const memberPages = computed(() => {
  const pages = []
  const pageSize = 45

  for (let i = 0; i < allMembers.value.length; i += pageSize) {
    pages.push(allMembers.value.slice(i, i + pageSize))
  }

  return pages
})

// 页面切换动画
const onSlideChange = (swiper: any) => {
  const fromIndex = currentSlide.value
  const toIndex = swiper.activeIndex

  animateSlideTransition(fromIndex, toIndex)
  currentSlide.value = toIndex
}
```

#### 力导向连接系统

```typescript
// useForceDirectedConnections.ts
import { computed } from 'vue'
import { forceSimulation, forceLink, forceManyBody, forceCenter } from 'd3-force'

export function useForceDirectedConnections(nodes: Node[], options: ForceOptions) {
  const simulation = forceSimulation(nodes)
    .force('link', forceLink().id(d => d.id).strength(options.linkStrength))
    .force('charge', forceManyBody().strength(options.chargeStrength))
    .force('center', forceCenter(0, 0))

  // 生成连接
  const links = computed(() => {
    const connections = []

    nodes.forEach((node, i) => {
      const nearestNodes = findNearestNodes(node, nodes, options.maxConnections)

      nearestNodes.forEach(target => {
        if (Math.random() < 0.3) { // 30%概率创建连接
          connections.push({
            source: node.id,
            target: target.id,
            strength: Math.random() * 0.5 + 0.5
          })
        }
      })
    })

    return connections
  })

  return { links, simulation }
}
```

### 3. Three.js深空背景

#### 星空场景渲染

```typescript
// DeepSpaceBackground.vue
import * as THREE from 'three'

class StarfieldScene {
  private scene: THREE.Scene
  private camera: THREE.PerspectiveCamera
  private renderer: THREE.WebGLRenderer
  private stars: THREE.Points

  constructor(canvas: HTMLCanvasElement) {
    this.initScene(canvas)
    this.createStarfield()
    this.animate()
  }

  private createStarfield() {
    const starCount = 300
    const positions = new Float32Array(starCount * 3)
    const colors = new Float32Array(starCount * 3)

    for (let i = 0; i < starCount; i++) {
      // 随机分布星点
      positions[i * 3] = (Math.random() - 0.5) * 2000
      positions[i * 3 + 1] = (Math.random() - 0.5) * 2000
      positions[i * 3 + 2] = (Math.random() - 0.5) * 2000

      // 星点颜色变化
      const color = new THREE.Color()
      color.setHSL(0.6 + Math.random() * 0.2, 0.8, 0.5 + Math.random() * 0.5)
      colors[i * 3] = color.r
      colors[i * 3 + 1] = color.g
      colors[i * 3 + 2] = color.b
    }

    const geometry = new THREE.BufferGeometry()
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3))

    const material = new THREE.PointsMaterial({
      size: 2,
      vertexColors: true,
      transparent: true,
      opacity: 0.8
    })

    this.stars = new THREE.Points(geometry, material)
    this.scene.add(this.stars)
  }
}
```

## 🎭 视觉效果系统

### GSAP动画架构

#### 1. 页面切换动画

```typescript
const animateSlideTransition = (fromIndex: number, toIndex: number) => {
  const tl = gsap.timeline()

  // 当前页面星球的退出动画
  const currentStars = document.querySelectorAll('.member-star')
  tl.to(currentStars, {
    scale: 0.8,
    opacity: 0.3,
    rotationY: toIndex > fromIndex ? -45 : 45,
    duration: 0.4,
    ease: "power2.out",
    stagger: { amount: 0.2, from: "random" }
  })

  // 新页面星球的进入动画
  tl.fromTo('.member-star',
    {
      scale: 0.6,
      opacity: 0,
      rotationY: toIndex > fromIndex ? 45 : -45,
      z: -100
    },
    {
      scale: 1,
      opacity: 1,
      rotationY: 0,
      z: 0,
      duration: 0.6,
      ease: "power4.out",
      stagger: { amount: 0.3, from: "center" }
    }, 0.2)
}
```

#### 2. ScrollTrigger视差效果

```typescript
const setupScrollTrigger = () => {
  // 整个section的进入动画
  gsap.fromTo(sectionRef.value,
    { opacity: 0, y: 100, scale: 0.95 },
    {
      opacity: 1,
      y: 0,
      scale: 1,
      duration: 1.2,
      ease: "power3.out",
      scrollTrigger: {
        trigger: sectionRef.value,
        start: "top 80%",
        end: "top 20%",
        toggleActions: "play none none reverse"
      }
    }
  )

  // 成员星球的交错动画
  gsap.fromTo('.member-star',
    { scale: 0, opacity: 0, rotationY: 180 },
    {
      scale: 1,
      opacity: 1,
      rotationY: 0,
      duration: 0.8,
      ease: "back.out(1.7)",
      stagger: { amount: 1.5, from: "random" },
      scrollTrigger: {
        trigger: sectionRef.value,
        start: "top 50%",
        toggleActions: "play none none reverse"
      }
    }
  )
}
```

### 粒子系统架构

#### 1. 全局粒子分布算法

```typescript
// GlobalParticles.vue
const getGlobalParticleStyle = (index: number) => {
  const seed = index * 0.618033988749 // 黄金比例

  return {
    left: `${(seed % 1) * 100}%`,
    top: `${((seed * 7) % 1) * 100}%`,
    animationDelay: `${(seed * 13) % 1 * 10}s`,
    animationDuration: `${8 + (seed * 17) % 1 * 12}s`
  }
}

const getCenterParticleStyle = (index: number) => {
  const angle = (index / centerParticleCount.value) * Math.PI * 2
  const radius = 15 + Math.random() * 25 // 15-40% 半径范围

  const x = props.centerX + Math.cos(angle) * radius
  const y = props.centerY + Math.sin(angle) * radius

  return {
    left: `${x}%`,
    top: `${y}%`,
    animationDelay: `${Math.random() * 5}s`,
    animationDuration: `${6 + Math.random() * 8}s`
  }
}
```

#### 2. 性能优化策略

```typescript
// 设备检测与性能调节
const useDeviceDetection = () => {
  const isMobile = computed(() => window.innerWidth <= 768)
  const isLowEnd = computed(() => {
    const canvas = document.createElement('canvas')
    const gl = canvas.getContext('webgl')
    const renderer = gl?.getParameter(gl.RENDERER) || ''
    return renderer.includes('Mali') || renderer.includes('Adreno')
  })

  const particleCount = computed(() => {
    if (isLowEnd.value) return 30
    if (isMobile.value) return 60
    return 120
  })

  return { isMobile, isLowEnd, particleCount }
}
```

## 🏗️ 组件架构

### 组件层次结构

```
App.vue (根组件)
├── GlassNavigation.vue (玻璃导航栏)
├── HeroSection.vue (首屏区域)
│   ├── Ring2D.vue (2D星际门)
│   └── Canvas (环形粒子系统)
├── MembersCircle.vue (成员星云)
│   ├── DeepSpaceBackground.vue (深空背景)
│   ├── GalaxyInfoWidget.vue (信息控件)
│   ├── ProgressBar.vue (进度条)
│   ├── PaginationArrows.vue (分页箭头)
│   └── Swiper
│       └── GalaxySlide.vue (星云页面)
│           ├── MemberStar.vue (成员星球)
│           └── ConnectionLines (连接线系统)
├── StarCalendar.vue (星历日历)
├── AppFooter.vue (页脚)
├── CustomPointer.vue (自定义光标)
└── GlobalParticles.vue (全局粒子)
```

### 状态管理架构

```typescript
// stores/members.ts
export const useMembersStore = defineStore('members', () => {
  // 状态
  const allMembers = ref<Member[]>([])
  const visibleMembers = ref<Member[]>([])
  const currentPage = ref(0)
  const isLoading = ref(false)

  // 计算属性
  const totalMembers = computed(() => allMembers.value.length)
  const memberPages = computed(() => {
    const pages = []
    const pageSize = 45
    for (let i = 0; i < allMembers.value.length; i += pageSize) {
      pages.push(allMembers.value.slice(i, i + pageSize))
    }
    return pages
  })

  // 异步操作
  const loadMembers = async (): Promise<Member[]> => {
    isLoading.value = true
    try {
      // 尝试加载真实QQ群成员数据
      let newMembers = await loadQQGroupMembers()

      // 如果加载失败，使用模拟数据
      if (newMembers.length === 0) {
        newMembers = generateMockMembers(1, 80)
      }

      allMembers.value = newMembers
      return newMembers
    } finally {
      isLoading.value = false
    }
  }

  return {
    allMembers,
    visibleMembers,
    currentPage,
    isLoading,
    totalMembers,
    memberPages,
    loadMembers
  }
})
```

### API服务架构

```typescript
// services/api.ts
export class ApiClient {
  private baseURL: string

  constructor() {
    this.baseURL = import.meta.env.VITE_API_BASE_URL ||
      (import.meta.env.PROD ? '' : 'http://localhost:8000')
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseURL}${endpoint}`

    try {
      const response = await fetch(url, {
        headers: { 'Content-Type': 'application/json' },
        ...options
      })

      if (!response.ok) {
        throw new ApiError(`HTTP ${response.status}`, response.status, endpoint)
      }

      return await response.json()
    } catch (error) {
      if (error instanceof ApiError) throw error
      throw new ApiError(`Network error: ${error.message}`, undefined, endpoint)
    }
  }

  // 获取成员列表
  async getMembers(page: number = 1, pageSize: number = 50): Promise<MemberListResponse> {
    return this.request<MemberListResponse>(
      `/api/members?page=${page}&page_size=${pageSize}`
    )
  }

  // 获取头像URL
  getAvatarUrl(memberId: number): string {
    return `${this.baseURL}/api/avatar/${memberId}`
  }
}

// 错误处理和重试机制
export const withRetry = async <T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  delay: number = 1000
): Promise<T> => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn()
    } catch (error) {
      if (i === maxRetries - 1) throw error
      await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)))
    }
  }
  throw new Error('Max retries exceeded')
}
```

## ⚡ 性能优化

### 1. Web Workers优化

```typescript
// 粒子系统使用Web Workers
const initRingParticles = () => {
  const canvas = ringParticlesCanvas.value
  if (!canvas) return

  // 转换为离屏Canvas
  const offscreen = canvas.transferControlToOffscreen()

  // 创建Worker
  particleWorker = new Worker(
    new URL('../utils/ringParticlesWorker.ts', import.meta.url),
    { type: 'module' }
  )

  // 发送Canvas到Worker
  particleWorker.postMessage({ type: 'init', canvas: offscreen }, [offscreen])
}
```

### 2. 动画性能优化

```typescript
// 使用GSAP的性能优化
gsap.config({
  force3D: true,        // 强制GPU加速
  nullTargetWarn: false // 禁用警告提升性能
})

// 批量动画优化
const animateStars = (elements: Element[]) => {
  gsap.set(elements, { force3D: true }) // 预设GPU加速

  gsap.fromTo(elements,
    { scale: 0, opacity: 0 },
    {
      scale: 1,
      opacity: 1,
      duration: 0.8,
      ease: "back.out(1.7)",
      stagger: { amount: 1.5, from: "random" }
    }
  )
}
```

### 3. 内存管理

```typescript
// 组件卸载时清理资源
onUnmounted(() => {
  // 清理粒子系统
  if (particleWorker) {
    particleWorker.terminate()
    particleWorker = null
  }

  // 清理GSAP动画
  gsap.killTweensOf("*")

  // 清理Three.js资源
  if (renderer) {
    renderer.dispose()
    scene.clear()
  }

  // 清理事件监听器
  window.removeEventListener('resize', handleResize)
  window.removeEventListener('mousemove', handleMouseMove)
})
```

### 4. 响应式优化

```scss
// 移动端优化
@media (max-width: 768px) {
  .hero-section {
    .ring-container {
      transform: scale(0.7); // 缩小星际门
    }

    .ring-particles-canvas {
      opacity: 0.5; // 降低粒子密度
    }
  }

  .members-galaxy {
    .member-star {
      transform: scale(0.8); // 缩小成员头像
    }
  }
}

// 减少动画偏好
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

## 🚀 构建与部署

### Vite配置优化

```typescript
// vite.config.ts
export default defineConfig({
  plugins: [
    vue(),
    // 生产环境移除console
    process.env.NODE_ENV === 'production' && {
      name: 'remove-console',
      transform(code, id) {
        if (id.includes('node_modules')) return
        return code.replace(/console\.(log|warn|error|info)\(.*?\);?/g, '')
      }
    }
  ].filter(Boolean),

  // 开发服务器配置
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      }
    }
  },

  // 构建优化
  build: {
    target: 'es2020',
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true
      }
    },
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor-vue': ['vue', 'pinia'],
          'vendor-three': ['three'],
          'vendor-gsap': ['gsap'],
          'vendor-swiper': ['swiper']
        }
      }
    },
    chunkSizeWarningLimit: 1000
  },

  // 依赖优化
  optimizeDeps: {
    include: ['vue', 'three', 'gsap', 'swiper', 'd3-force']
  }
})
```

### 环境配置

#### 开发环境 (.env.development)

```bash
# API配置
VITE_API_BASE_URL=http://localhost:8000

# 调试配置
VITE_DEBUG_MODE=true
VITE_PERFORMANCE_MONITOR=true

# 功能开关
VITE_ENABLE_3D_EFFECTS=true
VITE_ENABLE_PARTICLES=true
VITE_ENABLE_FORCE_CONNECTIONS=true
```

#### 生产环境 (.env.production)

```bash
# API配置
VITE_API_BASE_URL=

# 性能配置
VITE_DEBUG_MODE=false
VITE_PERFORMANCE_MONITOR=false

# 功能优化
VITE_ENABLE_3D_EFFECTS=true
VITE_ENABLE_PARTICLES=true
VITE_ENABLE_FORCE_CONNECTIONS=true
```

### 部署脚本

#### 开发环境启动

```bash
# 安装依赖
npm install
# 或
pnpm install

# 启动开发服务器
npm run dev
# 或
pnpm dev

# 类型检查
npm run type-check
```

#### 生产环境构建

```bash
# 构建生产版本
npm run build

# 预览构建结果
npm run preview

# 分析构建包大小
npm run build:analyze
```

### 性能监控

#### 运行时监控

```typescript
// 性能监控工具
export const usePerformanceMonitor = () => {
  const fps = ref(60)
  const memoryUsage = ref(0)

  const startMonitoring = () => {
    let lastTime = performance.now()
    let frameCount = 0

    const monitor = () => {
      frameCount++
      const currentTime = performance.now()

      if (currentTime - lastTime >= 1000) {
        fps.value = Math.round((frameCount * 1000) / (currentTime - lastTime))
        frameCount = 0
        lastTime = currentTime

        // 内存使用监控
        if ('memory' in performance) {
          memoryUsage.value = (performance as any).memory.usedJSHeapSize / 1024 / 1024
        }
      }

      requestAnimationFrame(monitor)
    }

    monitor()
  }

  return { fps, memoryUsage, startMonitoring }
}
```

### 部署检查清单

#### 生产环境检查

- [ ] 移除所有console.log和调试代码
- [ ] 启用代码压缩和混淆
- [ ] 配置正确的API端点
- [ ] 启用GZIP压缩
- [ ] 配置CDN加速
- [ ] 设置正确的缓存策略
- [ ] 检查移动端兼容性
- [ ] 验证所有动画性能
- [ ] 测试不同设备的表现

#### 性能优化检查

- [ ] 图片资源优化（WebP格式）
- [ ] 字体文件预加载
- [ ] 关键CSS内联
- [ ] 非关键资源延迟加载
- [ ] Service Worker缓存策略
- [ ] 代码分割和懒加载
- [ ] Tree Shaking优化
- [ ] 第三方库按需引入

---

## 📞 技术支持

### 开发调试

```bash
# 启用调试模式
VITE_DEBUG_MODE=true npm run dev

# 性能分析模式
VITE_PERFORMANCE_MONITOR=true npm run dev

# 禁用特效（低端设备测试）
VITE_ENABLE_3D_EFFECTS=false npm run dev
```

### 常见问题

1. **粒子效果卡顿**: 检查设备性能，降低粒子数量
2. **Three.js渲染问题**: 确认WebGL支持，检查GPU驱动
3. **Swiper滑动异常**: 检查触摸事件冲突，调整灵敏度
4. **GSAP动画不流畅**: 启用GPU加速，减少同时动画数量

如有问题，请查看浏览器控制台错误信息或联系开发团队。
