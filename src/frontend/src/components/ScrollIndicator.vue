<template>
  <div class="scroll-indicator" :class="{ 'scroll-indicator--visible': visible, 'scroll-indicator--collapsed': collapsed }" ref="rootRef">
    <!-- 进度条 + 分屏点（叠加组合） -->
    <div class="progress-combo" :class="{ 'progress-combo--collapsed': collapsed }" ref="comboRef">
      <div class="progress-track" ref="trackRef">
        <div class="progress-mask">
          <div class="progress-fill" ref="fillRef"></div>
        </div>
      </div>
    </div>



    <!-- 滚动提示 / 回到顶部（集成） -->
    <div class="scroll-hint" v-if="showHint && currentSection === 0">
      <div class="hint-icon">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <path
            d="M10 3V17M3 10L17 10"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
          />
        </svg>
      </div>
      <span class="hint-text" style="color: var(--text-secondary)">滚动探索</span>
    </div>
    <div v-else class="back-to-top-wrap">      
      <button
        class="back-to-top-mini"
        :data-index="`${currentSection + 1}/${sections.length}`"
        @click.stop="$emit('goToSection', 0)"
        :aria-label="`回到顶部，当前 ${currentSection + 1}/${sections.length}`"
      >
        <svg class="icon" width="16" height="16" viewBox="0 0 20 20" fill="none">
          <path d="M10 15L10 5M5 10L10 5L15 10" stroke="var(--text-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">

import type { SnapScrollSection } from '@/composables/useSnapScroll'

interface Props {
  currentSection: number
  sections: SnapScrollSection[]
  progress: number
  visible?: boolean
  showHint?: boolean
  isMobileProgressBarDisabled?: boolean
}

interface Emits {
  (e: 'goToSection', index: number): void
}

const props = withDefaults(defineProps<Props>(), {
  visible: true,
  showHint: false,
  isMobileProgressBarDisabled: false
})

defineEmits<Emits>()

// 获取section标签
const getSectionLabel = (index: number) => {
  const labels = ['首页', '成员', '活动']
  return labels[index] || `第${index + 1}屏`
}
import { ref, watch, onMounted, onUnmounted, computed } from 'vue'
import { gsap } from 'gsap'

// 折叠状态：切换分屏后短暂展开进度，再折叠为mini
const collapsed = ref(false)
let collapseTimer: number | null = null
const rootRef = ref<HTMLElement | null>(null)
const comboRef = ref<HTMLElement | null>(null)
const maskRef = ref<HTMLElement | null>(null)
const fillRef = ref<HTMLElement | null>(null)

// 展示用进度：基于当前分屏与总分屏（0 顶部 → 1 底部），避免 props.progress 与视觉方向不一致
const viewProgress = computed(() => {
  // 与右下角回顶计数保持一致：直接使用 useSnapScroll 提供的 progress（0→1）
  const p = typeof props.progress === 'number' ? props.progress : 0
  return Math.min(1, Math.max(0, p))
})

// 使用 GSAP 实现优雅的折叠/展开动画（包含高度动画，带动外框收缩）
const animateCombo = (isCollapsed: boolean) => {
  const el = comboRef.value
  if (!el) return
  const prefersReduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches
  const _gsap: any = (gsap as any)

  // 读自然高度
  const naturalHeight = el.scrollHeight

  if (!(_gsap && typeof _gsap.to === 'function') || prefersReduced) {
    // 降级：直接设置样式
    if (isCollapsed) {
      el.style.height = '0px'
      el.style.opacity = '0'
      el.style.transform = 'translateY(6px) scale(0.96)'
    } else {
      el.style.height = 'auto'
      el.style.opacity = '1'
      el.style.transform = 'translateY(0) scale(1)'
    }
    return
  }

  _gsap.killTweensOf(el)
  if (isCollapsed) {
    _gsap.fromTo(el,
      { height: naturalHeight, opacity: 1, y: 0, scale: 1 },
      { duration: 0.45, height: 0, opacity: 0, y: 6, scale: 0.96, ease: 'power2.out', onComplete: () => {
        el.style.height = '0px'
      }}
    )
  } else {
    // 展开：先设为 auto 读取高度，再从 0 撑开
    el.style.height = 'auto'
    const targetHeight = el.scrollHeight || naturalHeight
    _gsap.fromTo(el,
      { height: 0, opacity: 0, y: 6, scale: 0.96 },
      { duration: 0.5, height: targetHeight, opacity: 1, y: 0, scale: 1, ease: 'power2.out', onComplete: () => {
        el.style.height = 'auto'
      }}
    )
  }
}

