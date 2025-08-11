<template>
  <section class="daily-wall" @mouseenter="paused = true" @mouseleave="onResume()">
    <div class="header">
      <h3 class="title">群员日常</h3>
      <button class="more" @click="$router.push('/daily')">点击更多</button>
    </div>

    <div class="masonry" ref="masonryRef">
      <DailyCard v-for="p in posts" :key="p.id" :post="p" class="masonry-item" />
    </div>
  </section>
</template>

<script setup lang="ts">
// 中文注释：首页子屏幕，渲染 trending 列表，Masonry 基础布局 + 初始载入Stagger淡入
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
import { dailyApi, type DailyPostItem } from '@/services/daily'
import DailyCard from './DailyCard.vue'
import { gsap } from 'gsap'

const posts = ref<DailyPostItem[]>([])
const masonryRef = ref<HTMLElement | null>(null)
let cleanupFns: Array<() => void> = []
let rotationTimer: number | null = null
const paused = ref(false)

// 性能守护：FPS 监控与降级
let fpsSamples: number[] = []
let lastFrameTime = performance.now()
let rafId: number | null = null
function startFpsWatch() {
  if (prefersReducedMotion()) return
  const loop = (now: number) => {
    const delta = now - lastFrameTime
    lastFrameTime = now
    const fps = 1000 / Math.max(delta, 1)
    fpsSamples.push(fps)
    if (fpsSamples.length > 30) fpsSamples.shift()
    const avg = fpsSamples.reduce((a, b) => a + b, 0) / fpsSamples.length
    // 低于阈值时暂停轮换、避免并发动画
    if (avg < 45) {
      paused.value = true
    }
    rafId = requestAnimationFrame(loop)
  }
  rafId = requestAnimationFrame(loop)
}
function stopFpsWatch() {
  if (rafId) cancelAnimationFrame(rafId)
  rafId = null
  fpsSamples = []
}

function prefersReducedMotion(): boolean {
  try {
    return typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches
  } catch {
    return false
  }
}

async function runInitialStagger() {
  if (prefersReducedMotion()) return
  await nextTick()
  const container = masonryRef.value
  if (!container) return
  const items = Array.from(container.querySelectorAll<HTMLElement>('.masonry-item'))
  if (!items.length) return

  // 先清理可能的旧动画
  gsap.killTweensOf(items)

  const tween = gsap.fromTo(
    items,
    { autoAlpha: 0, y: 16 },
    {
      autoAlpha: 1,
      y: 0,
      duration: 0.6,
      ease: 'power2.out',
      stagger: { each: 0.06, from: 'start' }
    }
  )
  cleanupFns.push(() => tween.kill())
}

function randomDelay() { return 6000 + Math.floor(Math.random() * 4000) }

async function rotateBatch() {
  if (paused.value || prefersReducedMotion()) return
  if (!posts.value.length) return
  const container = masonryRef.value
  if (!container) return
  const items = Array.from(container.querySelectorAll<HTMLElement>('.masonry-item'))
  if (!items.length) return

  // 选择一批（2-4个）
  const batchSize = Math.min(4, Math.max(2, Math.floor(Math.random() * 3) + 2))
  const targets = items.slice(0, Math.min(batchSize, items.length))

  // 淡出头部一批
  await new Promise<void>((resolve) => {
    gsap.to(targets, { autoAlpha: 0, y: 12, duration: 0.35, ease: 'power1.out', stagger: 0.04, onComplete: () => resolve() })
  })

  // 移动数据：头->尾
  const moved = posts.value.splice(0, Math.min(batchSize, posts.value.length))
  posts.value.push(...moved)
  await nextTick()

  // 对新尾部（刚移动的）执行淡入
  const itemsAfter = Array.from(container.querySelectorAll<HTMLElement>('.masonry-item'))
  const tailTargets = itemsAfter.slice(-moved.length)
  gsap.set(tailTargets, { autoAlpha: 0, y: 12 })
  gsap.to(tailTargets, { autoAlpha: 1, y: 0, duration: 0.4, ease: 'power2.out', stagger: 0.04 })
}

function scheduleNext() {
  if (rotationTimer) window.clearTimeout(rotationTimer)
  rotationTimer = window.setTimeout(async () => {
    try { await rotateBatch() } catch {}
    scheduleNext()
  }, randomDelay())
}

function onResume() {
  paused.value = false
  scheduleNext()
}

onMounted(async () => {
  try {
    posts.value = await dailyApi.getTrending(12)
    await runInitialStagger()
    startFpsWatch()
    scheduleNext()
  } catch (e) {
    console.error('加载trending失败', e)
  }
})

onUnmounted(() => {
  cleanupFns.forEach(fn => {
    try { fn() } catch {}
  })
  cleanupFns = []
  if (rotationTimer) window.clearTimeout(rotationTimer)
  rotationTimer = null
  stopFpsWatch()
})
</script>

<style scoped>
/* 中文注释：纯CSS Masonry（columns + break-inside） */
.daily-wall { padding: 24px 0; }
.header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; padding: 0 8px; }
.title { color: var(--text-primary, #fff); font-size: 18px; font-weight: 600; }
.more { background: transparent; color: var(--text-secondary, #bbb); border: 1px solid rgba(255,255,255,0.15); padding: 6px 12px; border-radius: 8px; cursor: pointer; }
.more:hover { color: var(--text-primary, #fff); border-color: rgba(255,255,255,0.3); }

.masonry { column-gap: 16px; }
@media (max-width: 640px) {
  .masonry { columns: 1; }
}
@media (min-width: 641px) and (max-width: 960px) {
  .masonry { columns: 2; }
}
@media (min-width: 961px) and (max-width: 1280px) {
  .masonry { columns: 3; }
}
@media (min-width: 1281px) and (max-width: 1600px) {
  .masonry { columns: 4; }
}
@media (min-width: 1601px) {
  .masonry { columns: 5; }
}
.masonry-item { break-inside: avoid; margin-bottom: 16px; display: block; }
</style>

