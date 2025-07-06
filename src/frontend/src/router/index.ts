/**
 * Vue Router 配置
 * 支持主界面和后台管理系统的路由
 */
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// 路由组件懒加载
const Home = () => import('@/views/Home.vue')
const Login = () => import('@/views/Login.vue')
const SettingsLayout = () => import('@/views/settings/SettingsLayout.vue')
const MemberManagement = () => import('@/views/settings/MemberManagement.vue')
// const ActivityManagement = () => import('@/views/settings/ActivityManagement.vue')
// const ConfigManagement = () => import('@/views/settings/ConfigManagement.vue')
// const Dashboard = () => import('@/views/settings/Dashboard.vue')

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
        redirect: '/settings/member-management'
      },
      {
        path: 'member-management',
        name: 'member-management',
        component: MemberManagement,
        meta: {
          title: '成员管理',
          icon: 'people-outline'
        }
      },
      // 其他管理页面将在后续阶段实现
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

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // 设置页面标题
  if (to.meta.title) {
    document.title = to.meta.title as string
  }
  
  // 检查是否需要认证
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      // 未登录，跳转到登录页
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
      return
    }
  }
  
  // 已登录用户访问登录页，重定向到设置页
  if (to.meta.hideForAuth && authStore.isAuthenticated) {
    next('/settings')
    return
  }
  
  next()
})

export default router
