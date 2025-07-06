/**
 * Fluent Design System 特效工具
 * 包含 Reveal、Acrylic、Motion 等效果的实现
 */

// 导入 Vue 相关类型
import { type Ref, onMounted, onUnmounted } from 'vue'

/**
 * Reveal 效果 - 鼠标悬停高亮
 */
export class RevealEffect {
  private element: HTMLElement
  private isEnabled: boolean = true

  constructor(element: HTMLElement) {
    this.element = element
    this.init()
  }

  private init() {
    this.element.addEventListener('mousemove', this.handleMouseMove.bind(this))
    this.element.addEventListener('mouseleave', this.handleMouseLeave.bind(this))
  }

  private handleMouseMove(event: MouseEvent) {
    if (!this.isEnabled) return

    const rect = this.element.getBoundingClientRect()
    const x = ((event.clientX - rect.left) / rect.width) * 100
    const y = ((event.clientY - rect.top) / rect.height) * 100

    this.element.style.setProperty('--mouse-x', `${x}%`)
    this.element.style.setProperty('--mouse-y', `${y}%`)
  }

  private handleMouseLeave() {
    this.element.style.removeProperty('--mouse-x')
    this.element.style.removeProperty('--mouse-y')
  }

  public enable() {
    this.isEnabled = true
  }

  public disable() {
    this.isEnabled = false
  }

  public destroy() {
    this.element.removeEventListener('mousemove', this.handleMouseMove.bind(this))
    this.element.removeEventListener('mouseleave', this.handleMouseLeave.bind(this))
  }
}

/**
 * Acrylic 效果 - 毛玻璃背景
 */
export class AcrylicEffect {
  private element: HTMLElement
  private options: AcrylicOptions

  constructor(element: HTMLElement, options: Partial<AcrylicOptions> = {}) {
    this.element = element
    this.options = {
      opacity: 0.8,
      blur: 20,
      saturation: 180,
      brightness: 1.1,
      tintColor: 'rgba(255, 255, 255, 0.8)',
      ...options
    }
    this.apply()
  }

  private apply() {
    const { opacity, blur, saturation, brightness, tintColor } = this.options

    this.element.style.background = tintColor
    this.element.style.backdropFilter = `blur(${blur}px) saturate(${saturation}%) brightness(${brightness})`
    this.element.style.webkitBackdropFilter = `blur(${blur}px) saturate(${saturation}%) brightness(${brightness})`
    this.element.style.border = '1px solid rgba(255, 255, 255, 0.2)'
  }

  public updateOptions(newOptions: Partial<AcrylicOptions>) {
    this.options = { ...this.options, ...newOptions }
    this.apply()
  }

  public remove() {
    this.element.style.removeProperty('background')
    this.element.style.removeProperty('backdrop-filter')
    this.element.style.removeProperty('-webkit-backdrop-filter')
    this.element.style.removeProperty('border')
  }
}

interface AcrylicOptions {
  opacity: number
  blur: number
  saturation: number
  brightness: number
  tintColor: string
}

/**
 * Fluent Motion 动画
 */
export class FluentMotion {
  private static readonly EASING = {
    accelerate: 'cubic-bezier(0.7, 0, 1, 0.5)',
    decelerate: 'cubic-bezier(0.1, 0.9, 0.2, 1)',
    standard: 'cubic-bezier(0.8, 0, 0.2, 1)',
    max: 'cubic-bezier(0.8, 0, 0.1, 1)'
  }

  private static readonly DURATION = {
    ultraFast: 50,
    faster: 100,
    fast: 150,
    normal: 200,
    slow: 300,
    slower: 400,
    ultraSlow: 500
  }

  /**
   * 淡入动画
   */
  static fadeIn(
    element: HTMLElement, 
    duration: keyof typeof FluentMotion.DURATION = 'normal',
    easing: keyof typeof FluentMotion.EASING = 'decelerate'
  ): Promise<void> {
    return new Promise((resolve) => {
      element.style.opacity = '0'
      element.style.transition = `opacity ${this.DURATION[duration]}ms ${this.EASING[easing]}`
      
      requestAnimationFrame(() => {
        element.style.opacity = '1'
        setTimeout(resolve, this.DURATION[duration])
      })
    })
  }

  /**
   * 淡出动画
   */
  static fadeOut(
    element: HTMLElement,
    duration: keyof typeof FluentMotion.DURATION = 'normal',
    easing: keyof typeof FluentMotion.EASING = 'accelerate'
  ): Promise<void> {
    return new Promise((resolve) => {
      element.style.transition = `opacity ${this.DURATION[duration]}ms ${this.EASING[easing]}`
      element.style.opacity = '0'
      setTimeout(resolve, this.DURATION[duration])
    })
  }

