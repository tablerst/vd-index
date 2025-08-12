<template>
  <section class="daily-wall" ref="sectionRef" @mouseenter="pauseLoop()" @mouseleave="resumeLoop()">
    <!-- 顶部居中标题（参考 MembersCircle 顶部控件的浮动/下移风格） -->
    <div class="title-bar" ref="titleBarRef">
      <h3 class="title">群员日常</h3>
    </div>

    <!-- 横向无缝循环滚动轨道 -->
    <div class="loop-container" ref="loopContainer">
      <div class="loop-track" ref="trackRef">
        <DailyCard v-for="p in posts" :key="p.id" :post="p" class="loop-item" />
      </div>
    </div>

    <!-- 底部居中“点击更多”按钮，支持路由跳转 -->
    <div class="more-bar" ref="moreBarRef">
      <button class="more-btn" @click="$router.push('/daily')">点击更多</button>
    </div>
  </section>
</template>

<script setup lang="ts">
// 中文注释：DailyWall - 顶部居中标题 + 底部按钮 + GSAP 无缝横向循环
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
import { dailyApi, type DailyPostItem } from '@/services/daily'
import DailyCard from './DailyCard.vue'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

const posts = ref<DailyPostItem[]>([])
const loopContainer = ref<HTMLElement | null>(null)
const trackRef = ref<HTMLElement | null>(null)
const sectionRef = ref<HTMLElement | null>(null)
const titleBarRef = ref<HTMLElement | null>(null)
const moreBarRef = ref<HTMLElement | null>(null)
const paused = ref(false)
let loopTl: gsap.core.Timeline | null = null
let rafId: number | null = null
let lastFrameTime = performance.now()
let fpsSamples: number[] = []

function prefersReducedMotion(): boolean {
  try {
    return typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches
  } catch { return false }
}

// 来自 GSAP 官方 Helper 的轻量实现：创建无缝横向循环
function horizontalLoop(items: HTMLElement[], config: { speed?: number; paused?: boolean; repeat?: number } = {}) {
  const tl = gsap.timeline({ repeat: config.repeat ?? -1, paused: config.paused ?? false, defaults: { ease: 'none' } })
  const length = items.length
  const startX = items[0]?.offsetLeft ?? 0
  const times: number[] = []
  const widths: number[] = []
  const xPercents: number[] = []
  const pixelsPerSecond = (config.speed ?? 1) * 100
  const snap = gsap.utils.snap(1)

  gsap.set(items, {
    xPercent: (i, el) => {
      const w = (widths[i] = parseFloat(gsap.getProperty(el as Element, 'width', 'px') as string))
      xPercents[i] = snap(((parseFloat(gsap.getProperty(el as Element, 'x', 'px') as string) / w) * 100) + (gsap.getProperty(el as Element, 'xPercent') as number))
      return xPercents[i]
    }
  })
  gsap.set(items, { x: 0 })

  const totalWidth = items[length - 1].offsetLeft + (xPercents[length - 1] / 100) * widths[length - 1] - startX + items[length - 1].offsetWidth * (gsap.getProperty(items[length - 1], 'scaleX') as number)

  for (let i = 0; i < length; i++) {
    const item = items[i]
    const curX = (xPercents[i] / 100) * widths[i]
    const distanceToStart = item.offsetLeft + curX - startX
    const distanceToLoop = distanceToStart + widths[i] * (gsap.getProperty(item, 'scaleX') as number)

    tl.to(item, { xPercent: snap(((curX - distanceToLoop) / widths[i]) * 100), duration: distanceToLoop / pixelsPerSecond }, 0)
      .fromTo(item, { xPercent: snap(((curX - distanceToLoop + totalWidth) / widths[i]) * 100) }, { xPercent: xPercents[i], duration: (curX - distanceToLoop + totalWidth - curX) / pixelsPerSecond, immediateRender: false }, distanceToLoop / pixelsPerSecond)
      .add('label' + i, distanceToStart / pixelsPerSecond)
    times[i] = distanceToStart / pixelsPerSecond
  }
  return tl
}

function buildLoop() {
  if (prefersReducedMotion()) return
  const track = trackRef.value
  if (!track) return
  const items = Array.from(track.querySelectorAll<HTMLElement>('.loop-item'))
  if (!items.length) return
  loopTl?.kill()
  loopTl = horizontalLoop(items, { speed: 1, paused: false, repeat: -1 })
}

