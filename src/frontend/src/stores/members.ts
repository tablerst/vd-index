import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { memberApi, type Member as ApiMember, withRetry, cachedApiCall } from '../services/api'

// 使用API中的Member接口，但保持兼容性
export interface Member {
  id: number
  name: string
  avatarURL: string // 保持原有字段名以兼容现有组件
  bio?: string
  joinDate?: string
  contribution?: number
  role?: number // 群权限：0=群主, 1=管理员, 2=群员
  groupNick?: string // 群昵称
  qqNick?: string // QQ昵称
}

// 从API Member转换为本地Member的适配器
function adaptApiMember(apiMember: ApiMember): Member {
  return {
    id: apiMember.id,
    name: apiMember.name,
    avatarURL: apiMember.avatar_url, // 转换字段名
    bio: apiMember.bio,
    joinDate: apiMember.join_date, // 转换字段名
    contribution: 0, // QQ群没有贡献度概念，设为0
    role: apiMember.role,
    groupNick: apiMember.group_nick,
    qqNick: apiMember.qq_nick
  }
}

export interface QQGroupMember {
  uin: number
  role: number
  g: number
  join_time: number
  last_speak_time: number
  lv: {
    point: number
    level: number
  }
  card: string
  tags: string
  flag: number
  nick: string
  qage: number
  rm: number
}

export interface QQGroupData {
  ec: number
  errcode: number
  em: string
  cache: number
  adm_num: number
  levelname: Record<string, string>
  mems: QQGroupMember[]
  count: number
  total_count: number
  svr_time: number
  max_count: number
  search_count: number
  extmode: number
}

