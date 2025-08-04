<template>
  <n-config-provider
    :theme="null"
    :theme-overrides="currentThemeOverrides"
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
import { computed } from 'vue'
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
import type { GlobalThemeOverrides } from 'naive-ui'
import { useThemeStore } from '@/stores/theme'

// 获取主题store
const themeStore = useThemeStore()

// 深色主题覆盖配置
const darkThemeOverrides: GlobalThemeOverrides = {
  common: {
    // 使用首页的主题色彩
    primaryColor: '#AA83FF',
    primaryColorHover: '#B99AFD',
    primaryColorPressed: '#8F6BFF',
    primaryColorSuppl: 'rgba(170, 131, 255, 0.1)',

    // 深色背景
    bodyColor: '#0E1016',

    // 玻璃态效果
    cardColor: 'rgba(255, 255, 255, 0.08)',
    modalColor: 'rgba(14, 16, 22, 1)', // 使用深色背景，降低透明度提高可读性
    popoverColor: 'rgba(14, 16, 22, 0.9)', // 弹出框使用更不透明的背景

    // 文本颜色
    textColorBase: 'rgba(255, 255, 255, 0.95)',
    textColor1: 'rgba(255, 255, 255, 0.95)',
    textColor2: 'rgba(255, 255, 255, 0.7)',
    textColor3: 'rgba(255, 255, 255, 0.5)',

    // 边框颜色
    borderColor: 'rgba(255, 255, 255, 0.12)',
    dividerColor: 'rgba(255, 255, 255, 0.12)',

    // 圆角
    borderRadius: '8px',
    borderRadiusSmall: '4px'
  },

  // 针对特定组件的覆盖
  Button: {
    // 紫色主题按钮
    borderRadiusMedium: '8px',
    fontWeightStrong: '600'
  },

  Card: {
    // 玻璃态卡片效果
    borderRadius: '12px',
    paddingMedium: '20px 24px'
  },

  DataTable: {
    // 表格样式优化
    borderRadius: '12px',
    thFontWeight: '600'
  },

  Modal: {
    // 模态框样式优化 - 提高可读性
    borderRadius: '12px',
    color: 'rgba(14, 16, 22, 0.85)', // 深色背景，降低透明度
    // 模态框遮罩层
    maskColor: 'rgba(0, 0, 0, 0.6)', // 增强遮罩层不透明度
    // 文本颜色确保可读性
    textColor: 'rgba(255, 255, 255, 0.95)',
    titleTextColor: 'rgba(255, 255, 255, 0.95)',
    // 边框和阴影
    borderColor: 'rgba(255, 255, 255, 0.15)',
    boxShadow: '0 12px 32px rgba(0, 0, 0, 0.4), 0 0 20px rgba(170, 131, 255, 0.1)'
  },

  Input: {
    // 输入框样式
    borderRadius: '8px',
    // 输入框文字颜色 - 确保在深色背景上可见
    textColor: '#FFFFFF',
    textColorDisabled: 'rgba(255, 255, 255, 0.3)',
    placeholderColor: 'rgba(255, 255, 255, 0.6)',
    placeholderColorDisabled: 'rgba(255, 255, 255, 0.3)',
    // 输入框背景色
    color: 'rgba(255, 255, 255, 0.08)',
    colorDisabled: 'rgba(255, 255, 255, 0.05)',
    colorFocus: 'rgba(255, 255, 255, 0.12)',
    // 边框颜色
    border: '1px solid rgba(255, 255, 255, 0.15)',
    borderHover: '1px solid #AA83FF',
    borderDisabled: '1px solid rgba(255, 255, 255, 0.08)',
    borderFocus: '1px solid #AA83FF',
    // 焦点效果
    boxShadowFocus: '0 0 0 2px rgba(170, 131, 255, 0.3)',
    caretColor: '#AA83FF'
  },

  Select: {
    // 选择器样式
    borderRadius: '8px',
    // 选择器背景和边框颜色
    color: 'rgba(255, 255, 255, 0.08)',
    colorActive: 'rgba(255, 255, 255, 0.12)',
    border: '1px solid rgba(255, 255, 255, 0.15)',
    borderHover: '1px solid #AA83FF',
    borderActive: '1px solid #AA83FF',
    borderFocus: '1px solid #AA83FF',
    boxShadowFocus: '0 0 0 2px rgba(170, 131, 255, 0.3)',
    // 选择器文字颜色
    textColor: '#FFFFFF',
    placeholderColor: 'rgba(255, 255, 255, 0.6)',
    // 配置内部组件样式
    peers: {
      InternalSelection: {
        // 内部选择器的文字颜色
        textColor: '#FFFFFF',
        placeholderColor: 'rgba(255, 255, 255, 0.6)',
        color: 'rgba(255, 255, 255, 0.08)',
        colorActive: 'rgba(255, 255, 255, 0.12)',
        border: '1px solid rgba(255, 255, 255, 0.15)',
        borderHover: '1px solid #AA83FF',
        borderActive: '1px solid #AA83FF',
        borderFocus: '1px solid #AA83FF',
        boxShadowFocus: '0 0 0 2px rgba(170, 131, 255, 0.3)'
      },
      InternalSelectMenu: {
        // 下拉菜单样式
        color: 'rgba(255, 255, 255, 0.08)',
        optionTextColor: '#FFFFFF',
        optionTextColorActive: '#FFFFFF',
        optionColorActive: 'rgba(170, 131, 255, 0.3)',
        borderRadius: '8px'
      }
    }
  },

  Form: {
    // 表单样式
    labelTextColor: '#FFFFFF',
    labelFontWeight: '500',
    labelFontSize: '14px',
    feedbackTextColor: 'rgba(255, 255, 255, 0.7)',
    feedbackTextColorError: '#FF6B6B',
    feedbackTextColorWarning: '#FFB020',
    feedbackFontSize: '12px'
  },



  Menu: {
    // 菜单样式
    borderRadius: '8px'
  },

  Tag: {
    // 标签组件样式 - 深色主题适配
    borderRadius: '6px',
    // 默认标签
    color: 'rgba(255, 255, 255, 0.1)',
    textColor: 'rgba(255, 255, 255, 0.9)',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    // 主要标签
    colorPrimary: 'rgba(170, 131, 255, 0.2)',
    textColorPrimary: '#AA83FF',
    borderPrimary: '1px solid rgba(170, 131, 255, 0.4)',
    // 信息标签
    colorInfo: 'rgba(63, 125, 251, 0.2)',
    textColorInfo: '#3F7DFB',
    borderInfo: '1px solid rgba(63, 125, 251, 0.4)',
    // 成功标签
    colorSuccess: 'rgba(212, 222, 199, 0.2)',
    textColorSuccess: '#D4DEC7',
    borderSuccess: '1px solid rgba(212, 222, 199, 0.4)',
    // 警告标签
    colorWarning: 'rgba(255, 176, 32, 0.2)',
    textColorWarning: '#FFB020',
    borderWarning: '1px solid rgba(255, 176, 32, 0.4)',
    // 错误标签
    colorError: 'rgba(255, 65, 80, 0.2)',
    textColorError: '#FF4150',
    borderError: '1px solid rgba(255, 65, 80, 0.4)',
    // 可关闭标签
    closeIconColor: 'rgba(255, 255, 255, 0.6)',
    closeIconColorHover: 'rgba(255, 255, 255, 0.9)',
    closeIconColorPressed: 'rgba(255, 255, 255, 0.7)'
  },

  Transfer: {
    // 穿梭框组件样式 - 深色主题适配
    borderRadius: '8px',
    // 列表容器
    listColor: 'rgba(255, 255, 255, 0.08)',
    headerColor: 'rgba(255, 255, 255, 0.12)',
    // 文字颜色
    titleTextColor: 'rgba(255, 255, 255, 0.9)',
    itemTextColor: 'rgba(255, 255, 255, 0.8)',
    itemTextColorDisabled: 'rgba(255, 255, 255, 0.3)',
    // 边框
    borderColor: 'rgba(255, 255, 255, 0.15)',
    // 选中状态
    itemColorPending: 'rgba(170, 131, 255, 0.1)',
    itemColorPendingHover: 'rgba(170, 131, 255, 0.15)',
    // 按钮样式
    extraTextColor: 'rgba(255, 255, 255, 0.7)'
  }
}

