import { defineStore } from 'pinia'
import { actApi, type ActActivity, type ActRankingEntry, type ActVoteOption, type ActThreadPost, type ActThreadPostCreate } from '@/services/api'

interface OptionsState {
  items: ActVoteOption[]
  query?: string
  cursor?: string | null
  total?: number
}

interface LoadingState {
  activities: boolean
  ranking: Record<number, boolean>
  options: Record<number, boolean>
}

export const useActivitiesStore = defineStore('activities', {
  state: () => ({
    activities: [] as ActActivity[],
    currentIndex: 0,
    ranking: {} as Record<number, ActRankingEntry[]>,
    options: {} as Record<number, OptionsState>,
    threadPosts: {} as Record<number, { items: ActThreadPost[]; cursor?: string | null; loading?: boolean; hasMore?: boolean }>,
    anonymousPreference: true,
    loading: { activities: false, ranking: {}, options: {} } as LoadingState,
    pollingIntervalMs: 5000,
    pollingHandle: null as number | null,
  }),

  actions: {
    async fetchActivities(status: 'ongoing' | 'closed' | 'draft' = 'ongoing') {
      if (this.loading.activities) return
      this.loading.activities = true
      try {
        const res = await actApi.list(status, 1, 10)
        // 兼容不同返回结构
        const items = (Array.isArray(res) ? res : (res.activities || res.items || [])) as ActActivity[]
        // 展示所有类型活动（vote/thread）
        this.activities = items
      } catch (e) {
        this.activities = []
      } finally {
        this.loading.activities = false
      }
    },

    async fetchRankingTop(activityId: number, top = 10) {
      if (this.loading.ranking[activityId]) return
      this.loading.ranking[activityId] = true
      try {
        const res = await actApi.ranking(activityId, top, true)
        const entries = Array.isArray(res) ? res : (res?.entries || [])
        this.ranking[activityId] = entries
      } catch (e) {
        this.ranking[activityId] = []
      } finally {
        this.loading.ranking[activityId] = false
      }
    },

    async fetchOptions(activityId: number, query = '') {
      this.loading.options[activityId] = true
      try {
        const res = await actApi.options(activityId, query, null, 50)
        const items = Array.isArray(res) ? res : (res?.items || res?.options || [])
        this.options[activityId] = { items, query, cursor: null }
      } catch (e) {
        this.options[activityId] = { items: [] }
      } finally {
        this.loading.options[activityId] = false
      }
    },

    async submitVote(activityId: number, optionId: number, displayAnonymous: boolean) {
      await actApi.vote(activityId, { option_id: optionId, display_anonymous: displayAnonymous })
      await this.fetchRankingTop(activityId)
    },

    async revokeVote(activityId: number) {
      await actApi.revoke(activityId)
      await this.fetchRankingTop(activityId)
    },

    // Thread posts
    async fetchThreadPosts(activityId: number, cursor: string | null = null, size = 20) {
      const entry = this.threadPosts[activityId] || { items: [], cursor: null, loading: false, hasMore: true }
      if (entry.loading) return
      entry.loading = true
      this.threadPosts[activityId] = entry
      try {
        const res = await actApi.posts(activityId, cursor, size)
        const items = (res as any)?.items || (res as any) || []
        // 简化：后端如未返回cursor，这里仅依据是否满页判断hasMore
        entry.items = cursor ? [...entry.items, ...items] : items
        entry.cursor = null
        entry.hasMore = items.length >= size
      } finally {
        entry.loading = false
        this.threadPosts[activityId] = entry
      }
    },

    async createThreadPost(activityId: number, post: ActThreadPostCreate) {
      const created = await actApi.createPost(activityId, post)
      const entry = this.threadPosts[activityId] || { items: [], cursor: null, loading: false, hasMore: true }
      entry.items = [created, ...entry.items]
      this.threadPosts[activityId] = entry
    },

    // Admin / management actions
    async createActivity(payload: { type: 'vote' | 'thread'; title: string; description?: string; anonymous_allowed?: boolean; starts_at?: string; ends_at?: string; allow_change?: boolean }) {
      const created = await actApi.create(payload)
      // 刷新活动列表
      await this.fetchActivities('ongoing')
      return created
    },

    async createOption(activityId: number, label: string, memberId?: number | null) {
      await actApi.createOption(activityId, { label, member_id: memberId ?? null })
      await this.fetchOptions(activityId)
      await this.fetchRankingTop(activityId)
    },

    async closeActivity(activityId: number) {
      await actApi.close(activityId)
      await this.fetchActivities('ongoing')
    },

    setCurrentIndex(index: number) {
      this.currentIndex = index
    },

    startRankingPolling() {
      if (this.pollingHandle) return
      this.pollingHandle = window.setInterval(() => {
        const activityIds = this.activities.map(a => a.id)
        activityIds.forEach(id => {
          // 使用较小的 top 以降低开销
          this.fetchRankingTop(id, 10).catch(() => {})
        })
      }, this.pollingIntervalMs)
    },

    stopRankingPolling() {
      if (this.pollingHandle) {
        clearInterval(this.pollingHandle)
        this.pollingHandle = null
      }
    }
  }
})

