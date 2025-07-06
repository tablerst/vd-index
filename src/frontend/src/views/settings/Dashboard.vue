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
            <n-icon size="32" color="#0078D4">
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
            <n-icon size="32" color="#107C10">
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
            <n-icon size="32" color="#FF8C00">
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
    </div>

    <div class="dashboard-content">
      <n-grid :cols="2" :x-gap="16" :y-gap="16">
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
      </n-grid>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NCard, NIcon, NGrid, NGridItem, NList, NListItem, NTag } from 'naive-ui'
import { People, Calendar, Settings, TrendingUp } from '@vicons/ionicons5'

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

// 加载数据
const loadDashboardData = async () => {
  try {
    // TODO: 调用API获取实际数据
    memberStats.value.total = 42
    activityStats.value.total = 8
    configStats.value.total = 15
    systemStats.value.uptime = '7天'
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
      color: #1f2937;
    }
    
    p {
      margin: 0;
      color: #6b7280;
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
        color: #1f2937;
      }
      
      p {
        margin: 0;
        color: #6b7280;
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
      color: #1f2937;
    }
    
    p {
      margin: 0;
      color: #6b7280;
      font-size: 14px;
    }
  }
  
  .activity-date {
    color: #9ca3af;
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
    border-bottom: 1px solid #f3f4f6;
    
    &:last-child {
      border-bottom: none;
    }
    
    .status-label {
      font-weight: 500;
      color: #374151;
    }
  }
}
</style>