export const useMembersStore = defineStore('members', () => {
  // 状态
  const allMembers = ref<Member[]>([])
  const visibleMembers = ref<Member[]>([])
  const currentPage = ref(0)
  const isLoading = ref(false)
  const hasLoadedInitial = ref(false)
  
  // 常量
  const ITEMS_PER_BATCH = 80
  const TOTAL_MEMBERS = 80 // 模拟总成员数
  
  // 计算属性
  const totalMembers = computed(() => allMembers.value.length || TOTAL_MEMBERS)
  const hasMoreMembers = computed(() => visibleMembers.value.length < totalMembers.value)

  // UIN到头像路径的映射缓存
  const uinAvatarMap = ref<Map<number, string>>(new Map())

  // 将时间戳转换为日期字符串
  const formatTimestamp = (timestamp: number): string => {
    return new Date(timestamp * 1000).toISOString().split('T')[0]
  }

  // 获取群权限显示文本
  const getRoleText = (role: number): string => {
    switch (role) {
      case 0: return '群主'
      case 1: return '管理员'
      case 2: return '群员'
      default: return '未知'
    }
  }

  // 从后端API加载成员数据
  const loadQQGroupMembers = async (): Promise<Member[]> => {
    try {
      console.log('Loading members from backend API...')

      // 使用带重试的API调用
      const apiMembers = await withRetry(
        () => cachedApiCall('all-members', () => memberApi.getAllMembers(), 5 * 60 * 1000),
        3,
        1000
      )

      console.log(`Received ${apiMembers.length} members from API`)

      // 转换API数据为本地格式
      const members: Member[] = apiMembers.map(adaptApiMember)

      // 清空UIN映射（不再需要）
      uinAvatarMap.value.clear()

      console.log(`Successfully loaded ${members.length} members from backend`)
      return members

    } catch (error) {
      console.error('Failed to load members from backend:', error)

      // 如果API失败，回退到本地JSON文件
      console.log('API failed, falling back to local JSON data...')
      try {
        const response = await fetch('/qq_group_937303337_members.json')
        if (!response.ok) {
          throw new Error('Failed to load local QQ group data')
        }

        const data: QQGroupData = await response.json()
        const members: Member[] = []

        for (const qqMember of data.mems) {
          const memberId = qqMember.uin
          const avatarPath = `/avatars/mems/${qqMember.uin}.webp`
          uinAvatarMap.value.set(qqMember.uin, avatarPath)
          const displayName = qqMember.card.trim() || qqMember.nick.trim()
          const joinDateStr = formatTimestamp(qqMember.join_time)
          const bio = `加入于 ${joinDateStr}`

          members.push({
            id: memberId,
            name: displayName,
            avatarURL: avatarPath,
            bio,
            joinDate: formatTimestamp(qqMember.join_time),
            role: qqMember.role,
            groupNick: qqMember.card.trim(),
            qqNick: qqMember.nick.trim()
          })
        }

        console.log(`Fallback: loaded ${members.length} members from local JSON`)
        return members
      } catch (fallbackError) {
        console.error('Fallback also failed:', fallbackError)
        return []
      }
    }
  }

  // 生成模拟成员数据
  const generateMockMembers = (startId: number, count: number): Member[] => {
    const members: Member[] = []
    const names = [
      'Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank', 'Grace', 'Henry',
      'Ivy', 'Jack', 'Kate', 'Liam', 'Mia', 'Noah', 'Olivia', 'Paul',
      'Quinn', 'Ruby', 'Sam', 'Tina', 'Uma', 'Victor', 'Wendy', 'Xander',
      'Yara', 'Zoe', '小明', '小红', '小刚', '小丽', '小华', '小芳',
      '张三', '李四', '王五', '赵六', '钱七', '孙八', '周九', '吴十'
    ]
    
    const bios = [
      '热爱编程的开发者，专注于前端技术',
      '设计师，喜欢创造美好的用户体验',
      '后端工程师，擅长系统架构设计',
      '产品经理，致力于打造优秀产品',
      'UI/UX设计师，追求完美的视觉效果',
      '全栈开发者，技术栈广泛',
      '数据科学家，热爱数据分析',
      '运维工程师，保障系统稳定运行',
      '测试工程师，确保产品质量',
      '技术写作者，分享技术知识'
    ]
    
    for (let i = 0; i < count; i++) {
      const id = startId + i
      const nameIndex = (id - 1) % names.length
      const bioIndex = (id - 1) % bios.length
      
      // 生成头像URL - 使用占位符服务
      const avatarURL = `https://api.dicebear.com/7.x/avataaars/svg?seed=${id}&size=64`
      
      // 生成随机加入日期
      const joinDate = new Date(
        2020 + Math.floor(Math.random() * 4),
        Math.floor(Math.random() * 12),
        Math.floor(Math.random() * 28) + 1
      ).toISOString().split('T')[0]
      
      // 生成随机贡献度
      const contribution = Math.floor(Math.random() * 1000) + 10
      
      members.push({
        id,
        name: `${names[nameIndex]}${id > names.length ? id : ''}`,
        avatarURL,
        bio: bios[bioIndex],
        joinDate,
        contribution
      })
    }
    
    return members
  }
  
  // 加载初始成员
  const loadMembers = async (): Promise<Member[]> => {
    if (hasLoadedInitial.value) {
      return visibleMembers.value
    }

    isLoading.value = true

    try {
      // 模拟网络延迟
      await new Promise(resolve => setTimeout(resolve, 800))

      // 尝试加载真实QQ群成员数据
      let newMembers = await loadQQGroupMembers()

      // 如果加载失败或数据为空，使用模拟数据作为备用
      if (newMembers.length === 0) {
        console.warn('QQ群数据加载失败，使用模拟数据')
        newMembers = generateMockMembers(1, TOTAL_MEMBERS)
      }

      allMembers.value.push(...newMembers)
      visibleMembers.value.push(...newMembers)
      currentPage.value = 1
      hasLoadedInitial.value = true

      return newMembers
    } catch (error) {
      console.error('Failed to load members:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }
  
  // 加载更多成员
  const loadMoreMembers = async (): Promise<Member[]> => {
    if (!hasMoreMembers.value || isLoading.value) {
      return []
    }
    
    isLoading.value = true
    
    try {
      // 模拟网络延迟
      await new Promise(resolve => setTimeout(resolve, 500))
      
      const startId = currentPage.value * ITEMS_PER_BATCH + 1
      const remainingCount = TOTAL_MEMBERS - visibleMembers.value.length
      const batchSize = Math.min(ITEMS_PER_BATCH, remainingCount)
      
      if (batchSize <= 0) {
        return []
      }
      
      const newMembers = generateMockMembers(startId, batchSize)
      allMembers.value.push(...newMembers)
      visibleMembers.value.push(...newMembers)
      currentPage.value++
      
      return newMembers
    } catch (error) {
      console.error('Failed to load more members:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }
  
  // 根据ID查找成员
  const getMemberById = (id: number): Member | undefined => {
    return allMembers.value.find(member => member.id === id)
  }
  
  // 搜索成员
  const searchMembers = (query: string): Member[] => {
    if (!query.trim()) {
      return visibleMembers.value
    }
    
    const lowercaseQuery = query.toLowerCase()
    return visibleMembers.value.filter(member =>
      member.name.toLowerCase().includes(lowercaseQuery) ||
      member.bio?.toLowerCase().includes(lowercaseQuery)
    )
  }
  
  // 重置状态
  const reset = () => {
    allMembers.value = []
    visibleMembers.value = []
    currentPage.value = 0
    isLoading.value = false
    hasLoadedInitial.value = false
  }
  
  // 获取成员统计信息
  const getStats = () => {
    const totalContribution = visibleMembers.value.reduce(
      (sum, member) => sum + (member.contribution || 0),
      0
    )
    
    const averageContribution = visibleMembers.value.length > 0
      ? Math.round(totalContribution / visibleMembers.value.length)
      : 0
    
    // 按年份统计加入人数
    const joinYearStats = visibleMembers.value.reduce((stats, member) => {
      if (member.joinDate) {
        const year = new Date(member.joinDate).getFullYear()
        stats[year] = (stats[year] || 0) + 1
      }
      return stats
    }, {} as Record<number, number>)
    
    return {
      totalMembers: visibleMembers.value.length,
      totalContribution,
      averageContribution,
      joinYearStats
    }
  }
  
  return {
    // 状态
    allMembers,
    visibleMembers,
    currentPage,
    isLoading,
    hasLoadedInitial,
    uinAvatarMap,

    // 计算属性
    totalMembers,
    hasMoreMembers,

    // 方法
    loadMembers,
    loadMoreMembers,
    loadQQGroupMembers,
    formatTimestamp,
    getRoleText,
    getMemberById,
    searchMembers,
    reset,
    getStats
  }
})