// 白色主题覆盖配置
const lightThemeOverrides: GlobalThemeOverrides = {
  common: {
    // 使用首页的主题色彩
    primaryColor: '#AA83FF',
    primaryColorHover: '#B99AFD',
    primaryColorPressed: '#8F6BFF',
    primaryColorSuppl: 'rgba(170, 131, 255, 0.15)',

    // 白色背景
    bodyColor: '#FFFFFF',

    // 玻璃态效果 - 浅色主题（增强对比度）
    cardColor: 'rgba(0, 0, 0, 0.06)',
    modalColor: 'rgba(255, 255, 255, 0.95)',
    popoverColor: 'rgba(255, 255, 255, 0.95)',

    // 文本颜色 - 浅色主题（增强对比度）
    textColorBase: 'rgba(0, 0, 0, 0.88)',
    textColor1: 'rgba(0, 0, 0, 0.88)',
    textColor2: 'rgba(0, 0, 0, 0.65)',
    textColor3: 'rgba(0, 0, 0, 0.45)',

    // 边框颜色（增强可见性）
    borderColor: 'rgba(0, 0, 0, 0.08)',
    dividerColor: 'rgba(0, 0, 0, 0.08)',

    // 圆角
    borderRadius: '8px',
    borderRadiusSmall: '4px'
  },

  // 针对特定组件的覆盖
  Button: {
    borderRadiusMedium: '8px',
    fontWeightStrong: '600'
  },

  Card: {
    borderRadius: '12px',
    paddingMedium: '20px 24px',
    color: 'rgba(255, 255, 255, 0.85)',
    textColor: 'rgba(0, 0, 0, 0.88)',
    titleTextColor: 'rgba(0, 0, 0, 0.88)',
    borderColor: 'rgba(0, 0, 0, 0.08)',
    boxShadow: '0 4px 16px rgba(0, 0, 0, 0.08), 0 0 0 1px rgba(0, 0, 0, 0.04) inset, 0 1px 0 rgba(255, 255, 255, 0.8) inset'
  },

  DataTable: {
    borderRadius: '12px',
    thFontWeight: '600',
    borderColor: 'rgba(0, 0, 0, 0.08)',
    thColor: 'rgba(0, 0, 0, 0.04)',
    tdColor: 'rgba(255, 255, 255, 0.6)',
    thTextColor: 'rgba(0, 0, 0, 0.75)',
    tdTextColor: 'rgba(0, 0, 0, 0.85)'
  },

  Modal: {
    borderRadius: '12px',
    color: 'rgba(255, 255, 255, 0.95)',
    maskColor: 'rgba(0, 0, 0, 0.4)',
    textColor: 'rgba(0, 0, 0, 0.95)',
    titleTextColor: 'rgba(0, 0, 0, 0.95)',
    borderColor: 'rgba(0, 0, 0, 0.15)',
    boxShadow: '0 12px 32px rgba(0, 0, 0, 0.15), 0 0 20px rgba(170, 131, 255, 0.05)'
  },

  Tag: {
    borderRadius: '6px',
    color: 'rgba(0, 0, 0, 0.08)',
    textColor: 'rgba(0, 0, 0, 0.95)',
    border: '1px solid rgba(0, 0, 0, 0.12)',
    closeIconColor: 'rgba(0, 0, 0, 0.6)',
    closeIconColorHover: 'rgba(0, 0, 0, 0.9)',
    closeIconColorPressed: 'rgba(0, 0, 0, 0.7)'
  },

  Transfer: {
    borderRadius: '8px',
    listColor: 'rgba(0, 0, 0, 0.08)',
    headerColor: 'rgba(0, 0, 0, 0.12)',
    titleTextColor: 'rgba(0, 0, 0, 0.9)',
    itemTextColor: 'rgba(0, 0, 0, 0.8)',
    itemTextColorDisabled: 'rgba(0, 0, 0, 0.3)',
    borderColor: 'rgba(0, 0, 0, 0.15)',
    itemColorPending: 'rgba(170, 131, 255, 0.1)',
    itemColorPendingHover: 'rgba(170, 131, 255, 0.15)',
    extraTextColor: 'rgba(0, 0, 0, 0.7)'
  }
}

// 根据当前主题动态选择主题配置
const currentThemeOverrides = computed(() => {
  return themeStore.isDark ? darkThemeOverrides : lightThemeOverrides
})
</script>

<style scoped>
/* 组件级别的样式可以在这里添加 */
</style>
