/**
 * 路由守卫
 * 处理认证检查和权限控制
 */
import type { Router } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

/**
 * 设置路由守卫
 */
export function setupRouterGuards(router: Router) {
  // 全局前置守卫
  router.beforeEach(async (to, _from, next) => {
    const authStore = useAuthStore()
    
    // Special handling for /login route: redirect authenticated users by role
    // Admin -> /settings; Non-admin -> /
    if (to.path === '/login') {
      if (authStore.isAuthenticated) {
        next(authStore.user?.role === 'admin' ? '/settings' : '/')
        return
      }
      next()
      return
    }

    // 检查是否需要认证
    const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
    
    // 如果不需要认证，直接通过
    if (!requiresAuth) {
      next()
      return
    }
    
    // 检查是否已登录
    if (!authStore.isAuthenticated) {
      // 如果有token但没有用户信息，尝试验证token
      if (authStore.token) {
        try {
          const isValid = await authStore.validateToken()
          if (isValid) {
            next()
            return
          }
        } catch (error) {
          console.error('Token validation failed:', error)
        }
      }
      
      // 未登录，重定向到登录页
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
      return
    }
    
    // 检查角色权限
    const requiredRoles = to.meta.roles as string[] | undefined
    if (requiredRoles && requiredRoles.length > 0) {
      const userRole = authStore.user?.role
      if (!userRole || !requiredRoles.includes(userRole)) {
        // 权限不足，重定向到首页或显示错误页面
        next({
          path: '/',
          query: { error: 'insufficient_permissions' }
        })
        return
      }
    }
    
    // 通过所有检查
    next()
  })
  
  // 全局后置钩子
  router.afterEach((to, _from) => {
    // 更新页面标题
    if (to.meta.title) {
      document.title = `${to.meta.title} - VD群管理系统`
    } else {
      document.title = 'VD群管理系统'
    }
    
    // 记录路由变化（用于分析）
    if (import.meta.env.DEV) {
      console.log(`Route changed: ${_from.path} -> ${to.path}`)
    }
  })
  
  // 路由错误处理
  router.onError((error) => {
    console.error('Router error:', error)
    
    // 可以在这里添加错误上报逻辑
    if (import.meta.env.PROD) {
      // 上报错误到监控系统
      // reportError(error)
    }
  })
}

/**
 * 检查用户是否有指定权限
 */
export function hasPermission(permission: string): boolean {
  const authStore = useAuthStore()
  
  if (!authStore.isAuthenticated || !authStore.user) {
    return false
  }
  
  // 管理员拥有所有权限
  if (authStore.user.role === 'admin') {
    return true
  }
  
  // 这里可以根据实际需求实现更复杂的权限检查逻辑
  // 例如基于角色的权限系统 (RBAC)
  const rolePermissions: Record<string, string[]> = {
    admin: ['*'], // 管理员拥有所有权限
    moderator: [
      'members:read',
      'members:update',
      'activities:read',
      'activities:create',
      'activities:update',
      'activities:delete'
    ],
    user: [
      'members:read',
      'activities:read'
    ]
  }
  
  const userPermissions = rolePermissions[authStore.user.role] || []
  
  // 检查是否有通配符权限
  if (userPermissions.includes('*')) {
    return true
  }
  
  // 检查具体权限
  return userPermissions.includes(permission)
}

/**
 * 检查用户是否有指定角色
 */
export function hasRole(role: string): boolean {
  const authStore = useAuthStore()
  
  if (!authStore.isAuthenticated || !authStore.user) {
    return false
  }
  
  return authStore.user.role === role
}

/**
 * 检查用户是否是管理员
 */
export function isAdmin(): boolean {
  return hasRole('admin')
}

/**
 * 检查用户是否是版主
 */
export function isModerator(): boolean {
  return hasRole('moderator') || hasRole('admin')
}

/**
 * 路由元信息类型扩展
 */
declare module 'vue-router' {
  interface RouteMeta {
    // 是否需要认证
    requiresAuth?: boolean
    // 需要的角色
    roles?: string[]
    // 需要的权限
    permissions?: string[]
    // 页面标题
    title?: string
    // 页面图标
    icon?: string
    // 是否在菜单中隐藏
    hidden?: boolean
    // 菜单排序
    order?: number
  }
}
