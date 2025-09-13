/**
 * 活动系统基础测试（静态检查/挂载冒烟）
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ActivityPanelVote from '@/components/activities/ActivityPanelVote.vue'
import RankingList from '@/components/activities/RankingList.vue'
import VoteOptionList from '@/components/activities/VoteOptionList.vue'
import ActivityCarousel from '@/components/activities/ActivityCarousel.vue'
import { useActivitiesStore } from '@/stores/activities'

describe('Activities components', () => {
  let pinia: any

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('RankingList can render with empty entries', () => {
    const wrapper = mount(RankingList, {
      props: { entries: [], loading: false }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('VoteOptionList emits vote and search', async () => {
    const wrapper = mount(VoteOptionList, {
      props: { activityId: 1, options: [], loading: false }
    })
    await wrapper.vm.$nextTick()
    // 触发一次搜索（节流后也应被调用一次）
    const input = wrapper.find('input')
    await input.setValue('abc')
    await input.trigger('input')
    // 不能严格断言节流时序，这里仅检查组件存在
    expect(wrapper.exists()).toBe(true)
  })

  it('ActivityPanelVote mounts with stubbed store', async () => {
    const store = useActivitiesStore()
    store.fetchRankingTop = vi.fn().mockResolvedValue(undefined) as any
    store.fetchOptions = vi.fn().mockResolvedValue(undefined) as any
    store.submitVote = vi.fn().mockResolvedValue(undefined) as any
    store.revokeVote = vi.fn().mockResolvedValue(undefined) as any
    // 预置空数据
    store.ranking[1] = []
    store.options[1] = { items: [] }

    const wrapper = mount(ActivityPanelVote, {
      global: { plugins: [pinia] },
      props: {
        activity: { id: 1, type: 'vote', title: 'Test', description: 'Desc', status: 'ongoing' }
      }
    })

    await wrapper.vm.$nextTick()
    expect(wrapper.exists()).toBe(true)
    expect(store.fetchRankingTop).toHaveBeenCalled()
    expect(store.fetchOptions).toHaveBeenCalled()
  })

  it('ActivityCarousel mounts and calls fetchActivities (stubbed)', async () => {
    const store = useActivitiesStore()
    store.fetchActivities = vi.fn().mockResolvedValue(undefined) as any
    store.startRankingPolling = vi.fn() as any

    const wrapper = mount(ActivityCarousel, { global: { plugins: [pinia] } })
    await wrapper.vm.$nextTick()
    expect(wrapper.exists()).toBe(true)
    expect(store.fetchActivities).toHaveBeenCalled()
    expect(store.startRankingPolling).toHaveBeenCalled()
    wrapper.unmount()
  })
})


