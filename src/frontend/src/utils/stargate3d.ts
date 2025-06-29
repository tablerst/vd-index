import * as THREE from 'three'

let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let animationId: number
let stargateGroup: THREE.Group
let isVisible = true
let isAnimating = false

// 初始化星际跃迁门 3D 场景
export const initStargate = async (canvas: HTMLCanvasElement): Promise<void> => {
  // 创建场景
  scene = new THREE.Scene()
  
  // 创建相机
  camera = new THREE.PerspectiveCamera(
    75,
    canvas.clientWidth / canvas.clientHeight,
    0.1,
    1000
  )
  camera.position.z = 5
  
  // 创建渲染器
  renderer = new THREE.WebGLRenderer({
    canvas,
    antialias: true,
    alpha: true
  })
  renderer.setSize(canvas.clientWidth, canvas.clientHeight)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.setClearColor(0x000000, 0)
  
  // 创建星际跃迁门
  createStargate()
  
  // 添加灯光
  addLights()
  
  // 开始动画循环
  startAnimation()

  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)

  // 监听页面可见性变化
  document.addEventListener('visibilitychange', handleVisibilityChange)
  window.addEventListener('focus', handleWindowFocus)
  window.addEventListener('blur', handleWindowBlur)
}

// 创建星际跃迁门
const createStargate = () => {
  stargateGroup = new THREE.Group()
  
  // 外环
  const outerRingGeometry = new THREE.TorusGeometry(2, 0.1, 8, 100)
  const outerRingMaterial = new THREE.MeshBasicMaterial({
    color: 0xAA83FF,
    transparent: true,
    opacity: 0.8
  })
  const outerRing = new THREE.Mesh(outerRingGeometry, outerRingMaterial)
  stargateGroup.add(outerRing)
  
  // 中环
  const middleRingGeometry = new THREE.TorusGeometry(1.5, 0.05, 6, 80)
  const middleRingMaterial = new THREE.MeshBasicMaterial({
    color: 0xD4DEC7,
    transparent: true,
    opacity: 0.6
  })
  const middleRing = new THREE.Mesh(middleRingGeometry, middleRingMaterial)
  stargateGroup.add(middleRing)
  
  // 内环
  const innerRingGeometry = new THREE.TorusGeometry(1, 0.03, 4, 60)
  const innerRingMaterial = new THREE.MeshBasicMaterial({
    color: 0x3F7DFB,
    transparent: true,
    opacity: 0.7
  })
  const innerRing = new THREE.Mesh(innerRingGeometry, innerRingMaterial)
  stargateGroup.add(innerRing)
  
  // 中心能量核心
  const coreGeometry = new THREE.SphereGeometry(0.3, 32, 32)
  const coreMaterial = new THREE.MeshBasicMaterial({
    color: 0xAA83FF,
    transparent: true,
    opacity: 0.9
  })
  const core = new THREE.Mesh(coreGeometry, coreMaterial)
  stargateGroup.add(core)
  
  // 能量波纹
  for (let i = 0; i < 5; i++) {
    const rippleGeometry = new THREE.RingGeometry(0.5 + i * 0.3, 0.52 + i * 0.3, 32)
    const rippleMaterial = new THREE.MeshBasicMaterial({
      color: 0xAA83FF,
      transparent: true,
      opacity: 0.3 - i * 0.05,
      side: THREE.DoubleSide
    })
    const ripple = new THREE.Mesh(rippleGeometry, rippleMaterial)
    ripple.userData = { 
      originalOpacity: 0.3 - i * 0.05,
      phase: i * Math.PI / 3
    }
    stargateGroup.add(ripple)
  }
  
  scene.add(stargateGroup)
}

// 添加灯光
const addLights = () => {
  // 环境光
  const ambientLight = new THREE.AmbientLight(0x404040, 0.4)
  scene.add(ambientLight)
  
  // 点光源
  const pointLight = new THREE.PointLight(0xAA83FF, 1, 100)
  pointLight.position.set(0, 0, 5)
  scene.add(pointLight)
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

  if (stargateGroup) {
    // 旋转星际跃迁门
    stargateGroup.rotation.z = time * 0.2

    // 让不同的环以不同速度旋转
    stargateGroup.children.forEach((child, index) => {
      if (child instanceof THREE.Mesh) {
        if (index === 0) { // 外环
          child.rotation.z = time * 0.3
        } else if (index === 1) { // 中环
          child.rotation.z = -time * 0.4
        } else if (index === 2) { // 内环
          child.rotation.z = time * 0.5
        } else if (index === 3) { // 核心
          child.rotation.x = time * 0.6
          child.rotation.y = time * 0.4
          // 核心脉冲效果
          const scale = 1 + Math.sin(time * 3) * 0.1
          child.scale.setScalar(scale)
        } else { // 能量波纹
          const userData = child.userData
          if (userData) {
            const opacity = userData.originalOpacity * (1 + Math.sin(time * 2 + userData.phase) * 0.5)
            ;(child.material as THREE.MeshBasicMaterial).opacity = opacity
          }
        }
      }
    })
  }

  // 相机轻微摆动
  camera.position.x = Math.sin(time * 0.5) * 0.1
  camera.position.y = Math.cos(time * 0.3) * 0.1
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
export const disposeStargate = () => {
  // 停止动画
  stopAnimation()

  // 移除事件监听器
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
}
