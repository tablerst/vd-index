<template>
  <div class="comment-section">
    <div class="section-header">
      <h2 class="section-title">
        <i class="icon-comments"></i>
        评论区
        <span v-if="totalComments > 0" class="comment-count">({{ totalComments }})</span>
      </h2>
    </div>
    
    <!-- 评论输入 -->
    <CommentInput
      ref="commentInputRef"
      :member-id="memberId"
      :loading="submitting"
      @submit="handleSubmitComment"
      @cancel="handleCancelComment"
    />
    
    <!-- 评论列表 -->
    <div class="comments-container">
      <CommentTimeline
        :comments="comments"
        :loading="loading"
        :has-more="hasMore"
        :can-delete="canDelete"
        @like="handleLikeComment"
        @dislike="handleDislikeComment"
        @delete="handleDeleteComment"
        @load-more="handleLoadMore"
      />
    </div>
    
    <!-- 加载状态 -->
    <div v-if="loading && comments.length === 0" class="loading-state">
      <div class="loading-spinner"></div>
      <p>加载评论中...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useMessage } from 'naive-ui'
import { commentApi, type Comment, type CommentListResponse } from '@/services/api'
import CommentTimeline from './CommentTimeline.vue'
import CommentInput from './CommentInput.vue'

interface Props {
  memberId: number
  canDelete?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  canDelete: false
})

const message = useMessage()

// 响应式数据
const comments = ref<Comment[]>([])
const loading = ref(false)
const submitting = ref(false)
const currentPage = ref(1)
const totalComments = ref(0)
const totalPages = ref(1)
const pageSize = 20

// 组件引用
const commentInputRef = ref<InstanceType<typeof CommentInput>>()

// 计算属性
const hasMore = computed(() => currentPage.value < totalPages.value)

// 加载评论列表
const loadComments = async (page: number = 1, append: boolean = false) => {
  try {
    loading.value = true
    
    const response: CommentListResponse = await commentApi.getMemberComments(
      props.memberId,
      page,
      pageSize
    )
    
    if (append) {
      comments.value.push(...response.comments)
    } else {
      comments.value = response.comments
    }
    
    totalComments.value = response.total
    totalPages.value = response.total_pages
    currentPage.value = page
    
  } catch (error) {
    console.error('加载评论失败:', error)
    message.error('加载评论失败')
  } finally {
    loading.value = false
  }
}

// 提交评论
const handleSubmitComment = async (content: string) => {
  try {
    submitting.value = true
    
    const newComment = await commentApi.createComment(props.memberId, content, true)
    
    // 将新评论添加到列表顶部
    comments.value.unshift(newComment)
    totalComments.value += 1
    
    message.success('评论发布成功')
    
    // 清空输入框
    commentInputRef.value?.clear()
    
  } catch (error) {
    console.error('发布评论失败:', error)
    message.error('发布评论失败')
  } finally {
    submitting.value = false
  }
}

// 取消评论
const handleCancelComment = () => {
  // 可以添加一些取消逻辑
}

// 点赞评论
const handleLikeComment = async (comment: Comment) => {
  try {
    const response = await commentApi.likeComment(comment.id)
    
    if (response.success && response.comment) {
      // 更新本地评论数据
      const index = comments.value.findIndex(c => c.id === comment.id)
      if (index !== -1) {
        comments.value[index] = response.comment
      }
      
      message.success('点赞成功')
    }
  } catch (error) {
    console.error('点赞失败:', error)
    message.error('点赞失败')
  }
}

// 点踩评论
const handleDislikeComment = async (comment: Comment) => {
  try {
    const response = await commentApi.dislikeComment(comment.id)
    
    if (response.success && response.comment) {
      // 更新本地评论数据
      const index = comments.value.findIndex(c => c.id === comment.id)
      if (index !== -1) {
        comments.value[index] = response.comment
      }
      
      message.success('点踩成功')
    }
  } catch (error) {
    console.error('点踩失败:', error)
    message.error('点踩失败')
  }
}

// 删除评论
const handleDeleteComment = async (comment: Comment) => {
  try {
    const response = await commentApi.deleteComment(comment.id)
    
    if (response.success) {
      // 从列表中移除评论
      const index = comments.value.findIndex(c => c.id === comment.id)
      if (index !== -1) {
        comments.value.splice(index, 1)
        totalComments.value -= 1
      }
      
      message.success('评论删除成功')
    }
  } catch (error) {
    console.error('删除评论失败:', error)
    message.error('删除评论失败')
  }
}

// 加载更多评论
const handleLoadMore = () => {
  if (hasMore.value && !loading.value) {
    loadComments(currentPage.value + 1, true)
  }
}

// 刷新评论列表
const refresh = () => {
  currentPage.value = 1
  loadComments(1, false)
}

// 组件挂载时加载评论
onMounted(() => {
  loadComments()
})

// 暴露方法
defineExpose({
  refresh,
  focusInput: () => commentInputRef.value?.focus()
})
</script>

<style scoped lang="scss">
.comment-section {
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

.section-header {
  margin-bottom: 30px;
  text-align: center;
}

.section-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 24px;
  font-weight: 600;
  margin: 0;
  
  .icon-comments::before {
    content: '💬';
    font-size: 28px;
  }
}

.comment-count {
  color: var(--primary-color, #AA83FF);
  font-size: 18px;
  font-weight: 500;
}

.comments-container {
  margin-top: 40px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: rgba(255, 255, 255, 0.6);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(170, 131, 255, 0.3);
  border-top: 3px solid var(--primary-color, #AA83FF);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .comment-section {
    padding: 10px;
  }
  
  .section-title {
    font-size: 20px;
    flex-direction: column;
    gap: 8px;
  }
  
  .comment-count {
    font-size: 16px;
  }
  
  .comments-container {
    margin-top: 20px;
  }
}
</style>
