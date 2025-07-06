<template>
  <n-config-provider
    :theme="null"
    :theme-overrides="themeOverrides"
    :locale="zhCN"
    :date-locale="dateZhCN"
  >
    <n-global-style />
    <n-message-provider>
      <n-dialog-provider>
        <n-notification-provider>
          <n-loading-bar-provider>
            <slot />
          </n-loading-bar-provider>
        </n-notification-provider>
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup lang="ts">
import { 
  NConfigProvider, 
  NMessageProvider, 
  NDialogProvider, 
  NNotificationProvider,
  NLoadingBarProvider,
  NGlobalStyle,
  zhCN,
  dateZhCN
} from 'naive-ui'
import { fluentTheme } from '@/config/theme'
import type { GlobalThemeOverrides } from 'naive-ui'

// 主题覆盖配置
const themeOverrides: GlobalThemeOverrides = {
  common: {
    // 可以在这里添加运行时主题覆盖
  },
  
  // 针对特定组件的覆盖
  Button: {
    // 添加 Fluent Design 的 Reveal 效果
    borderRadiusMedium: '4px',
    fontWeightStrong: '600'
  },
  
  Card: {
    // 增强卡片的 Acrylic 效果
    borderRadius: '8px',
    paddingMedium: '20px 24px'
  },
  
  DataTable: {
    // 表格样式优化
    borderRadius: '8px',
    thFontWeight: '600'
  },
  
  Modal: {
    // 模态框 Acrylic 效果
    borderRadius: '8px'
  },
  
  Input: {
    // 输入框 Fluent 样式
    borderRadius: '4px'
  },
  
  Menu: {
    // 菜单 Fluent 样式
    borderRadius: '8px'
  }
}
</script>

<style scoped>
/* 组件级别的样式可以在这里添加 */
</style>
