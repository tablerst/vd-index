/**
 * 后端API服务
 * 提供安全的成员数据访问接口
 */
import { RequestInterceptor, TokenRefreshManager } from '@/utils/token'

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

export interface MemberUpdateRequest {
  display_name?: string
  group_nick?: string
  role?: number
  level_point?: number
  level_value?: number
}

export interface CreateMemberRequest {
  display_name: string
  group_nick?: string
  role?: number
  bio?: string
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

// 评论接口定义
export interface Comment {
  id: number
  member_id: number
  content: string
  likes: number
  dislikes: number
  is_anonymous: boolean
  created_at: string
  updated_at: string
  // 前端状态字段（可选）
  userLiked?: boolean
  userDisliked?: boolean
}

export interface CommentCreateRequest {
  content: string
  is_anonymous?: boolean
}

export interface CommentListResponse {
  comments: Comment[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface CommentActionResponse {
  success: boolean
  message: string
  comment?: Comment
}

export interface CommentStats {
  total_comments: number
  total_likes: number
  total_dislikes: number
  active_comments: number
  deleted_comments: number
}

export interface CacheStats {
  hits: number
  misses: number
  total_requests: number
  hit_rate: number
  cache_size: number
  max_size: number
  last_updated: string
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
  async getMemberDetail(id: number): Promise<MemberDetail> {
    return this.request<MemberDetail>(`/api/v1/members/${id}`)
  }

  // 创建成员
  async createMember(data: CreateMemberRequest): Promise<any> {
    return this.request('/api/v1/members', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })
  }

  // 导入：上传JSON文件（members模块）
  async adminImportFile(file: File): Promise<any> {
    const form = new FormData()
    form.append('file', file)
    // 注意：multipart时不要手动设置Content-Type
    return this.request('/api/v1/members/import-file', {
      method: 'POST',
      body: form
    })
  }

  // 导入：直接提交JSON结构（members模块）
  async adminImportJson(mems: any[]): Promise<any> {
    // 将 mems 转为 ImportBatchRequest 结构在后端解析
    return this.request('/api/v1/members/import', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ members: mems })
    })
  }

  // 导入：通过QQ群参数获取后导入（members模块）
  async adminImportFromQQ(params: {
    group_id: string
    cookie: string
    bkn: string
    user_agent?: string
    page_size?: number
    request_delay?: number
  }): Promise<any> {
    return this.request('/api/v1/members/import-from-qq', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    })
  }

  // 导入：直接调用 /api/v1/members/import（批量Upsert）
  async membersImport(batch: { members: any[] }): Promise<any> {
    return this.request('/api/v1/members/import', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(batch)
    })
  }

  // 更新成员信息
  async updateMember(id: number, data: MemberUpdateRequest): Promise<any> {
    return this.request(`/api/v1/members/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })
  }

  // 删除成员
  async deleteMember(id: number): Promise<any> {
    return this.request(`/api/v1/members/${id}`, {
      method: 'DELETE'
    })
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

  // 缓存管理相关方法
  async getCacheStats(): Promise<CacheStats> {
    return this.request<CacheStats>('/api/v1/cache/stats')
  }

  async clearCache(): Promise<{ message: string; success: boolean }> {
    return this.request('/api/v1/cache/clear', {
      method: 'POST'
    })
  }

  async deleteCacheKey(cacheKey: string): Promise<{ message: string; success: boolean }> {
    return this.request(`/api/v1/cache/key/${encodeURIComponent(cacheKey)}`, {
      method: 'DELETE'
    })
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

  // 评论相关方法
  // 获取成员评论列表
  async getMemberComments(
    memberId: number,
    page: number = 1,
    pageSize: number = 20
  ): Promise<CommentListResponse> {
    return this.request<CommentListResponse>(
      `/api/v1/comments/members/${memberId}/comments?page=${page}&page_size=${pageSize}`
    )
  }

  // 创建评论
  async createComment(memberId: number, data: CommentCreateRequest): Promise<Comment> {
    return this.request<Comment>(`/api/v1/comments/members/${memberId}/comments`, {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }

  // 点赞评论
  async likeComment(commentId: number): Promise<CommentActionResponse> {
    return this.request<CommentActionResponse>(`/api/v1/comments/${commentId}/like`, {
      method: 'PUT'
    })
  }

  // 点踩评论
  async dislikeComment(commentId: number): Promise<CommentActionResponse> {
    return this.request<CommentActionResponse>(`/api/v1/comments/${commentId}/dislike`, {
      method: 'PUT'
    })
  }

  // 删除评论（管理员功能）
  async deleteComment(commentId: number): Promise<CommentActionResponse> {
    return this.request<CommentActionResponse>(`/api/v1/comments/${commentId}`, {
      method: 'DELETE'
    })
  }

  // 获取评论统计（管理员功能）
  async getCommentStats(): Promise<CommentStats> {
    return this.request<CommentStats>('/api/v1/comments/stats')
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

  // 创建成员
  async createMember(data: CreateMemberRequest): Promise<any> {
    return apiClient.createMember(data)
  },

  // 获取统计信息
  async getStats(): Promise<MemberStats> {
    return apiClient.getMemberStats()
  },

  // 更新成员信息
  async updateMember(id: number, data: MemberUpdateRequest): Promise<any> {
    return apiClient.updateMember(id, data)
  },

  // 删除成员
  async deleteMember(id: number): Promise<any> {
    return apiClient.deleteMember(id)
  },

  // 导入：上传JSON文件
  async importMembersFile(file: File): Promise<any> {
    return apiClient.adminImportFile(file)
  },

  // 导入：直接传JSON（mems数组）
  async importMembersJson(mems: any[]): Promise<any> {
    return apiClient.adminImportJson(mems)
  },

  // 导入：通过QQ群参数获取
  async importMembersFromQQ(params: {
    group_id: string
    cookie: string
    bkn: string
    user_agent?: string
    page_size?: number
    request_delay?: number
  }): Promise<any> {
    return apiClient.adminImportFromQQ(params)
  },

  // 导入：成员 JSON 直接 Upsert
  async importMembersBatch(mems: any[]): Promise<any> {
    return apiClient.membersImport({ members: mems })
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
    // 后端现在返回ISO格式的时间字符串，包含时区信息
    const date = new Date(dateString)
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  },

  // 格式化活动日期（简短格式）
  formatDateShort(dateString: string): { day: string; month: string } {
    // 后端现在返回ISO格式的时间字符串，包含时区信息
    const date = new Date(dateString)
    return {
      day: date.getDate().toString().padStart(2, '0'),
      month: date.toLocaleDateString('zh-CN', { month: 'short' })
    }
  }
}

// 评论API便捷函数
export const commentApi = {
  // 获取成员评论列表
  async getMemberComments(
    memberId: number,
    page: number = 1,
    pageSize: number = 20
  ): Promise<CommentListResponse> {
    return apiClient.getMemberComments(memberId, page, pageSize)
  },

  // 创建评论
  async createComment(memberId: number, content: string, isAnonymous: boolean = true): Promise<Comment> {
    return apiClient.createComment(memberId, { content, is_anonymous: isAnonymous })
  },

  // 点赞评论
  async likeComment(commentId: number): Promise<CommentActionResponse> {
    return apiClient.likeComment(commentId)
  },

  // 点踩评论
  async dislikeComment(commentId: number): Promise<CommentActionResponse> {
    return apiClient.dislikeComment(commentId)
  },

  // 删除评论（管理员功能）
  async deleteComment(commentId: number): Promise<CommentActionResponse> {
    return apiClient.deleteComment(commentId)
  },

  // 获取评论统计（管理员功能）
  async getStats(): Promise<CommentStats> {
    return apiClient.getCommentStats()
  },

  // 格式化评论时间
  formatTime(dateString: string): string {
    // 后端现在返回ISO格式的时间字符串，包含时区信息
    const date = new Date(dateString)
    const now = new Date()
    const diff = now.getTime() - date.getTime()

    const minutes = Math.floor(diff / (1000 * 60))
    const hours = Math.floor(diff / (1000 * 60 * 60))
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))

    if (minutes < 1) return '刚刚'
    if (minutes < 60) return `${minutes}分钟前`
    if (hours < 24) return `${hours}小时前`
    if (days < 7) return `${days}天前`

    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  },

  // 验证评论内容
  validateContent(content: string): { valid: boolean; message?: string } {
    if (!content || content.trim().length === 0) {
      return { valid: false, message: '评论内容不能为空' }
    }

    if (content.length > 500) {
      return { valid: false, message: '评论内容不能超过500字符' }
    }

    return { valid: true }
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
