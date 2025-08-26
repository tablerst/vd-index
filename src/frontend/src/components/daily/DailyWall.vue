<template>
  <section class="daily-wall" ref="sectionRef">
    <!-- 顶部居中标题：应用 title-accent 渐变文本样式 -->


    <!-- 横向无缝循环弹幕轨道（上：最新评论右→左；下：仍保留卡片左→右） -->
    <div class="loop-container" ref="loopContainer" @mouseenter="pauseLoop()" @mouseleave="resumeLoop()">
      <!-- 顶部：弹幕评论（多行） -->
      <div class="loop-track loop-track--top danmaku-track" ref="trackTop">
        <div class="dan-row" v-for="(row, rIdx) in danmakuRows" :key="'row-' + rIdx">
          <DanmakuComment
            v-for="(c, i) in row"
            :key="`c-${rIdx}-${c.id}-${i}`"
            :comment="c"
            class="loop-item danmaku-item"
            :style="padStyle(rIdx, i, row.length)"
          />
        </div>
      </div>
      <!-- 底部：继续展示卡片（可后续也替换为弹幕） -->
      <div class="loop-track loop-track--bottom" ref="trackBottom">
        <DailyCard v-for="(p, i) in marqueePosts" :key="'bottom-' + p.id + '-' + i" :post="p" class="loop-item" />
      </div>
    </div>

    <!-- 底部居中“点击更多”按钮 + Gooey 融球引导效果 -->
    <div class="more-bar" ref="moreBarRef">
      <div class="gooey-container" ref="gooeyRef">
        <div class="blob-wrap" aria-hidden="true">
          <span class="blob blob-base"></span>
          <span class="blob blob-follow"></span>
          <span class="blob blob-pulse"></span>
        </div>
        <button class="gooey-label" @click="$router.push('/daily')">更多</button>
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
import { ref, onMounted, nextTick, onUnmounted, computed, watch } from 'vue'
import { dailyApi, type DailyPostItem, type DailyCommentItem } from '@/services/daily'
import DailyCard from './DailyCard.vue'
import DanmakuComment from './DanmakuComment.vue'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

// 全局平滑设置：大抖动时限制修正，避免卡顿传播
try { gsap.ticker.lagSmoothing(1000, 16) } catch { }

const recentComments = ref<DailyCommentItem[]>([])
// 中文注释：弹幕也需要双份以实现无缝（与卡片一致策略）；若不足则循环补齐
const marqueeComments = computed(() => {
  const base = recentComments.value
  if (!base.length) return []
  const MIN = 10
  const filled = base.length >= MIN ? base : Array.from({ length: MIN }, (_, i) => base[i % base.length])
  return [...filled, ...filled]
})

// 行数：根据屏幕宽度自适应（桌面3行，平板/移动2行）
const danmakuRowCount = ref(3)
function calcRowCount() {
  const w = typeof window !== 'undefined' ? window.innerWidth : 1280
  if (w >= 1280) return 3
  if (w >= 768) return 2
  return 2
}
danmakuRowCount.value = calcRowCount()

// Helpers for deterministic padding style used by template
function hashStr(s: string): number { let h = 5381; for (let i = 0; i < s.length; i++) h = ((h << 5) + h) + s.charCodeAt(i); return h >>> 0 }
function mulberry32(a: number) { return function () { let t = a += 0x6D2B79F5; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296 } }
function padStyle(rIdx: number, i: number, totalLen: number) {
  const baseLen = Math.max(1, (totalLen / 2) | 0)
  const baseIdx = i % baseLen
  const rng = mulberry32(hashStr(`${rIdx}:${baseLen}:${baseIdx}`))
  const pad = Math.round(8 + rng() * 28)
  return { '--pad': `${pad}px` }
}


