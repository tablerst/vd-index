<template>
  <div class="badge-preview">
    <!-- 顶部导航 -->
    <GlassNavigation />

    <!-- 主要内容区域 -->
    <main class="main-content">
      <!-- 页面标题 -->
      <div class="page-header">
        <div class="container">
          <h1 class="page-title">3D徽章打印预览</h1>
          <p class="page-description">上传图片，预览3D徽章效果，调整光源和角度</p>
        </div>
      </div>

      <!-- 3D预览区域 -->
      <div class="preview-section">
        <div class="container">
          <!-- 3D画布区域 -->
          <div class="canvas-container">
            <canvas
              ref="badgeCanvas"
              class="badge-canvas"
              @mousedown="onMouseDown"
              @mousemove="onMouseMove"
              @mouseup="onMouseUp"
              @wheel="onWheel"
            ></canvas>

            <!-- 加载状态 -->
            <div v-if="isLoading" class="loading-overlay">
              <div class="loading-spinner"></div>
              <p>正在初始化3D场景...</p>
            </div>

            <!-- 错误状态 -->
            <div v-if="error" class="error-overlay">
              <div class="error-icon">⚠️</div>
              <p>{{ error }}</p>
              <button class="btn btn-primary" @click="location.reload()">刷新页面</button>
            </div>

            <!-- 操作提示 -->
            <div class="controls-hint">
              <p>鼠标左键：旋转 | 滚轮：缩放 | 右键：平移</p>
              <p class="keyboard-hints">快捷键: Ctrl+O 上传 | Ctrl+R 重置 | Ctrl+S 导出</p>
            </div>
          </div>

          <!-- 控制面板 -->
          <div class="control-panel">
              <!-- 图片上传 -->
              <div class="control-section">
                <h3>图片上传</h3>
                <label class="upload-area" for="fileInput">
                  <input
                    id="fileInput"
                    ref="fileInput"
                    type="file"
                    accept="image/*"
                    @change="onFileUpload"
                    style="display: none;"
                  >
                  <div class="upload-content">
                    <div class="upload-icon">📁</div>
                    <p>点击上传图片</p>
                    <small>支持 JPG, PNG, GIF 格式</small>
                  </div>
                </label>
              </div>

              <!-- 徽章控制 -->
              <div class="control-section">
                <h3>徽章控制</h3>
                <div class="control-group">
                  <label>厚度</label>
                  <input 
                    type="range" 
                    v-model="badgeThickness" 
                    min="0.1" 
                    max="2" 
                    step="0.1"
                    @input="updateBadgeGeometry"
                  >
                  <span>{{ badgeThickness }}mm</span>
                </div>
                
                <div class="control-group">
                  <label>尺寸</label>
                  <input 
                    type="range" 
                    v-model="badgeSize" 
                    min="20" 
                    max="100" 
                    step="5"
                    @input="updateBadgeGeometry"
                  >
                  <span>{{ badgeSize }}mm</span>
                </div>
              </div>

              <!-- 光源控制 -->
              <div class="control-section">
                <h3>光源控制</h3>
                <div class="control-group">
                  <label>光源强度</label>
                  <input 
                    type="range" 
                    v-model="lightIntensity" 
                    min="0.1" 
                    max="3" 
                    step="0.1"
                    @input="updateLighting"
                  >
                  <span>{{ lightIntensity }}</span>
                </div>
                
                <div class="control-group">
                  <label>环境光</label>
                  <input 
                    type="range" 
                    v-model="ambientIntensity" 
                    min="0" 
                    max="1" 
                    step="0.1"
                    @input="updateLighting"
                  >
                  <span>{{ ambientIntensity }}</span>
                </div>
                
                <div class="control-group">
                  <label>光源X位置</label>
                  <input 
                    type="range" 
                    v-model="lightPosition.x" 
                    min="-10" 
                    max="10" 
                    step="0.5"
                    @input="updateLighting"
                  >
                  <span>{{ lightPosition.x }}</span>
                </div>
                
                <div class="control-group">
                  <label>光源Y位置</label>
                  <input 
                    type="range" 
                    v-model="lightPosition.y" 
                    min="-10" 
                    max="10" 
                    step="0.5"
                    @input="updateLighting"
                  >
                  <span>{{ lightPosition.y }}</span>
                </div>
                
                <div class="control-group">
                  <label>光源Z位置</label>
                  <input
                    type="range"
                    v-model="lightPosition.z"
                    min="1"
                    max="20"
                    step="0.5"
                    @input="updateLighting"
                  >
                  <span>{{ lightPosition.z }}</span>
                </div>

                <div class="control-group">
                  <label>光源颜色</label>
                  <input
                    type="color"
                    v-model="lightColor"
                    @input="updateLighting"
                  >
                  <span>{{ lightColor }}</span>
                </div>

                <div class="control-group">
                  <label>补光强度</label>
                  <input
                    type="range"
                    v-model="fillLightIntensity"
                    min="0"
                    max="1"
                    step="0.1"
                    @input="updateLighting"
                  >
                  <span>{{ fillLightIntensity }}</span>
                </div>

                <div class="control-group">
                  <label>背景光强度</label>
                  <input
                    type="range"
                    v-model="backLightIntensity"
                    min="0"
                    max="1"
                    step="0.1"
                    @input="updateLighting"
                  >
                  <span>{{ backLightIntensity }}</span>
                </div>

                <!-- 操作按钮 -->
                <div class="action-buttons">
                  <button class="btn btn-secondary" @click="resetView" title="重置视图 (Ctrl+R)">
                    🔄 重置
                  </button>
                  <button class="btn btn-primary" @click="exportPreview" title="导出预览 (Ctrl+S)">
                    💾 导出
                  </button>
                </div>
              </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 全局背景粒子 -->
    <GlobalParticles />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'
