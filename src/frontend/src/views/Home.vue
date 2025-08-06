<template>
  <div class="home">
    <!-- 顶部导航（建议固定高度，下面用变量参与布局） -->
    <GlassNavigation />

    <!-- 主要内容区域：被 ScrollTrigger pin 住 -->
    <main class="main-content" ref="mainRef">
      <!-- 每一屏都占 100vh，不滚动内部（重内容建议避免内滚） -->
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

    <!-- 全局背景粒子 -->
    <GlobalParticles />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'

import GlassNavigation from '@/components/GlassNavigation.vue'
import HeroSection from '@/components/HeroSection.vue'
import MembersCircle from '@/components/MembersCircle.vue'
import StarCalendar from '@/components/StarCalendar.vue'
import AppFooter from '@/components/AppFooter.vue'
import GlobalParticles from '@/components/GlobalParticles.vue'

import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { Observer } from 'gsap/Observer'
import { ScrollToPlugin } from 'gsap/ScrollToPlugin'

gsap.registerPlugin(ScrollTrigger, Observer, ScrollToPlugin)

const mainRef = ref<HTMLElement | null>(null)
const panels = ref<HTMLElement[]>([])
const setPanelRef = (el: HTMLElement | null) => {
  if (el) panels.value.push(el)
}

let st: ScrollTrigger | null = null
let observer: any = null
let activeIndex = 0
let isAnimating = false

// 自定义参数
const NAV_HEIGHT = 80 // 顶部导航高度（px），用于顶部留白
const DURATION = 0.65 // 每次切屏动画时长（秒）
const EASE = 'power2.out' // 切屏缓动
const WHEEL_TOLERANCE = 12 // 触摸板/触屏灵敏度
const KEYBOARD_ENABLED = true

// 是否启用“减少动画”无障碍偏好
const REDUCED = typeof window !== 'undefined'
  ? window.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches === true
  : false

// 计算 ScrollTrigger.end：共需滚动多少距离
const totalDistance = () => Math.max(0, panels.value.length - 1) * window.innerHeight

function clampIndex(i: number) {
  const max = Math.max(0, panels.value.length - 1)
  return Math.min(Math.max(0, i), max)
}

function dispatchPanelActive(newIndex: number, oldIndex: number) {
  const oldEl = panels.value[oldIndex]
  const newEl = panels.value[newIndex]
  if (oldEl && oldEl !== newEl) {
    oldEl.dispatchEvent(new CustomEvent('panel:active', { detail: { active: false, index: oldIndex } }))
    oldEl.classList.remove('is-active')
  }
  if (newEl) {
    newEl.dispatchEvent(new CustomEvent('panel:active', { detail: { active: true, index: newIndex } }))
    newEl.classList.add('is-active')
  }
}

function gotoIndex(next: number) {
  if (!st) return
  const target = clampIndex(next)
  if (target === activeIndex) return

  const y = st.start + target * window.innerHeight

  isAnimating = true
  gsap.to(window, {
    duration: REDUCED ? 0 : DURATION,
    ease: EASE as any,
    scrollTo: { y, autoKill: true }, // 用户手动滚动会自动打断
    overwrite: 'auto',
    onStart: () => {},
    onComplete: () => { isAnimating = false },
    onInterrupt: () => { isAnimating = false },
  })

  dispatchPanelActive(target, activeIndex)
  activeIndex = target
}

function gotoNext() { gotoIndex(activeIndex + 1) }
function gotoPrev() { gotoIndex(activeIndex - 1) }

