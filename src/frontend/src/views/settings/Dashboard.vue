<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>仪表板</h1>
      <p>系统概览和统计信息</p>
    </div>

    <div class="stats-grid">
      <n-card class="stat-card" hoverable>
        <div class="stat-content">
          <div class="stat-icon">
            <n-icon size="32" color="#AA83FF">
              <People />
            </n-icon>
          </div>
          <div class="stat-info">
            <h3>{{ memberStats.total }}</h3>
            <p>总成员数</p>
          </div>
        </div>
      </n-card>

      <n-card class="stat-card" hoverable>
        <div class="stat-content">
          <div class="stat-icon">
            <n-icon size="32" color="#D4DEC7">
              <Calendar />
            </n-icon>
          </div>
          <div class="stat-info">
            <h3>{{ activityStats.total }}</h3>
            <p>活动总数</p>
          </div>
        </div>
      </n-card>

      <n-card class="stat-card" hoverable>
        <div class="stat-content">
          <div class="stat-icon">
            <n-icon size="32" color="#3F7DFB">
              <Settings />
            </n-icon>
          </div>
          <div class="stat-info">
            <h3>{{ configStats.total }}</h3>
            <p>配置项数</p>
          </div>
        </div>
      </n-card>

      <n-card class="stat-card" hoverable>
        <div class="stat-content">
          <div class="stat-icon">
            <n-icon size="32" color="#D13438">
              <TrendingUp />
            </n-icon>
          </div>
          <div class="stat-info">
            <h3>{{ systemStats.uptime }}</h3>
            <p>系统运行时间</p>
          </div>
        </div>
      </n-card>

      <n-card class="stat-card" hoverable>
        <div class="stat-content">
          <div class="stat-icon">
            <n-icon size="32" color="#FF6B6B">
              <Flash />
            </n-icon>
          </div>
          <div class="stat-info">
            <h3>{{ formatPercentage(cacheStats.hit_rate) }}</h3>
            <p>缓存命中率</p>
          </div>
        </div>
      </n-card>

      <n-card class="stat-card" hoverable>
        <div class="stat-content">
          <div class="stat-icon">
            <n-icon size="32" color="#4ECDC4">
              <Server />
            </n-icon>
          </div>
          <div class="stat-info">
            <h3>{{ cacheStats.cache_size }}/{{ cacheStats.max_size }}</h3>
            <p>缓存使用量</p>
          </div>
        </div>
      </n-card>
    </div>

    <div class="dashboard-content">
      <n-grid :cols="3" :x-gap="16" :y-gap="16">
        <n-grid-item>
          <n-card title="最近活动" hoverable>
            <n-list>
              <n-list-item v-for="activity in recentActivities" :key="activity.id">
                <div class="activity-item">
                  <div class="activity-info">
                    <h4>{{ activity.title }}</h4>
                    <p>{{ activity.description }}</p>
                  </div>
                  <div class="activity-date">
                    {{ formatDate(activity.date) }}
                  </div>
                </div>
              </n-list-item>
            </n-list>
          </n-card>
        </n-grid-item>

        <n-grid-item>
          <n-card title="系统状态" hoverable>
            <div class="system-status">
              <div class="status-item">
                <span class="status-label">数据库连接</span>
                <n-tag :type="systemStatus.database ? 'success' : 'error'">
                  {{ systemStatus.database ? '正常' : '异常' }}
                </n-tag>
              </div>
              <div class="status-item">
                <span class="status-label">API服务</span>
                <n-tag :type="systemStatus.api ? 'success' : 'error'">
                  {{ systemStatus.api ? '正常' : '异常' }}
                </n-tag>
              </div>
              <div class="status-item">
                <span class="status-label">缓存服务</span>
                <n-tag :type="systemStatus.cache ? 'success' : 'error'">
                  {{ systemStatus.cache ? '正常' : '异常' }}
                </n-tag>
              </div>
            </div>
          </n-card>
        </n-grid-item>

        <n-grid-item>
          <n-card title="缓存监控" hoverable>
            <template #header-extra>
              <n-button
                size="small"
                type="primary"
                @click="refreshCacheStats"
                :loading="cacheLoading"
              >
                刷新
              </n-button>
            </template>
            <div class="cache-monitor">
              <div class="cache-metric">
                <span class="metric-label">总请求数</span>
                <span class="metric-value">{{ cacheStats.total_requests }}</span>
              </div>
              <div class="cache-metric">
                <span class="metric-label">命中次数</span>
                <span class="metric-value">{{ cacheStats.hits }}</span>
              </div>
              <div class="cache-metric">
                <span class="metric-label">未命中次数</span>
                <span class="metric-value">{{ cacheStats.misses }}</span>
              </div>
              <div class="cache-metric">
                <span class="metric-label">最后更新</span>
                <span class="metric-value">{{ formatCacheTime(cacheStats.last_updated) }}</span>
              </div>
              <div class="cache-actions">
                <n-button
                  size="small"
                  type="warning"
                  @click="handleClearCache"
                  :loading="clearingCache"
                >
                  清空缓存
                </n-button>
              </div>
            </div>
          </n-card>
        </n-grid-item>
      </n-grid>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NCard, NIcon, NGrid, NGridItem, NList, NListItem, NTag, NButton, useMessage } from 'naive-ui'