import GlassNavigation from '@/components/GlassNavigation.vue'
import GlobalParticles from '@/components/GlobalParticles.vue'

// 响应式数据
const badgeCanvas = ref<HTMLCanvasElement>()
const fileInput = ref<HTMLInputElement>()
const isLoading = ref(true)
const error = ref('')
const isWebGLSupported = ref(true)

// 徽章参数
const badgeThickness = ref(1.0)
const badgeSize = ref(50)

// 光源参数
const lightIntensity = ref(1.5)
const ambientIntensity = ref(0.3)
const lightPosition = ref({ x: 5, y: 5, z: 10 })
const lightColor = ref('#ffffff')
const fillLightIntensity = ref(0.3)
const backLightIntensity = ref(0.2)

// Three.js 对象
let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let controls: OrbitControls
let badgeMesh: THREE.Mesh
let directionalLight: THREE.DirectionalLight
let ambientLight: THREE.AmbientLight
let fillLight: THREE.DirectionalLight
let backLight: THREE.DirectionalLight
let animationId: number

// 鼠标交互状态
const isMouseDown = ref(false)
const mousePosition = ref({ x: 0, y: 0 })

// 检测WebGL支持
const checkWebGLSupport = (): boolean => {
  try {
    const canvas = document.createElement('canvas')
    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl')
    return !!gl
  } catch (e) {
    return false
  }
}

// 初始化3D场景
const initThreeJS = async () => {
  if (!badgeCanvas.value) return

  // 检测WebGL支持
  if (!checkWebGLSupport()) {
    isWebGLSupported.value = false
    error.value = '您的浏览器不支持WebGL，无法显示3D预览'
    isLoading.value = false
    return
  }

  try {
    const canvas = badgeCanvas.value
    const width = canvas.clientWidth
    const height = canvas.clientHeight

  // 创建场景
  scene = new THREE.Scene()
  scene.background = new THREE.Color(0x0a0a0a)

  // 创建相机
  camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000)
  camera.position.set(0, 0, 5)

  // 创建渲染器
  renderer = new THREE.WebGLRenderer({ 
    canvas, 
    antialias: true,
    alpha: true 
  })
  renderer.setSize(width, height)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.shadowMap.enabled = true
  renderer.shadowMap.type = THREE.PCFSoftShadowMap

  // 创建轨道控制器
  controls = new OrbitControls(camera, canvas)
  controls.enableDamping = true
  controls.dampingFactor = 0.05
  controls.enableZoom = true
  controls.enablePan = true

  // 创建默认徽章
  createDefaultBadge()

  // 创建地面
  createGround()

  // 设置光源
  setupLighting()

    // 开始渲染循环
    animate()

    isLoading.value = false
  } catch (err) {
    console.error('初始化3D场景失败:', err)
    error.value = '初始化3D场景失败，请刷新页面重试'
    isLoading.value = false
  }
}

