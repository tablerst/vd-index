import * as THREE from 'three'

interface Member {
  id: number
  name: string
  avatarURL: string
  bio?: string
  joinDate?: string
  contribution?: number
}

interface ScatterCallbacks {
  onMemberHover?: (member: Member) => void
  onMemberClick?: (member: Member) => void
  onMemberLeave?: () => void
}

// 主题检测函数
function getThemeAwareColors() {
  const isDarkTheme = document.documentElement.classList.contains('dark') ||
                     document.body.classList.contains('dark') ||
                     getComputedStyle(document.documentElement).getPropertyValue('--primary').trim() === '#AA83FF'

  return {
    saturation: isDarkTheme ? 0.7 : 0.85,  // 浅色主题增加饱和度
    lightness: isDarkTheme ? 0.7 : 0.55    // 浅色主题降低亮度增加对比度
  }
}

let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let animationId: number
let instancedMesh: THREE.InstancedMesh
let raycaster: THREE.Raycaster
let mouse: THREE.Vector2
let callbacks: ScatterCallbacks = {}
let members: Member[] = []
let hoveredInstanceId: number | null = null
let isVisible = true
let isAnimating = false

const SPHERE_RADIUS_MIN = 10
const SPHERE_RADIUS_MAX = 16

// 初始化 Gravity Scatter 3D 场景
export const initGravityScatter = async (
  canvas: HTMLCanvasElement,
  scatterCallbacks: ScatterCallbacks = {}
): Promise<void> => {
  callbacks = scatterCallbacks
  
  // 创建场景
  scene = new THREE.Scene()
  
  // 创建相机
  camera = new THREE.PerspectiveCamera(
    60,
    canvas.clientWidth / canvas.clientHeight,
    0.1,
    100
  )
  camera.position.set(20, 20, 20)
  camera.lookAt(0, 0, 0)
  
  // 创建渲染器
  renderer = new THREE.WebGLRenderer({
    canvas,
    antialias: true,
    alpha: true
  })
  renderer.setSize(canvas.clientWidth, canvas.clientHeight)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.setClearColor(0x000000, 0)
  
  // 创建射线投射器和鼠标向量
  raycaster = new THREE.Raycaster()
  mouse = new THREE.Vector2()
  
  // 添加灯光
  addLights()
  
  // 添加事件监听器
  canvas.addEventListener('mousemove', onMouseMove)
  canvas.addEventListener('click', onMouseClick)
  window.addEventListener('resize', handleResize)

  // 监听页面可见性变化
  document.addEventListener('visibilitychange', handleVisibilityChange)
  window.addEventListener('focus', handleWindowFocus)
  window.addEventListener('blur', handleWindowBlur)

  // 开始动画循环
  startAnimation()
}

// 添加成员到点云
export const addMembersToScatter = (newMembers: Member[]): void => {
  members.push(...newMembers)
  updateInstancedMesh()
}

// 更新实例化网格
const updateInstancedMesh = () => {
  if (members.length === 0) return
  
  // 如果已存在实例化网格，先移除
  if (instancedMesh) {
    scene.remove(instancedMesh)
    instancedMesh.geometry.dispose()
    if (Array.isArray(instancedMesh.material)) {
      instancedMesh.material.forEach(mat => mat.dispose())
    } else {
      instancedMesh.material.dispose()
    }
  }
  
  // 创建几何体 - 使用平面几何体作为头像载体
  const geometry = new THREE.PlaneGeometry(1, 1)
  
  // 创建材质
  const material = new THREE.MeshBasicMaterial({
    transparent: true,
    opacity: 0.8,
    side: THREE.DoubleSide
  })
  
  // 创建实例化网格
  instancedMesh = new THREE.InstancedMesh(geometry, material, members.length)
  instancedMesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage)
  
  // 设置每个实例的位置和旋转
  const dummy = new THREE.Object3D()
  const color = new THREE.Color()
  
  members.forEach((_member, index) => {
    // 在球壳内随机分布
    const radius = SPHERE_RADIUS_MIN + Math.random() * (SPHERE_RADIUS_MAX - SPHERE_RADIUS_MIN)
    const theta = Math.random() * Math.PI * 2
    const phi = Math.random() * Math.PI
    
    dummy.position.set(
      radius * Math.sin(phi) * Math.cos(theta),
      radius * Math.sin(phi) * Math.sin(theta),
      radius * Math.cos(phi)
    )
    
    // 随机旋转
    dummy.rotation.set(
      Math.random() * Math.PI * 2,
      Math.random() * Math.PI * 2,
      Math.random() * Math.PI * 2
    )
    
    // 随机缩放
    const scale = 0.8 + Math.random() * 0.4
    dummy.scale.setScalar(scale)
    
    dummy.updateMatrix()
    instancedMesh.setMatrixAt(index, dummy.matrix)
    
    // 设置主题感知的随机颜色
    const themeColors = getThemeAwareColors()
    color.setHSL(Math.random(), themeColors.saturation, themeColors.lightness)
    instancedMesh.setColorAt(index, color)
  })
  
  scene.add(instancedMesh)
  
  // 异步加载头像纹理
  loadAvatarTextures()
}