import { People, Calendar, Settings, TrendingUp, Flash, Server } from '@vicons/ionicons5'
import { apiClient, type CacheStats } from '@/services/api'

const message = useMessage()

// 统计数据
const memberStats = ref({
  total: 0
})

const activityStats = ref({
  total: 0
})

const configStats = ref({
  total: 0
})

const systemStats = ref({
  uptime: '0天'
})

// 缓存统计数据
const cacheStats = ref<CacheStats>({
  hits: 0,
  misses: 0,
  total_requests: 0,
  hit_rate: 0,
  cache_size: 0,
  max_size: 0,
  last_updated: ''
})

// 加载状态
const cacheLoading = ref(false)
const clearingCache = ref(false)

// 最近活动
const recentActivities = ref([
  {
    id: 1,
    title: '系统初始化',
    description: '管理系统初始化完成',
    date: new Date()
  }
])

// 系统状态
const systemStatus = ref({
  database: true,
  api: true,
  cache: true
})

// 格式化日期
const formatDate = (date: Date) => {
  return date.toLocaleDateString('zh-CN')
}

// 格式化百分比
const formatPercentage = (rate: number) => {
  return `${(rate * 100).toFixed(1)}%`
}

// 格式化缓存时间
const formatCacheTime = (timeStr: string) => {
  if (!timeStr) return '未知'
  try {
    const date = new Date(timeStr)
    return date.toLocaleTimeString('zh-CN')
  } catch {
    return '未知'
  }
}

// 加载缓存统计
const loadCacheStats = async () => {
  try {
    cacheLoading.value = true
    const stats = await apiClient.getCacheStats()
    cacheStats.value = stats

    // 更新系统状态中的缓存服务状态
    systemStatus.value.cache = true
  } catch (error) {
    console.error('加载缓存统计失败:', error)
    systemStatus.value.cache = false
  } finally {
    cacheLoading.value = false
  }
}

// 刷新缓存统计
const refreshCacheStats = async () => {
  await loadCacheStats()
}

// 清空缓存
const handleClearCache = async () => {
  try {
    clearingCache.value = true
    const result = await apiClient.clearCache()

    if (result.success) {
      message.success('缓存已清空')
      // 刷新统计数据
      await loadCacheStats()
    } else {
      message.error('清空缓存失败')
    }
  } catch (error) {
    console.error('清空缓存失败:', error)
    message.error('清空缓存失败')
  } finally {
    clearingCache.value = false
  }
}

// 加载数据
const loadDashboardData = async () => {
  try {
    // TODO: 调用API获取实际数据
    memberStats.value.total = 42
    activityStats.value.total = 8
    configStats.value.total = 15
    systemStats.value.uptime = '7天'

    // 加载缓存统计
    await loadCacheStats()
  } catch (error) {
    console.error('加载仪表板数据失败:', error)
  }
}

onMounted(() => {
  loadDashboardData()
})
</script>

<style scoped lang="scss">
.dashboard {
  padding: 24px;
  
  &-header {
    margin-bottom: 24px;
    
    h1 {
      margin: 0 0 8px 0;
      font-size: 28px;
      font-weight: 600;
      color: var(--text-primary);
    }

    p {
      margin: 0;
      color: var(--text-secondary);
      font-size: 16px;
    }
  }
  
  &-content {
    margin-top: 24px;
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  .stat-content {
    display: flex;
    align-items: center;
    gap: 16px;
    
    .stat-icon {
      flex-shrink: 0;
    }
    
    .stat-info {
      h3 {
        margin: 0 0 4px 0;
        font-size: 24px;
        font-weight: 600;
        color: var(--text-primary);
      }

      p {
        margin: 0;
        color: var(--text-secondary);
        font-size: 14px;
      }
    }
  }
}

.activity-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  width: 100%;
  
  .activity-info {
    flex: 1;
    
    h4 {
      margin: 0 0 4px 0;
      font-size: 16px;
      font-weight: 500;
      color: var(--text-primary);
    }

    p {
      margin: 0;
      color: var(--text-secondary);
      font-size: 14px;
    }
  }
  
  .activity-date {
    color: var(--text-tertiary);
    font-size: 12px;
    white-space: nowrap;
    margin-left: 16px;
  }
}

.system-status {
  .status-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 0;
    border-bottom: 1px solid var(--border-secondary);

    &:last-child {
      border-bottom: none;
    }

    .status-label {
      font-weight: 500;
      color: var(--text-secondary);
    }
  }
}

.cache-monitor {
  .cache-metric {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;

    .metric-label {
      color: var(--text-secondary);
      font-size: 14px;
    }

    .metric-value {
      color: var(--text-primary);
      font-size: 14px;
      font-weight: 500;
    }
  }

  .cache-actions {
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid var(--border-secondary);

    .n-button {
      width: 100%;
    }
  }
}
</style>
