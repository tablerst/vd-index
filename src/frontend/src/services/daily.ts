// Daily Posts API 封装（独立文件，避免污染 api.ts 类）
// 代码注释：中文

export interface DailyPostItem {
  id: number
  author_user_id: number
  author_display_name?: string | null
  author_avatar_url?: string | null
  content?: string | null
  images: string[]
  tags: string[]
  likes_count: number
  comments_count: number
  views_count: number
  published: boolean
  created_at: string
  updated_at: string
}

export interface DailyPostListResponse {
  posts: DailyPostItem[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface UploadImageItem { name: string; url: string; width?: number; height?: number }
export interface UploadImagesResponse { files: UploadImageItem[] }

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || (import.meta.env.PROD ? '' : 'http://localhost:8000')

// 开发环境开关：通过 VITE_DAILY_USE_MOCK 控制是否使用Mock数据
const USE_MOCK = (import.meta as any).env?.VITE_DAILY_USE_MOCK === 'true' && !import.meta.env.PROD

// 生成多样化Mock图片URL（使用占位图服务，或留空以测试纯文本）
function mockImage(w: number, h: number): string {
  return `https://picsum.photos/seed/${w}x${h}/${w}/${h}`
}

function randomPick<T>(arr: T[]): T { return arr[Math.floor(Math.random() * arr.length)] }
function randomInt(min: number, max: number): number { return Math.floor(Math.random() * (max - min + 1)) + min }

// 生成Mock数据（12-20条，包含不同高度/内容/标签组合）
function buildMockPosts(count: number = 16): DailyPostItem[] {
  const tagsPool = ['旅行', '手工', '上新', '日常', '摄影', '学习', '跑步', '美食']
  const names = ['星尘', '岚语', '林汐', '墨白', '夏末', '北城', '青璃', '南桥']
  const now = Date.now()
  const posts: DailyPostItem[] = []
  for (let i = 0; i < count; i++) {
    const hasImage = Math.random() > 0.3
    const imgCount = hasImage ? randomInt(1, 3) : 0
    const images = Array.from({ length: imgCount }).map(() => mockImage(randomInt(360, 640), randomInt(220, 480)))
    const contentTypes = [
      '今天练了两个小时，进步了一点点～',
      '夏日小集——手工饰品上新喔~',
      '在路上，风很轻，云很白。',
      '复盘：如何稳定 45fps 的渲染表现',
      '拾光：老相机与胶片的味道',
      '跑步第 42 天，5.2km 🏃',
      '平平无奇，但也值得记录的一天',
    ]
    const content = Math.random() > 0.15 ? randomPick(contentTypes) : ''

    const authorIdx = randomInt(0, names.length - 1)
    const memberId = authorIdx + 1
    const post: DailyPostItem = {
      id: i + 1,
      author_user_id: authorIdx + 100,
      author_display_name: names[authorIdx],
      author_avatar_url: `/api/v1/avatar/${memberId}`,
      content,
      images,
      tags: Array.from({ length: randomInt(0, 3) }).map(() => randomPick(tagsPool)),
      likes_count: randomInt(0, 120),
      comments_count: randomInt(0, 30),
      views_count: randomInt(50, 1500),
      published: true,
      created_at: new Date(now - randomInt(0, 7) * 86400_000 - randomInt(0, 3600_000)).toISOString(),
      updated_at: new Date(now - randomInt(0, 3600_000)).toISOString(),
    }
    posts.push(post)
  }
  // 视图里按 views_count desc, created_at desc 的感觉排序（仅Mock）
  posts.sort((a, b) => b.views_count - a.views_count || (b.created_at > a.created_at ? 1 : -1))
  return posts
}


async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`
  const resp = await fetch(url, options)
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
  return resp.json()
}

export const dailyApi = {
  // 获取首页 trending（默认12条）
  async getTrending(limit: number = 12): Promise<DailyPostItem[]> {
    if (USE_MOCK) {
      const data = buildMockPosts(Math.min(Math.max(limit, 8), 24))
      return Promise.resolve(data)
    }
    return request<DailyPostItem[]>(`/api/v1/daily/trending?limit=${limit}`)
  },
  // 获取分页列表
  async getList(page: number = 1, pageSize: number = 20, tag?: string, author_user_id?: number): Promise<DailyPostListResponse> {
    if (USE_MOCK) {
      const posts = buildMockPosts(pageSize)
      return Promise.resolve({ posts, total: 64, page, page_size: pageSize, total_pages: Math.ceil(64 / pageSize) })
    }
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) })
    if (tag) params.set('tag', tag)
    if (author_user_id) params.set('author_user_id', String(author_user_id))
    return request<DailyPostListResponse>(`/api/v1/daily/posts?${params.toString()}`)
  },
  // 获取详情（并自增浏览）
  async getDetail(id: number): Promise<DailyPostItem> {
    if (USE_MOCK) {
      const posts = buildMockPosts(20)
      const found = posts.find(p => p.id === id) || posts[0]
      return Promise.resolve(found)
    }
    return request<DailyPostItem>(`/api/v1/daily/posts/${id}`)
  },
  // 创建帖子（需要鉴权）
  async createPost(payload: { content?: string; images?: string[]; tags?: string[]; published?: boolean }): Promise<DailyPostItem> {
    return request<DailyPostItem>(`/api/v1/daily/posts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
  },
  // 更新帖子
  async updatePost(id: number, payload: Partial<{ content: string; images: string[]; tags: string[]; published: boolean; likes_count: number; comments_count: number }>): Promise<DailyPostItem> {
    return request<DailyPostItem>(`/api/v1/daily/posts/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
  },
  // 删除帖子
  async deletePost(id: number): Promise<{ success: boolean }> {
    return request<{ success: boolean }>(`/api/v1/daily/posts/${id}`, { method: 'DELETE' })
  },
  // 上传图片
  async uploadImages(files: File[]): Promise<UploadImagesResponse> {
    const form = new FormData()
    files.forEach(f => form.append('images', f))
    return request<UploadImagesResponse>(`/api/v1/daily/upload`, {
      method: 'POST',
      body: form
    })
  }
}

