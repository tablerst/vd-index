<template>
  <div class="home">
    <!-- 顶部导航 -->
    <GlassNavigation />

    <!-- 主要内容区域 -->
    <main class="main-content">
      <!-- Hero 首屏 -->
      <HeroSection />

      <!-- Members Circle 成员圆形展示 -->
      <MembersCircle />

      <!-- 星历活动板 -->
      <StarCalendar />
    </main>

    <!-- Footer -->
    <AppFooter />

    <!-- 自定义光标 -->
    <CustomPointer />
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
import CustomPointer from '@/components/CustomPointer.vue'
import GlobalParticles from '@/components/GlobalParticles.vue'
</script>

<style scoped>
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
</style>
