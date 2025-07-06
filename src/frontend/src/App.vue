<template>
  <div id="app" class="app">
    <n-config-provider :theme="null">
      <n-message-provider>
        <n-dialog-provider>
          <n-notification-provider>
            <!-- 路由视图 -->
            <router-view />
          </n-notification-provider>
        </n-dialog-provider>
      </n-message-provider>
    </n-config-provider>
  </div>
</template>

<script setup lang="ts">
import {
  NConfigProvider,
  NMessageProvider,
  NDialogProvider,
  NNotificationProvider
} from 'naive-ui'

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