watch(() => props.currentSection, () => {
  // 新屏进入：展开展示 2.8s
  collapsed.value = false
  animateCombo(false)
  if (collapseTimer) window.clearTimeout(collapseTimer)
  collapseTimer = window.setTimeout(() => {
    collapsed.value = true
    animateCombo(true)
  }, 2800)
})

onMounted(() => {
  // 初始时设置一次填充高度
  animateFill(viewProgress.value)
  // 初始时 1.6s 后折叠
  animateCombo(false)
  collapseTimer = window.setTimeout(() => {
    collapsed.value = true
    animateCombo(true)
  }, 1600)
})

onUnmounted(() => {
  if (collapseTimer) {
    window.clearTimeout(collapseTimer)
    collapseTimer = null
  }
})
// 进度填充动画：在 progress 变化时用 GSAP 平滑过渡
const animateFill = (val: number) => {
  const el = fillRef.value
  if (!el) return
  const prefersReduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches
  const _gsap: any = (gsap as any)
  const pct = Math.min(1, Math.max(0, val)) * 100
  if (prefersReduced || !(_gsap && typeof _gsap.to === 'function')) {
    el.style.height = pct + '%'
    return
  }
  _gsap.to(el, { duration: 0.45, height: pct + '%', ease: 'power2.out' })
}

watch(viewProgress, (val) => {
  animateFill(val)
}, { immediate: true })

watch(() => collapsed.value, (val) => {
  animateCombo(val)
})

</script>

<style scoped lang="scss">
@use '../styles/variables.scss' as *;

.scroll-indicator {
  /* 改为右下角“微型栈式”布局，避开中部分页箭头 */
  --indicator-track-width: 6px;
  position: fixed !important;
  right: var(--spacing-xl) !important;

/* 组合容器：叠加进度条与分屏点，更紧凑（GSAP 控制 opacity/transform）*/
.progress-combo {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-sm);
  will-change: transform, opacity;
  overflow: hidden;
}

.progress-combo--collapsed {
  opacity: 0;
  transform: translateY(6px) scale(0.96);
  pointer-events: none;
  overflow: hidden;
}

/* 折叠时暂停闪光动画，避免无意义渲染 */
.progress-combo--collapsed .progress-fill::after {
  animation: none !important;
}

  /* 预留给回到顶部/性能开关的安全距离（约 96~112px） */
  bottom: 72px !important;
  transform: translateY(12px) !important; /* 出场上移动画 */
  z-index: 80 !important; /* 提升层级，确保在页脚区域也可见 */
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-sm);
  opacity: 0;
  visibility: hidden;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  /* 使用主题化玻璃态变量，提升亮色主题可读性 */
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border: 1px solid var(--glass-border);
  padding: var(--spacing-sm) var(--spacing-sm);
  border-radius: var(--radius-lg);

  &--visible {
    opacity: 1;
    visibility: visible;
    transform: translateY(0) translateX(0);
  }

  @include media-down(md) {
    --indicator-track-width: 6px;
    right: var(--spacing-lg) !important;
    bottom: 80px !important; /* 移动端更紧凑 */
    gap: var(--spacing-sm);
    padding: var(--spacing-sm);
  }
}

.progress-track {
  width: var(--indicator-track-width);
  height: 140px;
  background: rgba(255,255,255,0.16); /* 统一明度，等宽视觉 */
  border-radius: calc(var(--indicator-track-width) / 2);
  position: relative;
  overflow: visible; /* 允许节点环外溢 */
  box-shadow: inset 0 0 0 1px rgba(0,0,0,0.35);
  z-index: 0;

  @include media-down(md) {
    height: 100px;
    width: var(--indicator-track-width);
  }
}

/* 新增：仅对填充区域进行裁剪，避免节点被截断 */
.progress-mask {
  position: absolute;
  inset: 0;
  overflow: hidden; /* 只裁剪填充，不裁剪节点 */
  border-radius: calc(var(--indicator-track-width) / 2);
  /* 用精确数值避免 50% 造成“圆锥形” */
  border-radius: calc(var(--indicator-track-width) / 2); /* 用圆角 mask 形成两端圆滑 */
  z-index: 1;
}

