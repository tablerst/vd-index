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
import { ref, computed, h, onMounted, onUnmounted } from 'vue'
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
  LogOutOutline
} from '@vicons/ionicons5'
import { useAuthStore } from '@/stores/auth'
import { RevealEffect } from '@/utils/fluentEffects'

// 路由和状态管理
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const message = useMessage()

// 当前选中的菜单项
const activeKey = ref(route.name as string || 'dashboard')

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
    label: '仪表板',
    key: 'dashboard',
    icon: () => h(NIcon, { component: BarChartOutline })
  },
  {
    label: '成员管理',
    key: 'members',
    icon: () => h(NIcon, { component: PeopleOutline })
  },
  {
    label: '活动管理',
    key: 'activities',
    icon: () => h(NIcon, { component: CalendarOutline })
  },
  {
    label: '配置管理',
    key: 'configs',
    icon: () => h(NIcon, { component: SettingsOutline })
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

// Reveal 效果
let revealEffects: RevealEffect[] = []

onMounted(() => {
  // 为侧边栏添加 Reveal 效果
  const sidebar = document.querySelector('.sidebar') as HTMLElement
  if (sidebar) {
    revealEffects.push(new RevealEffect(sidebar))
  }

  // 为菜单项添加 Reveal 效果
  setTimeout(() => {
    const menuItems = document.querySelectorAll('.n-menu-item') as NodeListOf<HTMLElement>
    menuItems.forEach(item => {
      revealEffects.push(new RevealEffect(item))
    })
  }, 100)
})

onUnmounted(() => {
  revealEffects.forEach(effect => effect.destroy())
  revealEffects = []
})
</script>

<style scoped lang="scss">
@import '@/styles/settings.scss';

// 所有样式已移至 @/styles/settings.scss 文件中，避免样式污染
</style>
