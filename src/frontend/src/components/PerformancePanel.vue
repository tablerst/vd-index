<template>
  <div v-if="isVisible" class="performance-panel" :class="{ 'performance-panel--minimized': isMinimized }">
    <!-- 标题栏 -->
    <div class="panel-header" @click="toggleMinimize">
      <h3 class="panel-title">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
          <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
          <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
          <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
        </svg>
        性能监控
      </h3>
      <div class="panel-controls">
        <button @click.stop="exportData" class="control-btn" title="导出数据">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
            <path d="M21 15V19A2 2 0 0 1 19 21H5A2 2 0 0 1 3 19V15" stroke="currentColor" stroke-width="2"/>
            <polyline points="7,10 12,15 17,10" stroke="currentColor" stroke-width="2"/>
            <line x1="12" y1="15" x2="12" y2="3" stroke="currentColor" stroke-width="2"/>
          </svg>
        </button>
        <button @click.stop="clearData" class="control-btn" title="清除数据">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
            <polyline points="3,6 5,6 21,6" stroke="currentColor" stroke-width="2"/>
            <path d="M19,6V20A2,2 0 0,1 17,22H7A2,2 0 0,1 5,20V6M8,6V4A2,2 0 0,1 10,2H14A2,2 0 0,1 16,4V6" stroke="currentColor" stroke-width="2"/>
          </svg>
        </button>
        <button @click.stop="toggleVisibility" class="control-btn" title="关闭">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
            <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2"/>
            <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- 内容区域 -->
    <div v-if="!isMinimized" class="panel-content">
      <!-- 实时指标 -->
      <div class="metrics-section">
        <div class="metric-card" :class="{ 'metric-card--warning': currentMetrics.fps < 30 }">
          <div class="metric-label">FPS</div>
          <div class="metric-value">{{ currentMetrics.fps.toFixed(1) }}</div>
          <div class="metric-bar">
            <div class="metric-bar-fill" :style="{ width: `${Math.min(currentMetrics.fps / 60 * 100, 100)}%` }"></div>
          </div>
        </div>

        <div class="metric-card" :class="{ 'metric-card--warning': currentMetrics.frameTime > 33 }">
          <div class="metric-label">帧时间</div>
          <div class="metric-value">{{ currentMetrics.frameTime.toFixed(1) }}ms</div>
          <div class="metric-bar">
            <div class="metric-bar-fill" :style="{ width: `${Math.max(0, 100 - currentMetrics.frameTime / 33 * 100)}%` }"></div>
          </div>
        </div>

        <div class="metric-card" v-if="currentMetrics.memoryUsage > 0">
          <div class="metric-label">内存</div>
          <div class="metric-value">{{ currentMetrics.memoryUsage.toFixed(1) }}MB</div>
          <div class="metric-bar">
            <div class="metric-bar-fill" :style="{ width: `${Math.min(currentMetrics.memoryUsage / 100 * 100, 100)}%` }"></div>
          </div>
        </div>
      </div>

      <!-- 组件性能 -->
      <div class="components-section">
        <h4 class="section-title">组件性能</h4>
        <div class="component-list">
          <div v-for="component in topComponents" :key="component.name" class="component-item">
            <div class="component-name">{{ component.name }}</div>
            <div class="component-metrics">
              <span class="component-time">{{ component.renderTime.toFixed(1) }}ms</span>
              <span class="component-calls">{{ component.callCount }}次</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 慢操作 -->
      <div class="operations-section">
        <h4 class="section-title">慢操作</h4>
        <div class="operation-list">
          <div v-for="operation in slowOperations" :key="operation.name" class="operation-item">
            <div class="operation-name">{{ operation.name }}</div>
            <div class="operation-duration">{{ (operation.duration || 0).toFixed(1) }}ms</div>
          </div>
        </div>
      </div>

      <!-- 控制按钮 -->
      <div class="controls-section">
        <button @click="toggleMonitoring" class="control-button" :class="{ 'control-button--active': isMonitoring }">
          {{ isMonitoring ? '暂停监控' : '开始监控' }}
        </button>
        <button @click="resetMetrics" class="control-button">重置数据</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { performanceProfiler } from '../utils/performanceProfiler'
import { performanceConfig } from '../config/performance'

const isVisible = ref(false)
const isMinimized = ref(false)
const isMonitoring = ref(true)
const currentMetrics = ref({
  fps: 0,
  frameTime: 0,
  memoryUsage: 0
})

let updateInterval: number | null = null

// 计算属性
const topComponents = computed(() => {
  const report = performanceProfiler.getReport()
  return report.componentPerformance.slice(0, 5)
})

