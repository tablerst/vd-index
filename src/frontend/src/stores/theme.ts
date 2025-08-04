/**
 * 主题状态管理
 * 处理深色/浅色主题切换和持久化存储
 */
import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { getThemeColors } from '../utils/themeColors'

export type ThemeMode = 'dark' | 'light'

export const useThemeStore = defineStore('theme', () => {
  // 状态 - 默认为亮色主题
  const currentTheme = ref<ThemeMode>('light')

  // 从localStorage获取保存的主题设置
  const getStoredTheme = (): ThemeMode => {
    try {
      const stored = localStorage.getItem('vd-theme')
      return (stored === 'light' || stored === 'dark') ? stored : 'light'
    } catch {
      return 'light'
    }
  }
  
  // 保存主题设置到localStorage
  const saveTheme = (theme: ThemeMode) => {
    try {
      localStorage.setItem('vd-theme', theme)
    } catch (error) {
      console.warn('Failed to save theme to localStorage:', error)
    }
  }
  
  // 初始化主题
  const initTheme = () => {
    currentTheme.value = getStoredTheme()
    updateCSSVariables(currentTheme.value)
  }
  
  // 更新CSS变量 - 使用科学配色算法
  const updateCSSVariables = (theme: ThemeMode) => {
    const root = document.documentElement
    const colors = getThemeColors(theme === 'dark')

    // 核心主题色彩
    root.style.setProperty('--primary', colors.primary)
    root.style.setProperty('--primary-hover', colors.primaryHover)
    root.style.setProperty('--primary-pressed', colors.primaryPressed)
    root.style.setProperty('--primary-light', colors.primaryLight)
    root.style.setProperty('--primary-lighter', colors.primaryLighter)

    root.style.setProperty('--secondary', colors.secondary)
    root.style.setProperty('--secondary-hover', colors.secondaryHover)
    root.style.setProperty('--secondary-pressed', colors.secondaryPressed)
    root.style.setProperty('--secondary-light', colors.secondaryLight)
    root.style.setProperty('--secondary-lighter', colors.secondaryLighter)

    root.style.setProperty('--accent-blue', colors.accent)
    root.style.setProperty('--accent-blue-hover', colors.accentHover)
    root.style.setProperty('--accent-blue-pressed', colors.accentPressed)
    root.style.setProperty('--accent-blue-light', colors.accentLight)

    // 背景色系统
    root.style.setProperty('--base-dark', colors.baseDark)
    root.style.setProperty('--base-light', colors.baseLight)
    root.style.setProperty('--surface-1', colors.surface1)
    root.style.setProperty('--surface-2', colors.surface2)
    root.style.setProperty('--surface-3', colors.surface3)
    root.style.setProperty('--surface-hover', colors.surfaceHover)
    root.style.setProperty('--surface-pressed', colors.surfacePressed)

    // 文本颜色系统
    root.style.setProperty('--text-primary', colors.textPrimary)
    root.style.setProperty('--text-secondary', colors.textSecondary)
    root.style.setProperty('--text-tertiary', colors.textTertiary)
    root.style.setProperty('--text-quaternary', colors.textQuaternary)
    root.style.setProperty('--text-disabled', colors.textDisabled)
    root.style.setProperty('--text-accent', colors.textAccent)
    root.style.setProperty('--text-inverse', colors.textInverse)

    // 边框和分割线
    root.style.setProperty('--border-primary', colors.borderPrimary)
    root.style.setProperty('--border-secondary', colors.borderSecondary)
    root.style.setProperty('--border-focus', colors.borderFocus)
    root.style.setProperty('--divider', colors.divider)

    // 玻璃态效果系统
    root.style.setProperty('--glass-bg', colors.glassBg)
    root.style.setProperty('--glass-bg-strong', colors.glassBgStrong)
    root.style.setProperty('--glass-border', colors.glassBorder)
    root.style.setProperty('--glass-layer', colors.glassBg)

    // 特殊效果颜色
    root.style.setProperty('--star-color', colors.starColor)
    root.style.setProperty('--nebula-color', colors.nebulaColor)
    root.style.setProperty('--cosmic-dust', colors.cosmicDust)
    root.style.setProperty('--particle-primary', colors.particlePrimary)
    root.style.setProperty('--particle-secondary', colors.particleSecondary)
    root.style.setProperty('--particle-accent', colors.particleAccent)

    // 状态颜色
    root.style.setProperty('--error-alert', colors.error)
    root.style.setProperty('--warning', colors.warning)
    root.style.setProperty('--success', colors.success)
    root.style.setProperty('--info', colors.info)

    // 主题特定的渐变和阴影
    if (theme === 'light') {
      // 浅色主题渐变（使用浅灰背景，让绿色更突出）
      root.style.setProperty('--bg-gradient', 'linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 30%, #E2E8F0 70%, #CBD5E1 100%)')
      root.style.setProperty('--hero-gradient', `radial-gradient(ellipse at center, ${colors.primaryLight} 0%, rgba(248, 250, 252, 0.9) 40%, rgba(241, 245, 249, 0.95) 70%, ${colors.baseDark} 100%)`)
      root.style.setProperty('--space-gradient', `radial-gradient(ellipse at center, rgba(248, 250, 252, 0.95) 0%, rgba(241, 245, 249, 0.98) 30%, rgba(226, 232, 240, 0.99) 60%, ${colors.baseDark} 100%)`)

      // 浅色主题阴影（增强深度感）
      root.style.setProperty('--shadow-soft', '0 4px 16px rgba(0, 0, 0, 0.08), 0 0 0 1px rgba(0, 0, 0, 0.04)')
      root.style.setProperty('--shadow-medium', '0 8px 24px rgba(0, 0, 0, 0.12), 0 0 0 1px rgba(0, 0, 0, 0.06)')
      root.style.setProperty('--shadow-strong', '0 12px 32px rgba(0, 0, 0, 0.16), 0 0 0 1px rgba(0, 0, 0, 0.08)')
      root.style.setProperty('--shadow-glow', `0 0 16px ${colors.primaryLight}, 0 4px 12px rgba(170, 131, 255, 0.15)`)
      root.style.setProperty('--shadow-glow-strong', `0 0 24px ${colors.primaryLight}, 0 8px 16px rgba(170, 131, 255, 0.2)`)
      root.style.setProperty('--shadow-secondary-glow', `0 0 12px ${colors.secondaryLight}, 0 4px 8px rgba(212, 222, 199, 0.15)`)
      root.style.setProperty('--shadow-mixed-glow', `0 0 20px ${colors.primaryLight}, 0 0 8px ${colors.secondaryLight}, 0 4px 12px rgba(170, 131, 255, 0.1)`)
      root.style.setProperty('--shadow-blue-glow', `0 0 16px ${colors.accentLight}, 0 4px 12px rgba(63, 125, 251, 0.15)`)

    } else {
      // 深色主题渐变
      root.style.setProperty('--bg-gradient', 'linear-gradient(135deg, #0E1016 0%, #1A1D29 50%, #252A3A 100%)')
      root.style.setProperty('--hero-gradient', `radial-gradient(ellipse at center, ${colors.primaryLight} 0%, rgba(14, 16, 22, 0.8) 50%, ${colors.baseDark} 100%)`)
      root.style.setProperty('--space-gradient', `radial-gradient(ellipse at center, rgba(14, 16, 22, 0.8) 0%, rgba(14, 16, 22, 0.9) 40%, rgba(14, 16, 22, 0.95) 70%, ${colors.baseDark} 100%)`)

      // 深色主题阴影
      root.style.setProperty('--shadow-soft', '0 8px 32px rgba(0, 0, 0, 0.3)')
      root.style.setProperty('--shadow-medium', '0 12px 48px rgba(0, 0, 0, 0.4)')
      root.style.setProperty('--shadow-strong', '0 16px 64px rgba(0, 0, 0, 0.5)')
      root.style.setProperty('--shadow-glow', `0 0 20px ${colors.primaryLight}`)
      root.style.setProperty('--shadow-glow-strong', `0 0 32px ${colors.primaryLight}`)
      root.style.setProperty('--shadow-secondary-glow', `0 0 16px ${colors.secondaryLight}`)
      root.style.setProperty('--shadow-mixed-glow', `0 0 24px ${colors.primaryLight}, 0 0 12px ${colors.secondaryLight}`)
      root.style.setProperty('--shadow-blue-glow', `0 0 20px ${colors.accentLight}`)
    }

    // 通用渐变（基于当前主题色彩）
    root.style.setProperty('--primary-gradient', `linear-gradient(135deg, ${colors.primaryHover} 0%, ${colors.primary} 33%, ${colors.primaryPressed} 66%)`)
    root.style.setProperty('--secondary-gradient', `linear-gradient(135deg, ${colors.secondaryHover} 0%, ${colors.secondary} 50%, ${colors.secondaryPressed} 100%)`)
    root.style.setProperty('--mixed-gradient', `linear-gradient(135deg, ${colors.primary} 0%, ${colors.secondary} 50%, ${colors.primary} 100%)`)

    // 玻璃态效果变量 - 使用themeColors.ts中的统一配色
    if (theme === 'light') {
      // 浅色主题：使用浅灰色玻璃效果，确保在白背景下可见
      root.style.setProperty('--glass-bg', colors.glassBg)
      root.style.setProperty('--glass-border', colors.glassBorder)
      root.style.setProperty('--glass-shadow', '0 4px 16px rgba(0, 0, 0, 0.08), 0 0 0 1px rgba(0, 0, 0, 0.04) inset')
      root.style.setProperty('--modal-overlay', 'rgba(0, 0, 0, 0.6)')
    } else {
      // 深色主题：保持原有的白色玻璃效果
      root.style.setProperty('--glass-bg', colors.glassBg)
      root.style.setProperty('--glass-border', colors.glassBorder)
      root.style.setProperty('--glass-shadow', '0 8px 32px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(255, 255, 255, 0.1) inset')
      root.style.setProperty('--modal-overlay', 'rgba(0, 0, 0, 0.85)')
    }
  }
  
  // 计算属性
  const isDark = computed(() => currentTheme.value === 'dark')
  const isLight = computed(() => currentTheme.value === 'light')
  
  // 切换主题
  const toggleTheme = () => {
    currentTheme.value = currentTheme.value === 'dark' ? 'light' : 'dark'
  }
  
  // 设置特定主题
  const setTheme = (theme: ThemeMode) => {
    currentTheme.value = theme
  }
  
  // 监听主题变化，自动保存和更新CSS变量
  watch(currentTheme, (newTheme) => {
    saveTheme(newTheme)
    updateCSSVariables(newTheme)
  }, { immediate: false })
  
  // 初始化
  initTheme()
  
  return {
    // 状态
    currentTheme: computed(() => currentTheme.value),
    
    // 计算属性
    isDark,
    isLight,
    
    // 方法
    toggleTheme,
    setTheme,
    initTheme
  }
})
