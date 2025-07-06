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
@import '@/styles/fluent-theme.scss';

.settings-layout {
  display: flex;
  height: 100vh;
  background: var(--fluent-bg-layer);
  font-family: var(--fluent-font-family);
}

.sidebar {
  width: 280px;
  @include fluent-acrylic(0.9, 20px);
  border-right: 1px solid var(--fluent-border-default);
  display: flex;
  flex-direction: column;
  @include fluent-depth(8);
  position: relative;
  z-index: 10;

  // Reveal 效果
  @include fluent-reveal();
}

.sidebar-header {
  padding: var(--fluent-spacing-xxl) var(--fluent-spacing-xl);
  border-bottom: 1px solid var(--fluent-border-subtle);

  h2 {
    margin: 0 0 var(--fluent-spacing-lg) 0;
    @include fluent-typography(title);
    color: var(--fluent-text-primary);
  }
}

.user-info {
  display: flex;
  align-items: center;
  gap: var(--fluent-spacing-sm);
  padding: var(--fluent-spacing-sm) var(--fluent-spacing-md);
  border-radius: var(--fluent-radius-medium);
  @include fluent-motion();

  &:hover {
    background: var(--fluent-bg-subtle);
  }
}

.username {
  @include fluent-typography(body);
  color: var(--fluent-text-secondary);
  font-weight: var(--fluent-font-weight-medium);
}

:deep(.n-menu) {
  flex: 1;
  padding: var(--fluent-spacing-lg) 0;
  background: transparent;
}

:deep(.n-menu-item) {
  border-radius: var(--fluent-radius-large);
  margin: 2px var(--fluent-spacing-md);
  @include fluent-motion();
  position: relative;
  overflow: hidden;

  // Reveal 效果
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(circle at var(--mouse-x, 50%) var(--mouse-y, 50%),
                               rgba(0, 120, 212, 0.1) 0%,
                               transparent 50%);
    opacity: 0;
    transition: opacity var(--fluent-duration-fast) var(--fluent-ease-standard);
    pointer-events: none;
  }

  &:hover::before {
    opacity: 1;
  }
}

:deep(.n-menu-item--selected) {
  background: var(--fluent-primary-light);
  color: var(--fluent-primary);
  font-weight: var(--fluent-font-weight-medium);

  .n-menu-item-content-header {
    color: var(--fluent-primary);
  }
}

:deep(.n-menu-item:hover) {
  background: var(--fluent-bg-subtle);
}

:deep(.n-menu-item-content) {
  @include fluent-typography(body);
}

.sidebar-footer {
  padding: var(--fluent-spacing-xl);
  border-top: 1px solid var(--fluent-border-subtle);
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--fluent-bg-canvas);
}

.content-header {
  @include fluent-acrylic(0.95, 15px);
  padding: var(--fluent-spacing-lg) var(--fluent-spacing-xxl);
  border-bottom: 1px solid var(--fluent-border-subtle);
  @include fluent-depth(2);
  position: relative;
  z-index: 5;
}

.content-body {
  flex: 1;
  padding: var(--fluent-spacing-xxl);
  overflow-y: auto;
  background: var(--fluent-bg-layer);

  // 自定义滚动条
  &::-webkit-scrollbar {
    width: 8px;
  }

  &::-webkit-scrollbar-track {
    background: var(--fluent-bg-subtle);
  }

  &::-webkit-scrollbar-thumb {
    background: var(--fluent-neutral-grey-20);
    border-radius: var(--fluent-radius-medium);

    &:hover {
      background: var(--fluent-neutral-grey-24);
    }
  }
}

// 按钮样式增强
:deep(.n-button) {
  border-radius: var(--fluent-radius-medium);
  font-weight: var(--fluent-font-weight-medium);
  @include fluent-motion();

  &:hover {
    @include fluent-depth(4);
  }

  &:active {
    @include fluent-depth(2);
  }
}

// 面包屑样式
:deep(.n-breadcrumb) {
  @include fluent-typography(body);

  .n-breadcrumb-item {
    color: var(--fluent-text-secondary);

    &:last-child {
      color: var(--fluent-text-primary);
      font-weight: var(--fluent-font-weight-medium);
    }
  }
}

// 头像样式
:deep(.n-avatar) {
  @include fluent-depth(2);
  @include fluent-motion();

  &:hover {
    @include fluent-depth(4);
  }
}

// 响应式设计
@media (max-width: 768px) {
  .sidebar {
    width: 240px;
  }

  .content-body {
    padding: var(--fluent-spacing-lg);
  }
}

@media (max-width: 640px) {
  .settings-layout {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    height: auto;
    border-right: none;
    border-bottom: 1px solid var(--fluent-border-default);
  }

  :deep(.n-menu) {
    padding: var(--fluent-spacing-sm) 0;
  }

  :deep(.n-menu-item) {
    margin: 1px var(--fluent-spacing-sm);
  }
}
</style>
