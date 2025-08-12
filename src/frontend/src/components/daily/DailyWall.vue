<template>
  <section class="daily-wall" ref="sectionRef">
    <!-- 顶部居中标题：应用 title-accent 渐变文本样式 -->
    <div class="title-bar" ref="titleBarRef">
      <h3 class="title section-title"><span class="title-accent" ref="titleTextRef">群员日常</span></h3>
    </div>

    <!-- 横向无缝循环滚动轨道（双轨道：上-右→左，下-左→右） -->
    <div class="loop-container" ref="loopContainer" @mouseenter="pauseLoop()" @mouseleave="resumeLoop()">
      <div class="loop-track loop-track--top" ref="trackTop">
        <DailyCard v-for="(p, i) in marqueePosts" :key="'top-' + p.id + '-' + i" :post="p" class="loop-item" />
      </div>
      <div class="loop-track loop-track--bottom" ref="trackBottom">
        <DailyCard v-for="(p, i) in marqueePosts" :key="'bottom-' + p.id + '-' + i" :post="p" class="loop-item" />
      </div>
    </div>

    <!-- 底部居中“点击更多”按钮 + Gooey 融球引导效果 -->
    <div class="more-bar" ref="moreBarRef">
      <div class="gooey-container" ref="gooeyRef">
        <button class="more-btn" @click="$router.push('/daily')">点击更多</button>
        <span class="blob blob-1"></span>
        <span class="blob blob-2"></span>
      </div>
    </div>

    <!-- SVG 滤镜：柔和 Gooey 融合效果（性能友好，stdDeviation 控制强度） -->
    <svg class="visually-hidden" width="0" height="0" aria-hidden="true" focusable="false">
      <defs>
        <filter id="gooey-soft">
          <feGaussianBlur in="SourceGraphic" stdDeviation="6" result="blur" />
          <feColorMatrix in="blur" mode="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 18 -7" result="goo" />
          <feBlend in="SourceGraphic" in2="goo" />
        </filter>
      </defs>
    </svg>
  </section>
</template>

<script setup lang="ts">
// 中文注释：DailyWall - 顶部居中标题 + 底部按钮 + GSAP 无缝横向循环；采用 gsap.context 管理、onRepeat 重置、可见性暂停
import { ref, onMounted, nextTick, onUnmounted, computed } from 'vue'
import { dailyApi, type DailyPostItem } from '@/services/daily'
import DailyCard from './DailyCard.vue'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

// 全局平滑设置：大抖动时限制修正，避免卡顿传播
try { gsap.ticker.lagSmoothing(1000, 16) } catch { }

const posts = ref<DailyPostItem[]>([])
const loopContainer = ref<HTMLElement | null>(null)
const sectionRef = ref<HTMLElement | null>(null)
const titleBarRef = ref<HTMLElement | null>(null)
const titleTextRef = ref<HTMLElement | null>(null)
const moreBarRef = ref<HTMLElement | null>(null)
const gooeyRef = ref<HTMLElement | null>(null)
const paused = ref(false)
const marqueePosts = computed(() => posts.value.length ? [...posts.value, ...posts.value] : [])
const trackTop = ref<HTMLElement | null>(null)
const trackBottom = ref<HTMLElement | null>(null)

let tlTop: gsap.core.Tween | null = null
let tlBottom: gsap.core.Tween | null = null
let resizeTimer: number | null = null
let ctx: gsap.Context | null = null

function prefersReducedMotion(): boolean {
  try {
    return typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches
  } catch { return false }
}

// 构建单条轨道的无缝跑马灯动画（双份内容 + 轨道平移 + onRepeat 重置，避免每帧 modifiers 计算）
function buildMarquee(track: HTMLElement, { dir = 'left', speed = 120 }: { dir?: 'left' | 'right', speed?: number }) {
  const W = track.scrollWidth / 2 // 单份内容宽度
  const from = dir === 'left' ? 0 : -W
  const to = dir === 'left' ? -W : 0
  const dur = Math.max(W / (speed || 120), 6)
  gsap.set(track, { x: from, force3D: true }) // 先设置起始位置，确保右向轨道正常运动
  return gsap.to(track, {
    x: to,
    duration: dur,
    ease: 'none',
    repeat: -1,
    force3D: true,
    onRepeat: () => { gsap.set(track, { x: from, force3D: true }) }
  })
}

