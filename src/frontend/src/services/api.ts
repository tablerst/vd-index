/**
 * 后端API服务
 * 提供安全的成员数据访问接口
 */

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
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    }

    try {
      const response = await fetch(url, config)
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      console.error(`API请求失败: ${endpoint}`, error)
      throw error
    }
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

  // 健康检查
  async healthCheck(): Promise<{ status: string; timestamp: number }> {
    return this.request('/health')
  }
}

// 创建全局API客户端实例
export const apiClient = new ApiClient()

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
