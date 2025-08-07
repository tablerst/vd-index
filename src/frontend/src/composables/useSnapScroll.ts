import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { gsap } from 'gsap'
import { Observer } from 'gsap/Observer'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { ScrollToPlugin } from 'gsap/ScrollToPlugin'

// 注册GSAP插件
gsap.registerPlugin(Observer, ScrollTrigger, ScrollToPlugin)

export interface SnapScrollSection {
  id: string
  element: HTMLElement | null
  offsetTop: number
  height: number
}

export interface SnapScrollConfig {
  tolerance: number
  duration: number
  ease: string
  debounceDelay: number
  footerThreshold: number
}

/**
 * 分屏推进滚动组合式函数
 * 使用GSAP Observer实现平滑的分屏切换效果
 */
export function useSnapScroll(sectionRefs: Array<{ value: HTMLElement | null }>, config?: Partial<SnapScrollConfig>) {
  // 默认配置
  const defaultConfig: SnapScrollConfig = {
    tolerance: 120,       // 最小滚动距离（已废弃，保留兼容性）
    duration: 1.2,        // 动画持续时间
    ease: "power2.out",   // 缓动函数
    debounceDelay: 300,   // 防抖延迟（增加延迟，确保动画完成后才能再次触发）
    footerThreshold: 0.8  // footer区域阈值
  }

  const finalConfig = { ...defaultConfig, ...config }

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

    // 过滤极小的滚动值
    if (Math.abs(e.deltaY) < 10) {
      console.log('handleWheel - deltaY too small:', e.deltaY)
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

    // 触摸滑动处理
  let touchStartY = 0

  const handleTouchStart = (e: TouchEvent) => {
    if (!isSnapMode.value) return
    touchStartY = e.touches[0].clientY
  }

  const handleTouchEnd = (e: TouchEvent) => {
    if (!isSnapMode.value || isAnimating.value) return
    const deltaY = touchStartY - e.changedTouches[0].clientY
    if (Math.abs(deltaY) < 50) return // 降低触摸阈值，使触摸更敏感

    console.log('Touch deltaY:', deltaY)

    if (deltaY > 0) {
      // 向上滑动（页面向下滚动）- 切换到下一屏
      if (currentSection.value < sections.value.length - 1) {
        scrollToSection(currentSection.value + 1)
      } else {
        checkFooterArea()
      }
    } else {
      // 向下滑动（页面向上滚动）- 切换到上一屏
      if (currentSection.value > 0) {
        scrollToSection(currentSection.value - 1)
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
    if (debounceTimer) {
      clearTimeout(debounceTimer)
    }

    if (wheelBlockTimer) {
      clearTimeout(wheelBlockTimer)
    }

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
    
    // 配置
    config: finalConfig
  }
}
