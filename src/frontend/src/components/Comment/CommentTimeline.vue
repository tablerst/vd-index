<template>
  <div class="comment-timeline">
    <!-- 时间线容器 -->
    <div class="timeline-container">
      <!-- 左侧时间线 -->
      <div class="timeline-line"></div>
      
      <!-- 评论列表 -->
      <div class="comments-list">
        <div 
          v-for="(comment, index) in comments" 
          :key="comment.id"
          class="comment-item"
          :style="{ animationDelay: `${index * 0.1}s` }"
        >
          <!-- 时间线节点 -->
          <div class="timeline-node">
            <div class="node-dot"></div>
            <div class="node-connector"></div>
          </div>
          
          <!-- 评论内容框 -->
          <div class="comment-box">
            <div class="comment-header">
              <span class="comment-author">匿名用户</span>
              <span class="comment-time">{{ formatTime(comment.created_at) }}</span>
            </div>
            
            <div class="comment-content">
              {{ comment.content }}
            </div>
            
            <div class="comment-actions">
              <button 
                class="action-btn like-btn"
                :class="{ active: comment.userLiked }"
                @click="handleLike(comment)"
                :disabled="loading"
              >
                <i class="icon-like"></i>
                <span>{{ comment.likes }}</span>
              </button>
              
              <button 
                class="action-btn dislike-btn"
                :class="{ active: comment.userDisliked }"
                @click="handleDislike(comment)"
                :disabled="loading"
              >
                <i class="icon-dislike"></i>
                <span>{{ comment.dislikes }}</span>
              </button>
              
              <button 
                v-if="canDelete"
                class="action-btn delete-btn"
                @click="handleDelete(comment)"
                :disabled="loading"
              >
                <i class="icon-delete"></i>
                删除
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 加载更多 -->
      <div v-if="hasMore" class="load-more">
        <button 
          class="load-more-btn"
          @click="loadMore"
          :disabled="loading"
        >
          {{ loading ? '加载中...' : '加载更多' }}
        </button>
      </div>
      
      <!-- 空状态 -->
      <div v-if="comments.length === 0 && !loading" class="empty-state">
        <div class="empty-icon">💬</div>
        <p>还没有评论，快来抢沙发吧！</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { commentApi, type Comment } from '@/services/api'
import { useMessage } from 'naive-ui'

interface Props {
  comments: Comment[]
  loading?: boolean
  hasMore?: boolean
  canDelete?: boolean
}

interface Emits {
  (e: 'like', comment: Comment): void
  (e: 'dislike', comment: Comment): void
  (e: 'delete', comment: Comment): void
  (e: 'load-more'): void
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  hasMore: false,
  canDelete: false
})

const emit = defineEmits<Emits>()
const message = useMessage()

// 格式化时间
const formatTime = (dateString: string) => {
  return commentApi.formatTime(dateString)
}

// 处理点赞
const handleLike = async (comment: Comment) => {
  try {
    emit('like', comment)
  } catch (error) {
    message.error('点赞失败')
  }
}

// 处理点踩
const handleDislike = async (comment: Comment) => {
  try {
    emit('dislike', comment)
  } catch (error) {
    message.error('点踩失败')
  }
}

// 处理删除
const handleDelete = async (comment: Comment) => {
  try {
    emit('delete', comment)
  } catch (error) {
    message.error('删除失败')
  }
}

// 加载更多
const loadMore = () => {
  emit('load-more')
}
</script>

<style scoped lang="scss">
.comment-timeline {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.timeline-container {
  position: relative;
  padding-left: 40px;
}

.timeline-line {
  position: absolute;
  left: 20px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: linear-gradient(
    to bottom,
    var(--primary-color, #AA83FF) 0%,
    var(--secondary-color, #D4DEC7) 50%,
    var(--accent-color, #3F7DFB) 100%
  );
  opacity: 0.6;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.comment-item {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 20px;
  opacity: 0;
  animation: slideInUp 0.6s ease-out forwards;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.timeline-node {
  position: absolute;
  left: -30px;
  top: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.node-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--primary-color, #AA83FF);
  border: 3px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 0 10px rgba(170, 131, 255, 0.5);
  z-index: 2;
}

.node-connector {
  width: 2px;
  height: 40px;
  background: linear-gradient(
    to bottom,
    var(--primary-color, #AA83FF),
    transparent
  );
  margin-top: -2px;
}

.comment-box {
  flex: 1;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 16px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(170, 131, 255, 0.3);
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
  }
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 14px;
}

.comment-author {
  color: var(--primary-color, #AA83FF);
  font-weight: 500;
}

.comment-time {
  color: rgba(255, 255, 255, 0.6);
  font-size: 12px;
}

.comment-content {
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.6;
  margin-bottom: 16px;
  word-wrap: break-word;
}

.comment-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  background: transparent;
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(255, 255, 255, 0.1);
    color: rgba(255, 255, 255, 0.9);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  &.active {
    background: var(--primary-color, #AA83FF);
    border-color: var(--primary-color, #AA83FF);
    color: white;
  }
}

.like-btn.active {
  background: #4CAF50;
  border-color: #4CAF50;
}

.dislike-btn.active {
  background: #f44336;
  border-color: #f44336;
}

.delete-btn {
  color: #f44336;
  
  &:hover {
    background: rgba(244, 67, 54, 0.1);
    border-color: #f44336;
  }
}

.load-more {
  text-align: center;
  margin-top: 30px;
}

.load-more-btn {
  padding: 12px 24px;
  border: 1px solid var(--primary-color, #AA83FF);
  border-radius: 8px;
  background: transparent;
  color: var(--primary-color, #AA83FF);
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: var(--primary-color, #AA83FF);
    color: white;
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: rgba(255, 255, 255, 0.6);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

/* 图标样式 */
.icon-like::before { content: '👍'; }
.icon-dislike::before { content: '👎'; }
.icon-delete::before { content: '🗑️'; }

/* 响应式设计 */
@media (max-width: 768px) {
  .comment-timeline {
    padding: 10px;
  }
  
  .timeline-container {
    padding-left: 30px;
  }
  
  .timeline-line {
    left: 15px;
  }
  
  .timeline-node {
    left: -25px;
  }
  
  .comment-box {
    padding: 12px;
  }
  
  .comment-actions {
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .action-btn {
    font-size: 11px;
    padding: 4px 8px;
  }
}
</style>
