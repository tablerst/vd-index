<template>
  <div class="home">
    <!-- 顶部导航 -->
    <GlassNavigation />

    <!-- 主要内容区域 -->
    <main class="main-content">
      <!-- Hero 首屏 -->
      <section ref="heroSectionRef" class="snap-section">
        <HeroSection />
      </section>

      <!-- Members Circle 成员圆形展示 -->
      <section ref="membersSectionRef" class="snap-section">
        <MembersCircle />
      </section>

      <!-- 星历活动板 -->
      <section ref="calendarSectionRef" class="snap-section">
        <StarCalendar />
      </section>
    </main>

    <!-- Footer -->
    <AppFooter />

    <!-- 滚动指示器 - 移动端隐藏 -->
    <ScrollIndicator
      :current-section="currentSection"
      :sections="sections"
      :progress="progress"
      :visible="!isAnimating && !isRealMobileDevice"
      :show-hint="currentSection === 0"
      :is-mobile-progress-bar-disabled="isMobileProgressBarDisabled"
      @go-to-section="goToSection"
    />

    <!-- 全局背景粒子 -->
    <GlobalParticles />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, provide } from 'vue'
import GlassNavigation from '@/components/GlassNavigation.vue'
import HeroSection from '@/components/HeroSection.vue'
import MembersCircle from '@/components/MembersCircle.vue'
import StarCalendar from '@/components/StarCalendar.vue'
import AppFooter from '@/components/AppFooter.vue'
import GlobalParticles from '@/components/GlobalParticles.vue'
import ScrollIndicator from '@/components/ScrollIndicator.vue'
import { useSnapScroll } from '@/composables/useSnapScroll'

// Section refs
const heroSectionRef = ref<HTMLElement | null>(null)
const membersSectionRef = ref<HTMLElement | null>(null)
const calendarSectionRef = ref<HTMLElement | null>(null)

// 真实的移动设备检测（不受我们的强制desktop配置影响）
const isRealMobileDevice = computed(() => {
  // 检查屏幕宽度
  const isMobileWidth = window.innerWidth <= 768
  // 检查用户代理
  const isMobileUserAgent = /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
  // 检查触摸设备
  const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0

  return isMobileWidth || (isMobileUserAgent && isTouchDevice)
})

// 使用分屏滚动
const {
  currentSection,
  isAnimating,

  sections,
  progress,
  goToSection,
  deviceType,
  isMobileProgressBarDisabled,
  setWheelListenerDisabled
} = useSnapScroll([
  heroSectionRef,
  membersSectionRef,
  calendarSectionRef
], {
  // 只保留必要的自定义配置，让设备特定配置生效
  footerThreshold: 0.85
})

// 提供滚轮监听器控制函数给子组件
provide('setWheelListenerDisabled', setWheelListenerDisabled)
</script>

<style scoped lang="scss">
@use '../styles/variables.scss' as *;

.home {
  min-height: 100vh;
  background: var(--base-dark);
  color: var(--text-primary);
  overflow-x: hidden;
}

.main-content {
  position: relative;
  z-index: 1;
}

.snap-section {
  position: relative;
  min-height: 100vh;
  display: flex;
  flex-direction: column;

  // 确保每个section都有足够的高度
  &:first-child {
    min-height: 100vh;
  }

  &:nth-child(2) {
    min-height: 100vh;
  }

  &:last-child {
    min-height: 100vh;
  }

  // 移动端适配
  @include media-down(md) {
    min-height: 100vh;
    min-height: 100dvh; // 动态视口高度
  }

  // 平板适配
  @include media-between(md, lg) {
    min-height: 100vh;
  }
}

// 滚动行为优化 - 确保GSAP完全接管滚动控制
html {
  scroll-behavior: auto !important; // 强制禁用浏览器默认的平滑滚动，使用GSAP控制
}

// 防止滚动条闪烁
body {
  overflow-x: hidden;
}

// 性能优化
.snap-section {
  contain: layout style paint;
  will-change: transform;
}

// 可访问性
@media (prefers-reduced-motion: reduce) {
  .snap-section {
    will-change: auto;
  }
}
</style>