function rebuildMarquees() {
  if (prefersReducedMotion()) return
  // 先清理旧动画
  tlTop?.kill(); tlTop = null
  tlBottom?.kill(); tlBottom = null
  // 重新计算并创建
  if (trackTop.value) tlTop = buildMarquee(trackTop.value, { dir: 'left', speed: 120 })
  if (trackBottom.value) tlBottom = buildMarquee(trackBottom.value, { dir: 'right', speed: 90 })
}

// 悬停控制（两条轨同时暂停/恢复）
function pauseLoop() {
  paused.value = true
  tlTop?.pause(); tlBottom?.pause()
}
function resumeLoop() {
  paused.value = false
  tlTop?.resume(); tlBottom?.resume()
}

function handleResize() {
  if (resizeTimer) window.clearTimeout(resizeTimer)
  resizeTimer = window.setTimeout(() => {
    rebuildMarquees()
  }, 150)
}

// 进入视差/下移动画，参考 MembersCircle 的进入节奏（放入 gsap.context 以统一管理）
function setupEnterAnimations() {
  if (!sectionRef.value) return

  gsap.context(() => {
    // 整体区块淡入+下移
    gsap.fromTo(sectionRef.value!,
      { opacity: 0, y: 60, scale: 0.98 },
      {
        opacity: 1,
        y: 0,
        scale: 1,
        duration: 0.9,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: sectionRef.value!,
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
            trigger: sectionRef.value!,
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
            trigger: sectionRef.value!,
            start: 'top 70%',
            end: 'top 30%',
            toggleActions: 'play none none reverse'
          }
        }
      )
    }
  }, sectionRef)
}

// 页面可见性：隐藏页签/切走时暂停动画，返回时恢复
function setupVisibilityPause() {
  const handler = () => {
    const hidden = document.hidden
    if (hidden) { tlTop?.pause(); tlBottom?.pause() }
    else if (!paused.value) { tlTop?.resume(); tlBottom?.resume() }
  }
  document.addEventListener('visibilitychange', handler)
  return () => document.removeEventListener('visibilitychange', handler)
}

// 标题入场与字符微动效（reduced-motion 下仅淡入）
function setupTitleAnimation() {
  if (!titleTextRef.value) return
  const text = titleTextRef.value
  if (prefersReducedMotion()) {
    gsap.set(text, { opacity: 0, y: 8 })
    gsap.to(text, { opacity: 1, y: 0, duration: 0.6, ease: 'power2.out' })
    return
  }
  // 字符拆分（非重排，仅包裹 span）
  const content = text.textContent || ''
  text.textContent = ''
  const frag = document.createDocumentFragment()
  for (const ch of content) {
    const s = document.createElement('span')
    s.textContent = ch
    s.className = 'char'
    frag.appendChild(s)
  }
  text.appendChild(frag)
  const chars = text.querySelectorAll('.char')
  gsap.set(chars, { opacity: 0, y: 10 })
  gsap.to(chars, { opacity: 1, y: 0, duration: 0.7, ease: 'power3.out', stagger: 0.03 })
}

// 按钮 Gooey 融球引导与 hover 柔光（reduced-motion 下只保留轻微淡入）
function setupButtonAnimations() {
  const wrap = gooeyRef.value
  if (!wrap) return
  const btn = wrap.querySelector('.more-btn') as HTMLElement | null
  const blobs = wrap.querySelectorAll('.blob') as NodeListOf<HTMLElement>
  if (!btn) return

  // hover 柔光（无强烈外发光）
  btn.addEventListener('mouseenter', () => {
    gsap.to(btn, { duration: 0.2, scale: 1.02, boxShadow: '0 0 12px var(--primary-light)', ease: 'power2.out' })
  })
  btn.addEventListener('mouseleave', () => {
    gsap.to(btn, { duration: 0.2, scale: 1.0, boxShadow: 'none', ease: 'power2.out' })
  })
  btn.addEventListener('mousedown', () => {
    gsap.to(btn, { duration: 0.12, scale: 0.98, y: 1, ease: 'power2.out' })
  })
  btn.addEventListener('mouseup', () => {
    gsap.to(btn, { duration: 0.18, scale: 1.02, y: 0, ease: 'power2.out' })
  })

  if (prefersReducedMotion()) return

  // Gooey 融球与方向引导：两个小球跟随鼠标方向轻微偏移（transform-only）
  const onMove = (e: MouseEvent) => {
    const rect = wrap.getBoundingClientRect()
    const cx = rect.left + rect.width / 2
    const cy = rect.top + rect.height / 2
    const dx = (e.clientX - cx) / rect.width
    const dy = (e.clientY - cy) / rect.height
    gsap.to(blobs[0], { x: dx * 18, y: dy * 18, duration: 0.3, ease: 'sine.out' })
    gsap.to(blobs[1], { x: -dx * 16, y: -dy * 16, duration: 0.35, ease: 'sine.out' })
  }
  wrap.addEventListener('mousemove', onMove)

  onUnmounted(() => { wrap.removeEventListener('mousemove', onMove) })
}