// 创建默认徽章
const createDefaultBadge = () => {
  // 创建徽章组
  const badgeGroup = new THREE.Group()

  // 主体圆形几何体
  const mainGeometry = new THREE.CylinderGeometry(
    badgeSize.value / 20,
    badgeSize.value / 20,
    badgeThickness.value / 10,
    32
  )

  // 主体材质 - 金属质感
  const mainMaterial = new THREE.MeshPhongMaterial({
    color: 0xc0c0c0,
    shininess: 100,
    transparent: false,
    side: THREE.DoubleSide
  })

  // 创建主体网格
  const mainMesh = new THREE.Mesh(mainGeometry, mainMaterial)
  mainMesh.castShadow = true
  mainMesh.receiveShadow = true

  // 添加到组
  badgeGroup.add(mainMesh)

  // 将组赋值给badgeMesh以便后续操作
  badgeMesh = badgeGroup
  scene.add(badgeGroup)
}

// 创建地面
const createGround = () => {
  const groundGeometry = new THREE.PlaneGeometry(20, 20)
  const groundMaterial = new THREE.MeshPhongMaterial({
    color: 0x333333,
    transparent: true,
    opacity: 0.3
  })

  const ground = new THREE.Mesh(groundGeometry, groundMaterial)
  ground.rotation.x = -Math.PI / 2
  ground.position.y = -2
  ground.receiveShadow = true

  scene.add(ground)
}

// 设置光源
const setupLighting = () => {
  // 环境光
  ambientLight = new THREE.AmbientLight(0x404040, ambientIntensity.value)
  scene.add(ambientLight)

  // 主方向光
  directionalLight = new THREE.DirectionalLight(0xffffff, lightIntensity.value)
  directionalLight.position.set(
    lightPosition.value.x,
    lightPosition.value.y,
    lightPosition.value.z
  )
  directionalLight.castShadow = true
  directionalLight.shadow.mapSize.width = 2048
  directionalLight.shadow.mapSize.height = 2048
  directionalLight.shadow.camera.near = 0.1
  directionalLight.shadow.camera.far = 50
  directionalLight.shadow.camera.left = -10
  directionalLight.shadow.camera.right = 10
  directionalLight.shadow.camera.top = 10
  directionalLight.shadow.camera.bottom = -10
  scene.add(directionalLight)

  // 添加补光
  fillLight = new THREE.DirectionalLight(0x4080ff, fillLightIntensity.value)
  fillLight.position.set(-5, -5, 5)
  scene.add(fillLight)

  // 添加背景光
  backLight = new THREE.DirectionalLight(0xff8040, backLightIntensity.value)
  backLight.position.set(0, 0, -10)
  scene.add(backLight)
}

// 动画循环
const animate = () => {
  animationId = requestAnimationFrame(animate)
  
  controls.update()
  renderer.render(scene, camera)
}

// 文件上传处理 - 现在使用label的原生关联，不需要JavaScript触发
const triggerFileUpload = () => {
  // 这个函数现在不需要了，因为使用了label的原生关联
}

const onFileUpload = (event: Event) => {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return

  // 检查文件类型
  if (!file.type.startsWith('image/')) {
    error.value = '请选择有效的图片文件'
    setTimeout(() => error.value = '', 3000)
    return
  }

  // 检查文件大小 (限制为5MB)
  if (file.size > 5 * 1024 * 1024) {
    error.value = '图片文件大小不能超过5MB'
    setTimeout(() => error.value = '', 3000)
    return
  }

  const reader = new FileReader()
  reader.onload = (e) => {
    const imageUrl = e.target?.result as string
    loadImageTexture(imageUrl)
  }
  reader.onerror = () => {
    error.value = '读取图片文件失败'
    setTimeout(() => error.value = '', 3000)
  }
  reader.readAsDataURL(file)
}

