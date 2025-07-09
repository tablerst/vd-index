/**
 * 性能优化器 - 动态调整星环效果性能
 */

export interface PerformanceConfig {
  particleCount: {
    low: number[]
    medium: number[]
    high: number[]
  }
  animationSpeed: {
    low: number
    medium: number
    high: number
  }
  targetFPS: {
    low: number
    medium: number
    high: number
  }
  enableEffects: {
    breathing: boolean
    pulse: boolean
    rotation: boolean
    parallax: boolean
  }
}

export type PerformanceLevel = 'low' | 'medium' | 'high'

export class PerformanceOptimizer {
  private currentLevel: PerformanceLevel = 'medium'
  private fpsHistory: number[] = []
  private readonly fpsHistorySize = 30
  private lastAdjustTime = 0
  private readonly adjustCooldown = 3000 // 3秒冷却时间
  
  private config: PerformanceConfig = {
    particleCount: {
      low: [40, 30, 20],
      medium: [80, 60, 40],
      high: [120, 90, 60]
    },
    animationSpeed: {
      low: 0.5,
      medium: 0.8,
      high: 1.0
    },
    targetFPS: {
      low: 30,
      medium: 45,
      high: 60
    },
    enableEffects: {
      breathing: true,
      pulse: true,
      rotation: true,
      parallax: true
    }
  }

  constructor(initialLevel: PerformanceLevel = 'medium') {
    this.currentLevel = initialLevel
    this.detectDeviceCapabilities()
  }

  /**
   * 检测设备性能能力
   */
  private detectDeviceCapabilities() {
    const isMobile = /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
    const isLowEndDevice = navigator.hardwareConcurrency <= 2
    const hasLimitedMemory = (navigator as any).deviceMemory && (navigator as any).deviceMemory <= 4
    
    // 根据设备能力调整初始性能等级
    if (isMobile || isLowEndDevice || hasLimitedMemory) {
      this.currentLevel = 'low'
      console.log('Detected low-end device, setting performance to LOW')
    } else if (navigator.hardwareConcurrency >= 8) {
      this.currentLevel = 'high'
      console.log('Detected high-end device, setting performance to HIGH')
    }
  }

  /**
   * 记录FPS数据
   */
  recordFPS(fps: number) {
    this.fpsHistory.push(fps)
    if (this.fpsHistory.length > this.fpsHistorySize) {
      this.fpsHistory.shift()
    }
  }

  /**
   * 获取平均FPS
   */
  getAverageFPS(): number {
    if (this.fpsHistory.length === 0) return 60
    return this.fpsHistory.reduce((sum, fps) => sum + fps, 0) / this.fpsHistory.length
  }

  /**
   * 自动调整性能等级
   */
  autoAdjust(): boolean {
    const now = Date.now()
    if (now - this.lastAdjustTime < this.adjustCooldown) {
      return false // 冷却期内不调整
    }

    if (this.fpsHistory.length < 10) {
      return false // 数据不足
    }

    const avgFPS = this.getAverageFPS()
    const targetFPS = this.config.targetFPS[this.currentLevel]
    let adjusted = false

    // 性能下降，降级
    if (avgFPS < targetFPS * 0.7 && this.currentLevel !== 'low') {
      if (this.currentLevel === 'high') {
        this.currentLevel = 'medium'
      } else {
        this.currentLevel = 'low'
      }
      adjusted = true
      console.log(`Performance downgraded to ${this.currentLevel.toUpperCase()}, avgFPS: ${avgFPS.toFixed(1)}`)
    }
    // 性能良好，升级
    else if (avgFPS > targetFPS * 1.2 && this.currentLevel !== 'high') {
      if (this.currentLevel === 'low') {
        this.currentLevel = 'medium'
      } else {
        this.currentLevel = 'high'
      }
      adjusted = true
      console.log(`Performance upgraded to ${this.currentLevel.toUpperCase()}, avgFPS: ${avgFPS.toFixed(1)}`)
    }

    if (adjusted) {
      this.lastAdjustTime = now
      this.fpsHistory = [] // 清空历史数据重新统计
    }

    return adjusted
  }

  /**
   * 获取当前性能等级
   */
  getCurrentLevel(): PerformanceLevel {
    return this.currentLevel
  }

  /**
   * 手动设置性能等级
   */
  setLevel(level: PerformanceLevel) {
    this.currentLevel = level
    this.fpsHistory = []
    console.log(`Performance manually set to ${level.toUpperCase()}`)
  }

  /**
   * 获取当前配置
   */
  getCurrentConfig() {
    const level = this.currentLevel
    return {
      particleCount: this.config.particleCount[level],
      animationSpeed: this.config.animationSpeed[level],
      targetFPS: this.config.targetFPS[level],
      enableEffects: this.getEnabledEffects()
    }
  }

  /**
   * 根据性能等级获取启用的效果
   */
  private getEnabledEffects() {
    const effects = { ...this.config.enableEffects }
    
    if (this.currentLevel === 'low') {
      effects.pulse = false
      effects.parallax = false
    } else if (this.currentLevel === 'medium') {
      effects.parallax = false
    }
    
    return effects
  }

  /**
   * 获取粒子数量倍数
   */
  getParticleMultiplier(): number {
    switch (this.currentLevel) {
      case 'low': return 0.4
      case 'medium': return 0.7
      case 'high': return 1.0
      default: return 0.7
    }
  }

  /**
   * 获取动画速度倍数
   */
  getAnimationSpeedMultiplier(): number {
    return this.config.animationSpeed[this.currentLevel]
  }

  /**
   * 获取目标FPS
   */
  getTargetFPS(): number {
    return this.config.targetFPS[this.currentLevel]
  }

  /**
   * 获取性能统计信息
   */
  getStats() {
    return {
      currentLevel: this.currentLevel,
      averageFPS: this.getAverageFPS(),
      targetFPS: this.getTargetFPS(),
      fpsHistoryLength: this.fpsHistory.length,
      particleMultiplier: this.getParticleMultiplier(),
      animationSpeed: this.getAnimationSpeedMultiplier()
    }
  }

  /**
   * 重置性能监控
   */
  reset() {
    this.fpsHistory = []
    this.lastAdjustTime = 0
    this.detectDeviceCapabilities()
  }
}

// 全局性能优化器实例
export const performanceOptimizer = new PerformanceOptimizer()
