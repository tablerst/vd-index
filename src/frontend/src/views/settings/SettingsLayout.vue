<template>
  <div class="settings-layout">
    <!-- 侧边栏 -->
    <div class="sidebar">
      <div class="sidebar-header">
        <h2>管理系统</h2>
        <div class="header-right">
          <div class="user-info">
            <n-avatar size="small" :src="userAvatar" />
            <span class="username">{{ authStore.user?.username }}</span>
          </div>
          <div class="theme-switcher" ref="themeSwitcherRef">
            <n-switch
              ref="switchRef"
              v-model:value="switchValue"
              size="small"
              :checked-value="true"
              :unchecked-value="false"
              :rail-style="railStyle"
            >
              <template #checked>
                <n-icon size="14" :component="MoonOutline" />
              </template>
              <template #unchecked>
                <n-icon size="14" :component="SunnyOutline" />
              </template>
            </n-switch>
          </div>
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
  NSwitch,
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
  LogOutOutline,
  MoonOutline,
  SunnyOutline
} from '@vicons/ionicons5'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { storeToRefs } from 'pinia'
import { RevealEffect } from '@/utils/fluentEffects'
import { gsap } from 'gsap'


// 主题切换
const themeStore = useThemeStore()
// 使用 storeToRefs 保持响应式（避免被解构为普通 boolean）
const { isDark: isDarkTheme } = storeToRefs(themeStore)
const switchValue = computed({
  get: () => isDarkTheme.value,
  set: (val: boolean) => { animateThemeSwitch(); themeStore.setTheme(val ? 'dark' : 'light') }
})
const railStyle = ({ focused, checked }: { focused: boolean; checked: boolean }) => {
  const style: Record<string, string> = {}
  style.background = checked ? 'var(--primary-gradient)' : 'var(--surface-2)'
  style.border = '1px solid var(--border-primary)'
  if (focused) style.boxShadow = 'var(--shadow-glow)'
  return style
}
// refs for theme switcher animations
const themeSwitcherRef = ref<HTMLElement | null>(null)
const switchRef = ref<any>(null)

// animate on toggle
const animateThemeSwitch = () => {
  if (!switchRef.value) return
  const switchEl = switchRef.value.$el
  const rail = switchEl?.querySelector('.n-switch__rail') as HTMLElement | null
  const button = switchEl?.querySelector('.n-switch__button') as HTMLElement | null
  if (rail && button) {
    const tl = gsap.timeline()
    tl.to(rail, { scale: 1.05, duration: 0.15, ease: 'power2.out' })
      .to(rail, { scale: 1, duration: 0.2, ease: 'elastic.out(1, 0.5)' })
      .to(button, { scale: 1.1, duration: 0.1, ease: 'power2.out' }, 0)
      .to(button, { scale: 1, duration: 0.3, ease: 'elastic.out(1, 0.6)' })
  }
}

// init hover animations
let cleanupHover: (() => void) | undefined
const initThemeSwitcherAnimations = () => {
  if (!switchRef.value) return
  const switchEl = switchRef.value.$el
  const rail = switchEl?.querySelector('.n-switch__rail') as HTMLElement | null
  const button = switchEl?.querySelector('.n-switch__button') as HTMLElement | null
  if (rail && button) {
    const onEnter = () => {
      gsap.to(rail, { y: -2, boxShadow: 'var(--shadow-glow)', duration: 0.3, ease: 'power2.out' })
      gsap.to(button, { scale: 1.05, duration: 0.3, ease: 'power2.out' })
    }
    const onLeave = () => {
      gsap.to(rail, { y: 0, boxShadow: '0 4px 12px rgba(0,0,0,0.12)', duration: 0.3, ease: 'power2.out' })
      gsap.to(button, { scale: 1, duration: 0.3, ease: 'power2.out' })
    }
    switchEl.addEventListener('mouseenter', onEnter)
    switchEl.addEventListener('mouseleave', onLeave)
    cleanupHover = () => {
      switchEl.removeEventListener('mouseenter', onEnter)
      switchEl.removeEventListener('mouseleave', onLeave)
    }
  }
}




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

  // 初始化主题切换器悬停动效
  initThemeSwitcherAnimations()
})

onUnmounted(() => {
  revealEffects.forEach(effect => effect.destroy())
  revealEffects = []
  if (cleanupHover) cleanupHover()
})
</script>

<style scoped lang="scss">
@import '@/styles/settings.scss';

// 所有样式已移至 @/styles/settings.scss 文件中，避免样式污染
</style>