// 重置视图
const resetView = () => {
  if (controls) {
    controls.reset()
  }

  // 重置所有参数到默认值
  badgeThickness.value = 1.0
  badgeSize.value = 50
  lightIntensity.value = 1.5
  ambientIntensity.value = 0.3
  lightPosition.value = { x: 5, y: 5, z: 10 }
  lightColor.value = '#ffffff'
  fillLightIntensity.value = 0.3
  backLightIntensity.value = 0.2

  // 更新几何体和光源
  updateBadgeGeometry()
  updateLighting()
}

// 导出预览图
const exportPreview = () => {
  if (!renderer) return

  try {
    const canvas = renderer.domElement
    const link = document.createElement('a')
    link.download = `badge-preview-${Date.now()}.png`
    link.href = canvas.toDataURL('image/png')
    link.click()
  } catch (err) {
    console.error('导出失败:', err)
    error.value = '导出预览图失败'
    setTimeout(() => error.value = '', 3000)
  }
}

// 加载图片纹理
const loadImageTexture = (imageUrl: string) => {
  const loader = new THREE.TextureLoader()
  loader.load(imageUrl, (texture) => {
    // 更新徽章主体材质
    if (badgeMesh && badgeMesh.children && badgeMesh.children[0]) {
      const mainMesh = badgeMesh.children[0] as THREE.Mesh
      const material = mainMesh.material as THREE.MeshPhongMaterial

      // 设置纹理
      texture.wrapS = THREE.RepeatWrapping
      texture.wrapT = THREE.RepeatWrapping
      texture.flipY = false

      material.map = texture
      material.needsUpdate = true
    }
  })
}

// 更新徽章几何体
const updateBadgeGeometry = () => {
  if (!badgeMesh || !badgeMesh.children) return

  // 更新主体几何体
  const mainMesh = badgeMesh.children[0]
  if (mainMesh && mainMesh.geometry) {
    mainMesh.geometry.dispose()
    const newMainGeometry = new THREE.CylinderGeometry(
      badgeSize.value / 20,
      badgeSize.value / 20,
      badgeThickness.value / 10,
      32
    )
    mainMesh.geometry = newMainGeometry
  }


}

// 更新光源
const updateLighting = () => {
  if (directionalLight) {
    directionalLight.intensity = lightIntensity.value
    directionalLight.position.set(
      lightPosition.value.x,
      lightPosition.value.y,
      lightPosition.value.z
    )
    // 更新光源颜色
    directionalLight.color.setHex(parseInt(lightColor.value.replace('#', '0x')))
  }

  if (ambientLight) {
    ambientLight.intensity = ambientIntensity.value
  }

  if (fillLight) {
    fillLight.intensity = fillLightIntensity.value
  }

  if (backLight) {
    backLight.intensity = backLightIntensity.value
  }
}

// 鼠标事件处理
const onMouseDown = (event: MouseEvent) => {
  isMouseDown.value = true
  mousePosition.value = { x: event.clientX, y: event.clientY }
}

const onMouseMove = (event: MouseEvent) => {
  if (!isMouseDown.value) return
  
  const deltaX = event.clientX - mousePosition.value.x
  const deltaY = event.clientY - mousePosition.value.y
  
  mousePosition.value = { x: event.clientX, y: event.clientY }
}

const onMouseUp = () => {
  isMouseDown.value = false
}

const onWheel = (event: WheelEvent) => {
  event.preventDefault()
}

// 窗口大小调整
const handleResize = () => {
  if (!badgeCanvas.value || !camera || !renderer) return

  const width = badgeCanvas.value.clientWidth
  const height = badgeCanvas.value.clientHeight

  camera.aspect = width / height
  camera.updateProjectionMatrix()
  renderer.setSize(width, height)
}