function setupScrollTrigger() {
  const container = mainRef.value!
  // 给 main 容器留出顶部导航的可视空间
  container.style.scrollMarginTop = `${NAV_HEIGHT}px`

  // 初始化激活态
  panels.value.forEach((el, i) => el.classList.toggle('is-active', i === 0))

  st = ScrollTrigger.create({
    trigger: container,
    start: `top top+=${NAV_HEIGHT}`, // 顶部向下偏移导航高度
    end: () => `+=${totalDistance()}`, // 总滚动距离
    pin: true,
    pinSpacing: true, // 让页面出现可滚动空间；避免“页尾大空白”的错觉
    anticipatePin: 1,
    scrub: false, // 不跟随滚动逐像素变化；我们自己用 Observer 步进
    invalidateOnRefresh: true,
    onUpdate(self) {
      // 保障刷新/窗口变化时，仍能保持正确激活屏
      const idx = clampIndex(Math.round(self.progress * (panels.value.length - 1)))
      if (idx !== activeIndex && !isAnimating) {
        dispatchPanelActive(idx, activeIndex)
        activeIndex = idx
      }
    },
  })

  // 进入 pinned 区域时，强制把滚动位置校正到当前屏的“整点”，避免刷新后的半屏状态
  ScrollTrigger.addEventListener('refresh', () => {
    if (!st) return
    const y = st.start + activeIndex * window.innerHeight
    window.scrollTo({ top: y })
  })
  ScrollTrigger.refresh()
}

function setupObserver() {
  // 仅在 pinned 期间劫持滚动；离开 pinned 区域恢复正常
  observer = Observer.create({
    target: window,
    type: 'wheel,touch',
    wheelSpeed: 1,
    tolerance: WHEEL_TOLERANCE,
    preventDefault: true, // 拦截默认滚动
    onDown() {
      if (!st?.isActive() || isAnimating) return
      gotoNext()
    },
    onUp() {
      if (!st?.isActive() || isAnimating) return
      gotoPrev()
    },
    // 触摸轻扫也会触发 onUp/onDown
  })
}

function onKeydown(e: KeyboardEvent) {
  if (!KEYBOARD_ENABLED || !st?.isActive() || isAnimating) return
  // 避免在输入框内抢键
  const tag = (e.target as HTMLElement)?.tagName?.toLowerCase()
  if (tag && ['input', 'textarea', 'select'].includes(tag)) return

  if (e.key === 'ArrowDown' || e.key === 'PageDown' || e.key === ' ') {
    e.preventDefault()
    gotoNext()
  } else if (e.key === 'ArrowUp' || e.key === 'PageUp') {
    e.preventDefault()
    gotoPrev()
  }
}

onMounted(async () => {
  await nextTick()

  // 若用户偏好减少动画：不启用劫持，退化为普通滚动 + pin（可按需直接跳过整个逻辑）
  if (REDUCED) {
    setupScrollTrigger()
    window.addEventListener('keydown', onKeydown, { passive: false })
    return
  }

  setupScrollTrigger()
  setupObserver()
  window.addEventListener('keydown', onKeydown, { passive: false })

  // 窗口变化：更新 end 与当前屏位置
  const onResize = () => {
    st?.refresh()
    const y = st!.start + activeIndex * window.innerHeight
    window.scrollTo({ top: y })
  }
  window.addEventListener('resize', onResize, { passive: true })
})

onBeforeUnmount(() => {
  observer?.kill?.()
  ScrollTrigger.getAll().forEach(t => t.kill())
  gsap.killTweensOf(window)
  window.removeEventListener('keydown', onKeydown)
})
</script>

<style scoped>
:root {
  /* 你也可以把导航高度做成 CSS 变量以便主题切换 */
  --nav-height: 80px;
}

.home {
  min-height: 100vh;
  background: var(--base-dark);
  color: var(--text-primary);
  overflow-x: hidden;
}

/* 让主区域与导航错开，避免被遮住；ScrollTrigger 的 start 里也做了同样的偏移 */
.main-content {
  position: relative;
  z-index: 1;
  margin-top: var(--nav-height);
}

/* 每屏满高，不允许内部滚动，避免出现“内层滚动 vs 外层切屏”的冲突 */
.panel {
  height: 100vh;
  width: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: center;
  will-change: transform;
}

/* 仅用于激活态的调试（可移除） */
.panel.is-active {
  outline: 0 solid transparent;
}

/* 无障碍：若用户选择减少动画，可以在此进一步弱化过渡（脚本里也已处理） */
@media (prefers-reduced-motion: reduce) {
  .panel {
    scroll-behavior: auto;
    transition: none !important;
    animation: none !important;
  }
}
</style>
