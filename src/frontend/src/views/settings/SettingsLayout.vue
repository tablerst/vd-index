<template>
  <div class="settings-layout">
    <!-- 侧边栏 -->
    <div class="sidebar">
      <div class="sidebar-header">
        <h2>管理系统</h2>
        <div class="user-info">
          <n-avatar size="small" :src="userAvatar" />
          <span class="username">{{ authStore.user?.username }}</span>
        </div>
      </div>
      
      <n-menu
        v-model:value="activeKey"
        :options="menuOptions"
        :root-indent="24"
        :indent="18"
        @update:value="handleMenuSelect"
      />
      
      <div class="sidebar-footer">
        <n-button
          text
          type="error"
          @click="handleLogout"
          style="width: 100%;"
        >
          <template #icon>
            <n-icon :component="LogOutOutline" />
          </template>
          退出登录
        </n-button>
      </div>
    </div>
    
    <!-- 主内容区 -->
    <div class="main-content">
      <div class="content-header">
        <n-breadcrumb>
          <n-breadcrumb-item>管理系统</n-breadcrumb-item>
          <n-breadcrumb-item>{{ currentPageTitle }}</n-breadcrumb-item>
        </n-breadcrumb>
      </div>
      
      <div class="content-body">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, h } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { 
  NMenu, 
  NAvatar, 
  NButton, 
  NIcon, 
  NBreadcrumb,
  NBreadcrumbItem,
  useMessage,
  type MenuOption
} from 'naive-ui'
import {
  PeopleOutline,
  CalendarOutline,
  BarChartOutline,
  SettingsOutline,
  ShieldCheckmarkOutline,
  LanguageOutline,
  LogOutOutline
} from '@vicons/ionicons5'
import { useAuthStore } from '@/stores/auth'

// 路由和状态管理
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const message = useMessage()

// 当前选中的菜单项
const activeKey = ref(route.name as string || 'member-management')

// 用户头像（默认头像）
const userAvatar = computed(() => {
  return `https://api.dicebear.com/7.x/avataaars/svg?seed=${authStore.user?.username}`
})

// 当前页面标题
const currentPageTitle = computed(() => {
  const menuItem = menuOptions.find(item => item.key === activeKey.value)
  return menuItem?.label || '管理系统'
})

// 菜单选项
const menuOptions: MenuOption[] = [
  {
    label: '成员管理',
    key: 'member-management',
    icon: () => h(NIcon, { component: PeopleOutline })
  },
  {
    label: '活动管理',
    key: 'activity-management',
    icon: () => h(NIcon, { component: CalendarOutline })
  },
  {
    label: '数据统计',
    key: 'data-statistics',
    icon: () => h(NIcon, { component: BarChartOutline })
  },
  {
    label: '权限管理',
    key: 'permission-management',
    icon: () => h(NIcon, { component: ShieldCheckmarkOutline })
  },
  {
    label: '系统配置',
    key: 'system-config',
    icon: () => h(NIcon, { component: SettingsOutline })
  },
  {
    label: '国际化',
    key: 'internationalization',
    icon: () => h(NIcon, { component: LanguageOutline })
  }
]

// 处理菜单选择
const handleMenuSelect = (key: string) => {
  activeKey.value = key
  router.push({ name: key })
}

// 处理登出
const handleLogout = async () => {
  try {
    await authStore.logout()
    message.success('已退出登录')
    router.push('/login')
  } catch (error) {
    console.error('登出失败:', error)
    message.error('登出失败')
  }
}
</script>

<style scoped>
.settings-layout {
  display: flex;
  height: 100vh;
  background: #f5f5f5;
}

.sidebar {
  width: 260px;
  background: #fff;
  border-right: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
}

.sidebar-header {
  padding: 24px 20px;
  border-bottom: 1px solid #e0e0e0;
}

.sidebar-header h2 {
  margin: 0 0 16px 0;
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.username {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

:deep(.n-menu) {
  flex: 1;
  padding: 16px 0;
}

.sidebar-footer {
  padding: 20px;
  border-top: 1px solid #e0e0e0;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.content-header {
  background: #fff;
  padding: 16px 24px;
  border-bottom: 1px solid #e0e0e0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.content-body {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background: #f5f5f5;
}

/* Microsoft Fluent Design System 样式 */
.sidebar {
  backdrop-filter: blur(30px);
  background: rgba(255, 255, 255, 0.9);
}

.content-header {
  backdrop-filter: blur(30px);
  background: rgba(255, 255, 255, 0.9);
}

:deep(.n-menu-item) {
  border-radius: 8px;
  margin: 2px 12px;
}

:deep(.n-menu-item--selected) {
  background: rgba(0, 120, 212, 0.1);
  color: #0078d4;
}

:deep(.n-menu-item:hover) {
  background: rgba(0, 120, 212, 0.05);
}

:deep(.n-button) {
  border-radius: 6px;
}

:deep(.n-breadcrumb) {
  font-size: 14px;
}
</style>
