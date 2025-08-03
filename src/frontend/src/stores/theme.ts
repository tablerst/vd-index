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
      // 白色主题CSS变量
      root.style.setProperty('--primary', '#AA83FF')
      root.style.setProperty('--secondary', '#D4DEC7')
      root.style.setProperty('--base-dark', '#FFFFFF')
      root.style.setProperty('--glass-layer', 'rgba(0, 0, 0, 0.08)')
      root.style.setProperty('--accent-blue', '#3F7DFB')
      root.style.setProperty('--error-alert', '#FF4150')
      
      // 文本颜色
      root.style.setProperty('--text-primary', 'rgba(0, 0, 0, 0.95)')
      root.style.setProperty('--text-secondary', 'rgba(0, 0, 0, 0.7)')
      root.style.setProperty('--text-muted', 'rgba(0, 0, 0, 0.5)')
      root.style.setProperty('--text-accent', '#D4DEC7')
      
      // 玻璃态效果
      root.style.setProperty('--glass-bg', 'rgba(0, 0, 0, 0.08)')
      root.style.setProperty('--glass-border', 'rgba(0, 0, 0, 0.12)')
      
      // 背景渐变
      root.style.setProperty('--bg-gradient', 'linear-gradient(135deg, #F8F9FA 0%, #E9ECEF 50%, #DEE2E6 100%)')
      
    } else {
      // 深色主题CSS变量（恢复默认值）
      root.style.setProperty('--primary', '#AA83FF')
      root.style.setProperty('--secondary', '#D4DEC7')
      root.style.setProperty('--base-dark', '#0E1016')
      root.style.setProperty('--glass-layer', 'rgba(255, 255, 255, 0.08)')
      root.style.setProperty('--accent-blue', '#3F7DFB')
      root.style.setProperty('--error-alert', '#FF4150')
      
      // 文本颜色
      root.style.setProperty('--text-primary', 'rgba(255, 255, 255, 0.95)')
      root.style.setProperty('--text-secondary', 'rgba(255, 255, 255, 0.7)')
      root.style.setProperty('--text-muted', 'rgba(255, 255, 255, 0.5)')
      root.style.setProperty('--text-accent', '#D4DEC7')
      
      // 玻璃态效果
      root.style.setProperty('--glass-bg', 'rgba(255, 255, 255, 0.08)')
      root.style.setProperty('--glass-border', 'rgba(255, 255, 255, 0.12)')
      
      // 背景渐变
      root.style.setProperty('--bg-gradient', 'linear-gradient(135deg, #0E1016 0%, #1A1D29 50%, #252A3A 100%)')
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
