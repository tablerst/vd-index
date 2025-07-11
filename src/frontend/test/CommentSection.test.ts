/**
 * 评论组件测试用例
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import CommentSection from '@/components/Comment/CommentSection.vue'
import CommentTimeline from '@/components/Comment/CommentTimeline.vue'
import CommentInput from '@/components/Comment/CommentInput.vue'
import { commentApi } from '@/services/api'

// Mock naive-ui
vi.mock('naive-ui', () => ({
  useMessage: () => ({
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    info: vi.fn()
  })
}))

// Mock API
vi.mock('@/services/api', () => ({
  commentApi: {
    getMemberComments: vi.fn(),
    createComment: vi.fn(),
    likeComment: vi.fn(),
    dislikeComment: vi.fn(),
    deleteComment: vi.fn(),
    formatTime: vi.fn((date) => '刚刚'),
    validateContent: vi.fn((content) => ({ valid: content.length > 0 && content.length <= 500 }))
  }
}))

const mockComments = [
  {
    id: 1,
    member_id: 1,
    content: '这是第一条评论',
    likes: 5,
    dislikes: 1,
    is_anonymous: true,
    created_at: '2024-01-01T10:00:00Z',
    updated_at: '2024-01-01T10:00:00Z'
  },
  {
    id: 2,
    member_id: 1,
    content: '这是第二条评论，内容稍微长一些，用来测试显示效果',
    likes: 3,
    dislikes: 0,
    is_anonymous: true,
    created_at: '2024-01-01T11:00:00Z',
    updated_at: '2024-01-01T11:00:00Z'
  }
]

describe('CommentSection', () => {
  let wrapper: any
  const pinia = createPinia()

  beforeEach(() => {
    vi.clearAllMocks()
    
    // Mock API responses
    vi.mocked(commentApi.getMemberComments).mockResolvedValue({
      comments: mockComments,
      total: 2,
      page: 1,
      page_size: 20,
      total_pages: 1
    })
    
    vi.mocked(commentApi.createComment).mockResolvedValue({
      id: 3,
      member_id: 1,
      content: '新创建的评论',
      likes: 0,
      dislikes: 0,
      is_anonymous: true,
      created_at: '2024-01-01T12:00:00Z',
      updated_at: '2024-01-01T12:00:00Z'
    })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('应该正确渲染评论区域', async () => {
    wrapper = mount(CommentSection, {
      props: {
        memberId: 1
      },
      global: {
        plugins: [pinia]
      }
    })

    await wrapper.vm.$nextTick()
    
    expect(wrapper.find('.comment-section').exists()).toBe(true)
    expect(wrapper.find('.section-title').text()).toContain('评论区')
  })

  it('应该在挂载时加载评论', async () => {
    wrapper = mount(CommentSection, {
      props: {
        memberId: 1
      },
      global: {
        plugins: [pinia]
      }
    })

    await wrapper.vm.$nextTick()
    
    expect(commentApi.getMemberComments).toHaveBeenCalledWith(1, 1, 20)
  })

  it('应该正确处理评论提交', async () => {
    wrapper = mount(CommentSection, {
      props: {
        memberId: 1
      },
      global: {
        plugins: [pinia]
      }
    })

    await wrapper.vm.$nextTick()
    
    // 模拟提交评论
    await wrapper.vm.handleSubmitComment('新评论内容')
    
    expect(commentApi.createComment).toHaveBeenCalledWith(1, '新评论内容', true)
  })

  it('应该正确处理点赞操作', async () => {
    vi.mocked(commentApi.likeComment).mockResolvedValue({
      success: true,
      message: '点赞成功',
      comment: {
        ...mockComments[0],
        likes: 6
      }
    })

    wrapper = mount(CommentSection, {
      props: {
        memberId: 1
      },
      global: {
        plugins: [pinia]
      }
    })

    await wrapper.vm.$nextTick()
    
    // 模拟点赞
    await wrapper.vm.handleLikeComment(mockComments[0])
    
    expect(commentApi.likeComment).toHaveBeenCalledWith(1)
  })

  it('应该正确处理点踩操作', async () => {
    vi.mocked(commentApi.dislikeComment).mockResolvedValue({
      success: true,
      message: '点踩成功',
      comment: {
        ...mockComments[0],
        dislikes: 2
      }
    })

    wrapper = mount(CommentSection, {
      props: {
        memberId: 1
      },
      global: {
        plugins: [pinia]
      }
    })

    await wrapper.vm.$nextTick()
    
    // 模拟点踩
    await wrapper.vm.handleDislikeComment(mockComments[0])
    
    expect(commentApi.dislikeComment).toHaveBeenCalledWith(1)
  })
})

describe('CommentTimeline', () => {
  let wrapper: any

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('应该正确渲染评论时间线', () => {
    wrapper = mount(CommentTimeline, {
      props: {
        comments: mockComments,
        loading: false,
        hasMore: false,
        canDelete: false
      }
    })

    expect(wrapper.find('.comment-timeline').exists()).toBe(true)
    expect(wrapper.find('.timeline-line').exists()).toBe(true)
    expect(wrapper.findAll('.comment-item')).toHaveLength(2)
  })

  it('应该显示空状态', () => {
    wrapper = mount(CommentTimeline, {
      props: {
        comments: [],
        loading: false,
        hasMore: false,
        canDelete: false
      }
    })

    expect(wrapper.find('.empty-state').exists()).toBe(true)
    expect(wrapper.find('.empty-state').text()).toContain('还没有评论')
  })

  it('应该显示加载更多按钮', () => {
    wrapper = mount(CommentTimeline, {
      props: {
        comments: mockComments,
        loading: false,
        hasMore: true,
        canDelete: false
      }
    })

    expect(wrapper.find('.load-more').exists()).toBe(true)
    expect(wrapper.find('.load-more-btn').exists()).toBe(true)
  })

  it('应该正确触发点赞事件', async () => {
    wrapper = mount(CommentTimeline, {
      props: {
        comments: mockComments,
        loading: false,
        hasMore: false,
        canDelete: false
      }
    })

    const likeBtn = wrapper.find('.like-btn')
    await likeBtn.trigger('click')

    expect(wrapper.emitted('like')).toBeTruthy()
    expect(wrapper.emitted('like')[0]).toEqual([mockComments[0]])
  })

  it('应该正确触发加载更多事件', async () => {
    wrapper = mount(CommentTimeline, {
      props: {
        comments: mockComments,
        loading: false,
        hasMore: true,
        canDelete: false
      }
    })

    const loadMoreBtn = wrapper.find('.load-more-btn')
    await loadMoreBtn.trigger('click')

    expect(wrapper.emitted('load-more')).toBeTruthy()
  })
})

describe('CommentInput', () => {
  let wrapper: any

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('应该正确渲染输入组件', () => {
    wrapper = mount(CommentInput, {
      props: {
        memberId: 1
      }
    })

    expect(wrapper.find('.comment-input').exists()).toBe(true)
    expect(wrapper.find('.comment-textarea').exists()).toBe(true)
    expect(wrapper.find('.submit-btn').exists()).toBe(true)
  })

  it('应该正确验证输入内容', async () => {
    wrapper = mount(CommentInput, {
      props: {
        memberId: 1
      }
    })

    const textarea = wrapper.find('.comment-textarea')
    
    // 测试空内容
    await textarea.setValue('')
    expect(wrapper.find('.submit-btn').attributes('disabled')).toBeDefined()
    
    // 测试正常内容
    await textarea.setValue('这是一条测试评论')
    expect(wrapper.find('.submit-btn').attributes('disabled')).toBeUndefined()
  })

  it('应该显示字符计数', async () => {
    wrapper = mount(CommentInput, {
      props: {
        memberId: 1
      }
    })

    const textarea = wrapper.find('.comment-textarea')
    await textarea.setValue('测试内容')

    expect(wrapper.find('.char-count').text()).toContain('4/500')
  })

  it('应该正确处理提交', async () => {
    wrapper = mount(CommentInput, {
      props: {
        memberId: 1
      }
    })

    const textarea = wrapper.find('.comment-textarea')
    await textarea.setValue('测试评论内容')

    const submitBtn = wrapper.find('.submit-btn')
    await submitBtn.trigger('click')

    expect(wrapper.emitted('submit')).toBeTruthy()
    expect(wrapper.emitted('submit')[0]).toEqual(['测试评论内容'])
  })

  it('应该支持Ctrl+Enter快捷键', async () => {
    wrapper = mount(CommentInput, {
      props: {
        memberId: 1
      }
    })

    const textarea = wrapper.find('.comment-textarea')
    await textarea.setValue('测试评论内容')

    await textarea.trigger('keydown', {
      key: 'Enter',
      ctrlKey: true
    })

    expect(wrapper.emitted('submit')).toBeTruthy()
  })

  it('应该正确处理取消操作', async () => {
    wrapper = mount(CommentInput, {
      props: {
        memberId: 1
      }
    })

    const textarea = wrapper.find('.comment-textarea')
    await textarea.setValue('测试内容')

    // 应该显示取消按钮
    expect(wrapper.find('.cancel-btn').exists()).toBe(true)

    const cancelBtn = wrapper.find('.cancel-btn')
    await cancelBtn.trigger('click')

    // 内容应该被清空
    expect(textarea.element.value).toBe('')
    expect(wrapper.emitted('cancel')).toBeTruthy()
  })
})
