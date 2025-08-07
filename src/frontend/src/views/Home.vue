<template>
  <div class="home">
    <!-- 顶部导航 -->
    <GlassNavigation />

    <!-- 主要内容区域：被 ScrollTrigger pin 住 -->
    <main class="main-content" ref="mainRef">
      <!-- 每一屏都占 100vh，不滚动内部 -->
      <section class="panel" ref="setPanelRef" data-section="hero">
        <HeroSection />
      </section>

      <section class="panel" ref="setPanelRef" data-section="members">
        <MembersCircle />
      </section>

      <section class="panel" ref="setPanelRef" data-section="calendar">
        <StarCalendar />
      </section>

      <!-- Footer 作为最后一屏 -->
      <section class="panel" ref="setPanelRef" data-section="footer">
        <AppFooter />
      </section>
    </main>

    <!-- 屏幕切换指示器 -->
    <ScreenIndicator 
      :screens="screenConfig"
      :active-index="activeIndex"
      :is-visible="showIndicator"
      @goto="gotoIndex"
    />

    <!-- 切换过渡效果 -->
    <div class="transition-overlay" ref="transitionRef"></div>

    <!-- 全局背景粒子 -->
    <GlobalParticles />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, nextTick, computed } from 'vue'

import GlassNavigation from '@/components/GlassNavigation.vue'
import HeroSection from '@/components/HeroSection.vue'
import MembersCircle from '@/components/MembersCircle.vue'
import StarCalendar from '@/components/StarCalendar.vue'
import AppFooter from '@/components/AppFooter.vue'
import GlobalParticles from '@/components/GlobalParticles.vue'
import ScreenIndicator from '@/components/ScreenIndicator.vue'

import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { Observer } from 'gsap/Observer'
import { ScrollToPlugin } from 'gsap/ScrollToPlugin'

gsap.registerPlugin(ScrollTrigger, Observer, ScrollToPlugin)

const mainRef = ref<HTMLElement | null>(null)
const transitionRef = ref<HTMLElement | null>(null)
const panels = ref<HTMLElement[]>([])
const setPanelRef = (el: HTMLElement | null) => {
  if (el) panels.value.push(el)
}

// 响应式状态
const activeIndex = ref(0)
const isAnimating = ref(false)
const showIndicator = ref(false)

// 屏幕配置
const screenConfig = [
  { title: '星际跃迁门', section: 'hero' },
  { title: '成员星云', section: 'members' },
  { title: '星历日历', section: 'calendar' },
  { title: '联系我们', section: 'footer' }
]

let st: ScrollTrigger | null = null
let observer: any = null
let wheelObserver: any = null
let touchObserver: any = null
let debounceTimer: number | null = null

// 增强配置参数
const CONFIG = {
  NAV_HEIGHT: 80, // 顶部导航高度（px）
  DURATION: 0.8, // 切屏动画时长（秒）
  EASE: 'power2.inOut', // 切屏缓动
  WHEEL_TOLERANCE: 10, // 滚轮灵敏度
  TOUCH_TOLERANCE: 50, // 触摸灵敏度
  KEYBOARD_ENABLED: true,
  MOMENTUM_DURATION: 0.3, // 惯性滚动时长
  DEBOUNCE_DELAY: 100, // 防抖延迟
  TRANSITION_STAGGER: 0.1 // 过渡错开时间
}

// 设备和性能检测
const REDUCED = typeof window !== 'undefined'
  ? window.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches === true
  : false

const IS_MOBILE = typeof window !== 'undefined'
  ? /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
  : false

const SUPPORTS_TOUCH = typeof window !== 'undefined'
  ? 'ontouchstart' in window
  : false

// 计算 ScrollTrigger.end：共需滚动多少距离
const totalDistance = () => Math.max(0, panels.value.length - 1) * window.innerHeight

function clampIndex(i: number) {
  const max = Math.max(0, panels.value.length - 1)
  return Math.min(Math.max(0, i), max)
}

// 增强的面板激活事件分发
function dispatchPanelActive(newIndex: number, oldIndex: number) {
  const oldEl = panels.value[oldIndex]
  const newEl = panels.value[newIndex]
  
  if (oldEl && oldEl !== newEl) {
    oldEl.dispatchEvent(new CustomEvent('panel:active', { 
      detail: { active: false, index: oldIndex } 
    }))
    oldEl.classList.remove('is-active')
    
    // 添加离开动画
    gsap.to(oldEl, {
      opacity: 0.8,
      scale: 0.95,
      duration: CONFIG.DURATION * 0.5,
      ease: CONFIG.EASE
    })
  }
  
  if (newEl) {
    newEl.dispatchEvent(new CustomEvent('panel:active', { 
      detail: { active: true, index: newIndex } 
    }))
    newEl.classList.add('is-active')
    
    // 添加进入动画
    gsap.fromTo(newEl, 
      { opacity: 0.8, scale: 0.95 },
      { 
        opacity: 1, 
        scale: 1, 
        duration: CONFIG.DURATION * 0.7,
        ease: CONFIG.EASE,
        delay: CONFIG.TRANSITION_STAGGER
      }
    )
  }
}

