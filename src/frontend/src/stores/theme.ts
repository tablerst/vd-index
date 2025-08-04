/**
 * 主题状态管理
 * 处理深色/浅色主题切换和持久化存储
 */
import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'

export type ThemeMode = 'dark' | 'light'

export const useThemeStore = defineStore('theme', () => {
  // 状态
  const currentTheme = ref<ThemeMode>('dark')
  
  // 从localStorage获取保存的主题设置
  const getStoredTheme = (): ThemeMode => {
    try {
      const stored = localStorage.getItem('vd-theme')
      return (stored === 'light' || stored === 'dark') ? stored : 'dark'
    } catch {
      return 'dark'
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
  
  // 更新CSS变量
  const updateCSSVariables = (theme: ThemeMode) => {
    const root = document.documentElement

    if (theme === 'light') {
      // ========== 浅色主题配置 ==========

      // 核心主题色彩（保持不变）
      root.style.setProperty('--primary', '#AA83FF')
      root.style.setProperty('--primary-hover', '#B99AFD')
      root.style.setProperty('--primary-pressed', '#8F6BFF')
      root.style.setProperty('--primary-light', 'rgba(170, 131, 255, 0.1)')
      root.style.setProperty('--primary-lighter', 'rgba(170, 131, 255, 0.05)')

      root.style.setProperty('--secondary', '#D4DEC7')
      root.style.setProperty('--secondary-hover', '#E8F2DB')
      root.style.setProperty('--secondary-pressed', '#C0CA9F')
      root.style.setProperty('--secondary-light', 'rgba(212, 222, 199, 0.1)')
      root.style.setProperty('--secondary-lighter', 'rgba(212, 222, 199, 0.05)')

      root.style.setProperty('--accent-blue', '#3F7DFB')
      root.style.setProperty('--accent-blue-hover', '#5A8FFC')
      root.style.setProperty('--accent-blue-pressed', '#2A6BFA')
      root.style.setProperty('--accent-blue-light', 'rgba(63, 125, 251, 0.1)')

      // 背景色系统
      root.style.setProperty('--base-dark', '#FFFFFF')
      root.style.setProperty('--base-light', '#F8F9FA')
      root.style.setProperty('--surface-1', 'rgba(0, 0, 0, 0.05)')
      root.style.setProperty('--surface-2', 'rgba(0, 0, 0, 0.08)')
      root.style.setProperty('--surface-3', 'rgba(0, 0, 0, 0.12)')
      root.style.setProperty('--surface-hover', 'rgba(0, 0, 0, 0.15)')
      root.style.setProperty('--surface-pressed', 'rgba(0, 0, 0, 0.06)')

      // 文本颜色系统
      root.style.setProperty('--text-primary', 'rgba(0, 0, 0, 0.95)')
      root.style.setProperty('--text-secondary', 'rgba(0, 0, 0, 0.7)')
      root.style.setProperty('--text-tertiary', 'rgba(0, 0, 0, 0.5)')
      root.style.setProperty('--text-quaternary', 'rgba(0, 0, 0, 0.3)')
      root.style.setProperty('--text-disabled', 'rgba(0, 0, 0, 0.2)')
      root.style.setProperty('--text-accent', '#D4DEC7')
      root.style.setProperty('--text-inverse', 'rgba(255, 255, 255, 0.95)')

      // 边框和分割线
      root.style.setProperty('--border-primary', 'rgba(0, 0, 0, 0.12)')
      root.style.setProperty('--border-secondary', 'rgba(0, 0, 0, 0.08)')
      root.style.setProperty('--divider', 'rgba(0, 0, 0, 0.12)')

      // 玻璃态效果系统
      root.style.setProperty('--glass-bg', 'rgba(0, 0, 0, 0.08)')
      root.style.setProperty('--glass-bg-strong', 'rgba(0, 0, 0, 0.12)')
      root.style.setProperty('--glass-border', 'rgba(0, 0, 0, 0.12)')
      root.style.setProperty('--glass-layer', 'rgba(0, 0, 0, 0.08)')

      // 渐变系统 - 浅色主题优化
      root.style.setProperty('--bg-gradient', 'linear-gradient(135deg, #F8F9FA 0%, #E9ECEF 50%, #DEE2E6 100%)')
      root.style.setProperty('--hero-gradient', 'radial-gradient(ellipse at center, rgba(170, 131, 255, 0.06) 0%, rgba(248, 249, 250, 0.95) 50%, var(--base-dark) 100%)')
      root.style.setProperty('--space-gradient', 'radial-gradient(ellipse at center, rgba(248, 249, 250, 0.95) 0%, rgba(233, 236, 239, 0.98) 40%, rgba(222, 226, 230, 0.99) 70%, var(--base-dark) 100%)')
      root.style.setProperty('--primary-gradient', 'linear-gradient(135deg, #B99AFD 0%, #AA83FF 33%, #8F6BFF 66%)')
      root.style.setProperty('--secondary-gradient', 'linear-gradient(135deg, #E8F2DB 0%, #D4DEC7 50%, #C0CA9F 100%)')
      root.style.setProperty('--mixed-gradient', 'linear-gradient(135deg, #AA83FF 0%, #D4DEC7 50%, #AA83FF 100%)')

      // 阴影系统（浅色主题适配）
      root.style.setProperty('--shadow-soft', '0 8px 32px rgba(0, 0, 0, 0.1)')
      root.style.setProperty('--shadow-medium', '0 12px 48px rgba(0, 0, 0, 0.15)')
      root.style.setProperty('--shadow-strong', '0 16px 64px rgba(0, 0, 0, 0.2)')
      root.style.setProperty('--shadow-glow', '0 0 20px rgba(170, 131, 255, 0.2)')
      root.style.setProperty('--shadow-glow-strong', '0 0 32px rgba(170, 131, 255, 0.3)')
      root.style.setProperty('--shadow-secondary-glow', '0 0 16px rgba(212, 222, 199, 0.3)')
      root.style.setProperty('--shadow-mixed-glow', '0 0 24px rgba(170, 131, 255, 0.15), 0 0 12px rgba(212, 222, 199, 0.2)')
      root.style.setProperty('--shadow-blue-glow', '0 0 20px rgba(63, 125, 251, 0.2)')

      // 特殊效果颜色 - 浅色主题优化
      root.style.setProperty('--star-color', 'rgba(0, 0, 0, 0.4)')
      root.style.setProperty('--nebula-color', 'rgba(170, 131, 255, 0.15)')
      root.style.setProperty('--cosmic-dust', 'rgba(170, 131, 255, 0.1)')
      root.style.setProperty('--particle-primary', 'rgba(170, 131, 255, 0.6)')
      root.style.setProperty('--particle-secondary', 'rgba(212, 222, 199, 0.5)')
      root.style.setProperty('--particle-accent', 'rgba(63, 125, 251, 0.4)')

    } else {
      // ========== 深色主题配置（恢复默认值）==========

      // 核心主题色彩
      root.style.setProperty('--primary', '#AA83FF')
      root.style.setProperty('--primary-hover', '#B99AFD')
      root.style.setProperty('--primary-pressed', '#8F6BFF')
      root.style.setProperty('--primary-light', 'rgba(170, 131, 255, 0.1)')
      root.style.setProperty('--primary-lighter', 'rgba(170, 131, 255, 0.05)')

      root.style.setProperty('--secondary', '#D4DEC7')
      root.style.setProperty('--secondary-hover', '#E8F2DB')
      root.style.setProperty('--secondary-pressed', '#C0CA9F')
      root.style.setProperty('--secondary-light', 'rgba(212, 222, 199, 0.1)')
      root.style.setProperty('--secondary-lighter', 'rgba(212, 222, 199, 0.05)')

      root.style.setProperty('--accent-blue', '#3F7DFB')
      root.style.setProperty('--accent-blue-hover', '#5A8FFC')
      root.style.setProperty('--accent-blue-pressed', '#2A6BFA')
      root.style.setProperty('--accent-blue-light', 'rgba(63, 125, 251, 0.1)')

      // 背景色系统
      root.style.setProperty('--base-dark', '#0E1016')
      root.style.setProperty('--base-light', '#FFFFFF')
      root.style.setProperty('--surface-1', 'rgba(255, 255, 255, 0.05)')
      root.style.setProperty('--surface-2', 'rgba(255, 255, 255, 0.08)')
      root.style.setProperty('--surface-3', 'rgba(255, 255, 255, 0.12)')
      root.style.setProperty('--surface-hover', 'rgba(255, 255, 255, 0.15)')
      root.style.setProperty('--surface-pressed', 'rgba(255, 255, 255, 0.06)')

      // 文本颜色系统
      root.style.setProperty('--text-primary', 'rgba(255, 255, 255, 0.95)')
      root.style.setProperty('--text-secondary', 'rgba(255, 255, 255, 0.7)')
      root.style.setProperty('--text-tertiary', 'rgba(255, 255, 255, 0.5)')
      root.style.setProperty('--text-quaternary', 'rgba(255, 255, 255, 0.3)')
      root.style.setProperty('--text-disabled', 'rgba(255, 255, 255, 0.2)')
      root.style.setProperty('--text-accent', '#D4DEC7')
      root.style.setProperty('--text-inverse', 'rgba(0, 0, 0, 0.95)')

      // 边框和分割线
      root.style.setProperty('--border-primary', 'rgba(255, 255, 255, 0.12)')
      root.style.setProperty('--border-secondary', 'rgba(255, 255, 255, 0.08)')
      root.style.setProperty('--divider', 'rgba(255, 255, 255, 0.12)')

      // 玻璃态效果系统
      root.style.setProperty('--glass-bg', 'rgba(255, 255, 255, 0.08)')
      root.style.setProperty('--glass-bg-strong', 'rgba(255, 255, 255, 0.12)')
      root.style.setProperty('--glass-border', 'rgba(255, 255, 255, 0.12)')
      root.style.setProperty('--glass-layer', 'rgba(255, 255, 255, 0.08)')

      // 渐变系统
      root.style.setProperty('--bg-gradient', 'linear-gradient(135deg, #0E1016 0%, #1A1D29 50%, #252A3A 100%)')
      root.style.setProperty('--hero-gradient', 'radial-gradient(ellipse at center, rgba(170, 131, 255, 0.1) 0%, rgba(14, 16, 22, 0.8) 50%, var(--base-dark) 100%)')
      root.style.setProperty('--space-gradient', 'radial-gradient(ellipse at center, rgba(14, 16, 22, 0.8) 0%, rgba(14, 16, 22, 0.9) 40%, rgba(14, 16, 22, 0.95) 70%, var(--base-dark) 100%)')

      // 阴影系统
      root.style.setProperty('--shadow-soft', '0 8px 32px rgba(0, 0, 0, 0.3)')
      root.style.setProperty('--shadow-medium', '0 12px 48px rgba(0, 0, 0, 0.4)')
      root.style.setProperty('--shadow-strong', '0 16px 64px rgba(0, 0, 0, 0.5)')
      root.style.setProperty('--shadow-glow', '0 0 20px rgba(170, 131, 255, 0.3)')
      root.style.setProperty('--shadow-glow-strong', '0 0 32px rgba(170, 131, 255, 0.4)')
      root.style.setProperty('--shadow-secondary-glow', '0 0 16px rgba(212, 222, 199, 0.4)')
      root.style.setProperty('--shadow-mixed-glow', '0 0 24px rgba(170, 131, 255, 0.2), 0 0 12px rgba(212, 222, 199, 0.3)')
      root.style.setProperty('--shadow-blue-glow', '0 0 20px rgba(63, 125, 251, 0.3)')

      // 特殊效果颜色 - 深色主题
      root.style.setProperty('--star-color', 'rgba(255, 255, 255, 0.8)')
      root.style.setProperty('--nebula-color', 'rgba(170, 131, 255, 0.3)')
      root.style.setProperty('--cosmic-dust', 'rgba(212, 222, 199, 0.2)')
      root.style.setProperty('--particle-primary', 'var(--primary)')
      root.style.setProperty('--particle-secondary', 'var(--secondary)')
      root.style.setProperty('--particle-accent', 'var(--accent-blue)')
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
