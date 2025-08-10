<template>
  <div
    class="galaxy-info-widget"
    :class="{
      'galaxy-info-widget--expanded': isExpanded,
      'galaxy-info-widget--mobile': deviceInfo.isMobile
    }"
  >
      <!-- 主按钮 -->
      <button
        ref="triggerButton"
        class="info-trigger"
        :class="{ 'info-trigger--expanded': isExpanded }"
        @click="toggleExpanded"
        @keydown.escape="collapse"
        @keydown.enter="toggleExpanded"
        @keydown.space.prevent="toggleExpanded"
        @touchstart="handleTouchStart"
        @touchend="handleTouchEnd"
        :aria-expanded="isExpanded"
        :aria-label="isExpanded ? '收起信息面板' : '展开信息面板'"
        :aria-describedby="isExpanded ? 'info-panel-content' : undefined"
        role="button"
        tabindex="0"
      >
        <!-- 成员数量指示器 -->
        <div class="member-count">
          <span class="count-number">{{ totalMembers }}</span>
          <span class="count-label">成员</span>
        </div>
        
        <!-- 展开/收起图标 -->
        <div class="expand-icon" :class="{ 'expand-icon--rotated': isExpanded }">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path 
              d="M4 6L8 10L12 6" 
              stroke="currentColor" 
              stroke-width="2" 
              stroke-linecap="round" 
              stroke-linejoin="round"
            />
          </svg>
        </div>
        
        <!-- 呼吸光效 -->
        <div class="breathing-glow"></div>
      </button>

      <!-- 展开的信息面板 -->
      <div
        ref="infoPanel"
        id="info-panel-content"
        class="info-panel"
        :class="{ 'info-panel--visible': isExpanded }"
        role="region"
        :aria-label="'成员信息面板'"
        :aria-hidden="!isExpanded"
      >
        <div class="panel-content">
          <!-- 标题区域 -->
          <div class="panel-header">
            <h3 class="panel-title">
              <span class="title-accent">成员</span>星云
            </h3>
            <p class="panel-subtitle">
              探索VRC Division中的每一颗闪亮星球
            </p>
          </div>
          
          <!-- 统计信息 -->
          <div class="stats-grid">
            <div class="stat-item">
              <span class="stat-number">{{ totalMembers }}</span>
              <span class="stat-label">位成员</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">{{ totalPages }}</span>
              <span class="stat-label">个星系</span>
            </div>
          </div>
          
          <!-- 搜索控件 -->
          <div class="search-section">
            <div class="search-input-wrapper">
              <svg class="search-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path 
                  d="M7.333 12.667A5.333 5.333 0 1 0 7.333 2a5.333 5.333 0 0 0 0 10.667ZM14 14l-2.9-2.9" 
                  stroke="currentColor" 
                  stroke-width="1.5" 
                  stroke-linecap="round" 
                  stroke-linejoin="round"
                />
              </svg>
              <input
                ref="searchInput"
                type="text"
                placeholder="搜索成员..."
                v-model="searchQuery"
                class="search-input"
                @keydown.escape="collapse"
              >
              <button 
                v-if="searchQuery"
                @click="clearSearch"
                class="clear-search"
                aria-label="清除搜索"
              >
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <path 
                    d="M10.5 3.5L3.5 10.5M3.5 3.5L10.5 10.5" 
                    stroke="currentColor" 
                    stroke-width="1.5" 
                    stroke-linecap="round"
                  />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 背景遮罩 -->
      <Teleport to="body">
        <div
          v-if="isExpanded && deviceInfo.isMobile"
          class="backdrop"
          @click="collapse"
        ></div>
      </Teleport>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue'
import { gsap } from 'gsap'
import { useDeviceDetection } from '../composables/useDeviceDetection'

interface Props {
  totalMembers: number
  totalPages: number
  searchQuery: string
}

