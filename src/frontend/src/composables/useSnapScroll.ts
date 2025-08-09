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

  // 简化模式参数（可选）
  simplifiedMode?: boolean     // 是否启用简化模式
  singleTriggerMode?: boolean  // 是否启用单次触发模式

  // 震荡抑制参数（可选，简化模式下不使用）
  dampingFactor?: number       // 阻尼系数 (0-1)
  velocitySmoothing?: number   // 速度平滑采样数
  maxAcceleration?: number     // 最大加速度限制
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
 * 注意：移动端和平板端配置已保留但暂时不启用
 * 当前所有设备都使用desktop配置以确保最佳PC端体验
 */
function getDeviceSpecificConfig(deviceType: 'mobile' | 'tablet' | 'desktop'): SnapScrollConfig {
  const baseConfigs = {
    // 移动端配置（已保留但暂时不启用）
    mobile: {
      tolerance: 120,
      duration: 1.4,
      ease: "power1.out",
      debounceDelay: 800,  // 大幅增加防抖时间，确保只执行一次
      footerThreshold: 0.85,
      touch: {
        minDistance: 30,  // 只保留最小触发阈值
        minQuickDistance: 30,  // 统一阈值
        minVelocity: 0.2,  // 降低速度要求
        maxVelocity: 999,  // 移除速度上限
        directionThreshold: 0.6,  // 适中的方向判断
        enableVibration: true,
        enableVisualFeedback: true,
        disableProgressBar: true,  // 移动端禁用进度条点击
        // 简化模式：只要达到阈值就触发，其他都靠防抖控制
        simplifiedMode: true,  // 启用简化模式
        singleTriggerMode: true  // 单次触发模式
      },
      performance: {
        enableGPUAcceleration: true,
        reducedMotion: false,
        targetFPS: 30
      }
    },
    // 平板端配置（已保留但暂时不启用）
    tablet: {
      tolerance: 120,
      duration: 1.2,
      ease: "power1.out",
      debounceDelay: 280,
      footerThreshold: 0.8,
      touch: {
        minDistance: 40,
        minQuickDistance: 20,
        minVelocity: 0.4,
        maxVelocity: 2.0,
        directionThreshold: 0.7,
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

  // 简化的触摸手势防抖控制
  let isGestureBlocked = false
  let gestureBlockTimer: number | null = null
  let lastGestureTime = 0

  // 简化的手势阻塞函数
  const blockGesture = () => {
    if (!finalConfig.touch?.singleTriggerMode) return

    isGestureBlocked = true

    // 清除之前的定时器
    if (gestureBlockTimer) {
      clearTimeout(gestureBlockTimer)
    }

    // 设置新的阻塞定时器
    gestureBlockTimer = setTimeout(() => {
      isGestureBlocked = false
      gestureBlockTimer = null
    }, finalConfig.debounceDelay)
  }

  // 全局滚轮监听禁用状态
  const isWheelListenerDisabled = ref(false)

  // 禁用/启用全局滚轮监听
  const setWheelListenerDisabled = (disabled: boolean) => {
    isWheelListenerDisabled.value = disabled
    console.log('Wheel listener disabled:', disabled)
  }

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

  // 暂停/恢复装饰性动画
  const pauseDecorationAnimations = (pause: boolean) => {
    // 发送全局事件暂停粒子动画
    window.dispatchEvent(new CustomEvent('particles-pause', {
      detail: { pause }
    }))

    // 暂停其他装饰性动画
    const decorativeElements = document.querySelectorAll('.ring-svg, .member-star')
    decorativeElements.forEach(el => {
      if (el instanceof HTMLElement || el instanceof SVGElement) {
        if (pause) {
          el.style.animationPlayState = 'paused'
        } else {
          el.style.animationPlayState = 'running'
        }
      }
    })
  }

  // 滚动到指定section
  const scrollToSection = (index: number, force = false, gestureVelocity?: number) => {
    if (isAnimating.value && !force) return
    if (index < 0 || index >= sections.value.length) return

    const targetSection = sections.value[index]
    if (!targetSection.element) return

    isAnimating.value = true
    currentSection.value = index
    setWheelBlocked(true) // 使用新的阻止方法

    // 滑动开始时暂停装饰性动画
    pauseDecorationAnimations(true)

    console.log(`Scrolling to section ${index}:`, targetSection.offsetTop)

    // 根据手势速度和距离动态调整参数（仅移动端）
    let dynamicDuration = finalConfig.duration
    let dynamicEase = finalConfig.ease

    if (gestureVelocity && deviceInfo.value.isMobile) {
      // 计算滚动距离
      const currentScrollY = window.scrollY
      const targetScrollY = targetSection.offsetTop
      const scrollDistance = Math.abs(targetScrollY - currentScrollY)

      // 根据速度和距离调整参数
      if (gestureVelocity > 2.0 || scrollDistance > window.innerHeight * 1.5) {
        // 极快手势或大距离滚动：使用最平滑的设置
        dynamicDuration = finalConfig.duration * 1.5
        dynamicEase = "power1.out" // 最平滑的缓动
      } else if (gestureVelocity > 1.5 || scrollDistance > window.innerHeight) {
        // 快速手势或中等距离：适度增加平滑度
        dynamicDuration = finalConfig.duration * 1.3
        dynamicEase = "power1.out"
      } else if (gestureVelocity > 1.0) {
        // 中速手势：轻微调整
        dynamicDuration = finalConfig.duration * 1.1
        dynamicEase = "power1.out"
      }

      console.log(`Dynamic adjustment: velocity=${gestureVelocity.toFixed(2)}, distance=${scrollDistance.toFixed(0)}px, duration=${dynamicDuration.toFixed(2)}, ease=${dynamicEase}`)
    }

    // 执行滚动动画
    gsap.to(window, {
      duration: dynamicDuration,
      scrollTo: {
        y: targetSection.offsetTop,
        autoKill: false
      },
      ease: dynamicEase,
      onComplete: () => {
        isAnimating.value = false
        setWheelBlocked(false) // 使用新的解除阻止方法

        // 滑动完成后恢复装饰性动画
        setTimeout(() => {
          pauseDecorationAnimations(false)
        }, 100)

        console.log(`Scroll to section ${index} completed - wheel block released`)

        // 刷新ScrollTrigger
        ScrollTrigger.refresh()
      },
      onInterrupt: () => {
        // 动画被中断时也要解除阻止和恢复动画
        console.log(`Scroll to section ${index} interrupted - releasing wheel block`)
        isAnimating.value = false
        setWheelBlocked(false)
        pauseDecorationAnimations(false)
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
    console.log('handleWheel - isSnapMode:', isSnapMode.value, 'isAnimating:', isAnimating.value, 'isWheelBlocked:', isWheelBlocked, 'isWheelListenerDisabled:', isWheelListenerDisabled.value)

    // 如果滚轮监听被禁用，完全不处理事件
    if (isWheelListenerDisabled.value) {
      console.log('handleWheel - wheel listener disabled, allowing default behavior')
      return
    }

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

  // 触摸滑动处理 - 暂时禁用，保留代码以备将来启用
  let touchStartX = 0
  let touchStartY = 0
  let touchStartTime = 0

  const handleTouchStart = (e: TouchEvent) => {
    // 暂时禁用触摸手势功能，只在PC端使用滚轮
    return

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
    // 暂时禁用触摸手势功能，只在PC端使用滚轮
    return

    if (!isSnapMode.value || isAnimating.value) return

    const touchEndX = e.changedTouches[0].clientX
    const touchEndY = e.changedTouches[0].clientY
    const touchEndTime = Date.now()
    const deltaTime = touchEndTime - touchStartTime

    // 简化模式：检查是否被阻塞
    if (finalConfig.touch?.singleTriggerMode && isGestureBlocked) {
      console.log('Touch gesture blocked by single trigger mode')
      return
    }

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

    // 手势有效性检查 - 简化模式下使用更宽松的验证
    const isValidGesture = finalConfig.touch?.simplifiedMode
      ? gesture.distanceY >= finalConfig.touch.minDistance  // 简化模式：只检查最小距离
      : gesture.isValidGesture()  // 标准模式：完整验证

    if (!isValidGesture) {
      console.log('Touch gesture rejected:', {
        reason: finalConfig.touch?.simplifiedMode
          ? `distance ${gesture.distanceY.toFixed(1)} < ${finalConfig.touch.minDistance}`
          : (!gesture.isVerticalDominant ? 'not vertical dominant' : 'insufficient distance and velocity'),
        simplifiedMode: finalConfig.touch?.simplifiedMode || false
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

    // 简化模式：直接使用原始速度，不进行平滑处理
    const effectiveVelocity = finalConfig.touch?.simplifiedMode ? gesture.velocityY : gesture.velocityY

    console.log('Touch gesture details:', {
      deltaY: gesture.deltaY.toFixed(1),
      velocity: effectiveVelocity.toFixed(3),
      distance: gesture.distanceY.toFixed(1),
      simplifiedMode: finalConfig.touch?.simplifiedMode || false
    })

    // 在简化模式下启用手势阻塞
    if (finalConfig.touch?.singleTriggerMode) {
      blockGesture()
    }

    if (gesture.deltaY > 0) {
      // 向上滑动（页面向下滚动）- 切换到下一屏
      if (currentSection.value < sections.value.length - 1) {
        scrollToSection(currentSection.value + 1, false, effectiveVelocity)
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
        scrollToSection(currentSection.value - 1, false, effectiveVelocity)
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

    // 暂时禁用触摸事件监听器，只在PC端使用滚轮
    // 移动端将使用标准的滚动方式，避免触摸手势冲突
    // window.addEventListener('touchstart', handleTouchStart, { passive: true })
    // window.addEventListener('touchend', handleTouchEnd, { passive: false })

    // 设置调试信息到全局对象
    ;(window as any).__snapScrollDebug = {
      isSnapMode,
      isAnimating,
      currentSection,
      currentDevice: deviceInfo,
      finalConfig,
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

    if (gestureBlockTimer) {
      clearTimeout(gestureBlockTimer)
    }

    // 移除事件监听器
    window.removeEventListener('scroll', handleScroll)
    window.removeEventListener('resize', handleResize)
    window.removeEventListener('wheel', handleWheel)

    // 触摸事件监听器已被禁用，无需移除
    // window.removeEventListener('touchstart', handleTouchStart)
    // window.removeEventListener('touchend', handleTouchEnd)
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
    setWheelListenerDisabled,

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