// 加载头像纹理
const loadAvatarTextures = async () => {
  const textureLoader = new THREE.TextureLoader()
  
  // 为每个成员加载头像纹理
  for (let i = 0; i < members.length; i++) {
    try {
      const texture = await new Promise<THREE.Texture>((resolve, reject) => {
        textureLoader.load(
          members[i].avatarURL,
          resolve,
          undefined,
          reject
        )
      })
      
      // 创建带纹理的材质
      const material = new THREE.MeshBasicMaterial({
        map: texture,
        transparent: true,
        opacity: 0.8,
        side: THREE.DoubleSide
      })
      
      // 更新实例的材质（这里简化处理，实际应该为每个实例创建单独材质）
      if (i === 0 && instancedMesh) {
        instancedMesh.material = material
      }
    } catch (error) {
      console.warn(`Failed to load avatar for ${members[i].name}:`, error)
    }
  }
}

// 添加灯光
const addLights = () => {
  // 环境光
  const ambientLight = new THREE.AmbientLight(0x404040, 0.6)
  scene.add(ambientLight)
  
  // 方向光
  const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8)
  directionalLight.position.set(10, 10, 5)
  scene.add(directionalLight)
  
  // 点光源
  const pointLight = new THREE.PointLight(0xAA83FF, 0.5, 50)
  pointLight.position.set(0, 0, 0)
  scene.add(pointLight)
}

// 鼠标移动事件
const onMouseMove = (event: MouseEvent) => {
  const canvas = renderer.domElement
  const rect = canvas.getBoundingClientRect()
  
  mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
  mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1
  
  // 射线检测
  if (instancedMesh) {
    raycaster.setFromCamera(mouse, camera)
    const intersects = raycaster.intersectObject(instancedMesh)
    
    if (intersects.length > 0) {
      const instanceId = intersects[0].instanceId
      
      if (instanceId !== undefined && instanceId !== hoveredInstanceId) {
        hoveredInstanceId = instanceId
        
        // 触发悬停回调
        if (callbacks.onMemberHover && members[instanceId]) {
          callbacks.onMemberHover(members[instanceId])
        }
        
        // 添加悬停效果
        addHoverEffect(instanceId)
      }
    } else if (hoveredInstanceId !== null) {
      removeHoverEffect(hoveredInstanceId)
      hoveredInstanceId = null
      
      if (callbacks.onMemberLeave) {
        callbacks.onMemberLeave()
      }
    }
  }
}

// 鼠标点击事件
const onMouseClick = (_event: MouseEvent) => {
  if (hoveredInstanceId !== null && members[hoveredInstanceId]) {
    if (callbacks.onMemberClick) {
      callbacks.onMemberClick(members[hoveredInstanceId])
    }
  }
}

// 添加悬停效果
const addHoverEffect = (instanceId: number) => {
  if (!instancedMesh) return
  
  const dummy = new THREE.Object3D()
  instancedMesh.getMatrixAt(instanceId, dummy.matrix)
  dummy.matrix.decompose(dummy.position, dummy.quaternion, dummy.scale)
  
  // 轻微偏移和缩放
  dummy.position.y += 0.5
  dummy.scale.multiplyScalar(1.2)
  
  dummy.updateMatrix()
  instancedMesh.setMatrixAt(instanceId, dummy.matrix)
  instancedMesh.instanceMatrix.needsUpdate = true
  
  // 改变颜色为绿色辉光
  const color = new THREE.Color(0xD4DEC7)
  instancedMesh.setColorAt(instanceId, color)
  if (instancedMesh.instanceColor) {
    instancedMesh.instanceColor.needsUpdate = true
  }
}