interface Emits {
  'update:searchQuery': [value: string]
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 设备检测
const { deviceInfo } = useDeviceDetection()

// 组件状态
const isExpanded = ref(false)
const triggerButton = ref<HTMLButtonElement>()
const infoPanel = ref<HTMLElement>()
const searchInput = ref<HTMLInputElement>()

// 搜索查询的双向绑定
const searchQuery = computed({
  get: () => props.searchQuery,
  set: (value: string) => emit('update:searchQuery', value)
})

// 切换展开状态
const toggleExpanded = async () => {
  if (isExpanded.value) {
    collapse()
  } else {
    expand()
  }
}

// 展开面板
const expand = async () => {
  if (!infoPanel.value) return

  isExpanded.value = true

  // 等待DOM更新
  await nextTick()

  // GSAP 展开动画
  const tl = gsap.timeline()

  if (deviceInfo.value.isMobile) {
    // 移动端：从中心缩放展开
    tl.fromTo(infoPanel.value,
      {
        opacity: 0,
        scale: 0.8,
        y: 0
      },
      {
        opacity: 1,
        scale: 1,
        y: 0,
        duration: 0.4,
        ease: "back.out(1.7)"
      }
    )
  } else {
    // 桌面端：从上方滑入
    tl.fromTo(infoPanel.value,
      {
        opacity: 0,
        y: -20,
        scale: 0.95
      },
      {
        opacity: 1,
        y: 0,
        scale: 1,
        duration: 0.3,
        ease: "power2.out"
      }
    )
  }

  // 内容元素依次出现
  const contentElements = infoPanel.value.querySelectorAll('.panel-header, .stats-grid, .search-section')
  tl.fromTo(contentElements,
    {
      opacity: 0,
      y: 10
    },
    {
      opacity: 1,
      y: 0,
      duration: 0.2,
      stagger: 0.1,
      ease: "power2.out"
    },
    "-=0.2"
  )

  // 聚焦搜索框
  if (searchInput.value && !deviceInfo.value.isMobile) {
    tl.call(() => {
      searchInput.value?.focus()
    })
  }
}

// 收起面板
const collapse = () => {
  if (!infoPanel.value) return

  // GSAP 收起动画
  const tl = gsap.timeline({
    onComplete: () => {
      isExpanded.value = false
      // 返回焦点到触发按钮
      if (triggerButton.value) {
        triggerButton.value.focus()
      }
    }
  })

  if (deviceInfo.value.isMobile) {
    // 移动端：缩放收起
    tl.to(infoPanel.value, {
      opacity: 0,
      scale: 0.8,
      duration: 0.25,
      ease: "power2.in"
    })
  } else {
    // 桌面端：向上滑出
    tl.to(infoPanel.value, {
      opacity: 0,
      y: -10,
      scale: 0.98,
      duration: 0.2,
      ease: "power2.in"
    })
  }
}

// 清除搜索
const clearSearch = () => {
  searchQuery.value = ''
  if (searchInput.value) {
    searchInput.value.focus()
  }
}

// 触摸交互处理
let touchStartTime = 0
const handleTouchStart = (_e: TouchEvent) => {
  touchStartTime = Date.now()

  // 触觉反馈（如果支持）
  if ('vibrate' in navigator) {
    navigator.vibrate(10)
  }

  // 触摸按下效果
  if (triggerButton.value) {
    gsap.to(triggerButton.value, {
      scale: 0.95,
      duration: 0.1,
      ease: "power2.out"
    })
  }
}

const handleTouchEnd = (e: TouchEvent) => {
  const touchDuration = Date.now() - touchStartTime

  // 恢复按钮大小
  if (triggerButton.value) {
    gsap.to(triggerButton.value, {
      scale: 1,
      duration: 0.2,
      ease: "back.out(1.7)"
    })
  }

  // 防止意外触发（触摸时间太短）
  if (touchDuration < 50) {
    e.preventDefault()
    return
  }
}

// 键盘事件处理
const handleKeyDown = (e: KeyboardEvent) => {
  if (e.key === 'Escape' && isExpanded.value) {
    collapse()
  }
}

// 点击外部关闭
const handleClickOutside = (e: Event) => {
  if (!isExpanded.value) return
  
  const target = e.target as Element
  const widget = document.querySelector('.galaxy-info-widget')
  
  if (widget && !widget.contains(target)) {
    collapse()
  }
}

// 触发按钮微交互
const addButtonMicroInteractions = () => {
  if (!triggerButton.value) return

  const button = triggerButton.value
  const glow = button.querySelector('.breathing-glow') as HTMLElement

  // 悬停效果
  button.addEventListener('mouseenter', () => {
    gsap.to(button, {
      scale: 1.05,
      duration: 0.2,
      ease: "power2.out"
    })

    if (glow) {
      gsap.to(glow, {
        opacity: 0.8,
        scale: 1.2,
        duration: 0.3,
        ease: "power2.out"
      })
    }
  })

  button.addEventListener('mouseleave', () => {
    gsap.to(button, {
      scale: 1,
      duration: 0.2,
      ease: "power2.out"
    })

    if (glow) {
      gsap.to(glow, {
        opacity: 0,
        scale: 1,
        duration: 0.3,
        ease: "power2.out"
      })
    }
  })

  // 点击效果
  button.addEventListener('mousedown', () => {
    gsap.to(button, {
      scale: 0.98,
      duration: 0.1,
      ease: "power2.out"
    })
  })

  button.addEventListener('mouseup', () => {
    gsap.to(button, {
      scale: isExpanded.value ? 1.02 : 1.05,
      duration: 0.1,
      ease: "power2.out"
    })
  })
}

// 生命周期
onMounted(() => {
  document.addEventListener('keydown', handleKeyDown)
  document.addEventListener('click', handleClickOutside)

  // 添加按钮微交互
  nextTick(() => {
    addButtonMicroInteractions()
  })
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown)
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped lang="scss">
@use '../styles/variables.scss' as *;

.galaxy-info-widget {
  position: absolute;
  top: calc(var(--spacing-lg) + var(--nav-height, 0px));
  left: var(--spacing-lg);
  z-index: var(--z-popover);

  @include media-down(md) {
    top: calc(var(--spacing-md) + var(--nav-height, 0px));
    left: var(--spacing-md);
  }
}

.info-trigger {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--glass-bg);
  backdrop-filter: blur(16px);
  border: var(--border-glass);
  border-radius: var(--radius-xl);
  color: var(--text-primary);
  cursor: pointer;
  transition: all var(--transition-base) var(--ease-hover);
  position: relative;
  overflow: hidden;
  min-height: 44px; // 触摸友好
  box-shadow: var(--shadow-soft);

  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-glow);
  }

  &:active {
    transform: translateY(0);
  }

  &:focus-visible {
    outline: 2px solid var(--secondary);
    outline-offset: 2px;
  }

  &--expanded {
    background: var(--primary-light);
    border-color: var(--primary);
    box-shadow: var(--shadow-glow);
  }
}

