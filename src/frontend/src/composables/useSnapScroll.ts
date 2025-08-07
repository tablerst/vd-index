import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { gsap } from 'gsap'
import { Observer } from 'gsap/Observer'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { ScrollToPlugin } from 'gsap/ScrollToPlugin'
import { useDeviceDetection } from './useDeviceDetection'

// 注册GSAP插件
gsap.registerPlugin(Observer, ScrollTrigger, ScrollToPlugin)

export interface SnapScrollSection {
  id: string
  element: HTMLElement | null
  offsetTop: number
  height: number
}

export interface TouchGestureConfig {
  // 距离阈值
  minDistance: number          // 最小滑动距离
  minQuickDistance: number     // 快速滑动最小距离

  // 速度阈值
  minVelocity: number          // 最小滑动速度 (px/ms)
  maxVelocity: number          // 最大有效速度

  // 方向检测
  directionThreshold: number   // 方向置信度阈值 (0-1)

  // 反馈配置
  enableVibration: boolean     // 是否启用触觉反馈
  enableVisualFeedback: boolean // 是否启用视觉反馈
  disableProgressBar: boolean  // 是否禁用进度条交互（防止误触）
}

export interface WheelConfig {
  minDeltaY: number           // 最小滚轮增量
  sensitivity: number         // 滚轮灵敏度倍数
}

export interface PerformanceConfig {
  enableGPUAcceleration: boolean
  reducedMotion: boolean
  targetFPS: number
}

export interface SnapScrollConfig {
  // 通用配置
  tolerance: number
  duration: number
  ease: string
  debounceDelay: number
  footerThreshold: number

  // 设备特定配置
  touch?: TouchGestureConfig
  wheel?: WheelConfig
  performance?: PerformanceConfig
}

/**
 * 获取设备特定的配置
 */
function getDeviceSpecificConfig(deviceType: 'mobile' | 'tablet' | 'desktop'): SnapScrollConfig {
  const baseConfigs = {
    mobile: {
      tolerance: 120,
      duration: 0.8,
      ease: "power2.inOut",
      debounceDelay: 200,
      footerThreshold: 0.85,
      touch: {
        minDistance: 30,
        minQuickDistance: 15,
        minVelocity: 0.5,
        maxVelocity: 3.0,
        directionThreshold: 0.7,
        enableVibration: true,
        enableVisualFeedback: true,
        disableProgressBar: true  // 移动端禁用进度条点击
      },
      performance: {
        enableGPUAcceleration: true,
        reducedMotion: false,
        targetFPS: 30
      }
    },
    tablet: {
      tolerance: 120,
      duration: 1.0,
      ease: "power2.out",
      debounceDelay: 250,
      footerThreshold: 0.8,
      touch: {
        minDistance: 40,
        minQuickDistance: 20,
        minVelocity: 0.4,
        maxVelocity: 2.5,
        directionThreshold: 0.75,
        enableVibration: false,
        enableVisualFeedback: true,
        disableProgressBar: false  // 平板端保持进度条交互
      },
      wheel: {
        minDeltaY: 8,
        sensitivity: 1.0
      },
      performance: {
        enableGPUAcceleration: true,
        reducedMotion: false,
        targetFPS: 45
      }
    },
    desktop: {
      tolerance: 120,
      duration: 1.2,
      ease: "power2.out",
      debounceDelay: 300,
      footerThreshold: 0.8,
      wheel: {
        minDeltaY: 10,
        sensitivity: 1.0
      },
      touch: {
        minDistance: 50,
        minQuickDistance: 25,
        minVelocity: 0.3,
        maxVelocity: 2.0,
        directionThreshold: 0.8,
        enableVibration: false,
        enableVisualFeedback: false,
        disableProgressBar: false  // 桌面端保持进度条交互
      },
      performance: {
        enableGPUAcceleration: true,
        reducedMotion: false,
        targetFPS: 60
      }
    }
  }

  return baseConfigs[deviceType]
}