  /**
   * 缩放进入动画
   */
  static scaleIn(
    element: HTMLElement,
    duration: keyof typeof FluentMotion.DURATION = 'normal',
    easing: keyof typeof FluentMotion.EASING = 'decelerate'
  ): Promise<void> {
    return new Promise((resolve) => {
      element.style.transform = 'scale(0.8)'
      element.style.opacity = '0'
      element.style.transition = `transform ${this.DURATION[duration]}ms ${this.EASING[easing]}, opacity ${this.DURATION[duration]}ms ${this.EASING[easing]}`
      
      requestAnimationFrame(() => {
        element.style.transform = 'scale(1)'
        element.style.opacity = '1'
        setTimeout(resolve, this.DURATION[duration])
      })
    })
  }

  /**
   * 滑入动画
   */
  static slideIn(
    element: HTMLElement,
    direction: 'up' | 'down' | 'left' | 'right' = 'up',
    duration: keyof typeof FluentMotion.DURATION = 'normal',
    easing: keyof typeof FluentMotion.EASING = 'decelerate'
  ): Promise<void> {
    return new Promise((resolve) => {
      const distance = 40
      let transform = ''
      
      switch (direction) {
        case 'up':
          transform = `translateY(${distance}px)`
          break
        case 'down':
          transform = `translateY(-${distance}px)`
          break
        case 'left':
          transform = `translateX(${distance}px)`
          break
        case 'right':
          transform = `translateX(-${distance}px)`
          break
      }
      
      element.style.transform = transform
      element.style.opacity = '0'
      element.style.transition = `transform ${this.DURATION[duration]}ms ${this.EASING[easing]}, opacity ${this.DURATION[duration]}ms ${this.EASING[easing]}`
      
      requestAnimationFrame(() => {
        element.style.transform = 'translateX(0) translateY(0)'
        element.style.opacity = '1'
        setTimeout(resolve, this.DURATION[duration])
      })
    })
  }

  /**
   * 连续动画
   */
  static stagger(
    elements: HTMLElement[],
    animation: (element: HTMLElement, index: number) => Promise<void>,
    delay: number = 50
  ): Promise<void[]> {
    return Promise.all(
      elements.map((element, index) => 
        new Promise<void>((resolve) => {
          setTimeout(() => {
            animation(element, index).then(resolve)
          }, index * delay)
        })
      )
    )
  }
}

/**
 * 深度阴影工具
 */
export class DepthShadow {
  private static readonly SHADOWS = {
    2: '0 1px 2px rgba(0, 0, 0, 0.14), 0 0px 2px rgba(0, 0, 0, 0.12)',
    4: '0 2px 4px rgba(0, 0, 0, 0.14), 0 0px 2px rgba(0, 0, 0, 0.12)',
    8: '0 4px 8px rgba(0, 0, 0, 0.14), 0 0px 2px rgba(0, 0, 0, 0.12)',
    16: '0 8px 16px rgba(0, 0, 0, 0.14), 0 0px 2px rgba(0, 0, 0, 0.12)',
    64: '0 32px 64px rgba(0, 0, 0, 0.24), 0 0px 2px rgba(0, 0, 0, 0.12)'
  }

  static apply(element: HTMLElement, level: keyof typeof DepthShadow.SHADOWS) {
    element.style.boxShadow = this.SHADOWS[level]
  }

  static remove(element: HTMLElement) {
    element.style.removeProperty('box-shadow')
  }

  static animate(
    element: HTMLElement,
    fromLevel: keyof typeof DepthShadow.SHADOWS,
    toLevel: keyof typeof DepthShadow.SHADOWS,
    duration: number = 200
  ) {
    element.style.transition = `box-shadow ${duration}ms cubic-bezier(0.4, 0, 0.2, 1)`
    element.style.boxShadow = this.SHADOWS[fromLevel]
    
    requestAnimationFrame(() => {
      element.style.boxShadow = this.SHADOWS[toLevel]
    })
  }
}

/**
 * Vue 3 组合式 API 钩子
 */
export function useRevealEffect(elementRef: Ref<HTMLElement | null>) {
  let revealInstance: RevealEffect | null = null

  onMounted(() => {
    if (elementRef.value) {
      revealInstance = new RevealEffect(elementRef.value)
    }
  })

  onUnmounted(() => {
    if (revealInstance) {
      revealInstance.destroy()
    }
  })

  return {
    enable: () => revealInstance?.enable(),
    disable: () => revealInstance?.disable()
  }
}

export function useAcrylicEffect(
  elementRef: Ref<HTMLElement | null>,
  options: Partial<AcrylicOptions> = {}
) {
  let acrylicInstance: AcrylicEffect | null = null

  onMounted(() => {
    if (elementRef.value) {
      acrylicInstance = new AcrylicEffect(elementRef.value, options)
    }
  })

  onUnmounted(() => {
    if (acrylicInstance) {
      acrylicInstance.remove()
    }
  })

  return {
    updateOptions: (newOptions: Partial<AcrylicOptions>) => 
      acrylicInstance?.updateOptions(newOptions)
  }
}


