/**
 * 性能插桩工具 - 精确测量和分析前端性能
 */

export interface PerformanceMark {
  name: string
  startTime: number
  endTime?: number
  duration?: number
  metadata?: Record<string, any>
}

export interface ComponentMetrics {
  name: string
  renderTime: number
  updateTime: number
  mountTime: number
  unmountTime: number
  memoryUsage?: number
  callCount: number
  lastUpdate: number
}

export interface PerformanceSnapshot {
  timestamp: number
  fps: number
  frameTime: number
  memoryUsage: number
  activeMarks: PerformanceMark[]
  componentMetrics: ComponentMetrics[]
  customMetrics: Record<string, number>
}

export interface ProfilerConfig {
  enabled: boolean
  enableInProduction: boolean
  maxMarks: number
  maxSnapshots: number
  sampleInterval: number
  enableMemoryTracking: boolean
  enableComponentTracking: boolean
  enableCustomMetrics: boolean
  logLevel: 'none' | 'error' | 'warn' | 'info' | 'debug'
}

class PerformanceProfiler {
  private config: ProfilerConfig = {
    enabled: true,
    enableInProduction: false,
    maxMarks: 1000,
    maxSnapshots: 100,
    sampleInterval: 1000, // 1秒
    enableMemoryTracking: true,
    enableComponentTracking: true,
    enableCustomMetrics: true,
    logLevel: 'info'
  }

  private marks: Map<string, PerformanceMark> = new Map()
  private componentMetrics: Map<string, ComponentMetrics> = new Map()
  private snapshots: PerformanceSnapshot[] = []
  private customMetrics: Map<string, number> = new Map()
  
  private fpsHistory: number[] = []
  private lastFrameTime = 0
  private frameCount = 0
  private isMonitoring = false
  private monitoringId: number | null = null

  constructor(config?: Partial<ProfilerConfig>) {
    if (config) {
      this.config = { ...this.config, ...config }
    }

    // 生产环境检查
    if (import.meta.env.PROD && !this.config.enableInProduction) {
      this.config.enabled = false
    }

    this.initializeMonitoring()
  }

  /**
   * 配置性能分析器
   */
  configure(config: Partial<ProfilerConfig>) {
    this.config = { ...this.config, ...config }
    
    if (this.config.enabled && !this.isMonitoring) {
      this.startMonitoring()
    } else if (!this.config.enabled && this.isMonitoring) {
      this.stopMonitoring()
    }
  }

  /**
   * 开始性能标记
   */
  mark(name: string, metadata?: Record<string, any>): void {
    if (!this.config.enabled) return

    const mark: PerformanceMark = {
      name,
      startTime: performance.now(),
      metadata
    }

    this.marks.set(name, mark)
    
    // 限制标记数量
    if (this.marks.size > this.config.maxMarks) {
      const firstKey = this.marks.keys().next().value
      this.marks.delete(firstKey)
    }

    this.log('debug', `Performance mark started: ${name}`)
  }

  /**
   * 结束性能标记
   */
  measure(name: string, additionalMetadata?: Record<string, any>): number | null {
    if (!this.config.enabled) return null

    const mark = this.marks.get(name)
    if (!mark) {
      this.log('warn', `Performance mark not found: ${name}`)
      return null
    }

    const endTime = performance.now()
    const duration = endTime - mark.startTime

    mark.endTime = endTime
    mark.duration = duration
    
    if (additionalMetadata) {
      mark.metadata = { ...mark.metadata, ...additionalMetadata }
    }

    this.log('debug', `Performance measure completed: ${name} - ${duration.toFixed(2)}ms`)
    return duration
  }

  /**
   * 记录组件性能指标
   */
  recordComponent(
    componentName: string, 
    type: 'render' | 'update' | 'mount' | 'unmount',
    duration: number,
    metadata?: Record<string, any>
  ): void {
    if (!this.config.enabled || !this.config.enableComponentTracking) return

    let metrics = this.componentMetrics.get(componentName)
    if (!metrics) {
      metrics = {
        name: componentName,
        renderTime: 0,
        updateTime: 0,
        mountTime: 0,
        unmountTime: 0,
        callCount: 0,
        lastUpdate: Date.now()
      }
      this.componentMetrics.set(componentName, metrics)
    }

    metrics.callCount++
    metrics.lastUpdate = Date.now()

    switch (type) {
      case 'render':
        metrics.renderTime = duration
        break
      case 'update':
        metrics.updateTime = duration
        break
      case 'mount':
        metrics.mountTime = duration
        break
      case 'unmount':
        metrics.unmountTime = duration
        break
    }

    if (this.config.enableMemoryTracking && 'memory' in performance) {
      metrics.memoryUsage = (performance as any).memory.usedJSHeapSize
    }

    this.log('debug', `Component ${componentName} ${type}: ${duration.toFixed(2)}ms`)
  }

  /**
   * 记录自定义指标
   */
  recordMetric(name: string, value: number): void {
    if (!this.config.enabled || !this.config.enableCustomMetrics) return

    this.customMetrics.set(name, value)
    this.log('debug', `Custom metric ${name}: ${value}`)
  }

