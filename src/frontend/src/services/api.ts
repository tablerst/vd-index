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
      `/api/members?page=${page}&page_size=${pageSize}`
    )
  }

  // 获取成员详情
  async getMemberDetail(memberId: number): Promise<MemberDetail> {
    return this.request<MemberDetail>(`/api/members/${memberId}`)
  }

  // 获取成员统计信息
  async getMemberStats(): Promise<MemberStats> {
    return this.request<MemberStats>('/api/members/stats')
  }

  // 获取头像URL（直接返回URL，由浏览器处理缓存）
  getAvatarUrl(memberId: number): string {
    return `${this.baseURL}/api/avatar/${memberId}`
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
    const match = avatarUrl.match(/\/api\/avatar\/(\d+)/)
    return match ? parseInt(match[1], 10) : 0
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