// 增强的过渡效果
function createTransitionEffect(direction: 'up' | 'down') {
  if (!transitionRef.value || REDUCED) return
  
  const overlay = transitionRef.value
  const isUp = direction === 'up'
  
  gsap.set(overlay, {
    background: `linear-gradient(${isUp ? '180deg' : '0deg'}, 
      rgba(0, 212, 255, 0.1) 0%, 
      rgba(255, 107, 157, 0.1) 100%)`,
    opacity: 0,
    scaleY: 0,
    transformOrigin: isUp ? 'bottom' : 'top'
  })
  
  gsap.to(overlay, {
    opacity: 1,
    scaleY: 1,
    duration: CONFIG.DURATION * 0.3,
    ease: 'power2.out',
    onComplete: () => {
      gsap.to(overlay, {
        opacity: 0,
        scaleY: 0,
        duration: CONFIG.DURATION * 0.4,
        ease: 'power2.in',
        delay: CONFIG.DURATION * 0.2
      })
    }
  })
}

function gotoIndex(next: number) {
  if (!st) return
  const target = clampIndex(next)
  if (target === activeIndex.value) return

  // 防抖处理
  if (debounceTimer) {
    clearTimeout(debounceTimer)
  }
  
  debounceTimer = window.setTimeout(() => {
    const direction = target > activeIndex.value ? 'down' : 'up'
    const y = st!.start + target * window.innerHeight

    isAnimating.value = true
    
    // 创建过渡效果
    createTransitionEffect(direction)

    gsap.to(window, {
      duration: REDUCED ? 0 : CONFIG.DURATION,
      ease: CONFIG.EASE as any,
      scrollTo: { y, autoKill: true },
      overwrite: 'auto',
      onStart: () => {
        // 触觉反馈（如果支持）
        if (navigator.vibrate && IS_MOBILE) {
          navigator.vibrate(50)
        }
      },
      onComplete: () => { 
        isAnimating.value = false 
        debounceTimer = null
      },
      onInterrupt: () => { 
        isAnimating.value = false 
        debounceTimer = null
      },
    })

    dispatchPanelActive(target, activeIndex.value)
    activeIndex.value = target
  }, CONFIG.DEBOUNCE_DELAY)
}

function gotoNext() { gotoIndex(activeIndex.value + 1) }
function gotoPrev() { gotoIndex(activeIndex.value - 1) }

function setupScrollTrigger() {
  const container = mainRef.value!
  // 给 main 容器留出顶部导航的可视空间
  container.style.scrollMarginTop = `${CONFIG.NAV_HEIGHT}px`

  // 初始化激活态
  panels.value.forEach((el, i) => {
    el.classList.toggle('is-active', i === 0)
    // 为非活跃面板设置初始状态
    if (i !== 0) {
      gsap.set(el, { opacity: 0.8, scale: 0.95 })
    }
  })

  st = ScrollTrigger.create({
    trigger: container,
    start: `top top+=${CONFIG.NAV_HEIGHT}`,
    end: () => `+=${totalDistance()}`,
    pin: true,
    pinSpacing: true,
    anticipatePin: 1,
    scrub: false,
    invalidateOnRefresh: true,
    onUpdate(self) {
      // 保障刷新/窗口变化时，仍能保持正确激活屏
      const idx = clampIndex(Math.round(self.progress * (panels.value.length - 1)))
      if (idx !== activeIndex.value && !isAnimating.value) {
        dispatchPanelActive(idx, activeIndex.value)
        activeIndex.value = idx
      }
    },
    onToggle(self) {
      // 进入/离开 pinned 区域时显示/隐藏指示器
      showIndicator.value = self.isActive
    }
  })

  // 进入 pinned 区域时，强制把滚动位置校正到当前屏的"整点"
  ScrollTrigger.addEventListener('refresh', () => {
    if (!st) return
    const y = st.start + activeIndex.value * window.innerHeight
    window.scrollTo({ top: y })
  })
  ScrollTrigger.refresh()
}

// 增强的 Observer 设置
function setupObserver() {
  // 主要的滚轮和触摸观察器
  observer = Observer.create({
    target: window,
    type: 'wheel,touch,pointer',
    wheelSpeed: IS_MOBILE ? 0.5 : 1,
    tolerance: CONFIG.WHEEL_TOLERANCE,
    preventDefault: true,
    onDown() {
      if (!st?.isActive() || isAnimating.value) return
      gotoNext()
    },
    onUp() {
      if (!st?.isActive() || isAnimating.value) return
      gotoPrev()
    },
    onPress() {
      // 触摸开始时的反馈
      if (IS_MOBILE && navigator.vibrate) {
        navigator.vibrate(10)
      }
    }
  })

  // 专门的触摸手势观察器（移动端）
  if (SUPPORTS_TOUCH) {
    touchObserver = Observer.create({
      target: window,
      type: 'touch',
      tolerance: CONFIG.TOUCH_TOLERANCE,
      preventDefault: false, // 允许其他触摸事件
      onDown() {
        if (!st?.isActive() || isAnimating.value) return
        gotoNext()
      },
      onUp() {
        if (!st?.isActive() || isAnimating.value) return
        gotoPrev()
      }
    })
  }
}