const slowOperations = computed(() => {
  const report = performanceProfiler.getReport()
  return report.slowestOperations.slice(0, 5)
})

// 方法
const toggleVisibility = () => {
  isVisible.value = !isVisible.value
}

const toggleMinimize = () => {
  isMinimized.value = !isMinimized.value
}

const toggleMonitoring = () => {
  isMonitoring.value = !isMonitoring.value
  const settings = performanceConfig.getSettings()
  performanceConfig.updateSettings({ enabled: isMonitoring.value })
}

const exportData = () => {
  const data = performanceProfiler.export()
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `performance-data-${new Date().toISOString().slice(0, 19)}.json`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

const clearData = () => {
  performanceProfiler.clear()
}

const resetMetrics = () => {
  performanceProfiler.clear()
  currentMetrics.value = {
    fps: 0,
    frameTime: 0,
    memoryUsage: 0
  }
}

const updateMetrics = () => {
  const snapshot = performanceProfiler.getSnapshot()
  currentMetrics.value = {
    fps: snapshot.fps,
    frameTime: snapshot.frameTime,
    memoryUsage: snapshot.memoryUsage
  }
}

// 键盘快捷键
const handleKeyDown = (e: KeyboardEvent) => {
  // Ctrl/Cmd + Shift + P 切换面板显示
  if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'P') {
    e.preventDefault()
    toggleVisibility()
  }
}

// 生命周期
onMounted(() => {
  // 监听配置变化
  const unwatch = performanceConfig.onSettingsChange((settings) => {
    isVisible.value = settings.showPerformancePanel
    isMonitoring.value = settings.enabled
  })

  // 初始化显示状态
  const settings = performanceConfig.getSettings()
  isVisible.value = settings.showPerformancePanel
  isMonitoring.value = settings.enabled

  // 定期更新指标
  updateInterval = setInterval(updateMetrics, 1000)

  // 添加键盘监听
  document.addEventListener('keydown', handleKeyDown)

  // 清理函数
  onUnmounted(() => {
    unwatch()
    if (updateInterval) {
      clearInterval(updateInterval)
    }
    document.removeEventListener('keydown', handleKeyDown)
  })
})

// 暴露控制方法
defineExpose({
  show: () => { isVisible.value = true },
  hide: () => { isVisible.value = false },
  toggle: toggleVisibility,
  minimize: () => { isMinimized.value = true },
  maximize: () => { isMinimized.value = false }
})
</script>

<style scoped lang="scss">
.performance-panel {
  position: fixed;
  top: 20px;
  right: 20px;
  width: 320px;
  background: rgba(0, 0, 0, 0.9);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: white;
  font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
  font-size: 12px;
  z-index: 10000;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;

  &--minimized {
    height: 40px;
    overflow: hidden;
  }
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  cursor: pointer;
  user-select: none;

  &:hover {
    background: rgba(255, 255, 255, 0.05);
  }
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #AA83FF;
}

.panel-controls {
  display: flex;
  gap: 4px;
}

.control-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: none;
  border: none;
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.1);
    color: white;
  }
}

.panel-content {
  padding: 16px;
  max-height: 500px;
  overflow-y: auto;
}

.metrics-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
}

.metric-card {
  padding: 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  text-align: center;
  transition: all 0.2s ease;

  &--warning {
    background: rgba(255, 107, 107, 0.1);
    border: 1px solid rgba(255, 107, 107, 0.3);
  }
}

.metric-label {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.metric-value {
  font-size: 16px;
  font-weight: 600;
  color: #D4DEC7;
  margin-bottom: 8px;
}

.metric-bar {
  height: 3px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.metric-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #3F7DFB, #AA83FF);
  transition: width 0.3s ease;
}

.section-title {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  margin: 0 0 12px 0;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.component-list,
.operation-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 20px;
}

.component-item,
.operation-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
  border-left: 3px solid #AA83FF;
}

.component-name,
.operation-name {
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
}

.component-metrics {
  display: flex;
  gap: 8px;
  font-size: 11px;
}

.component-time,
.operation-duration {
  color: #D4DEC7;
  font-weight: 600;
}

.component-calls {
  color: rgba(255, 255, 255, 0.6);
}

.controls-section {
  display: flex;
  gap: 8px;
}

.control-button {
  flex: 1;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  color: white;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.15);
  }

  &--active {
    background: #AA83FF;
    border-color: #AA83FF;
  }
}

/* 滚动条样式 */
.panel-content::-webkit-scrollbar {
  width: 4px;
}

.panel-content::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
}

.panel-content::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
}

.panel-content::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}
</style>