// 键盘快捷键处理
const handleKeyDown = (event: KeyboardEvent) => {
  if (event.ctrlKey || event.metaKey) {
    switch (event.key) {
      case 'r':
        event.preventDefault()
        resetView()
        break
      case 's':
        event.preventDefault()
        exportPreview()
        break
      case 'o':
        event.preventDefault()
        triggerFileUpload()
        break
    }
  }
}

// 生命周期
onMounted(() => {
  initThreeJS()
  window.addEventListener('resize', handleResize)
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  if (animationId) {
    cancelAnimationFrame(animationId)
  }

  if (renderer) {
    renderer.dispose()
  }

  window.removeEventListener('resize', handleResize)
  window.removeEventListener('keydown', handleKeyDown)
})
</script>

<style scoped lang="scss">
@use '../styles/variables.scss' as *;

.badge-preview {
  min-height: 100vh;
  background: var(--base-dark);
  color: var(--text-primary);
}

.main-content {
  padding-top: 80px; // 为导航栏留出空间
}

.page-header {
  padding: var(--spacing-3xl) 0 var(--spacing-2xl);
  text-align: center;
  
  .page-title {
    font-size: var(--font-size-4xl);
    font-weight: var(--font-weight-bold);
    background: var(--primary-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: var(--spacing-md);
  }
  
  .page-description {
    font-size: var(--font-size-lg);
    color: var(--text-secondary);
    max-width: 600px;
    margin: 0 auto;
  }
}

.preview-section {
  padding: 0 0 var(--spacing-3xl);
}

.container {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2xl);
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--spacing-lg);
  
  @include media-down(lg) {
    grid-template-columns: 1fr;
    gap: var(--spacing-xl);
  }
}

.canvas-container {
  position: relative;
  width: 100%;
  height: 60vh;
  min-height: 500px;
  @include glass-effect();
  border-radius: var(--radius-lg);
  overflow: hidden;
  
  .badge-canvas {
    width: 100%;
    height: 100%;
    display: block;
    cursor: grab;
    
    &:active {
      cursor: grabbing;
    }
  }
  
  .loading-overlay,
  .error-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: rgba(0, 0, 0, 0.8);
    color: var(--text-primary);
    text-align: center;
    padding: var(--spacing-xl);

    .loading-spinner {
      width: 40px;
      height: 40px;
      border: 3px solid var(--primary-alpha);
      border-top: 3px solid var(--primary);
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin-bottom: var(--spacing-md);
    }

    .error-icon {
      font-size: 3rem;
      margin-bottom: var(--spacing-md);
    }

    p {
      margin-bottom: var(--spacing-lg);
      max-width: 300px;
    }

    .btn {
      padding: var(--spacing-md) var(--spacing-lg);
      border-radius: var(--radius-md);
      font-weight: var(--font-weight-medium);
      transition: all var(--transition-base);
      cursor: pointer;
      border: none;

      &.btn-primary {
        background: var(--primary-gradient);
        color: white;

        &:hover {
          transform: translateY(-2px);
          box-shadow: var(--shadow-glow);
        }
      }
    }
  }
  
  .controls-hint {
    position: absolute;
    bottom: var(--spacing-md);
    left: var(--spacing-md);
    right: var(--spacing-md);
    text-align: center;

    p {
      font-size: var(--font-size-sm);
      color: var(--text-secondary);
      @include glass-effect();
      padding: var(--spacing-sm) var(--spacing-md);
      border-radius: var(--radius-md);
      margin: 0 0 var(--spacing-xs) 0;

      &.keyboard-hints {
        font-size: var(--font-size-xs);
        opacity: 0.8;
        margin: var(--spacing-xs) 0 0 0;
      }
    }

    .action-buttons {
      display: flex;
      gap: var(--spacing-md);
      margin-top: var(--spacing-lg);

      .btn {
        flex: 1;
        padding: var(--spacing-md);
        border-radius: var(--radius-md);
        font-weight: var(--font-weight-medium);
        transition: all var(--transition-base);
        cursor: pointer;
        border: none;
        font-size: var(--font-size-sm);

        &.btn-primary {
          background: var(--primary-gradient);
          color: white;

          &:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-glow);
          }
        }

        &.btn-secondary {
          background: var(--glass-bg);
          color: var(--text-primary);
          border: 1px solid var(--border-color);

          &:hover {
            background: var(--glass-bg-hover);
            transform: translateY(-2px);
          }
        }
      }
    }
  }
}