.member-count {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.count-number {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  color: var(--primary);
  line-height: 1;
}

.count-label {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  line-height: 1;
}

.expand-icon {
  transition: transform var(--transition-base) var(--ease-hover);
  color: var(--text-secondary);
  
  &--rotated {
    transform: rotate(180deg);
  }
}

.breathing-glow {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, var(--primary-light) 0%, transparent 70%);
  border-radius: 50%;
  opacity: 0;
  animation: breathe 3s ease-in-out infinite;
  pointer-events: none;
}

@keyframes breathe {
  0%, 100% { 
    opacity: 0;
    transform: scale(1);
  }
  50% { 
    opacity: 0.6;
    transform: scale(1.1);
  }
}

.info-panel {
  position: absolute;
  top: calc(100% + var(--spacing-sm));
  left: 0;
  min-width: 280px;
  max-width: 320px;
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border: var(--border-glass);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-medium);
  opacity: 0;
  visibility: hidden;
  transform: translateY(-10px) scale(0.95);
  transition: all var(--transition-base) var(--ease-hover);
  box-shadow: var(--shadow-soft);
  
  &--visible {
    opacity: 1;
    visibility: visible;
    transform: translateY(0) scale(1);
  }
  
  @include media-down(md) {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%) scale(0.95);
    min-width: calc(100vw - var(--spacing-xl));
    max-width: 400px;
    z-index: var(--z-modal); // 确保在移动端时层级足够高

    &--visible {
      transform: translate(-50%, -50%) scale(1);
    }
  }
}