// 悬停控制
function pauseLoop() {
  paused.value = true
  loopTl?.pause()
}
function resumeLoop() {
  paused.value = false
  loopTl?.resume()
}

// FPS 监控：过低自动暂停，恢复后继续
function startFpsWatch() {
  if (prefersReducedMotion()) return
  const loop = (now: number) => {
    const delta = now - lastFrameTime
    lastFrameTime = now
    const fps = 1000 / Math.max(delta, 1)
    fpsSamples.push(fps)
    if (fpsSamples.length > 30) fpsSamples.shift()
    const avg = fpsSamples.reduce((a, b) => a + b, 0) / fpsSamples.length
    if (avg < 45) pauseLoop()
    else if (!paused.value) loopTl?.resume()
    rafId = requestAnimationFrame(loop)
  }

// 进入视差/下移动画，参考 MembersCircle 的进入节奏
function setupEnterAnimations() {
  if (!sectionRef.value) return

  // 整体区块淡入+下移
  gsap.fromTo(sectionRef.value,
    { opacity: 0, y: 60, scale: 0.98 },
    {
      opacity: 1,
      y: 0,
      scale: 1,
      duration: 0.9,
      ease: 'power3.out',
      scrollTrigger: {
        trigger: sectionRef.value,
        start: 'top 80%',
        end: 'top 20%',
        toggleActions: 'play none none reverse'
      }
    }
  )

  // 顶部标题的轻微下移
  if (titleBarRef.value) {
    gsap.fromTo(titleBarRef.value,
      { y: -20, opacity: 0 },
      {
        y: 0,
        opacity: 1,
        duration: 0.6,
        ease: 'power2.out',
        scrollTrigger: {
          trigger: sectionRef.value,
          start: 'top 75%',
          end: 'top 40%',
          toggleActions: 'play none none reverse'
        }
      }
    )
  }

  // 底部按钮的轻微上移
  if (moreBarRef.value) {
    gsap.fromTo(moreBarRef.value,
      { y: 20, opacity: 0 },
      {
        y: 0,
        opacity: 1,
        duration: 0.6,
        ease: 'power2.out',
        scrollTrigger: {
          trigger: sectionRef.value,
          start: 'top 70%',
          end: 'top 30%',
          toggleActions: 'play none none reverse'
        }
      }
    )
  }
}

  rafId = requestAnimationFrame(loop)
}
function stopFpsWatch() {
  if (rafId) cancelAnimationFrame(rafId)
  rafId = null
  fpsSamples = []
}

onMounted(async () => {
  try {
    posts.value = await dailyApi.getTrending(12)
    await nextTick()
    buildLoop()
    setupEnterAnimations()
    startFpsWatch()
  } catch (e) {
    console.error('加载trending失败', e)
  }
})

onUnmounted(() => {
  loopTl?.kill()
  loopTl = null
  stopFpsWatch()
})
</script>

<style scoped>
/* 中文注释：DailyWall 样式：顶部标题+底部按钮+横向循环轨道。所有颜色使用主题变量 */
.daily-wall {
  position: relative;
  padding: 72px 0 64px; /* 下移整体区块，避免贴近导航 */
}

.title-bar {
  position: sticky; /* 跟随滚动轻微下移，保持在顶部可见 */
  top: 48px; /* 参考 MembersCircle 顶部控件的下移距离 */
  display: flex;
  justify-content: center;
  z-index: 2;
  pointer-events: none; /* 仅标题，不阻挡交互 */
}
.title {
  color: var(--text-primary);
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.loop-container {
  position: relative;
  overflow: hidden;
  width: 100%;
}
.loop-track {
  display: flex;
  gap: 16px;
  will-change: transform;
  padding: 16px 8px;
}
.loop-item { flex: 0 0 auto; width: min(360px, 32vw); }

.more-bar {
  position: sticky;
  bottom: 12px;
  display: flex;
  justify-content: center;
  margin-top: 8px;
  z-index: 2;
}
.more-btn {
  appearance: none;
  background: var(--glass-bg);
  color: var(--text-secondary);
  border: var(--border-glass);
  border-radius: 10px;
  padding: 8px 14px;
  cursor: pointer;
  transition: background .2s ease, color .2s ease, box-shadow .2s ease, border-color .2s ease;
}
.more-btn:hover { color: var(--text-primary); box-shadow: var(--shadow-blue-glow); border-color: var(--border-primary); }

@media (max-width: 640px) {
  .loop-item { width: 80vw; }
}
</style>