.progress-fill {
  position: absolute;
  top: 0; /* 从上往下填充：第二屏时上方更多 */
  left: 0;
  width: 100%;
  height: 100%;
  background: var(--primary);
  /* 末端为圆形：只给底部两个角设置半径，形成半圆端盖 */
  border-bottom-left-radius: calc(var(--indicator-track-width) / 2);
  border-bottom-right-radius: calc(var(--indicator-track-width) / 2);
  border-top-left-radius: 0;
  border-top-right-radius: 0;
  height: 0%; /* 使用高度动画，避免缩放带来的视觉畸变 */
  will-change: height;
  box-shadow: none;
  position: relative;
  z-index: 1;

  /* 纵向闪光（从上向下） */
  &::after {
    content: '';
    position: absolute;
    left: 0;
    bottom: 0;
    top: auto;
    width: 100%;
    height: 34px;
    /* 更强的高光，锚定在最新填充的末端，末端圆滑 */
    background: linear-gradient(to top, rgba(255,255,255,0.78), rgba(255,255,255,0));
    border-bottom-left-radius: calc(var(--indicator-track-width) / 2);
    border-bottom-right-radius: calc(var(--indicator-track-width) / 2);
    border-top-left-radius: 0;
    border-top-right-radius: 0;
    transform-origin: bottom center;
    animation: trailingShine 0.8s cubic-bezier(.2,.6,.2,1) infinite;
    pointer-events: none;
    mix-blend-mode: screen;
  }
}



.scroll-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-xs);
  margin-top: var(--spacing-md);
  color: var(--text-secondary);
  animation: pulse 2s ease-in-out infinite;

  @include media-down(md) {
    margin-top: var(--spacing-sm);
  }
}

.hint-icon {
  width: 20px;
  height: 20px;
  display: flex;
/* 回顶按钮上方的计数器 */
.back-to-top-wrap { display:flex; flex-direction:column; align-items:center; gap:6px; }
.progress-counter {
  padding: 2px 6px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 999px;
  backdrop-filter: blur(10px);
}

  align-items: center;
  justify-content: center;

  svg { width: 100%; height: 100%; }

  @include media-down(md) {
    width: 16px;
    height: 16px;
  }
}

/* 右下角的迷你回顶按钮（与指示器集成） */
.back-to-top-mini {
  position: relative;
  z-index: 2;
  pointer-events: auto;
  width: 32px;
  height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-full);
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border: 1px solid var(--glass-border);
  color: var(--text-primary);
  transition: all var(--transition-base) var(--ease-hover);
  cursor: pointer;
  animation: breathe 2.4s ease-in-out infinite;

  svg { color: var(--text-primary); }

  /* 兜底：如果 SVG 内 path/stroke 未继承 color，强制覆盖为文本主色 */
  & .icon, & .icon path {
    color: var(--text-primary) !important;
    stroke: var(--text-primary) !important;
  }

  &::after {
    content: attr(data-index);
    position: absolute;
    bottom: -10px;
    right: -10px;
    min-width: 18px;
    height: 18px;
    padding: 0 4px;
    border-radius: 10px;
    background: var(--primary);
    color: var(--text-inverse); /* 遵循主题的反色文本 */
    font-size: 10px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  &:hover {
    box-shadow: var(--shadow-glow);
    transform: translateY(-2px);
  }

  @include media-down(md) {
    width: 28px;
    height: 28px;
  }
}

@keyframes breathe {
  0%, 100% { box-shadow: 0 0 0 0 rgba(170, 131, 255, 0.25); }
  50% { box-shadow: 0 0 0 8px rgba(170, 131, 255, 0.0); }
}

.hint-text {
  font-size: var(--font-size-xs);
  font-weight: 400;
  writing-mode: vertical-rl;
  text-orientation: mixed;

  @include media-down(md) {
    font-size: 10px;
  }
}

@keyframes pulse {
  0%, 100% { opacity: 0.6; transform: translateY(0); }
  50% { opacity: 1; transform: translateY(-2px); }
}

@keyframes trailingShine {
  0% { transform: translateY(-10px) scaleY(0.92); opacity: .85; }
  60% { transform: translateY(0) scaleY(1); opacity: 1; }
  100% { transform: translateY(10px) scaleY(0.96); opacity: 0; }
}

/* 主题统一改用 CSS 变量，无需额外的 light 覆盖 */

// 性能优化
.scroll-indicator {
  will-change: opacity, visibility;

  .progress-fill {
    will-change: transform;
  }

  .section-dot {
    will-change: transform;
  }
}

// 可访问性
@media (prefers-reduced-motion: reduce) {
  .scroll-indicator {
    .progress-fill,
    .section-dot,
    .dot-label {
      transition-duration: 0.1s;
    }

    .scroll-hint {
      animation: none;
    }
  }
}
</style>