// 将弹幕内容按行均匀分配；每行不足则复用补齐，并做双份复制以实现无缝
const danmakuRows = computed(() => {
  // 使用洗牌后的数据，确保复用时不显重复模式
  const shuffled = shuffle(marqueeComments.value)
  const base = shuffled
  const rows = danmakuRowCount.value
  if (!base.length || rows <= 0) return []

  // 每行至少需要的条数（估算值），不足复用
  const PER_MIN = 8
  const per = Math.max(PER_MIN, Math.ceil(base.length / rows))

  // 轮询分配到多行
  const tmp: DailyCommentItem[][] = Array.from({ length: rows }, () => [])
  base.slice(0, per * rows).forEach((item, idx) => {
    tmp[idx % rows].push(item)
  })
  // 补齐每行
  for (let r = 0; r < rows; r++) {
    const arr = tmp[r]
    let i = 0
    while (arr.length < per) {
      arr.push(base[i % base.length])
      i++
    }

  }
  // 每行再复制一份用于无缝
  return tmp.map(arr => [...arr, ...arr])
})

// 洗牌函数：Fisher-Yates，确保复用数据时打乱一次
function shuffle<T>(arr: T[]): T[] {
  const a = arr.slice()
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

const posts = ref<DailyPostItem[]>([])
const loopContainer = ref<HTMLElement | null>(null)
const sectionRef = ref<HTMLElement | null>(null)
const titleBarRef = ref<HTMLElement | null>(null)
const titleTextRef = ref<HTMLElement | null>(null)
const moreBarRef = ref<HTMLElement | null>(null)
const gooeyRef = ref<HTMLElement | null>(null)
const paused = ref(false)
// 中文注释：保证最少 12 条，若不足则循环复用后端返回的条目进行补齐；再复制一份以实现无缝滚动
const marqueePosts = computed(() => {
  const base = posts.value
  if (!base.length) return []
  const MIN = 12
  const filled = base.length >= MIN
    ? base
    : Array.from({ length: MIN }, (_, i) => base[i % base.length])
  // 返回双份内容：上/下两条轨道动画按 scrollWidth/2 计算，要求内容成对
  return [...filled, ...filled]
})

// 针对单行弹幕的无缝跑马灯动画（ModifiersPlugin 包裹，实现真正无缝）
function buildRowMarquee(row: HTMLElement, { speed = 120 }: { speed?: number }) {
  const W = row.scrollWidth / 2 // 单份内容宽度（我们已对每行做了双份）
  const start = -Math.random() * W // 随机起点，避免行间对齐
  const dur = Math.max(W / (speed || 120), 6)
  gsap.set(row, { x: start, force3D: true })
  return gsap.to(row, {
    x: start - W, // 每周期左移一个 W
    duration: dur,
    ease: 'none',
    repeat: -1,
    force3D: true,
    onRepeat: () => { gsap.set(row, { x: start, force3D: true }) }
  })
}

const trackTop = ref<HTMLElement | null>(null)
const trackBottom = ref<HTMLElement | null>(null)

let tlTop: gsap.core.Tween | null = null
let tlBottom: gsap.core.Tween | null = null
// 为顶部多行弹幕分别创建不同速度的无缝动画
function rebuildDanmakuRows() {
  if (!trackTop.value) return
  // 清理旧动画
  tlTop?.kill(); tlTop = null
  // 为每一行分别构建动画
  const rows = trackTop.value.querySelectorAll<HTMLElement>('.dan-row')
  const tweens: gsap.core.Tween[] = []
  rows.forEach((row, idx) => {
    // 行间速度差异：基准 110 + idx*12，制造不对齐效果
    const speed = 110 + (idx % 3) * 12
    const t = buildRowMarquee(row, { speed })
    tweens.push(t)
  })
  // 记录第一个 tween，后续统一暂停/恢复
  tlTop = tweens[0] || null
}

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
  // 顶部：为每一行分别创建无缝且不等速动画
  rebuildDanmakuRows()
  // 底部：卡片保留原跑马灯（也改为无缝modifiers以优化）
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
    // 自适应行数重算
    danmakuRowCount.value = calcRowCount()
    // 重建无缝动画
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
  // 中文注释：构建液态圆形融球按钮的交互逻辑（52px 主圆 + 鼠标追踪 + 悬停融合 + 离开复位）
  const wrap = gooeyRef.value
  if (!wrap) return
  const base = wrap.querySelector('.blob-base') as HTMLElement | null
  const follow = wrap.querySelector('.blob-follow') as HTMLElement | null
  const pulse = wrap.querySelector('.blob-pulse') as HTMLElement | null
  const label = wrap.querySelector('.gooey-label') as HTMLElement | null
  if (!base || !follow || !label) return

  // 初始化 transform 原点与初始缩放
  gsap.set([base, follow, pulse], { transformOrigin: '50% 50% 0.1px' })
  gsap.set(follow, { scale: 0.9 })

  // 轻微的 label 交互反馈（不改变布局）
  label.addEventListener('mouseenter', () => {
    gsap.to(label, { duration: 0.2, scale: 1.02, ease: 'power2.out' })
  })
  label.addEventListener('mouseleave', () => {
    gsap.to(label, { duration: 0.2, scale: 1.0, ease: 'power2.out' })
  })
  label.addEventListener('mousedown', () => {
    gsap.to(label, { duration: 0.12, scale: 0.97, y: 1, ease: 'power2.out' })
  })
  label.addEventListener('mouseup', () => {
    gsap.to(label, { duration: 0.18, scale: 1.02, y: 0, ease: 'power2.out' })
  })
  // 同步代理 mousemove 到 wrap 以提升在子元素上的响应
  label.addEventListener('mousemove', (e) => onMove(e as MouseEvent))

  if (prefersReducedMotion()) return

  // 基础呼吸动画：主圆轻微呼吸，pulse 轻微往返移动
  const breath = gsap.timeline({ repeat: -1, yoyo: true })
  breath.to(base, { scale: 1.02, duration: 1.6, ease: 'sine.inOut' })
        .to(base, { scale: 0.98, duration: 1.6, ease: 'sine.inOut' }, 0)
  if (pulse) {
    gsap.to(pulse, { x: 7, y: -7, duration: 2.0, ease: 'sine.inOut', repeat: -1, yoyo: true })
  }

  // 添加细微的随机波动（小波浪扰动）
  const noise = () => (Math.random() * 2 - 1) // [-1,1]
  const jitter = () => {
    gsap.to(base, {
      x: noise() * 1.2,
      y: noise() * 1.2,
      duration: 0.8 + Math.random() * 0.6,
      ease: 'sine.inOut',
      onComplete: jitter
    })
  }
  jitter()

  // 鼠标追踪 & 悬停融合
  const R = 24 // 60px 主圆对应更大的跟随半径
  const threshold = 0.18 // 悬停融合阈值（相对容器的归一化距离）

  const onMove = (e: MouseEvent) => {
    const rect = wrap.getBoundingClientRect()
    const cx = rect.left + rect.width / 2
    const cy = rect.top + rect.height / 2

    // 使用像素坐标计算向量，便于做半径限制
    const dx = e.clientX - cx
    const dy = e.clientY - cy
    const len = Math.hypot(dx, dy)

    // 归一化距离用于融合阈值判断（不改变现有手感）
    const nx = dx / rect.width
    const ny = dy / rect.height
    const dist = Math.hypot(nx, ny)

    // 计算最大位移：主圆半径 + 10px - 跟随圆半径，并与 R 取较小值以兼容旧配置
    const mainRadius = (base as HTMLElement).offsetWidth / 2
    const followRadius = (follow as HTMLElement).offsetWidth / 2
    const clampR = Math.max(0, mainRadius + 10 - followRadius) // px
    const maxLen = Math.min(R, clampR)

    // 将向量限制在允许半径内
    let tx = dx, ty = dy
    if (len > maxLen && len > 0) {
      const k = maxLen / len
      tx = dx * k
      ty = dy * k
    }

    gsap.to(follow, { x: tx, y: ty, duration: 0.25, ease: 'sine.out' })

    if (dist < threshold) {
      gsap.to(follow, { x: 0, y: 0, scale: 0.82, duration: 0.3, ease: 'sine.out' })
      gsap.to(base, { scale: 1.04, duration: 0.3, ease: 'sine.out' })
    } else {
      gsap.to(follow, { scale: 1, duration: 0.3, ease: 'sine.out' })
      gsap.to(base, { scale: 1, duration: 0.35, ease: 'sine.out' })
    }
  }

  const onEnter = () => {
    gsap.to(base, { scale: 1.03, duration: 0.25, ease: 'power2.out' })
  }
  const onLeave = () => {
    gsap.to([follow], { x: 0, y: 0, scale: 0.9, duration: 0.25, ease: 'sine.out' })
    gsap.to(base, { scale: 1.0, duration: 0.3, ease: 'sine.out' })
  }

  // 在可视区域内全局响应鼠标移动：使用 IntersectionObserver 开关监听
  let listenWin = false
  const io = new IntersectionObserver((entries) => {
    const visible = entries.some(e => e.isIntersecting)
    if (visible && !listenWin) {
      window.addEventListener('mousemove', onMove)
      listenWin = true
    } else if (!visible && listenWin) {
      window.removeEventListener('mousemove', onMove)
      listenWin = false
    }
  }, { root: null, threshold: 0.1 })
  io.observe(wrap)

  wrap.addEventListener('mouseenter', onEnter)
  wrap.addEventListener('mouseleave', onLeave)

  onUnmounted(() => {
    window.removeEventListener('mousemove', onMove)
    wrap.removeEventListener('mouseenter', onEnter)
    wrap.removeEventListener('mouseleave', onLeave)
    io.disconnect()
  })
}


