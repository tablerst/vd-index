/**
 * 性能监控配置系统
 */

import { performanceProfiler, type ProfilerConfig } from '../utils/performanceProfiler'

export interface PerformanceSettings {
  // 基础配置
  enabled: boolean
  enableInProduction: boolean
  
  // 监控配置
  enableFPSMonitoring: boolean
  enableMemoryMonitoring: boolean
  enableComponentTracking: boolean
  enableCustomMetrics: boolean
  
  // 采样配置
  sampleInterval: number
  maxMarks: number
  maxSnapshots: number
  
  // 显示配置
  showPerformancePanel: boolean
  showFPSCounter: boolean
  showMemoryUsage: boolean
  
  // 日志配置
  logLevel: 'none' | 'error' | 'warn' | 'info' | 'debug'
  
  // 自动优化配置
  enableAutoOptimization: boolean
  fpsThreshold: number
  memoryThreshold: number // MB
  
  // 开发者工具
  enableDevTools: boolean
  enableExport: boolean
}

// 默认配置
const defaultSettings: PerformanceSettings = {
  // 基础配置
  enabled: import.meta.env.DEV || import.meta.env.VITE_ENABLE_PERFORMANCE_MONITOR === 'true',
  enableInProduction: import.meta.env.VITE_ENABLE_PERFORMANCE_MONITOR === 'true',
  
  // 监控配置
  enableFPSMonitoring: true,
  enableMemoryMonitoring: true,
  enableComponentTracking: true,
  enableCustomMetrics: true,
  
  // 采样配置
  sampleInterval: 1000, // 1秒
  maxMarks: 1000,
  maxSnapshots: 100,
  
  // 显示配置
  showPerformancePanel: import.meta.env.DEV,
  showFPSCounter: import.meta.env.DEV,
  showMemoryUsage: import.meta.env.DEV,
  
  // 日志配置
  logLevel: import.meta.env.DEV ? 'info' : 'error',
  
  // 自动优化配置
  enableAutoOptimization: true,
  fpsThreshold: 30,
  memoryThreshold: 100, // 100MB
  
  // 开发者工具
  enableDevTools: import.meta.env.DEV,
  enableExport: import.meta.env.DEV
}

// 环境特定配置
const environmentConfigs = {
  development: {
    enabled: true,
    enableInProduction: false,
    showPerformancePanel: true,
    showFPSCounter: true,
    showMemoryUsage: true,
    logLevel: 'debug' as const,
    enableDevTools: true,
    enableExport: true
  },
  
  production: {
    enabled: false,
    enableInProduction: false,
    showPerformancePanel: false,
    showFPSCounter: false,
    showMemoryUsage: false,
    logLevel: 'error' as const,
    enableDevTools: false,
    enableExport: false,
    sampleInterval: 5000, // 生产环境降低采样频率
    maxMarks: 100,
    maxSnapshots: 20
  },
  
  testing: {
    enabled: true,
    enableInProduction: true,
    showPerformancePanel: false,
    showFPSCounter: false,
    showMemoryUsage: false,
    logLevel: 'warn' as const,
    enableDevTools: true,
    enableExport: true
  }
}

class PerformanceConfig {
  private settings: PerformanceSettings
  private listeners: Set<(settings: PerformanceSettings) => void> = new Set()

  constructor() {
    // 根据环境加载配置
    const env = import.meta.env.MODE as keyof typeof environmentConfigs
    const envConfig = environmentConfigs[env] || environmentConfigs.development
    
    this.settings = {
      ...defaultSettings,
      ...envConfig,
      ...this.loadFromStorage()
    }

    this.applySettings()
  }

  /**
   * 获取当前设置
   */
  getSettings(): PerformanceSettings {
    return { ...this.settings }
  }

  /**
   * 更新设置
   */
  updateSettings(newSettings: Partial<PerformanceSettings>): void {
    this.settings = { ...this.settings, ...newSettings }
    this.saveToStorage()
    this.applySettings()
    this.notifyListeners()
  }

  /**
   * 重置为默认设置
   */
  resetToDefaults(): void {
    const env = import.meta.env.MODE as keyof typeof environmentConfigs
    const envConfig = environmentConfigs[env] || environmentConfigs.development
    
    this.settings = {
      ...defaultSettings,
      ...envConfig
    }
    
    this.saveToStorage()
    this.applySettings()
    this.notifyListeners()
  }

  /**
   * 启用性能监控
   */
  enable(): void {
    this.updateSettings({ enabled: true })
  }

  /**
   * 禁用性能监控
   */
  disable(): void {
    this.updateSettings({ enabled: false })
  }

  /**
   * 切换性能面板显示
   */
  togglePanel(): void {
    this.updateSettings({ showPerformancePanel: !this.settings.showPerformancePanel })
  }

