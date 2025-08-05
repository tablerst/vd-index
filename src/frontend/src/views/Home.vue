<template>
  <div class="home">
    <!-- 顶部导航 -->
    <GlassNavigation />

    <!-- 主要内容区域 -->
    <main class="main-content" ref="mainRef">
      <!-- Hero 首屏 -->
      <section class="panel">
        <HeroSection />
      </section>

      <!-- Members Circle 成员圆形展示 -->
      <section class="panel">
        <MembersCircle />
      </section>

      <!-- 星历活动板 -->
      <section class="panel">
        <StarCalendar />
      </section>

      <!-- 页脚 -->
      <section class="panel">
        <!-- TODO 莫名其妙的大范围空白 -->
        <AppFooter />
      </section>
    </main>
    <!-- 全局背景粒子 -->
    <GlobalParticles />
  </div>
</template>

<script setup lang="ts">
import GlassNavigation from '@/components/GlassNavigation.vue'
import HeroSection from '@/components/HeroSection.vue'
import MembersCircle from '@/components/MembersCircle.vue'
import StarCalendar from '@/components/StarCalendar.vue'
import AppFooter from '@/components/AppFooter.vue'
import GlobalParticles from '@/components/GlobalParticles.vue'

import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

const mainRef = ref<HTMLElement | null>(null)

onMounted(() => {
  nextTick(() => {
    const panels = gsap.utils.toArray<HTMLElement>('.panel')
    const container = mainRef.value!

    const total = () => (panels.length - 1) * window.innerHeight

    gsap.set(panels, { force3D: true })
    gsap.to(panels, {
      yPercent: -100 * (panels.length - 1),
      ease: 'none',
      scrollTrigger: {
        trigger: container,
        start: 'top top+=80',
        end: () => `+=${total()}`, // ① 直接使用整体高度
        scrub: 0.3,
        pin: true,
        pinSpacing: false,
        anticipatePin: 1,
        invalidateOnRefresh: true,
        snap: {
          snapTo: 1 / (panels.length - 1),
          duration: 0.5,
          ease: 'power1.inOut'
        }
      }
    })
  })
})

onUnmounted(() => {
  ScrollTrigger.getAll().forEach(t => t.kill())
})
</script>

<style scoped>
.home {
  min-height: 100vh;
  background: var(--base-dark);
  color: var(--text-primary);
  overflow-x: hidden;
}

.panel {
  height: 100vh;
  width: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: center;
  will-change: transform;
}

.panel>* {
  flex: 1 0 auto;
  overflow: auto;
}

.main-content {
  position: relative;
  z-index: 1;
}
</style>
