import { ref, onMounted, onUnmounted } from 'vue'

export interface PerformanceMetrics {
  fps: number
  frameTime: number
  memoryUsage?: number
  isLowPerformance: boolean
}

export function usePerformanceMonitor(threshold = 45) {
  const metrics = ref<PerformanceMetrics>({
    fps: 60,
    frameTime: 16.67,
    isLowPerformance: false
  })

  let frameCount = 0
  let lastTime = performance.now()
  let animationId: number
  let fpsHistory: number[] = []
  const historySize = 60 // 保持60帧的历史记录

  // 计算FPS
  const calculateFPS = () => {
    frameCount++
    const currentTime = performance.now()
    const deltaTime = currentTime - lastTime

    if (deltaTime >= 1000) { // 每秒更新一次
      const fps = Math.round((frameCount * 1000) / deltaTime)
      const frameTime = deltaTime / frameCount

      // 更新FPS历史
      fpsHistory.push(fps)
      if (fpsHistory.length > historySize) {
        fpsHistory.shift()
      }

      // 计算平均FPS
      const avgFPS = fpsHistory.reduce((sum, f) => sum + f, 0) / fpsHistory.length

      metrics.value = {
        fps: Math.round(avgFPS),
        frameTime: Number(frameTime.toFixed(2)),
        memoryUsage: getMemoryUsage(),
        isLowPerformance: avgFPS < threshold
      }

      frameCount = 0
      lastTime = currentTime
    }

    animationId = requestAnimationFrame(calculateFPS)
  }

  // 获取内存使用情况（如果支持）
  const getMemoryUsage = (): number | undefined => {
    if ('memory' in performance) {
      const memory = (performance as any).memory
      return Math.round(memory.usedJSHeapSize / 1024 / 1024) // MB
    }
    return undefined
  }

  // 性能优化建议
  const getOptimizationSuggestions = () => {
    const suggestions: string[] = []
    
    if (metrics.value.fps < 30) {
      suggestions.push('帧率过低，建议减少粒子数量')
      suggestions.push('考虑降低动画复杂度')
    } else if (metrics.value.fps < threshold) {
      suggestions.push('性能略低，建议优化动画效果')
    }

    if (metrics.value.memoryUsage && metrics.value.memoryUsage > 100) {
      suggestions.push('内存使用较高，建议优化资源管理')
    }

    if (metrics.value.frameTime > 33) {
      suggestions.push('帧时间过长，建议优化渲染逻辑')
    }

    return suggestions
  }

  // 自动性能调整
  const autoOptimize = () => {
    if (metrics.value.isLowPerformance) {
      // 发送性能优化事件
      window.dispatchEvent(new CustomEvent('performance-low', {
        detail: {
          fps: metrics.value.fps,
          suggestions: getOptimizationSuggestions()
        }
      }))
    }
  }

  // 监听性能变化
  const watchPerformance = () => {
    const prevFPS = metrics.value.fps
    
    // 如果FPS显著下降，触发优化
    if (prevFPS - metrics.value.fps > 10) {
      autoOptimize()
    }
  }

  // 开始监控
  const startMonitoring = () => {
    lastTime = performance.now()
    calculateFPS()
  }

  // 停止监控
  const stopMonitoring = () => {
    if (animationId) {
      cancelAnimationFrame(animationId)
    }
  }

  // 重置统计
  const reset = () => {
    frameCount = 0
    fpsHistory = []
    metrics.value = {
      fps: 60,
      frameTime: 16.67,
      isLowPerformance: false
    }
  }

  onMounted(() => {
    startMonitoring()
  })

  onUnmounted(() => {
    stopMonitoring()
  })

  return {
    metrics,
    getOptimizationSuggestions,
    startMonitoring,
    stopMonitoring,
    reset,
    watchPerformance
  }
}