/**
 * 分屏推进滚动组合式函数
 * 使用GSAP Observer实现平滑的分屏切换效果
 */
export function useSnapScroll(sectionRefs: Array<{ value: HTMLElement | null }>, config?: Partial<SnapScrollConfig>) {
  // 集成设备检测
  const { deviceInfo } = useDeviceDetection()

  // 获取设备特定的默认配置
  const deviceConfig = getDeviceSpecificConfig(deviceInfo.value.type)

  // 合并用户配置
  const finalConfig = { ...deviceConfig, ...config }

  // 响应式状态
  const currentSection = ref(0)
  const isAnimating = ref(false)
  const isSnapMode = ref(true)
  const sections = ref<SnapScrollSection[]>([])
  
  // 防抖定时器
  let debounceTimer: number | null = null

  // 防抖控制
  let isWheelBlocked = false
  let wheelBlockTimer: number | null = null // 滚轮阻止超时定时器

  // 触摸手势防抖控制
  let isTouchBlocked = false
  let touchBlockTimer: number | null = null
  let lastGestureTime = 0

  // 计算属性
  const totalSections = computed(() => sections.value.length)
  const progress = computed(() => 
    totalSections.value > 0 ? (currentSection.value + 1) / totalSections.value : 0
  )

  // 更新sections信息
  const updateSections = async () => {
    await nextTick()

    sections.value = sectionRefs.map((ref, index) => ({
      id: `section-${index}`,
      element: ref.value,
      offsetTop: ref.value?.offsetTop || 0,
      height: ref.value?.offsetHeight || 0
    })).filter(section => section.element !== null)

    console.log('Updated sections:', sections.value.map(s => ({
      id: s.id,
      offsetTop: s.offsetTop,
      height: s.height
    })))

    // 更新当前section
    updateCurrentSection()
  }

  // 更新当前section索引
  const updateCurrentSection = () => {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop
    const windowHeight = window.innerHeight
    const viewportCenter = scrollTop + windowHeight / 2

    for (let i = 0; i < sections.value.length; i++) {
      const section = sections.value[i]
      const sectionTop = section.offsetTop
      const sectionBottom = sectionTop + section.height

      if (viewportCenter >= sectionTop && viewportCenter < sectionBottom) {
        currentSection.value = i
        break
      }
    }
  }

  // 滚动到指定section
  const scrollToSection = (index: number, force = false) => {
    if (isAnimating.value && !force) return
    if (index < 0 || index >= sections.value.length) return

    const targetSection = sections.value[index]
    if (!targetSection.element) return

    isAnimating.value = true
    currentSection.value = index
    setWheelBlocked(true) // 使用新的阻止方法

    console.log(`Scrolling to section ${index}:`, targetSection.offsetTop)

    // 执行滚动动画
    gsap.to(window, {
      duration: finalConfig.duration,
      scrollTo: {
        y: targetSection.offsetTop,
        autoKill: false
      },
      ease: finalConfig.ease,
      onComplete: () => {
        isAnimating.value = false
        setWheelBlocked(false) // 使用新的解除阻止方法
        console.log(`Scroll to section ${index} completed - wheel block released`)

        // 刷新ScrollTrigger
        ScrollTrigger.refresh()
      },
      onInterrupt: () => {
        // 动画被中断时也要解除阻止
        console.log(`Scroll to section ${index} interrupted - releasing wheel block`)
        isAnimating.value = false
        setWheelBlocked(false)
      }
    })
  }

  // 检查是否在footer区域
  const checkFooterArea = () => {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop
    const windowHeight = window.innerHeight
    const documentHeight = document.documentElement.scrollHeight
    
    const scrollProgress = (scrollTop + windowHeight) / documentHeight
    
    console.log('checkFooterArea - scrollProgress:', scrollProgress, 'threshold:', finalConfig.footerThreshold)
    
    if (scrollProgress >= finalConfig.footerThreshold) {
      // 进入footer区域，禁用snap模式
      if (isSnapMode.value) {
        isSnapMode.value = false
        console.log('Entered footer area, disabled snap mode')
      }
    } else {
      // 离开footer区域，启用snap模式
      if (!isSnapMode.value && !isAnimating.value) {
        isSnapMode.value = true
        console.log('Left footer area, enabled snap mode')
      }
    }
  }

  // 防抖处理
  const debounce = (func: Function) => {
    if (debounceTimer) {
      clearTimeout(debounceTimer)
    }
    debounceTimer = window.setTimeout(func, finalConfig.debounceDelay)
  }

  // 设置滚轮阻止状态，带超时保护
  const setWheelBlocked = (blocked: boolean, timeout = 2000) => {
    isWheelBlocked = blocked

    // 清除之前的定时器
    if (wheelBlockTimer) {
      clearTimeout(wheelBlockTimer)
      wheelBlockTimer = null
    }

    if (blocked) {
      // 设置超时保护，防止永久阻止
      wheelBlockTimer = window.setTimeout(() => {
        console.log('Wheel block timeout - force releasing')
        isWheelBlocked = false
        isAnimating.value = false
        wheelBlockTimer = null
      }, timeout)
    }
  }



  // 初始化事件监听
  const initEventListeners = () => {
    console.log('SnapScroll event listeners initialized')
  }

  // 监听常规滚动事件（仅用于footer区域的正常滚动）
  const handleScroll = () => {
    // 只在snap模式禁用时处理滚动事件（footer区域）
    if (!isSnapMode.value && !isAnimating.value) {
      updateCurrentSection()
      checkFooterArea()
    } else if (isSnapMode.value) {
      // 在snap模式下，阻止任何非GSAP控制的滚动
      // 这里不做任何处理，让GSAP完全接管
      return
    }
  }

  // 全局wheel事件拦截 - 一次滚轮操作直接切换一屏
  const handleWheel = (e: WheelEvent) => {
    console.log('handleWheel - isSnapMode:', isSnapMode.value, 'isAnimating:', isAnimating.value, 'isWheelBlocked:', isWheelBlocked)

    // 在snap模式下，始终阻止默认滚动行为
    if (isSnapMode.value) {
      e.preventDefault()
      e.stopPropagation()
    }

    if (!isSnapMode.value || isAnimating.value || isWheelBlocked) {
      console.log('handleWheel blocked - returning')
      return
    }

    // 使用设备特定的滚轮配置
    const wheelConfig = finalConfig.wheel
    const minDeltaY = wheelConfig?.minDeltaY || 10

    // 过滤极小的滚动值
    if (Math.abs(e.deltaY) < minDeltaY) {
      console.log('handleWheel - deltaY too small:', e.deltaY, 'minDeltaY:', minDeltaY)
      return
    }

    const direction = e.deltaY > 0 ? 1 : -1
    console.log('Wheel triggered - direction:', direction, 'deltaY:', e.deltaY, 'currentSection:', currentSection.value)

    if (direction > 0) {
      // 向下滚动 - 切换到下一屏
      if (currentSection.value < sections.value.length - 1) {
        scrollToSection(currentSection.value + 1)
      } else {
        // 已在最后一屏，检查是否进入footer区域
        console.log('At last section, checking footer area')
        checkFooterArea()
      }
    } else {
      // 向上滚动 - 切换到上一屏
      if (currentSection.value > 0) {
        scrollToSection(currentSection.value - 1)
      } else {
        // 已在第一屏，可以选择滚动到页面顶部或不做任何操作
        console.log('At first section, scrolling to top')
        gsap.to(window, {
          duration: 0.5,
          scrollTo: { y: 0 },
          ease: "power2.out"
        })
      }
    }
  }

  // 触摸滑动处理 - 使用智能手势识别
  let touchStartX = 0
  let touchStartY = 0
  let touchStartTime = 0

  const handleTouchStart = (e: TouchEvent) => {
    if (!isSnapMode.value) return
    touchStartX = e.touches[0].clientX
    touchStartY = e.touches[0].clientY
    touchStartTime = Date.now()
  }

  /**
   * 智能触摸手势识别算法
   * 基于距离+速度+方向的综合判断
   */
  const analyzeGesture = (startX: number, startY: number, endX: number, endY: number, deltaTime: number) => {
    const deltaX = endX - startX
    const deltaY = startY - endY // 注意：Y轴方向，向上为正

    const distanceX = Math.abs(deltaX)
    const distanceY = Math.abs(deltaY)
    const totalDistance = Math.sqrt(deltaX * deltaX + deltaY * deltaY)

    // 速度计算
    const velocity = totalDistance / Math.max(deltaTime, 1) // px/ms
    const velocityY = distanceY / Math.max(deltaTime, 1)

    // 方向置信度计算
    const directionConfidence = totalDistance > 0 ? distanceY / totalDistance : 0

    // 获取触摸配置
    const touchConfig = finalConfig.touch!

    return {
      deltaX,
      deltaY,
      distanceX,
      distanceY,
      totalDistance,
      velocity,
      velocityY,
      directionConfidence,
      isVerticalDominant: directionConfidence >= touchConfig.directionThreshold,
      isValidDistance: distanceY > touchConfig.minDistance,
      isValidVelocity: velocityY > touchConfig.minVelocity && distanceY > touchConfig.minQuickDistance,
      isValidGesture: function() {
        return this.isVerticalDominant && (this.isValidDistance || this.isValidVelocity)
      }
    }
  }

  const handleTouchEnd = (e: TouchEvent) => {
    if (!isSnapMode.value || isAnimating.value) return

    const touchEndX = e.changedTouches[0].clientX
    const touchEndY = e.changedTouches[0].clientY
    const touchEndTime = Date.now()
    const deltaTime = touchEndTime - touchStartTime

    // 防抖控制：防止过快的连续手势
    const timeSinceLastGesture = touchEndTime - lastGestureTime
    if (timeSinceLastGesture < finalConfig.debounceDelay) {
      console.log('Touch gesture debounced:', { timeSinceLastGesture, debounceDelay: finalConfig.debounceDelay })
      return
    }

    // 边界情况：触摸时间过短（可能是意外触摸）
    if (deltaTime < 50) {
      console.log('Touch gesture too quick:', { deltaTime })
      return
    }

    // 边界情况：触摸时间过长（可能是长按或拖拽）
    if (deltaTime > 1000) {
      console.log('Touch gesture too long:', { deltaTime })
      return
    }

    // 智能手势分析
    const gesture = analyzeGesture(touchStartX, touchStartY, touchEndX, touchEndY, deltaTime)

    // 详细的调试信息
    console.log('Touch gesture analysis:', {
      deltaY: gesture.deltaY,
      distanceY: gesture.distanceY,
      velocity: gesture.velocity,
      velocityY: gesture.velocityY,
      directionConfidence: gesture.directionConfidence.toFixed(2),
      isVerticalDominant: gesture.isVerticalDominant,
      isValidDistance: gesture.isValidDistance,
      isValidVelocity: gesture.isValidVelocity,
      deltaTime
    })

    // 手势有效性检查
    if (!gesture.isValidGesture()) {
      console.log('Touch gesture rejected:', {
        reason: !gesture.isVerticalDominant ? 'not vertical dominant' : 'insufficient distance and velocity'
      })
      return
    }

    // 触觉反馈
    const touchConfig = finalConfig.touch!
    if (touchConfig.enableVibration && 'vibrate' in navigator) {
      navigator.vibrate(10)
    }

    console.log('Touch gesture accepted - triggering scroll')

    // 更新防抖状态
    lastGestureTime = touchEndTime

    if (gesture.deltaY > 0) {
      // 向上滑动（页面向下滚动）- 切换到下一屏
      if (currentSection.value < sections.value.length - 1) {
        scrollToSection(currentSection.value + 1)
      } else {
        // 边界情况：已在最后一屏，提供触觉反馈
        console.log('Already at last section')
        if (touchConfig.enableVibration && 'vibrate' in navigator) {
          navigator.vibrate([50, 30, 50]) // 不同的振动模式表示到达边界
        }
        checkFooterArea()
      }
    } else {
      // 向下滑动（页面向上滚动）- 切换到上一屏
      if (currentSection.value > 0) {
        scrollToSection(currentSection.value - 1)
      } else {
        // 边界情况：已在第一屏，提供触觉反馈
        console.log('Already at first section')
        if (touchConfig.enableVibration && 'vibrate' in navigator) {
          navigator.vibrate([50, 30, 50]) // 边界振动反馈
        }
      }
    }
  }

  // 窗口resize处理
  const handleResize = () => {
    debounce(async () => {
      await updateSections()
      ScrollTrigger.refresh()
    })
  }

  // 公共方法
  const goToSection = (index: number) => {
    scrollToSection(index, true)
  }

  const nextSection = () => {
    if (currentSection.value < sections.value.length - 1) {
      scrollToSection(currentSection.value + 1)
    }
  }

  const prevSection = () => {
    if (currentSection.value > 0) {
      scrollToSection(currentSection.value - 1)
    }
  }

  const enableSnapMode = () => {
    isSnapMode.value = true
    console.log('Snap mode enabled')
  }

  const disableSnapMode = () => {
    isSnapMode.value = false
    console.log('Snap mode disabled')
  }

  // 生命周期管理
  onMounted(async () => {
    await updateSections()
    initEventListeners()

    // 添加滚动监听
    window.addEventListener('scroll', handleScroll, { passive: true })
    window.addEventListener('resize', handleResize, { passive: true })
    window.addEventListener('wheel', handleWheel, { passive: false })
    window.addEventListener('touchstart', handleTouchStart, { passive: true })
    window.addEventListener('touchend', handleTouchEnd, { passive: false })

    // 设置调试信息到全局对象
    ;(window as any).__snapScrollDebug = {
      isSnapMode,
      isAnimating,
      currentSection,
      sectionsCount: computed(() => sections.value.length),
      sections: sections.value,
      handleWheel,
      scrollToSection
    }

    console.log('SnapScroll event listeners initialized')
    console.log('SnapScroll initialized with', sections.value.length, 'sections')
    console.log('Debug info set to window.__snapScrollDebug')
  })

  onUnmounted(() => {
    // 清理所有定时器
    if (debounceTimer) {
      clearTimeout(debounceTimer)
    }

    if (wheelBlockTimer) {
      clearTimeout(wheelBlockTimer)
    }

    if (touchBlockTimer) {
      clearTimeout(touchBlockTimer)
    }

    // 移除事件监听器
    window.removeEventListener('scroll', handleScroll)
    window.removeEventListener('resize', handleResize)
    window.removeEventListener('wheel', handleWheel)
    window.removeEventListener('touchstart', handleTouchStart)
    window.removeEventListener('touchend', handleTouchEnd)
  })

  return {
    // 状态
    currentSection,
    isAnimating,
    isSnapMode,
    sections,
    totalSections,
    progress,

    // 方法
    goToSection,
    nextSection,
    prevSection,
    enableSnapMode,
    disableSnapMode,
    updateSections,

    // 配置和设备信息
    config: finalConfig,
    deviceInfo: deviceInfo.value,
    deviceType: deviceInfo.value.type,

    // 移动端特定配置
    isMobileProgressBarDisabled: computed(() =>
      deviceInfo.value.isMobile && finalConfig.touch?.disableProgressBar
    )
  }
}
