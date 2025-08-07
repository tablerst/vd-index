import { ref, computed, onMounted, onUnmounted } from 'vue'

export interface DeviceInfo {
  type: 'mobile' | 'tablet' | 'desktop'
  isMobile: boolean
  isTablet: boolean
  isDesktop: boolean
  screenWidth: number
  screenHeight: number
  pixelRatio: number
  isTouchDevice: boolean
  isLandscape: boolean
  isPortrait: boolean
}

export interface ResponsiveConfig {
  membersPerPage: number
  avatarSize: {
    min: number
    max: number
  }
  spacing: {
    min: number
    max: number
  }
  spiralRadius: number
  animationIntensity: number
}

/**
 * 设备检测和响应式配置组合式函数
 * 提供智能设备检测和基于设备类型的配置优化
 */
export function useDeviceDetection() {
  // 响应式状态
  const screenWidth = ref(0)
  const screenHeight = ref(0)
  const pixelRatio = ref(1)

  // 设备类型检测
  const deviceType = computed<DeviceInfo['type']>(() => {
    const width = screenWidth.value
    // 暂时禁用移动端和平板端的snap scroll功能
    // 所有设备都使用desktop配置，确保PC端体验最佳
    // 移动端将使用标准的滚动方式
    // if (width <= 768) return 'mobile'
    // if (width <= 1024) return 'tablet'
    return 'desktop'
  })

  // 设备信息
  const deviceInfo = computed<DeviceInfo>(() => ({
    type: deviceType.value,
    isMobile: deviceType.value === 'mobile',
    isTablet: deviceType.value === 'tablet',
    isDesktop: deviceType.value === 'desktop',
    screenWidth: screenWidth.value,
    screenHeight: screenHeight.value,
    pixelRatio: pixelRatio.value,
    isTouchDevice: 'ontouchstart' in window || navigator.maxTouchPoints > 0,
    isLandscape: screenWidth.value > screenHeight.value,
    isPortrait: screenWidth.value <= screenHeight.value
  }))

  // 响应式配置
  const responsiveConfig = computed<ResponsiveConfig>(() => {
    const { type } = deviceInfo.value
    
    switch (type) {
      case 'mobile':
        return {
          membersPerPage: 12, // 移动端显示更少成员
          avatarSize: {
            min: 45, // 更大的头像便于触摸
            max: 65
          },
          spacing: {
            min: 15, // 更大的间距避免拥挤
            max: 25
          },
          spiralRadius: 30, // 更紧凑的螺旋半径
          animationIntensity: 0.6 // 降低动画强度提升性能
        }
      
      case 'tablet':
        return {
          membersPerPage: 20,
          avatarSize: {
            min: 40,
            max: 60
          },
          spacing: {
            min: 12,
            max: 20
          },
          spiralRadius: 35,
          animationIntensity: 0.8
        }
      
      default: // desktop
        return {
          membersPerPage: 30,
          avatarSize: {
            min: 35,
            max: 55
          },
          spacing: {
            min: 10,
            max: 16
          },
          spiralRadius: 40,
          animationIntensity: 1.0
        }
    }
  })

  // 性能配置
  const performanceConfig = computed(() => {
    const { type, pixelRatio: ratio } = deviceInfo.value
    
    return {
      // 粒子数量倍数
      particleMultiplier: type === 'mobile' ? 0.5 : type === 'tablet' ? 0.7 : 1.0,
      // 渲染质量
      renderQuality: ratio > 2 ? 'high' : ratio > 1.5 ? 'medium' : 'low',
      // 动画帧率目标
      targetFPS: type === 'mobile' ? 30 : 45,
      // 是否启用高级效果
      enableAdvancedEffects: type === 'desktop',
      // 是否启用视差效果
      enableParallax: type !== 'mobile'
    }
  })

  // 更新屏幕信息
  const updateScreenInfo = () => {
    screenWidth.value = window.innerWidth
    screenHeight.value = window.innerHeight
    pixelRatio.value = window.devicePixelRatio || 1
  }

  // 防抖的resize处理
  let resizeTimeout: number | null = null
  const handleResize = () => {
    if (resizeTimeout) {
      clearTimeout(resizeTimeout)
    }
    resizeTimeout = window.setTimeout(() => {
      updateScreenInfo()
    }, 150)
  }

  // 检测用户是否偏好减少动画
  const prefersReducedMotion = computed(() => {
    if (typeof window === 'undefined') return false
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches
  })

  // 检测网络连接质量
  const networkQuality = computed(() => {
    if (typeof navigator === 'undefined' || !('connection' in navigator)) {
      return 'unknown'
    }
    
    const connection = (navigator as any).connection
    if (!connection) return 'unknown'
    
    const effectiveType = connection.effectiveType
    if (effectiveType === '4g') return 'fast'
    if (effectiveType === '3g') return 'medium'
    return 'slow'
  })

  // 生命周期管理
  onMounted(() => {
    updateScreenInfo()
    window.addEventListener('resize', handleResize, { passive: true })
    window.addEventListener('orientationchange', handleResize, { passive: true })
  })

  onUnmounted(() => {
    if (resizeTimeout) {
      clearTimeout(resizeTimeout)
    }
    window.removeEventListener('resize', handleResize)
    window.removeEventListener('orientationchange', handleResize)
  })

  return {
    // 设备信息
    deviceInfo,
    deviceType,
    
    // 配置
    responsiveConfig,
    performanceConfig,
    
    // 用户偏好
    prefersReducedMotion,
    networkQuality,
    
    // 工具方法
    updateScreenInfo
  }
}

// 类型已在上面通过 export interface 导出