onMounted(async () => {
  try {
    posts.value = await dailyApi.getTrending(12)
    await nextTick()

    // 使用 gsap.context 管理本组件内的所有动画/ScrollTrigger
    ctx = gsap.context(() => {
      rebuildMarquees()
      setupEnterAnimations()
      setupTitleAnimation()
      setupButtonAnimations()
    }, sectionRef)


    window.addEventListener('resize', handleResize)
    var removeVisibility = setupVisibilityPause()

    // 在卸载时通过 ctx.revert() 清理，附带额外清理器
    onUnmounted(() => { removeVisibility() })
  } catch (e) {
    console.error('加载trending失败', e)
  }
})

onUnmounted(() => {
  tlTop?.kill(); tlTop = null
  tlBottom?.kill(); tlBottom = null
  if (resizeTimer) window.clearTimeout(resizeTimer)
  window.removeEventListener('resize', handleResize)
  ctx?.revert(); ctx = null
})
</script>

<style scoped>
/* 中文注释：DailyWall 样式：顶部标题+底部按钮+横向循环轨道。所有颜色使用主题变量；增加合成层优化与标题/按钮装饰 */
.daily-wall {
  position: relative;
  padding: 72px 0 64px;
  contain: content;
}

.title-bar {
  position: sticky;
  top: 48px;
  display: flex;
  justify-content: center;
  z-index: 2;
  pointer-events: none;
}

.title.section-title {
  font-size: var(--font-size-2xl, 22px);
  font-weight: 800;
  letter-spacing: 0.6px;
}

.title-accent {
  background: var(--mixed-gradient);
  /* 参考 starCalendar 的 title-accent 实现 */
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: var(--shadow-glow);
}

.loop-container {
  position: relative;
  overflow: hidden;
  width: 100%;
  padding: 24px 8px;
  display: grid;
  row-gap: 16px;
  will-change: transform;
}

.loop-track {
  display: flex;
  gap: 16px;
  will-change: transform;
  padding: 0 8px;
  backface-visibility: hidden;
}

.loop-item {
  flex: 0 0 auto;
  width: min(300px, 26vw);
  margin-block: 8px;
}

.more-bar {
  position: sticky;
  bottom: 12px;
  display: flex;
  justify-content: center;
  margin-top: 8px;
  z-index: 2;
}

.gooey-container {
  position: relative;
  filter: url(#gooey-soft);
  isolation: isolate;
}

.more-btn {
  appearance: none;
  background: var(--glass-bg);
  color: var(--text-secondary);
  border: var(--border-glass);
  border-radius: 12px;
  padding: 10px 16px;
  cursor: pointer;
  transition: background .2s ease, color .2s ease, box-shadow .2s ease, border-color .2s ease, transform .1s ease;
}

.more-btn:hover {
  color: var(--text-primary);
  border-color: var(--primary);
  box-shadow: var(--shadow-glow); }
.more-btn:active { transform: translateY(1px) scale(0.98); }

/* Gooey blobs：柔和引导球体 */
.blob { position: absolute; inset: 0; margin: auto; width: 40px; height: 40px; border-radius: 50%; pointer-events: none; mix-blend-mode: screen; opacity: 0.5; will-change: transform; }
.blob-1 { background: radial-gradient(circle at 30% 30%, color-mix(in srgb, var(--primary) 70%, transparent), transparent); filter: blur(2px); }
.blob-2 { background: radial-gradient(circle at 70% 70%, color-mix(in srgb, var(--accent-blue) 70%, transparent), transparent); filter: blur(2px); }

@media (max-width: 640px) { .loop-item { width: 78vw; } }
:deep(.daily-card) .cover { aspect-ratio: 4 / 3; }
</style>