.panel-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.panel-header {
  text-align: center;
}

.panel-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
  margin-bottom: var(--spacing-xs);
}

.title-accent {
  color: var(--primary);
}

.panel-subtitle {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  line-height: var(--line-height-relaxed);
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
}

.stat-item {
  text-align: center;
  padding: var(--spacing-md);
  background: var(--primary-lighter);
  border-radius: var(--radius-md);
  border: 1px solid var(--glass-border);
}

.stat-number {
  display: block;
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  color: var(--primary);
  margin-bottom: var(--spacing-xs);
}

.stat-label {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.search-section {
  margin-top: var(--spacing-sm);
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: var(--spacing-sm);
  color: var(--text-secondary);
  pointer-events: none;
  z-index: 1;
}

.search-input {
  width: 100%;
  padding: var(--spacing-sm) var(--spacing-xl) var(--spacing-sm) var(--spacing-xl);
  background: var(--primary-lighter);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: var(--font-size-sm);
  transition: all var(--transition-base);

  &::placeholder {
    color: var(--text-secondary);
  }

  &:focus {
    outline: none;
    border-color: var(--primary);
    background: var(--primary-light);
    box-shadow: 0 0 0 2px var(--primary-light);
  }
}

.clear-search {
  position: absolute;
  right: var(--spacing-sm);
  padding: var(--spacing-xs);
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
  
  &:hover {
    color: var(--text-primary);
    background: var(--glass-border);
  }
}

.backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: var(--modal-overlay);
  z-index: var(--z-modal-backdrop);
}

// 移动端优化
.galaxy-info-widget--mobile {
  .info-trigger {
    padding: var(--spacing-md);
    min-height: 48px;
    touch-action: manipulation; // 优化触摸响应
    -webkit-tap-highlight-color: transparent; // 移除点击高亮

    // 增强触摸反馈
    &:active {
      transform: scale(0.95);
    }
  }

  .breathing-glow {
    animation-duration: 4s; // 移动端稍慢的动画
  }

  .info-panel {
    // 移动端面板优化
    max-height: 80vh;
    overflow-y: auto;
    -webkit-overflow-scrolling: touch; // iOS 平滑滚动

    // 安全区域适配
    padding-bottom: calc(var(--spacing-lg) + env(safe-area-inset-bottom));
  }

  .search-input {
    // 移动端输入框优化
    font-size: 16px; // 防止 iOS 缩放
    -webkit-appearance: none; // 移除默认样式

    &:focus {
      // 移动端聚焦时不缩放
      transform: none;
    }
  }

  .stat-item {
    // 移动端统计项优化
    padding: var(--spacing-lg) var(--spacing-md);
    min-height: 44px; // 触摸友好
  }

  .clear-search {
    // 移动端清除按钮优化
    min-width: 44px;
    min-height: 44px;
    padding: var(--spacing-md);
  }
}

// 高对比度模式支持
@media (prefers-contrast: high) {
  .info-trigger {
    border-width: 2px;
    border-color: var(--text-primary);
  }

  .info-panel {
    border-width: 2px;
    background: var(--base-dark);
  }
}

// 减少动画偏好支持
@media (prefers-reduced-motion: reduce) {
  .breathing-glow {
    animation: none;
  }

  .expand-icon {
    transition: none;
  }

  .info-trigger,
  .info-panel,
  .search-input {
    transition: none;
  }
}
</style>
