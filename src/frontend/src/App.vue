<template>
  <div id="app" class="app">
    <ThemeProvider>
      <!-- 路由视图 -->
      <router-view />

      <!-- 全局自定义光标 -->
      <CustomPointer />
    </ThemeProvider>
  </div>
</template>

<script setup lang="ts">
import ThemeProvider from '@/components/ThemeProvider.vue'
import CustomPointer from '@/components/CustomPointer.vue'

// 应用入口，所有页面通过路由渲染
</script>

<style scoped>
.app {
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
