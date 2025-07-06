/**
 * 后端API服务
 * 提供安全的成员数据访问接口
 */
import { TokenManager, RequestInterceptor, TokenRefreshManager } from '@/utils/token'

// API基础配置
// 在生产环境中使用相对路径，开发环境使用完整URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.PROD ? '' : 'http://localhost:8000')

// 成员接口定义（与后端保持一致）
export interface Member {
  id: number
  name: string
  avatar_url: string
  bio?: string
  join_date: string
  role: number
  group_nick?: string
  qq_nick?: string
}

export interface MemberDetail extends Member {
  level_point?: number
  level_value?: number
  q_age?: number
  last_speak_time?: string
}

export interface MemberListResponse {
  members: Member[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface MemberStats {
  total_members: number
  role_distribution: {
    群主: number
    管理员: number
    群员: number
  }
  join_year_stats: Record<string, number>
}

// 活动接口定义
export interface ParticipantInfo {
  id: number
  name: string
  avatar_url: string
}

export interface Activity {
  id: number
  title: string
  description: string
  date: string
  tags: string[]
  participants: ParticipantInfo[]
  participants_total: number
  created_at: string
  updated_at: string
}

export interface ActivityListResponse {
  activities: Activity[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface ActivityStats {
  total_activities: number
  total_participants: number
  unique_participants: number
}

export interface ActivityCreateRequest {
  title: string
  description: string
  date: string
  tags: string[]
  participant_ids: number[]
}

export interface ActivityUpdateRequest {
  title?: string
  description?: string
  date?: string
  tags?: string[]
  participant_ids?: number[]
}

// 配置接口定义
export interface Config {
  id: number
  key: string
  value: string
  description: string
  type: 'string' | 'number' | 'boolean' | 'json'
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface ConfigListResponse {
  configs: Config[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface ConfigCreateRequest {
  key: string
  value: string
  description: string
  type: 'string' | 'number' | 'boolean' | 'json'
  is_active: boolean
}

export interface ConfigUpdateRequest {
  value?: string
  description?: string
  type?: 'string' | 'number' | 'boolean' | 'json'
  is_active?: boolean
}

// HTTP客户端类
class ApiClient {
  private baseURL: string

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`

    // 检查并刷新token
    await TokenRefreshManager.autoRefreshToken()

    // 添加认证头
    const config = RequestInterceptor.addAuthHeader({
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    })

    try {
      const response = await fetch(url, config)

      if (!response.ok) {
        // 处理认证错误
        if (response.status === 401) {
          const retryConfig = await RequestInterceptor.handleAuthError({
            response,
            config: { ...config, url }
          })

          if (retryConfig) {
            // 重试请求
            const retryResponse = await fetch(url, retryConfig)
            if (retryResponse.ok) {
              return await retryResponse.json()
            }
          }
        }

        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      console.error(`API请求失败: ${endpoint}`, error)
      throw error
    }
  }

  // 认证相关方法
  async login(credentials: { username: string; password: string }): Promise<any> {
    const formData = new FormData()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)

    return this.request('/api/v1/auth/login', {
      method: 'POST',
      headers: {
        // 移除Content-Type，让浏览器自动设置multipart/form-data
      },
      body: formData
    })
  }

  async getCurrentUser(): Promise<any> {
    return this.request('/api/v1/auth/me')
  }

  async logout(): Promise<any> {
    return this.request('/api/v1/auth/logout', {
      method: 'POST'
    })
  }

  // 获取成员列表
  async getMembers(page: number = 1, pageSize: number = 50): Promise<MemberListResponse> {
    return this.request<MemberListResponse>(
      `/api/v1/members?page=${page}&page_size=${pageSize}`
    )
  }

  // 获取成员详情
  async getMemberDetail(memberId: number): Promise<MemberDetail> {
    return this.request<MemberDetail>(`/api/v1/members/${memberId}`)
  }

  // 获取成员统计信息
  async getMemberStats(): Promise<MemberStats> {
    return this.request<MemberStats>('/api/v1/members/stats')
  }

  // 获取头像URL（直接返回URL，由浏览器处理缓存）
  getAvatarUrl(memberId: number): string {
    return `${this.baseURL}/api/v1/avatar/${memberId}`
  }

  // 获取活动列表
  async getActivities(page: number = 1, pageSize: number = 10): Promise<ActivityListResponse> {
    return this.request<ActivityListResponse>(
      `/api/v1/star_calendar/activities?page=${page}&page_size=${pageSize}`
    )
  }

  // 获取活动统计信息
  async getActivityStats(): Promise<ActivityStats> {
    return this.request<ActivityStats>('/api/v1/star_calendar/activities/stats')
  }

  // 获取单个活动详情
  async getActivity(activityId: number): Promise<Activity> {
    return this.request<Activity>(`/api/v1/star_calendar/activity/${activityId}`)
  }

  // 创建活动
  async createActivity(activityData: ActivityCreateRequest): Promise<Activity> {
    return this.request<Activity>('/api/v1/star_calendar/activity/create', {
      method: 'POST',
      body: JSON.stringify(activityData)
    })
  }

  // 更新活动
  async updateActivity(activityId: number, activityData: ActivityUpdateRequest): Promise<Activity> {
    return this.request<Activity>(`/api/v1/star_calendar/activity/update/${activityId}`, {
      method: 'PUT',
      body: JSON.stringify(activityData)
    })
  }

  // 删除活动
  async deleteActivity(activityId: number): Promise<{ success: boolean; message: string }> {
    return this.request<{ success: boolean; message: string }>(`/api/v1/star_calendar/activity/delete/${activityId}`, {
      method: 'DELETE'
    })
  }

  // 获取配置列表
  async getConfigs(page: number = 1, pageSize: number = 10): Promise<ConfigListResponse> {
    return this.request<ConfigListResponse>(
      `/api/v1/configs?page=${page}&page_size=${pageSize}`
    )
  }

  // 获取单个配置
  async getConfig(configId: number): Promise<Config> {
    return this.request<Config>(`/api/v1/configs/${configId}`)
  }

  // 根据键获取配置
  async getConfigByKey(key: string): Promise<Config> {
    return this.request<Config>(`/api/v1/configs/key/${key}`)
  }

  // 创建配置
  async createConfig(configData: ConfigCreateRequest): Promise<Config> {
    return this.request<Config>('/api/v1/configs', {
      method: 'POST',
      body: JSON.stringify(configData)
    })
  }

  // 更新配置
  async updateConfig(configId: number, configData: ConfigUpdateRequest): Promise<Config> {
    return this.request<Config>(`/api/v1/configs/${configId}`, {
      method: 'PUT',
      body: JSON.stringify(configData)
    })
  }

  // 删除配置
  async deleteConfig(configId: number): Promise<{ success: boolean; message: string }> {
    return this.request<{ success: boolean; message: string }>(`/api/v1/configs/${configId}`, {
      method: 'DELETE'
    })
  }

  // 健康检查
  async healthCheck(): Promise<{ status: string; timestamp: number }> {
    return this.request('/health')
  }
}

// 创建全局API客户端实例
export const apiClient = new ApiClient()

// 简化的API接口，用于auth store
export const api = {
  post: async <T>(endpoint: string, data: any): Promise<{ data: T }> => {
    if (endpoint === '/api/v1/auth/login') {
      const result = await apiClient.login(data)
      return { data: result }
    }
    throw new Error(`Unsupported endpoint: ${endpoint}`)
  },
  get: async <T>(endpoint: string): Promise<{ data: T }> => {
    if (endpoint === '/api/v1/auth/me') {
      const result = await apiClient.getCurrentUser()
      return { data: result }
    }
    throw new Error(`Unsupported endpoint: ${endpoint}`)
  }
}

// 便捷函数
export const memberApi = {
  // 获取所有成员（自动处理分页）
  async getAllMembers(): Promise<Member[]> {
    const firstPage = await apiClient.getMembers(1, 50)
    const allMembers = [...firstPage.members]
    
    // 如果有多页，继续获取
    if (firstPage.total_pages > 1) {
      const promises = []
      for (let page = 2; page <= firstPage.total_pages; page++) {
        promises.push(apiClient.getMembers(page, 50))
      }
      
      const additionalPages = await Promise.all(promises)
      additionalPages.forEach(pageData => {
        allMembers.push(...pageData.members)
      })
    }
    
    return allMembers
  },

  // 获取分页成员
  async getMembers(page: number = 1, pageSize: number = 50): Promise<MemberListResponse> {
    return apiClient.getMembers(page, pageSize)
  },

  // 获取成员详情
  async getMemberDetail(memberId: number): Promise<MemberDetail> {
    return apiClient.getMemberDetail(memberId)
  },

  // 获取统计信息
  async getStats(): Promise<MemberStats> {
    return apiClient.getMemberStats()
  },

  // 获取头像URL
  getAvatarUrl(memberId: number): string {
    return apiClient.getAvatarUrl(memberId)
  },

  // 从avatar_url中提取成员ID
  extractMemberId(avatarUrl: string): number {
    const match = avatarUrl.match(/\/api\/v1\/avatar\/(\d+)/)
    return match ? parseInt(match[1], 10) : 0
  }
}

// 活动API便捷函数
export const activityApi = {
  // 获取所有活动（自动处理分页）
  async getAllActivities(): Promise<Activity[]> {
    const firstPage = await apiClient.getActivities(1, 50)
    const allActivities = [...firstPage.activities]

    // 如果有多页，继续获取
    if (firstPage.total_pages > 1) {
      const promises = []
      for (let page = 2; page <= firstPage.total_pages; page++) {
        promises.push(apiClient.getActivities(page, 50))
      }

      const additionalPages = await Promise.all(promises)
      additionalPages.forEach(pageData => {
        allActivities.push(...pageData.activities)
      })
    }

    return allActivities
  },

  // 获取分页活动
  async getActivities(page: number = 1, pageSize: number = 10): Promise<ActivityListResponse> {
    return apiClient.getActivities(page, pageSize)
  },

  // 获取活动详情
  async getActivity(activityId: number): Promise<Activity> {
    return apiClient.getActivity(activityId)
  },

  // 获取活动统计信息
  async getStats(): Promise<ActivityStats> {
    return apiClient.getActivityStats()
  },

  // 创建活动
  async createActivity(activityData: ActivityCreateRequest): Promise<Activity> {
    return apiClient.createActivity(activityData)
  },

  // 更新活动
  async updateActivity(activityId: number, activityData: ActivityUpdateRequest): Promise<Activity> {
    return apiClient.updateActivity(activityId, activityData)
  },

  // 删除活动
  async deleteActivity(activityId: number): Promise<{ success: boolean; message: string }> {
    return apiClient.deleteActivity(activityId)
  },

  // 格式化活动日期
  formatDate(dateString: string): string {
    const date = new Date(dateString)
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  },

  // 格式化活动日期（简短格式）
  formatDateShort(dateString: string): { day: string; month: string } {
    const date = new Date(dateString)
    return {
      day: date.getDate().toString().padStart(2, '0'),
      month: date.toLocaleDateString('zh-CN', { month: 'short' })
    }
  }
}

// 配置API便捷函数
export const configApi = {
  // 获取所有配置（自动处理分页）
  async getAllConfigs(): Promise<Config[]> {
    const firstPage = await apiClient.getConfigs(1, 50)
    const allConfigs = [...firstPage.configs]

    // 如果有多页，继续获取
    if (firstPage.total_pages > 1) {
      const promises = []
      for (let page = 2; page <= firstPage.total_pages; page++) {
        promises.push(apiClient.getConfigs(page, 50))
      }

      const additionalPages = await Promise.all(promises)
      additionalPages.forEach(pageData => {
        allConfigs.push(...pageData.configs)
      })
    }

    return allConfigs
  },

  // 获取分页配置
  async getConfigs(page: number = 1, pageSize: number = 10): Promise<ConfigListResponse> {
    return apiClient.getConfigs(page, pageSize)
  },

  // 获取配置详情
  async getConfig(configId: number): Promise<Config> {
    return apiClient.getConfig(configId)
  },

  // 根据键获取配置
  async getConfigByKey(key: string): Promise<Config> {
    return apiClient.getConfigByKey(key)
  },

  // 创建配置
  async createConfig(configData: ConfigCreateRequest): Promise<Config> {
    return apiClient.createConfig(configData)
  },

  // 更新配置
  async updateConfig(configId: number, configData: ConfigUpdateRequest): Promise<Config> {
    return apiClient.updateConfig(configId, configData)
  },

  // 删除配置
  async deleteConfig(configId: number): Promise<{ success: boolean; message: string }> {
    return apiClient.deleteConfig(configId)
  },

  // 验证配置值格式
  validateConfigValue(type: string, value: string): { valid: boolean; error?: string } {
    switch (type) {
      case 'number':
        const num = Number(value)
        if (isNaN(num)) {
          return { valid: false, error: '请输入有效的数字' }
        }
        return { valid: true }

      case 'boolean':
        if (!['true', 'false', '1', '0'].includes(value.toLowerCase())) {
          return { valid: false, error: '布尔值只能是 true/false 或 1/0' }
        }
        return { valid: true }

      case 'json':
        try {
          JSON.parse(value)
          return { valid: true }
        } catch {
          return { valid: false, error: 'JSON格式不正确' }
        }

      case 'string':
      default:
        return { valid: true }
    }
  },

  // 格式化配置值用于显示
  formatConfigValue(config: Config): string {
    switch (config.type) {
      case 'json':
        try {
          return JSON.stringify(JSON.parse(config.value), null, 2)
        } catch {
          return config.value
        }
      case 'boolean':
        return ['true', '1'].includes(config.value.toLowerCase()) ? '是' : '否'
      default:
        return config.value
    }
  },

  // 获取配置的实际值（转换为正确的类型）
  getConfigValue(config: Config): any {
    switch (config.type) {
      case 'number':
        return Number(config.value)
      case 'boolean':
        return ['true', '1'].includes(config.value.toLowerCase())
      case 'json':
        try {
          return JSON.parse(config.value)
        } catch {
          return config.value
        }
      case 'string':
      default:
        return config.value
    }
  }
}

// 错误处理工具
export class ApiError extends Error {
  public status?: number
  public endpoint?: string

  constructor(
    message: string,
    status?: number,
    endpoint?: string
  ) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.endpoint = endpoint
  }
}

// 重试机制
export async function withRetry<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  delay: number = 1000
): Promise<T> {
  let lastError: Error

  for (let i = 0; i <= maxRetries; i++) {
    try {
      return await fn()
    } catch (error) {
      lastError = error as Error
      
      if (i === maxRetries) {
        break
      }
      
      // 等待后重试
      await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)))
    }
  }
  
  throw lastError!
}

// 缓存管理
class ApiCache {
  private cache = new Map<string, { data: any; timestamp: number; ttl: number }>()

  set(key: string, data: any, ttl: number = 5 * 60 * 1000): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl
    })
  }

  get<T>(key: string): T | null {
    const item = this.cache.get(key)
    
    if (!item) {
      return null
    }
    
    if (Date.now() - item.timestamp > item.ttl) {
      this.cache.delete(key)
      return null
    }
    
    return item.data as T
  }

  clear(): void {
    this.cache.clear()
  }
}

export const apiCache = new ApiCache()

// 带缓存的API调用
export async function cachedApiCall<T>(
  key: string,
  apiCall: () => Promise<T>,
  ttl?: number
): Promise<T> {
  // 尝试从缓存获取
  const cached = apiCache.get<T>(key)
  if (cached) {
    return cached
  }
  
  // 调用API并缓存结果
  const result = await apiCall()
  apiCache.set(key, result, ttl)
  
  return result
}
