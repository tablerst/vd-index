/**
 * 认证状态管理
 * 处理用户登录、登出和认证状态
 */
import { defineStore } from 'pinia'
import { ref, computed, readonly } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/services/api'
import { TokenManager, TokenWatcher } from '@/utils/token'

export interface User {
  id: number
  username: string
  role: string
  is_active: boolean
  created_at: string
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

export type RegisterResponse = LoginResponse

export const useAuthStore = defineStore('auth', () => {
  const router = useRouter()
  
  // 状态
  const user = ref<User | null>(TokenManager.getUser())
  const token = ref<string | null>(TokenManager.getAccessToken())
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  
  // 计算属性
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  
  // 设置认证信息
  const setAuth = (authData: LoginResponse) => {
    token.value = authData.access_token
    user.value = authData.user
    TokenManager.setAccessToken(authData.access_token)
    TokenManager.setUser(authData.user)

    // 开始token监控
    TokenWatcher.start()
  }

  // 清除认证信息
  const clearAuth = () => {
    token.value = null
    user.value = null
    TokenManager.clear()

    // 停止token监控
    TokenWatcher.stop()
  }
  
  // 登录
  const login = async (credentials: LoginCredentials) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await api.post<LoginResponse>('/api/v1/auth/login', credentials)
      setAuth(response.data)
      
      // 登录成功后跳转
      const redirect = router.currentRoute.value.query.redirect as string
      await router.push(redirect || '/settings')
      
      return true
    } catch (err: any) {
      error.value = err.response?.data?.message || '登录失败'
      return false
    } finally {
      isLoading.value = false
    }
  }
  
  // 注册（不自动跳转，交给调用者控制后续绑定流程）
  const register = async (credentials: LoginCredentials) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.post<RegisterResponse>('/api/v1/auth/register', credentials)
      setAuth(response.data)
      return true
    } catch (err: any) {
      error.value = err.response?.data?.message || '注册失败'
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 登出
  const logout = async () => {
    try {
      // 可以调用后端登出接口
      // await api.post('/api/v1/auth/logout')
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      clearAuth()
      await router.push('/')
    }
  }

  // 验证token有效性
  const validateToken = async () => {
    if (!token.value) return false

    // 检查token是否过期
    if (TokenManager.isTokenExpired(token.value)) {
      clearAuth()
      return false
    }

    try {
      const response = await api.get<User>('/api/v1/auth/me')
      user.value = response.data
      TokenManager.setUser(response.data)
      return true
    } catch (err) {
      console.error('Token validation failed:', err)
      clearAuth()
      return false
    }
  }

  // 初始化认证状态
  const initAuth = () => {
    if (TokenManager.hasToken() && !TokenManager.isTokenExpired()) {
      // 如果有有效token，开始监控
      TokenWatcher.start()
    } else {
      // 清除无效token
      clearAuth()
    }
  }

  // 初始化
  initAuth()
  
  return {
    // 状态
    user: readonly(user),
    token: readonly(token),
    isLoading: readonly(isLoading),
    error: readonly(error),
    
    // 计算属性
    isAuthenticated,
    
    // 方法
    login,
    register,
    logout,
    validateToken,
    clearAuth
  }
})
