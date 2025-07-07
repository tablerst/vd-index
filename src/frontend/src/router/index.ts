/**
 * Vue Router 配置
 * 支持主界面和后台管理系统的路由
 */
import { createRouter, createWebHistory } from 'vue-router'
import { setupRouterGuards } from './guards'

// 路由组件懒加载
const Home = () => import('@/views/Home.vue')
const BadgePreview = () => import('@/views/BadgePreview.vue')
const Login = () => import('@/views/Login.vue')
const SettingsLayout = () => import('@/views/settings/SettingsLayout.vue')
const MemberManagement = () => import('@/views/settings/MemberManagement.vue')
const ActivityManagement = () => import('@/views/settings/ActivityManagement.vue')
const ConfigManagement = () => import('@/views/settings/ConfigManagement.vue')
const Dashboard = () => import('@/views/settings/Dashboard.vue')

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: {
      title: 'VD Index - 群成员星云'
    }
  },
  {
    path: '/badge-preview',
    name: 'BadgePreview',
    component: BadgePreview,
    meta: {
      title: '3D徽章打印预览'
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: {
      title: '管理员登录',
      hideForAuth: true // 已登录用户隐藏
    }
  },
  {
    path: '/settings',
    component: SettingsLayout,
    meta: {
      requiresAuth: true,
      title: '后台管理'
    },
    children: [
      {
        path: '',
        redirect: '/settings/dashboard'
      },
      {
        path: 'dashboard',
        name: 'dashboard',
        component: Dashboard,
        meta: {
          title: '仪表板',
          icon: 'dashboard-outline',
          requiresAuth: true,
          permissions: ['dashboard:read']
        }
      },
      {
        path: 'members',
        name: 'members',
        component: MemberManagement,
        meta: {
          title: '成员管理',
          icon: 'people-outline',
          requiresAuth: true,
          permissions: ['members:read']
        }
      },
      {
        path: 'activities',
        name: 'activities',
        component: ActivityManagement,
        meta: {
          title: '活动管理',
          icon: 'calendar-outline',
          requiresAuth: true,
          permissions: ['activities:read']
        }
      },
      {
        path: 'configs',
        name: 'configs',
        component: ConfigManagement,
        meta: {
          title: '配置管理',
          icon: 'settings-outline',
          requiresAuth: true,
          roles: ['admin'],
          permissions: ['configs:read']
        }
      }
    ]
  },
  {
    // 404 页面
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 设置路由守卫
setupRouterGuards(router)

export default router