  /**
   * 设置日志级别
   */
  setLogLevel(level: PerformanceSettings['logLevel']): void {
    this.updateSettings({ logLevel: level })
  }

  /**
   * 监听设置变化
   */
  onSettingsChange(callback: (settings: PerformanceSettings) => void): () => void {
    this.listeners.add(callback)
    
    // 返回取消监听的函数
    return () => {
      this.listeners.delete(callback)
    }
  }

  /**
   * 获取性能预设配置
   */
  getPresets() {
    return {
      minimal: {
        enabled: true,
        enableFPSMonitoring: true,
        enableMemoryMonitoring: false,
        enableComponentTracking: false,
        enableCustomMetrics: false,
        showPerformancePanel: false,
        showFPSCounter: true,
        showMemoryUsage: false,
        logLevel: 'error' as const,
        sampleInterval: 2000,
        maxMarks: 100,
        maxSnapshots: 20
      },
      
      standard: {
        enabled: true,
        enableFPSMonitoring: true,
        enableMemoryMonitoring: true,
        enableComponentTracking: true,
        enableCustomMetrics: true,
        showPerformancePanel: true,
        showFPSCounter: true,
        showMemoryUsage: true,
        logLevel: 'info' as const,
        sampleInterval: 1000,
        maxMarks: 500,
        maxSnapshots: 50
      },
      
      detailed: {
        enabled: true,
        enableFPSMonitoring: true,
        enableMemoryMonitoring: true,
        enableComponentTracking: true,
        enableCustomMetrics: true,
        showPerformancePanel: true,
        showFPSCounter: true,
        showMemoryUsage: true,
        logLevel: 'debug' as const,
        sampleInterval: 500,
        maxMarks: 1000,
        maxSnapshots: 100,
        enableDevTools: true,
        enableExport: true
      }
    }
  }

  /**
   * 应用预设配置
   */
  applyPreset(presetName: keyof ReturnType<typeof this.getPresets>): void {
    const presets = this.getPresets()
    const preset = presets[presetName]
    
    if (preset) {
      this.updateSettings(preset)
    }
  }

  // 私有方法
  private applySettings(): void {
    // 将设置应用到性能分析器
    const profilerConfig: Partial<ProfilerConfig> = {
      enabled: this.settings.enabled,
      enableInProduction: this.settings.enableInProduction,
      maxMarks: this.settings.maxMarks,
      maxSnapshots: this.settings.maxSnapshots,
      sampleInterval: this.settings.sampleInterval,
      enableMemoryTracking: this.settings.enableMemoryMonitoring,
      enableComponentTracking: this.settings.enableComponentTracking,
      enableCustomMetrics: this.settings.enableCustomMetrics,
      logLevel: this.settings.logLevel
    }

    performanceProfiler.configure(profilerConfig)
  }

  private saveToStorage(): void {
    try {
      localStorage.setItem('performance-settings', JSON.stringify(this.settings))
    } catch (error) {
      console.warn('Failed to save performance settings to localStorage:', error)
    }
  }

  private loadFromStorage(): Partial<PerformanceSettings> {
    try {
      const stored = localStorage.getItem('performance-settings')
      return stored ? JSON.parse(stored) : {}
    } catch (error) {
      console.warn('Failed to load performance settings from localStorage:', error)
      return {}
    }
  }

  private notifyListeners(): void {
    this.listeners.forEach(callback => {
      try {
        callback(this.settings)
      } catch (error) {
        console.error('Error in performance settings listener:', error)
      }
    })
  }
}

// 全局配置实例
export const performanceConfig = new PerformanceConfig()

// 在开发环境中暴露到全局对象，便于调试
if (import.meta.env.DEV) {
  ;(window as any).performanceConfig = performanceConfig
}

// 便捷的配置方法
export const PerformanceUtils = {
  /**
   * 快速启用/禁用性能监控
   */
  toggle: () => {
    const settings = performanceConfig.getSettings()
    performanceConfig.updateSettings({ enabled: !settings.enabled })
  },

  /**
   * 快速切换性能面板
   */
  togglePanel: () => performanceConfig.togglePanel(),

  /**
   * 获取当前性能状态
   */
  getStatus: () => {
    const settings = performanceConfig.getSettings()
    return {
      enabled: settings.enabled,
      panelVisible: settings.showPerformancePanel,
      fpsCounterVisible: settings.showFPSCounter,
      memoryVisible: settings.showMemoryUsage
    }
  },

  /**
   * 快速设置开发模式
   */
  setDevelopmentMode: () => {
    performanceConfig.applyPreset('detailed')
  },

  /**
   * 快速设置生产模式
   */
  setProductionMode: () => {
    performanceConfig.applyPreset('minimal')
  }
}

// 导出类型
export type { PerformanceSettings }
