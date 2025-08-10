<template>
  <n-config-provider
    :theme="null"
    :theme-overrides="currentThemeOverrides"
    :locale="zhCN"
    :date-locale="dateZhCN"
    preflight-style-disabled
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

  Pagination: {
    // 分页（深色）
    itemTextColor: 'rgba(255, 255, 255, 0.82)',
    itemTextColorHover: 'rgba(255, 255, 255, 0.95)',
    itemTextColorActive: '#FFFFFF',
    itemColor: 'rgba(14, 16, 22, 0.85)',
    itemColorHover: 'rgba(14, 16, 22, 1)',
    itemColorActive: '#AA83FF',
    itemBorder: '1px solid rgba(255, 255, 255, 0.15)',
    itemBorderHover: '1px solid rgba(255, 255, 255, 0.25)',
    itemBorderActive: '1px solid #AA83FF'
  },

  Card: {
    // 玻璃态卡片效果
    borderRadius: '12px',
    paddingMedium: '20px 24px'
  },

  DataTable: {
    // 表格样式优化（深色）
    borderRadius: '12px',
    thFontWeight: '600',
    borderColor: 'rgba(255, 255, 255, 0.12)',
    thColor: 'rgba(255, 255, 255, 0.08)',
    tdColor: 'rgba(255, 255, 255, 0.05)',
    tdColorHover: 'rgba(255, 255, 255, 0.08)',
    tdColorStriped: 'rgba(255, 255, 255, 0.03)',
    thTextColor: 'rgba(255, 255, 255, 0.95)',
    tdTextColor: 'rgba(255, 255, 255, 0.95)'
  },

  Modal: {
    // 模态框样式优化 - 提高可读性
    borderRadius: '12px',
    color: 'rgba(14, 16, 22, 0.85)', // 深色背景，降低透明度
    maskColor: 'rgba(0, 0, 0, 0.6)',
    textColor: 'rgba(255, 255, 255, 0.95)',
    titleTextColor: 'rgba(255, 255, 255, 0.95)',
    borderColor: 'rgba(255, 255, 255, 0.15)',
    boxShadow: '0 12px 32px rgba(0, 0, 0, 0.4), 0 0 20px rgba(170, 131, 255, 0.1)'
  },
  Dialog: {
    // 注意：preset="dialog" 的 n-modal 底层使用的是 Dialog 的 token
    borderRadius: '12px',
    color: 'rgba(14, 16, 22, 0.9)',
    textColor: 'rgba(255, 255, 255, 0.95)',
    titleTextColor: 'rgba(255, 255, 255, 0.95)',
    border: '1px solid rgba(255, 255, 255, 0.15)',
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
    // 菜单（深色）
    borderRadius: '8px',
    itemTextColor: 'rgba(255, 255, 255, 0.95)',
    itemTextColorHover: 'rgba(255, 255, 255, 0.95)',
    itemTextColorActive: 'rgba(255, 255, 255, 0.95)',
    itemTextColorChildActive: 'rgba(255, 255, 255, 0.95)',
    itemColorHover: 'rgba(255, 255, 255, 0.05)',
    itemColorActive: 'rgba(170, 131, 255, 0.2)',
    itemColorActiveHover: 'rgba(170, 131, 255, 0.3)',
    groupTextColor: 'rgba(255, 255, 255, 0.7)',
    dividerColor: 'rgba(255, 255, 255, 0.12)'
  },

  Breadcrumb: {
    // 面包屑（深色）
    itemTextColor: 'rgba(255, 255, 255, 0.7)',
    itemTextColorHover: 'rgba(255, 255, 255, 0.95)',
    itemTextColorPressed: '#AA83FF',
    separatorColor: 'rgba(255, 255, 255, 0.5)'
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

// 白色主题覆盖配置 - 使用新的科学优化配色
const lightThemeOverrides: GlobalThemeOverrides = {
  common: {
    // 使用优化后的主题色彩，确保足够对比度
    primaryColor: '#7C3AED',        // 更深的紫色，确保对比度
    primaryColorHover: '#8B5CF6',   // 悬停状态
    primaryColorPressed: '#6D28D9', // 按下状态
    primaryColorSuppl: 'rgba(124, 58, 237, 0.12)', // 12% 透明度

    // 稍微暗一些的背景，让绿色更突出
    bodyColor: '#F8FAFC',           // 浅灰背景，而非纯白

    // 玻璃态效果 - 使用实色背景而非透明度
    cardColor: '#F1F5F9',           // 浅灰表面
    modalColor: 'rgba(248, 250, 252, 0.95)',
    popoverColor: 'rgba(248, 250, 252, 0.95)',

    // 文本颜色 - 使用更深的颜色确保最佳可读性
    textColorBase: '#000000',       // 纯黑色，确保最佳可读性
    textColor1: '#000000',          // 主要文本使用纯黑色
    textColor2: '#1F2937',          // 次要文本使用深灰色
    textColor3: '#4B5563',          // 辅助文本使用中灰色

    // 边框颜色 - 使用实色而非透明度
    borderColor: '#D1D5DB',         // 明确的边框色
    dividerColor: '#E5E7EB',        // 分割线颜色

    // 圆角
    borderRadius: '8px',
    borderRadiusSmall: '4px'
  },

  // 针对特定组件的覆盖
  Button: {
    borderRadiusMedium: '8px',
    fontWeightStrong: '600'
  },

  Pagination: {
    // 分页（浅色）
    itemTextColor: 'rgba(31, 41, 55, 0.85)',
    itemTextColorHover: 'rgba(0, 0, 0, 0.95)',
    itemTextColorActive: '#FFFFFF',
    itemColor: 'rgba(255, 255, 255, 0.95)',
    itemColorHover: 'rgba(248, 250, 252, 1)',
    itemColorActive: '#7C3AED',
    itemBorder: '1px solid rgba(0, 0, 0, 0.12)',
    itemBorderHover: '1px solid rgba(0, 0, 0, 0.2)',
    itemBorderActive: '1px solid #7C3AED'
  },

  Card: {
    borderRadius: '12px',
    paddingMedium: '20px 24px',
    color: 'rgba(255, 255, 255, 0.85)',
    textColor: '#000000',
    titleTextColor: '#000000',
    borderColor: 'rgba(0, 0, 0, 0.08)',
    boxShadow: '0 4px 16px rgba(0, 0, 0, 0.08), 0 0 0 1px rgba(0, 0, 0, 0.04) inset, 0 1px 0 rgba(255, 255, 255, 0.8) inset'
  },

  DataTable: {
    // 表格样式优化（浅色）
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
    textColor: '#000000',
    titleTextColor: '#000000',
    borderColor: 'rgba(0, 0, 0, 0.15)',
    boxShadow: '0 12px 32px rgba(0, 0, 0, 0.15), 0 0 20px rgba(170, 131, 255, 0.05)'
  },

  // 输入框（浅色）
  Input: {
    borderRadius: '8px',
    textColor: '#000000',
    textColorDisabled: 'rgba(0, 0, 0, 0.3)',
    placeholderColor: 'rgba(0, 0, 0, 0.45)',
    placeholderColorDisabled: 'rgba(0, 0, 0, 0.3)',
    color: 'rgba(255, 255, 255, 0.98)',
    colorDisabled: 'rgba(255, 255, 255, 0.92)',
    colorFocus: '#FFFFFF',
    border: '1px solid rgba(0, 0, 0, 0.12)',
    borderHover: '1px solid #7C3AED',
    borderDisabled: '1px solid rgba(0, 0, 0, 0.08)',
    borderFocus: '1px solid #7C3AED',
    boxShadowFocus: '0 0 0 2px rgba(124, 58, 237, 0.25)',
    caretColor: '#7C3AED'
  },

  // 选择器（浅色）
  Select: {
    borderRadius: '8px',
    color: 'rgba(255, 255, 255, 0.98)',
    colorActive: '#FFFFFF',
    border: '1px solid rgba(0, 0, 0, 0.12)',
    borderHover: '1px solid #7C3AED',
    borderActive: '1px solid #7C3AED',
    borderFocus: '1px solid #7C3AED',
    boxShadowFocus: '0 0 0 2px rgba(124, 58, 237, 0.25)',
    textColor: '#000000',
    placeholderColor: 'rgba(0, 0, 0, 0.45)',
    peers: {
      InternalSelection: {
        textColor: '#000000',
        placeholderColor: 'rgba(0, 0, 0, 0.45)'
      }
    },
  },

  Dialog: {
    borderRadius: '12px',
    color: 'rgba(255, 255, 255, 0.98)',
    textColor: '#000000',
    titleTextColor: '#000000',
    border: '1px solid rgba(0, 0, 0, 0.15)',
    boxShadow: '0 12px 32px rgba(0, 0, 0, 0.15), 0 0 20px rgba(170, 131, 255, 0.05)'
  },

  Tag: {
    borderRadius: '6px',
    // 默认标签
    color: 'rgba(0, 0, 0, 0.08)',
    textColor: '#000000',
    border: '1px solid rgba(0, 0, 0, 0.12)',
    // 主要标签 - 使用新的紫色
    colorPrimary: 'rgba(124, 58, 237, 0.12)',
    textColorPrimary: '#7C3AED',
    borderPrimary: '1px solid rgba(124, 58, 237, 0.3)',
    // 成功标签 - 使用新的绿色
    colorSuccess: 'rgba(81, 112, 41, 0.12)',
    textColorSuccess: '#517029',
    borderSuccess: '1px solid rgba(81, 112, 41, 0.3)',
    // 信息标签 - 使用新的蓝色
    colorInfo: 'rgba(37, 99, 235, 0.12)',
    textColorInfo: '#2563EB',
    borderInfo: '1px solid rgba(37, 99, 235, 0.3)',
    // 关闭图标
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
  },
  Breadcrumb: {
    itemTextColor: 'rgba(0, 0, 0, 0.6)',
    itemTextColorHover: 'rgba(0, 0, 0, 0.95)',
    itemTextColorPressed: '#7C3AED',
    separatorColor: 'rgba(0, 0, 0, 0.45)'
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
