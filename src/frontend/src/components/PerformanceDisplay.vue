<template>
  <div 
    v-if="showStats && isDevelopment" 
    class="performance-display"
    :class="{ 'performance-display--warning': metrics.isLowPerformance }"
  >
    <div class="performance-header">
      <span class="performance-title">性能监控</span>
      <button 
        class="performance-toggle"
        @click="toggleDisplay"
        aria-label="切换性能显示"
      >
        ×
      </button>
    </div>
    
    <div class="performance-metrics">
      <div class="metric">
        <span class="metric-label">FPS:</span>
        <span class="metric-value" :class="getFPSClass(metrics.fps)">
          {{ metrics.fps }}
        </span>
      </div>
      
      <div class="metric">
        <span class="metric-label">帧时间:</span>
        <span class="metric-value">{{ metrics.frameTime }}ms</span>
      </div>
      
      <div v-if="metrics.memoryUsage" class="metric">
        <span class="metric-label">内存:</span>
        <span class="metric-value">{{ metrics.memoryUsage }}MB</span>
      </div>

      <div class="metric">
        <span class="metric-label">性能等级:</span>
        <span class="metric-value" :class="getPerformanceLevelClass(optimizerStats.currentLevel)">
          {{ optimizerStats.currentLevel.toUpperCase() }}
        </span>
      </div>

      <div class="metric">
        <span class="metric-label">粒子倍数:</span>
        <span class="metric-value">{{ (optimizerStats.particleMultiplier * 100).toFixed(0) }}%</span>
      </div>
    </div>
    
    <div v-if="suggestions.length > 0" class="performance-suggestions">
      <div class="suggestions-title">优化建议:</div>
      <ul class="suggestions-list">
        <li v-for="suggestion in suggestions" :key="suggestion" class="suggestion-item">
          {{ suggestion }}
        </li>
      </ul>
    </div>
  </div>
  
  <!-- 开发环境下的快捷键提示 -->
  <div 
    v-if="isDevelopment && !showStats" 
    class="performance-hint"
    @click="toggleDisplay"
  >
    📊
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { usePerformanceMonitor } from '../composables/usePerformanceMonitor'
import { performanceOptimizer } from '../utils/performanceOptimizer'

const { metrics, getOptimizationSuggestions } = usePerformanceMonitor()

// 性能优化器状态
const optimizerStats = ref(performanceOptimizer.getStats())
let statsUpdateInterval: number

// 更新优化器统计
const updateOptimizerStats = () => {
  optimizerStats.value = performanceOptimizer.getStats()

  // 记录FPS到优化器
  performanceOptimizer.recordFPS(metrics.value.fps)

  // 尝试自动调整性能
  const adjusted = performanceOptimizer.autoAdjust()
  if (adjusted) {
    // 发送性能调整事件
    window.dispatchEvent(new CustomEvent('performance-adjusted', {
      detail: {
        newLevel: performanceOptimizer.getCurrentLevel(),
        stats: performanceOptimizer.getStats()
      }
    }))
  }
}

const showStats = ref(false)

// 检查是否为开发环境
const isDevelopment = computed(() => {
  return import.meta.env.DEV
})

// 获取优化建议
const suggestions = computed(() => {
  return getOptimizationSuggestions()
})

// 切换显示
const toggleDisplay = () => {
  showStats.value = !showStats.value
}

// 获取FPS颜色类
const getFPSClass = (fps: number) => {
  if (fps >= 50) return 'metric-value--good'
  if (fps >= 30) return 'metric-value--warning'
  return 'metric-value--critical'
}

const getPerformanceLevelClass = (level: string) => {
  switch (level) {
    case 'high': return 'metric-value--good'
    case 'medium': return 'metric-value--warning'
    case 'low': return 'metric-value--danger'
    default: return ''
  }
}

// 生命周期管理
onMounted(() => {
  statsUpdateInterval = setInterval(updateOptimizerStats, 1000)
})

onUnmounted(() => {
  if (statsUpdateInterval) {
    clearInterval(statsUpdateInterval)
  }
})

// 键盘快捷键
const handleKeyDown = (e: KeyboardEvent) => {
  // Ctrl + Shift + P 切换性能显示
  if (e.ctrlKey && e.shiftKey && e.key === 'P') {
    e.preventDefault()
    toggleDisplay()
  }
}

// 只在开发环境下添加键盘监听
if (isDevelopment.value) {
  document.addEventListener('keydown', handleKeyDown)
}
</script>

<style scoped lang="scss">
.performance-display {
  position: fixed;
  top: 80px;
  right: 20px;
  z-index: 9999;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 12px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: #fff;
  min-width: 200px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);

  &--warning {
    border-color: #ff6b6b;
    background: rgba(255, 107, 107, 0.1);
  }
}

.performance-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  padding-bottom: 4px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.performance-title {
  font-weight: bold;
  color: #4ecdc4;
}

.performance-toggle {
  background: none;
  border: none;
  color: #fff;
  cursor: pointer;
  font-size: 16px;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 2px;
  transition: background-color 0.2s;

  &:hover {
    background: rgba(255, 255, 255, 0.1);
  }
}

.performance-metrics {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.metric {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric-label {
  color: #ccc;
}

.metric-value {
  font-weight: bold;
  
  &--good {
    color: #4ecdc4;
  }
  
  &--warning {
    color: #ffd93d;
  }
  
  &--critical {
    color: #ff6b6b;
  }
}

.performance-suggestions {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}

.suggestions-title {
  font-weight: bold;
  color: #ffd93d;
  margin-bottom: 4px;
}

.suggestions-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.suggestion-item {
  font-size: 11px;
  color: #ccc;
  margin-bottom: 2px;
  padding-left: 8px;
  position: relative;

  &::before {
    content: '•';
    position: absolute;
    left: 0;
    color: #ffd93d;
  }
}

.performance-hint {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 9999;
  width: 40px;
  height: 40px;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 18px;
  transition: all 0.3s ease;

  &:hover {
    background: rgba(0, 0, 0, 0.9);
    transform: scale(1.1);
  }
}

@media (max-width: 768px) {
  .performance-display {
    top: 60px;
    right: 10px;
    min-width: 180px;
    font-size: 11px;
  }

  .performance-hint {
    bottom: 80px;
    right: 10px;
    width: 35px;
    height: 35px;
    font-size: 16px;
  }
}
</style>