.control-panel {
  @include glass-effect();
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  width: 100%;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--spacing-lg);
  
  .control-section {
    margin-bottom: var(--spacing-xl);
    
    &:last-child {
      margin-bottom: 0;
    }
    
    h3 {
      font-size: var(--font-size-lg);
      font-weight: var(--font-weight-semibold);
      margin-bottom: var(--spacing-md);
      color: var(--text-primary);
    }
  }
  
  .upload-area {
    display: block;
    border: 2px dashed var(--border-color);
    border-radius: var(--radius-md);
    padding: var(--spacing-xl);
    text-align: center;
    cursor: pointer;
    transition: all var(--transition-base);

    &:hover {
      border-color: var(--primary);
      background: var(--primary-alpha);
    }
    
    .upload-icon {
      font-size: 2rem;
      margin-bottom: var(--spacing-sm);
    }
    
    p {
      margin: 0 0 var(--spacing-xs);
      font-weight: var(--font-weight-medium);
    }
    
    small {
      color: var(--text-secondary);
    }
  }
  
  .control-group {
    display: grid;
    grid-template-columns: 80px 1fr 60px;
    align-items: center;
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-md);
    
    label {
      font-size: var(--font-size-sm);
      color: var(--text-secondary);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    input[type="range"] {
      width: 100%;
      height: 4px;
      background: var(--border-color);
      border-radius: var(--radius-sm);
      outline: none;

      &::-webkit-slider-thumb {
        appearance: none;
        width: 16px;
        height: 16px;
        background: var(--primary);
        border-radius: 50%;
        cursor: pointer;
      }

      &::-moz-range-thumb {
        width: 16px;
        height: 16px;
        background: var(--primary);
        border-radius: 50%;
        cursor: pointer;
        border: none;
      }
    }

    input[type="color"] {
      width: 100%;
      height: 32px;
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
      background: transparent;
      cursor: pointer;

      &::-webkit-color-swatch-wrapper {
        padding: 0;
      }

      &::-webkit-color-swatch {
        border: none;
        border-radius: var(--radius-sm);
      }
    }

    span {
      font-size: var(--font-size-xs);
      color: var(--text-secondary);
      text-align: right;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      min-width: 0;
    }
    
    span {
      min-width: 60px;
      text-align: right;
      font-size: var(--font-size-sm);
      color: var(--text-primary);
    }
  }
  
  .button-group {
    display: flex;
    gap: var(--spacing-md);
    
    .btn {
      flex: 1;
      padding: var(--spacing-md) var(--spacing-lg);
      border-radius: var(--radius-md);
      font-weight: var(--font-weight-medium);
      transition: all var(--transition-base);
      cursor: pointer;
      
      &.btn-primary {
        background: var(--primary-gradient);
        color: white;
        border: none;
        
        &:hover {
          transform: translateY(-2px);
          box-shadow: var(--shadow-glow);
        }
      }
      
      &.btn-secondary {
        background: transparent;
        color: var(--text-primary);
        border: 1px solid var(--border-color);
        
        &:hover {
          border-color: var(--primary);
          background: var(--primary-alpha);
        }
      }
    }
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

// 响应式设计
@media (max-width: 1024px) {
  .container {
    padding: 0 var(--spacing-md);
  }

  .control-panel {
    grid-template-columns: 1fr;
    gap: var(--spacing-md);
  }
}

@media (max-width: 768px) {
  .canvas-container {
    height: 50vh;
    min-height: 400px;
  }

  .control-panel {
    .control-group {
      grid-template-columns: 1fr;
      text-align: center;
      gap: var(--spacing-xs);

      label {
        margin-bottom: var(--spacing-xs);
      }

      span {
        margin-top: var(--spacing-xs);
      }
    }

    .action-buttons {
      flex-direction: column;
      gap: var(--spacing-sm);
    }
  }

  .controls-hint {
    p.keyboard-hints {
      display: none;
    }
  }
}
</style>
