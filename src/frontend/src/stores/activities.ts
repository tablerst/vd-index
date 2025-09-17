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
  revoke?: Record<number, boolean>
}

export const useActivitiesStore = defineStore('activities', {
  state: () => ({
    activities: [] as ActActivity[],
    currentIndex: 0,
    ranking: {} as Record<number, ActRankingEntry[]>,
    options: {} as Record<number, OptionsState>,
    myVotes: {} as Record<number, number | null>,
    threadPosts: {} as Record<number, { items: ActThreadPost[]; cursor?: string | null; loading?: boolean; hasMore?: boolean; refreshing?: boolean }>,
    anonymousPreference: true,
    loading: { activities: false, ranking: {}, options: {}, revoke: {} } as LoadingState,
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

    async fetchRankingTop(activityId: number, top = 10, force = false) {
      // 允许并发去重：若已有请求在进行中则跳过；用户动作触发可 force 强制拉取
      if (!force && this.loading.ranking[activityId]) return
      this.loading.ranking[activityId] = true
      try {
        const res = await actApi.ranking(activityId, top, true)
        const next = Array.isArray(res) ? res : (res?.entries || [])
        const prev = this.ranking[activityId] || []
        // 浅比较：若数据未变化则不触发更新，避免不必要重渲染
        const sameLen = prev.length === next.length
        const sameItems = sameLen && prev.every((p, i) => p.option_id === next[i].option_id && p.votes === next[i].votes)
        if (!sameItems) {
          this.ranking[activityId] = next
        }
      } catch (e) {
        // 保留旧快照，避免抖动
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
      const previousOptionId = this.myVotes[activityId] ?? null
      await actApi.vote(activityId, { option_id: optionId, display_anonymous: displayAnonymous })
      this.myVotes[activityId] = optionId

      // Optimistic ranking update for snappy UI
      try {
        const currentEntries = [...(this.ranking[activityId] || [])]
        const ensureLabel = (id: number) => {
          const opts = this.options[activityId]?.items || []
          return opts.find(o => o.id === id)?.label || String(id)
        }
        const adjust = (id: number | null, delta: number) => {
          if (!id || delta === 0) return
          const idx = currentEntries.findIndex(e => e.option_id === id)
          if (idx >= 0) {
            const nextVotes = Math.max(0, (currentEntries[idx].votes || 0) + delta)
            currentEntries[idx] = { ...currentEntries[idx], votes: nextVotes }
          } else if (delta > 0) {
            currentEntries.push({ option_id: id, label: ensureLabel(id), votes: delta })
          }
        }
        if (previousOptionId && previousOptionId !== optionId) adjust(previousOptionId, -1)
        adjust(optionId, +1)
        currentEntries.sort((a, b) => b.votes - a.votes)
        this.ranking[activityId] = currentEntries
      } catch {}

      // Force refresh from server; widen top to include all options (capped to 100)
      const optionCount = this.options[activityId]?.items?.length || 10
      const top = Math.min(100, Math.max(10, optionCount))
      await this.fetchRankingTop(activityId, top, true)
    },

    async revokeVote(activityId: number) {
      this.loading.revoke![activityId] = true
      try {
        const previousOptionId = this.myVotes[activityId] ?? null
        await actApi.revoke(activityId)
        this.myVotes[activityId] = null

        // Optimistic ranking update: decrement previous vote
        try {
          const currentEntries = [...(this.ranking[activityId] || [])]
          const idx = previousOptionId ? currentEntries.findIndex(e => e.option_id === previousOptionId) : -1
          if (idx >= 0) {
            const nextVotes = Math.max(0, (currentEntries[idx].votes || 0) - 1)
            currentEntries[idx] = { ...currentEntries[idx], votes: nextVotes }
            currentEntries.sort((a, b) => b.votes - a.votes)
            this.ranking[activityId] = currentEntries
          }
        } catch {}

        await this.fetchRankingTop(activityId, 10, true)
      } finally {
        this.loading.revoke![activityId] = false
      }
    },

    // Thread posts
    async fetchThreadPosts(activityId: number, cursor: string | null = null, size = 20, opts?: { silent?: boolean }) {
      const entry = this.threadPosts[activityId] || { items: [], cursor: null, loading: false, hasMore: true, refreshing: false }
      const silent = !!opts?.silent
      // 避免并发：正在加载或静默刷新时直接跳过
      if (entry.loading || entry.refreshing) return
      if (silent) {
        entry.refreshing = true
      } else {
        entry.loading = true
      }
      this.threadPosts[activityId] = entry
      try {
        const res = await actApi.posts(activityId, cursor, size)
        const items = (res as any)?.items || (res as any) || []
        // 简化：后端如未返回cursor，这里仅依据是否满页判断hasMore
        entry.items = cursor ? [...entry.items, ...items] : items
        entry.cursor = null
        entry.hasMore = items.length >= size
      } finally {
        if (silent) {
          entry.refreshing = false
        } else {
          entry.loading = false
        }
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
    async createActivity(payload: { type?: 'vote'; title: string; description?: string; anonymous_allowed?: boolean; starts_at?: string; ends_at?: string; allow_change?: boolean }) {
      const created = await actApi.create(payload)
      // 刷新活动列表
      await this.fetchActivities('ongoing')
      return created
    },

    async createOption(activityId: number, label: string, memberId?: number | null) {
      // 乐观更新：先把新项插入到本地，避免“新增后不显示”的困惑
      const optionsEntry = this.options[activityId] || { items: [] as ActVoteOption[], query: '', cursor: null }
      const optimistic: ActVoteOption = { id: Date.now(), label, member_id: memberId ?? undefined, votes: 0 }
      optionsEntry.items = [optimistic, ...(optionsEntry.items || [])]
      this.options[activityId] = optionsEntry

      try {
        await actApi.createOption(activityId, { label, member_id: memberId ?? null })
      } finally {
        // 以服务端为准刷新一次列表与排行
        await this.fetchOptions(activityId)
        await this.fetchRankingTop(activityId, 10, true)
      }
    },

    async deleteOption(activityId: number, optionId: number) {
      await actApi.deleteOption(activityId, optionId)
      // 列表/排行均会受影响，刷新
      await this.fetchOptions(activityId)
      await this.fetchRankingTop(activityId, 10, true)
    },

    async fetchMyVote(activityId: number) {
      try {
        const res = await actApi.myVote(activityId)
        this.myVotes[activityId] = (res as any)?.option_id ?? null
      } catch {
        // 未登录或无记录，保持为空
      }
    },

    async closeActivity(activityId: number) {
      await actApi.close(activityId)
      await this.fetchActivities('ongoing')
    },

    async deleteActivity(activityId: number) {
      await actApi.deleteActivity(activityId)
      // 本地状态清理
      this.activities = this.activities.filter(a => a.id !== activityId)
      delete this.ranking[activityId]
      delete this.options[activityId]
      delete this.myVotes[activityId]
      delete this.threadPosts[activityId]
      // 纠正当前索引
      if (this.currentIndex >= this.activities.length) {
        this.currentIndex = Math.max(0, this.activities.length - 1)
      }
    },

    setCurrentIndex(index: number) {
      this.currentIndex = index
    },

    startRankingPolling() {
      if (this.pollingHandle) return
      const tick = () => {
        // 页面不可见时暂停轮询，恢复时立即同步一次
        if (document.visibilityState === 'hidden') return
        const activityIds = this.activities.map(a => a.id)
        activityIds.forEach(id => this.fetchRankingTop(id, 10).catch(() => {}))
      }
      this.pollingHandle = window.setInterval(tick, this.pollingIntervalMs)
      document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible') tick()
      })
    },

    stopRankingPolling() {
      if (this.pollingHandle) {
        clearInterval(this.pollingHandle)
        this.pollingHandle = null
      }
    }
  }
})