onMounted(async () => {
  try {
    // 同时加载首页卡片与最新评论（20条）
    const [postsData, commentsData] = await Promise.all([
      dailyApi.getTrending(12),
      dailyApi.getRecentComments(20)
    ])
    posts.value = postsData
    recentComments.value = commentsData
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
    console.error('加载trending/最新评论失败', e)
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

/* 顶部弹幕轨道由多行组成：每行横向排列 */
.loop-track {
  display: flex;
  gap: 16px;
  will-change: transform;
  padding: 0 8px;
  backface-visibility: hidden;
}
.danmaku-track { flex-direction: column; gap: 10px; }
.danmaku-track .dan-row { display: flex; gap: 16px; align-items: center; }
.danmaku-track .danmaku-item { padding-right: var(--pad, 0px); }

.loop-item {
  flex: 0 0 auto;
  /* 缩小卡片尺寸以留出底部按钮空间 */
  width: min(260px, 22vw);
  margin-block: 8px;
}
/* 顶部弹幕项可以更宽 */
.danmaku-track .danmaku-item { width: auto; }

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
  width: 60px; /* 主圆直径 60px */
  height: 60px;
}
.gooey-container .blob-wrap { position: absolute; inset: 0; filter: url(#gooey-soft); isolation: isolate; z-index: 0; pointer-events: none; }

/* 主圆与小圆：仅使用 transform 改变位置/缩放；颜色使用主题变量渐变 */
.blob {
  position: absolute;
  inset: 0;
  margin: auto;
  border-radius: 50%;
  pointer-events: none;
  will-change: transform;
}
.blob-base {
  width: 60px; height: 60px;
  background: radial-gradient(circle at 30% 30%, color-mix(in srgb, var(--primary) 85%, transparent), transparent 60%),
              radial-gradient(circle at 70% 70%, color-mix(in srgb, var(--accent-blue) 65%, transparent), transparent 70%);
}
.blob-follow { width: 32px; height: 32px; background: color-mix(in srgb, var(--primary) 60%, var(--accent-blue) 40%); }
.blob-pulse   { width: 21px; height: 21px; background: color-mix(in srgb, var(--accent-blue) 70%, transparent); }

/* 文本按钮层：不套 gooey 滤镜，保证清晰 */
.gooey-label {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%; height: 100%;
  border: none;
  background: transparent;
  color: #fff; /* 固定白色，提高在浅色背景下的可见性 */
  text-shadow: 0 1px 2px rgba(0,0,0,.25);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  border-radius: 50%;
  outline: none;
  transition: transform .15s ease;
}
.gooey-label:focus-visible { box-shadow: 0 0 0 2px color-mix(in srgb, var(--primary) 60%, transparent); }


/* 兼容旧类名，清理矩形按钮视觉（保留无样式影响） */
.more-btn { display: none; }

@media (max-width: 640px) { .loop-item { width: 68vw; } }
:deep(.daily-card) .cover { aspect-ratio: 4 / 3; }
</style>