// 键盘事件处理
function onKeydown(e: KeyboardEvent) {
  if (!CONFIG.KEYBOARD_ENABLED || !st?.isActive() || isAnimating.value) return

  // 避免在输入框内抢键
  const tag = (e.target as HTMLElement)?.tagName?.toLowerCase()
  if (tag && ['input', 'textarea', 'select'].includes(tag)) return

  const keyActions: Record<string, () => void> = {
    'ArrowDown': gotoNext,
    'PageDown': gotoNext,
    ' ': gotoNext,
    'ArrowUp': gotoPrev,
    'PageUp': gotoPrev,
    'Home': () => gotoIndex(0),
    'End': () => gotoIndex(panels.value.length - 1)
  }

  const action = keyActions[e.key]
  if (action) {
    e.preventDefault()
    action()
  }
}

// 窗口大小变化处理
function onResize() {
  if (!st) return

  // 防抖处理窗口变化
  if (debounceTimer) {
    clearTimeout(debounceTimer)
  }

  debounceTimer = window.setTimeout(() => {
    st?.refresh()
    const y = st!.start + activeIndex.value * window.innerHeight
    window.scrollTo({ top: y })
    debounceTimer = null
  }, 150)
}

onMounted(async () => {
  await nextTick()

  // 若用户偏好减少动画：简化处理
  if (REDUCED) {
    setupScrollTrigger()
    window.addEventListener('keydown', onKeydown, { passive: false })
    return
  }

  setupScrollTrigger()
  setupObserver()
  window.addEventListener('keydown', onKeydown, { passive: false })
  window.addEventListener('resize', onResize, { passive: true })

  // 延迟显示指示器，避免初始化时的闪烁
  setTimeout(() => {
    showIndicator.value = true
  }, 500)
})

onBeforeUnmount(() => {
  observer?.kill?.()
  touchObserver?.kill?.()
  wheelObserver?.kill?.()
  ScrollTrigger.getAll().forEach(t => t.kill())
  gsap.killTweensOf(window)
  window.removeEventListener('keydown', onKeydown)
  window.removeEventListener('resize', onResize)

  if (debounceTimer) {
    clearTimeout(debounceTimer)
  }
})
</script>

<style scoped>
:root {
  --nav-height: 80px;
}

.home {
  min-height: 100vh;
  background: var(--base-dark);
  color: var(--text-primary);
  overflow-x: hidden;
  position: relative;
}

/* 让主区域与导航错开，避免被遮住 */
.main-content {
  position: relative;
  z-index: 1;
  margin-top: var(--nav-height);
}

/* 每屏满高，不允许内部滚动 */
.panel {
  height: 100vh;
  width: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: center;
  will-change: transform, opacity;
  transition: opacity 0.3s ease, transform 0.3s ease;
}

/* 激活态样式 */
.panel.is-active {
  outline: 0 solid transparent;
}

/* 过渡覆盖层 */
.transition-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 50;
  opacity: 0;
  transform: scaleY(0);
}

/* 性能优化 */
.panel,
.transition-overlay {
  backface-visibility: hidden;
  perspective: 1000px;
}

/* 移动端优化 */
@media (max-width: 768px) {
  .main-content {
    margin-top: calc(var(--nav-height) * 0.8);
  }

  .panel {
    padding: 1rem;
  }
}

/* 横屏模式优化 */
@media (orientation: landscape) and (max-height: 600px) {
  .main-content {
    margin-top: calc(var(--nav-height) * 0.6);
  }
}

/* 高对比度模式 */
@media (prefers-contrast: high) {
  .panel.is-active {
    outline: 2px solid var(--primary-color, #00d4ff);
  }
}

/* 减少动画模式 */
@media (prefers-reduced-motion: reduce) {
  .panel,
  .transition-overlay {
    transition: none !important;
    animation: none !important;
  }

  .panel {
    will-change: auto;
  }
}

/* 触摸设备优化 */
@media (hover: none) and (pointer: coarse) {
  .panel {
    touch-action: pan-y;
  }
}

/* 暗色主题优化 */
@media (prefers-color-scheme: dark) {
  .transition-overlay {
    background: linear-gradient(
      0deg,
      rgba(0, 212, 255, 0.05) 0%,
      rgba(255, 107, 157, 0.05) 100%
    ) !important;
  }
}

/* 浅色主题优化 */
@media (prefers-color-scheme: light) {
  .transition-overlay {
    background: linear-gradient(
      0deg,
      rgba(0, 212, 255, 0.15) 0%,
      rgba(255, 107, 157, 0.15) 100%
    ) !important;
  }
}
</style>