  /**
   * 获取当前性能快照
   */
  getSnapshot(): PerformanceSnapshot {
    const snapshot: PerformanceSnapshot = {
      timestamp: Date.now(),
      fps: this.getCurrentFPS(),
      frameTime: this.getAverageFrameTime(),
      memoryUsage: this.getMemoryUsage(),
      activeMarks: Array.from(this.marks.values()).filter(mark => !mark.endTime),
      componentMetrics: Array.from(this.componentMetrics.values()),
      customMetrics: Object.fromEntries(this.customMetrics)
    }

    // 保存快照
    this.snapshots.push(snapshot)
    if (this.snapshots.length > this.config.maxSnapshots) {
      this.snapshots.shift()
    }

    return snapshot
  }

  /**
   * 获取性能报告
   */
  getReport(): {
    summary: {
      averageFPS: number
      averageFrameTime: number
      memoryUsage: number
      totalMarks: number
      totalComponents: number
    }
    slowestOperations: PerformanceMark[]
    componentPerformance: ComponentMetrics[]
    recentSnapshots: PerformanceSnapshot[]
  } {
    const completedMarks = Array.from(this.marks.values())
      .filter(mark => mark.duration !== undefined)
      .sort((a, b) => (b.duration || 0) - (a.duration || 0))

    return {
      summary: {
        averageFPS: this.getAverageFPS(),
        averageFrameTime: this.getAverageFrameTime(),
        memoryUsage: this.getMemoryUsage(),
        totalMarks: this.marks.size,
        totalComponents: this.componentMetrics.size
      },
      slowestOperations: completedMarks.slice(0, 10),
      componentPerformance: Array.from(this.componentMetrics.values())
        .sort((a, b) => b.renderTime - a.renderTime),
      recentSnapshots: this.snapshots.slice(-10)
    }
  }

  /**
   * 清除所有数据
   */
  clear(): void {
    this.marks.clear()
    this.componentMetrics.clear()
    this.snapshots.length = 0
    this.customMetrics.clear()
    this.fpsHistory.length = 0
    this.log('info', 'Performance profiler data cleared')
  }

  /**
   * 导出性能数据
   */
  export(): string {
    const data = {
      config: this.config,
      report: this.getReport(),
      exportTime: new Date().toISOString()
    }
    return JSON.stringify(data, null, 2)
  }

  // 私有方法
  private initializeMonitoring(): void {
    if (this.config.enabled) {
      this.startMonitoring()
    }
  }

  private startMonitoring(): void {
    if (this.isMonitoring) return

    this.isMonitoring = true
    this.lastFrameTime = performance.now()
    
    const monitor = () => {
      if (!this.isMonitoring) return

      const currentTime = performance.now()
      const deltaTime = currentTime - this.lastFrameTime
      
      if (deltaTime > 0) {
        const fps = 1000 / deltaTime
        this.fpsHistory.push(fps)
        
        // 保持FPS历史记录在合理范围内
        if (this.fpsHistory.length > 60) {
          this.fpsHistory.shift()
        }
      }

      this.lastFrameTime = currentTime
      this.frameCount++

      // 定期创建快照
      if (this.frameCount % (this.config.sampleInterval / 16) === 0) {
        this.getSnapshot()
      }

      this.monitoringId = requestAnimationFrame(monitor)
    }

    monitor()
    this.log('info', 'Performance monitoring started')
  }

  private stopMonitoring(): void {
    this.isMonitoring = false
    if (this.monitoringId) {
      cancelAnimationFrame(this.monitoringId)
      this.monitoringId = null
    }
    this.log('info', 'Performance monitoring stopped')
  }

  private getCurrentFPS(): number {
    return this.fpsHistory.length > 0 ? this.fpsHistory[this.fpsHistory.length - 1] : 0
  }

  private getAverageFPS(): number {
    if (this.fpsHistory.length === 0) return 0
    return this.fpsHistory.reduce((sum, fps) => sum + fps, 0) / this.fpsHistory.length
  }

  private getAverageFrameTime(): number {
    const avgFPS = this.getAverageFPS()
    return avgFPS > 0 ? 1000 / avgFPS : 0
  }

  private getMemoryUsage(): number {
    if (!this.config.enableMemoryTracking || !('memory' in performance)) {
      return 0
    }
    return (performance as any).memory.usedJSHeapSize / 1024 / 1024 // MB
  }

  private log(level: string, message: string): void {
    const levels = ['none', 'error', 'warn', 'info', 'debug']
    const currentLevelIndex = levels.indexOf(this.config.logLevel)
    const messageLevelIndex = levels.indexOf(level)

    if (messageLevelIndex <= currentLevelIndex && messageLevelIndex > 0) {
      console[level as keyof Console](`[PerformanceProfiler] ${message}`)
    }
  }
}

// 全局实例
export const performanceProfiler = new PerformanceProfiler()

// Vue 组件装饰器
export function withPerformanceTracking(componentName: string) {
  return function(target: any) {
    const originalMounted = target.mounted
    const originalUpdated = target.updated
    const originalUnmounted = target.unmounted

    target.mounted = function() {
      const startTime = performance.now()
      const result = originalMounted?.call(this)
      const duration = performance.now() - startTime
      performanceProfiler.recordComponent(componentName, 'mount', duration)
      return result
    }

    target.updated = function() {
      const startTime = performance.now()
      const result = originalUpdated?.call(this)
      const duration = performance.now() - startTime
      performanceProfiler.recordComponent(componentName, 'update', duration)
      return result
    }

    target.unmounted = function() {
      const startTime = performance.now()
      const result = originalUnmounted?.call(this)
      const duration = performance.now() - startTime
      performanceProfiler.recordComponent(componentName, 'unmount', duration)
      return result
    }

    return target
  }
}
