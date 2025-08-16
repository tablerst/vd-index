/**
 * JWT Token 管理工具
 * 处理token的存储、验证和刷新
 */

const TOKEN_KEY = 'access_token'
const REFRESH_TOKEN_KEY = 'refresh_token'
const USER_KEY = 'user'

/**
 * Token 存储管理
 */
export class TokenManager {
  /**
   * 获取访问令牌
   */
  static getAccessToken(): string | null {
    return localStorage.getItem(TOKEN_KEY)
  }

  /**
   * 设置访问令牌
   */
  static setAccessToken(token: string): void {
    localStorage.setItem(TOKEN_KEY, token)
  }

  /**
   * 获取刷新令牌
   */
  static getRefreshToken(): string | null {
    return localStorage.getItem(REFRESH_TOKEN_KEY)
  }

  /**
   * 设置刷新令牌
   */
  static setRefreshToken(token: string): void {
    localStorage.setItem(REFRESH_TOKEN_KEY, token)
  }

  /**
   * 获取用户信息
   */
  static getUser(): any | null {
    const userStr = localStorage.getItem(USER_KEY)
    if (!userStr) return null
    
    try {
      return JSON.parse(userStr)
    } catch (error) {
      console.error('Failed to parse user data:', error)
      return null
    }
  }

  /**
   * 设置用户信息
   */
  static setUser(user: any): void {
    localStorage.setItem(USER_KEY, JSON.stringify(user))
  }

  /**
   * 清除所有认证信息
   */
  static clear(): void {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  }

  /**
   * 检查token是否存在
   */
  static hasToken(): boolean {
    return !!this.getAccessToken()
  }

  /**
   * 检查token是否过期
   */
  static isTokenExpired(token?: string): boolean {
    const accessToken = token || this.getAccessToken()
    if (!accessToken) return true

    try {
      const payload = this.parseJWT(accessToken)
      if (!payload.exp) return false

      // 检查是否在5分钟内过期（提前刷新）
      const expirationTime = payload.exp * 1000
      const currentTime = Date.now()
      const bufferTime = 5 * 60 * 1000 // 5分钟缓冲

      return currentTime >= (expirationTime - bufferTime)
    } catch (error) {
      console.error('Failed to parse token:', error)
      return true
    }
  }

  /**
   * 解析JWT token
   */
  static parseJWT(token: string): any {
    try {
      const base64Url = token.split('.')[1]
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      )
      return JSON.parse(jsonPayload)
    } catch (error) {
      throw new Error('Invalid token format')
    }
  }

  /**
   * 获取token的过期时间
   */
  static getTokenExpiration(token?: string): Date | null {
    const accessToken = token || this.getAccessToken()
    if (!accessToken) return null

    try {
      const payload = this.parseJWT(accessToken)
      if (!payload.exp) return null

      return new Date(payload.exp * 1000)
    } catch (error) {
      return null
    }
  }

  /**
   * 获取token中的用户信息
   */
  static getTokenUser(token?: string): any | null {
    const accessToken = token || this.getAccessToken()
    if (!accessToken) return null

    try {
      const payload = this.parseJWT(accessToken)
      return {
        id: payload.sub,
        username: payload.username,
        role: payload.role,
        ...payload
      }
    } catch (error) {
      return null
    }
  }
}

/**
 * Token 刷新管理
 */
export class TokenRefreshManager {
  private static refreshPromise: Promise<string | null> | null = null

  /**
   * 刷新访问令牌
   */
  static async refreshAccessToken(): Promise<string | null> {
    // 防止并发刷新
    if (this.refreshPromise) {
      return this.refreshPromise
    }

    const refreshToken = TokenManager.getRefreshToken()
    if (!refreshToken) {
      return null
    }

    this.refreshPromise = this.performRefresh(refreshToken)
    
    try {
      const newToken = await this.refreshPromise
      return newToken
    } finally {
      this.refreshPromise = null
    }
  }

  /**
   * 执行token刷新
   */
  private static async performRefresh(refreshToken: string): Promise<string | null> {
    try {
      // 这里应该调用后端的刷新接口
      const response = await fetch('/api/v1/auth/refresh', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken })
      })

      if (!response.ok) {
        throw new Error('Token refresh failed')
      }

      const data = await response.json()
      
      // 更新token
      TokenManager.setAccessToken(data.access_token)
      if (data.refresh_token) {
        TokenManager.setRefreshToken(data.refresh_token)
      }
      if (data.user) {
        TokenManager.setUser(data.user)
      }

      return data.access_token
    } catch (error) {
      console.error('Token refresh failed:', error)
      // 刷新失败，清除所有认证信息
      TokenManager.clear()
      return null
    }
  }

  /**
   * 自动刷新token
   */
  static async autoRefreshToken(): Promise<boolean> {
    const token = TokenManager.getAccessToken()
    if (!token) return false

    if (TokenManager.isTokenExpired(token)) {
      const newToken = await this.refreshAccessToken()
      return !!newToken
    }

    return true
  }
}

/**
 * 请求拦截器助手
 */
export class RequestInterceptor {
  /**
   * 为请求添加认证头
   */
  static addAuthHeader(config: any): any {
    const token = TokenManager.getAccessToken()
    if (token) {
      config.headers = config.headers || {}
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  }

  /**
   * 处理认证错误响应
   */
  static async handleAuthError(error: any): Promise<any> {
    const originalRequest = error.config || {}
    const url: string | undefined = originalRequest.url || error?.config?.url

    // 对登录/注册等认证端点：交给调用方自行处理错误，不要全局跳转
    if (error.response?.status === 401 && url && (
      url.includes('/api/v1/auth/login') ||
      url.includes('/api/v1/auth/register')
    )) {
      return Promise.reject(error)
    }

    // 如果是401错误且还没有重试过
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      // 尝试刷新token
      const newToken = await TokenRefreshManager.refreshAccessToken()
      if (newToken) {
        // 更新请求头并重试
        originalRequest.headers = originalRequest.headers || {}
        originalRequest.headers.Authorization = `Bearer ${newToken}`
        return originalRequest
      } else {
        // 无可用token或刷新失败：若当前本就未登录，则不强制跳转，交给调用方处理
        try {
          const hasToken = !!TokenManager.getAccessToken()
          if (!hasToken) return Promise.reject(error)
        } catch {}
        // 已登录但刷新失败，回到登录页
        window.location.href = '/login'
        return Promise.reject(error)
      }
    }

    return Promise.reject(error)
  }
}

/**
 * 定时检查token状态
 */
export class TokenWatcher {
  private static intervalId: number | null = null
  private static readonly CHECK_INTERVAL = 60 * 1000 // 每分钟检查一次

  /**
   * 开始监控token状态
   */
  static start(): void {
    if (this.intervalId) return

    this.intervalId = window.setInterval(async () => {
      await TokenRefreshManager.autoRefreshToken()
    }, this.CHECK_INTERVAL)
  }

  /**
   * 停止监控token状态
   */
  static stop(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId)
      this.intervalId = null
    }
  }
}

// 导出默认实例
export default TokenManager
