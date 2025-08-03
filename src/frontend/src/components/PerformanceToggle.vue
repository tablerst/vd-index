<template>
  <div class="performance-toggle" v-if="showToggle">
    <button 
      @click="togglePanel" 
      class="toggle-button"
      :class="{ 'toggle-button--active': isPanelVisible }"
      title="切换性能监控面板 (Ctrl+Shift+P)"
    >
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
        <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
        <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
        <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
      </svg>
      <span class="fps-indicator" :class="{ 'fps-indicator--warning': currentFPS < 30 }">
        {{ currentFPS.toFixed(0) }}
      </span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { performanceConfig } from '../config/performance'
import { performanceProfiler } from '../utils/performanceProfiler'

const showToggle = ref(false)
const isPanelVisible = ref(false)
const currentFPS = ref(60)

let updateInterval: number | null = null

const togglePanel = () => {
  performanceConfig.togglePanel()
}

const updateFPS = () => {
  const snapshot = performanceProfiler.getSnapshot()
  currentFPS.value = snapshot.fps
}

onMounted(() => {
  // 监听配置变化
  const unwatch = performanceConfig.onSettingsChange((settings) => {
    showToggle.value = settings.enableDevTools
    isPanelVisible.value = settings.showPerformancePanel
  })

  // 初始化状态
  const settings = performanceConfig.getSettings()
  showToggle.value = settings.enableDevTools
  isPanelVisible.value = settings.showPerformancePanel

  // 定期更新FPS
  updateInterval = setInterval(updateFPS, 500)

  onUnmounted(() => {
    unwatch()
    if (updateInterval) {
      clearInterval(updateInterval)
    }
  })
})
</script>

<style scoped lang="scss">
.performance-toggle {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 9999;
}

.toggle-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  color: rgba(255, 255, 255, 0.7);
  font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);

  &:hover {
    background: rgba(0, 0, 0, 0.9);
    color: white;
    border-color: rgba(255, 255, 255, 0.2);
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
  }

  &--active {
    background: rgba(170, 131, 255, 0.2);
    border-color: #AA83FF;
    color: #AA83FF;

    &:hover {
      background: rgba(170, 131, 255, 0.3);
    }
  }
}

.fps-indicator {
  font-weight: 600;
  color: #D4DEC7;
  min-width: 20px;
  text-align: center;

  &--warning {
    color: #ff6b6b;
  }
}

/* 移动设备隐藏 */
@media (max-width: 768px) {
  .performance-toggle {
    display: none;
  }
}
</style>