// 移除悬停效果
const removeHoverEffect = (instanceId: number) => {
  if (!instancedMesh) return
  
  // 恢复原始位置和缩放
  const dummy = new THREE.Object3D()
  instancedMesh.getMatrixAt(instanceId, dummy.matrix)
  dummy.matrix.decompose(dummy.position, dummy.quaternion, dummy.scale)
  
  dummy.position.y -= 0.5
  dummy.scale.divideScalar(1.2)
  
  dummy.updateMatrix()
  instancedMesh.setMatrixAt(instanceId, dummy.matrix)
  instancedMesh.instanceMatrix.needsUpdate = true
  
  // 恢复主题感知的原始颜色
  const color = new THREE.Color()
  const themeColors = getThemeAwareColors()
  color.setHSL(Math.random(), themeColors.saturation, themeColors.lightness)
  instancedMesh.setColorAt(instanceId, color)
  if (instancedMesh.instanceColor) {
    instancedMesh.instanceColor.needsUpdate = true
  }
}

// 启动动画
const startAnimation = () => {
  if (!isAnimating && isVisible) {
    isAnimating = true
    animate()
  }
}

// 停止动画
const stopAnimation = () => {
  isAnimating = false
  if (animationId) {
    cancelAnimationFrame(animationId)
    animationId = 0
  }
}

// 页面可见性变化处理
const handleVisibilityChange = () => {
  isVisible = !document.hidden

  if (isVisible) {
    startAnimation()
  } else {
    stopAnimation()
  }
}

// 窗口焦点处理
const handleWindowFocus = () => {
  isVisible = true
  startAnimation()
}

const handleWindowBlur = () => {
  isVisible = false
  stopAnimation()
}

// 动画循环
const animate = () => {
  if (!isAnimating || !isVisible) {
    animationId = 0
    return
  }

  animationId = requestAnimationFrame(animate)

  const time = Date.now() * 0.001

  if (instancedMesh) {
    // 整体旋转
    instancedMesh.rotation.y = time * 0.1

    // 个别实例的微动画
    const dummy = new THREE.Object3D()
    for (let i = 0; i < members.length; i++) {
      instancedMesh.getMatrixAt(i, dummy.matrix)
      dummy.matrix.decompose(dummy.position, dummy.quaternion, dummy.scale)

      // 轻微的浮动效果
      dummy.position.y += Math.sin(time * 2 + i) * 0.01

      dummy.updateMatrix()
      instancedMesh.setMatrixAt(i, dummy.matrix)
    }
    instancedMesh.instanceMatrix.needsUpdate = true
  }

  // 相机轨道运动
  camera.position.x = Math.cos(time * 0.1) * 25
  camera.position.z = Math.sin(time * 0.1) * 25
  camera.lookAt(0, 0, 0)

  renderer.render(scene, camera)
}

// 处理窗口大小变化
const handleResize = () => {
  if (!camera || !renderer) return
  
  const canvas = renderer.domElement
  const width = canvas.clientWidth
  const height = canvas.clientHeight
  
  camera.aspect = width / height
  camera.updateProjectionMatrix()
  
  renderer.setSize(width, height)
}

// 清理资源
export const disposeGravityScatter = () => {
  // 停止动画
  stopAnimation()

  // 移除事件监听器
  if (renderer && renderer.domElement) {
    renderer.domElement.removeEventListener('mousemove', onMouseMove)
    renderer.domElement.removeEventListener('click', onMouseClick)
  }
  window.removeEventListener('resize', handleResize)
  document.removeEventListener('visibilitychange', handleVisibilityChange)
  window.removeEventListener('focus', handleWindowFocus)
  window.removeEventListener('blur', handleWindowBlur)

  if (scene) {
    // 清理几何体和材质
    scene.traverse((object) => {
      if (object instanceof THREE.Mesh) {
        object.geometry.dispose()
        if (Array.isArray(object.material)) {
          object.material.forEach(material => material.dispose())
        } else {
          object.material.dispose()
        }
      }
    })

    // 清理场景
    scene.clear()
  }

  if (renderer) {
    renderer.dispose()
  }

  // 重置变量
  members = []
  hoveredInstanceId = null
  callbacks = {}
}
