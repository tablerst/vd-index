<template>
  <div class="comment-timeline">
    <!-- 时间线容器 -->
    <div class="timeline-container">
      <!-- 左侧主时间线 -->
      <div class="main-timeline"></div>

      <!-- 评论列表 -->
      <div class="comments-list">
        <div
          v-for="(comment, index) in comments"
          :key="comment.id"
          class="comment-item"
          :style="{ animationDelay: `${index * 0.1}s` }"
        >
          <!-- 时间线节点和连接器 -->
          <div class="timeline-node">
            <div class="node-dot">
              <div class="node-pulse"></div>
            </div>
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
                <svg class="action-icon" viewBox="0 0 24 24" fill="none">
                  <path d="M7 22H4a2 2 0 01-2-2v-7a2 2 0 012-2h3m0 0V9a2 2 0 012-2h9l-3.5 12H9a2 2 0 01-2-2v-2.5"
                        stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <span class="action-count">{{ comment.likes }}</span>
              </button>

              <button
                class="action-btn dislike-btn"
                :class="{ active: comment.userDisliked }"
                @click="handleDislike(comment)"
                :disabled="loading"
              >
                <svg class="action-icon" viewBox="0 0 24 24" fill="none">
                  <path d="M17 2H20a2 2 0 012 2v7a2 2 0 01-2 2h-3m0 0v4a2 2 0 01-2 2H6l3.5-12H15a2 2 0 012 2v2.5"
                        stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <span class="action-count">{{ comment.dislikes }}</span>
              </button>

              <button
                v-if="canDelete"
                class="action-btn delete-btn"
                @click="handleDelete(comment)"
                :disabled="loading"
              >
                <svg class="action-icon" viewBox="0 0 24 24" fill="none">
                  <path d="M3 6h18M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2m3 0v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6h14zM10 11v6M14 11v6"
                        stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <span class="action-text">删除</span>
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

withDefaults(defineProps<Props>(), {
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
  padding-left: 60px;
}

.main-timeline {
  position: absolute;
  left: 10px;
  top: 0;
  bottom: 0;
  width: 3px;
  background: linear-gradient(
    to bottom,
    var(--primary) 0%,
    var(--secondary) 50%,
    var(--accent-blue) 100%
  );
  border-radius: 2px;
  opacity: 0.8;
  box-shadow: var(--shadow-glow);
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 40px;
}

.comment-item {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 0;
  opacity: 0;
  animation: slideInUp 0.6s ease-out forwards;

  &:hover {
    .node-connector {      
      width: 25px;
    }
  }
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.timeline-node {
  position: absolute;
  left: -27px;
  top: 20px;
  display: flex;
  align-items: center;
  z-index: 3;
}

.node-dot {
  position: relative;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--primary);
  border: 4px solid var(--base-light);
  box-shadow:
    0 0 0 2px var(--primary),
    var(--shadow-glow);
  animation: nodePulse 3s ease-in-out infinite;
}

.node-pulse {
  position: absolute;
  top: -4px;
  left: -4px;
  right: -4px;
  bottom: -4px;
  border-radius: 50%;
  border: 2px solid var(--primary);
  opacity: 0;
  animation: pulseRing 2s ease-out infinite;
}

@keyframes nodePulse {
  0%, 100% {
    transform: scale(1);
    box-shadow:
      0 0 0 2px var(--primary),
      var(--shadow-glow);
  }
  50% {
    transform: scale(1.1);
    box-shadow:
      0 0 0 2px var(--primary),
      var(--shadow-glow);
  }
}

@keyframes pulseRing {
  0% {
    transform: scale(0.8);
    opacity: 1;
  }
  100% {
    transform: scale(2);
    opacity: 0;
  }
}

@keyframes connectorPulse {
  0%, 100% {
    opacity: 0.8;
    box-shadow: 0 0 5px rgba(170, 131, 255, 0.3);
  }
  50% {
    opacity: 1;
    box-shadow: 0 0 10px rgba(170, 131, 255, 0.6);
  }
}

@keyframes connectorGlow {
  0% {
    opacity: 0;
    transform: scaleY(1);
  }
  50% {
    opacity: 0.6;
    transform: scaleY(1.5);
  }
  100% {
    opacity: 0;
    transform: scaleY(1);
  }
}

.node-connector {
  width: 19px;
  height: 2px;
  background: linear-gradient(
    to right,
    var(--primary) 0%,
    var(--primary-light) 100%
  );
  margin-left: 0px;
  border-radius: 1px;
  position: relative;
  animation: connectorPulse 3s ease-in-out infinite;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);

  &::before {
    content: '';
    position: absolute;
    top: -1px;
    left: 0;
    right: 0;
    bottom: -1px;
    background: linear-gradient(
      to right,
      var(--primary) 0%,
      var(--primary-lighter) 100%
    );
    border-radius: 2px;
    opacity: 0;
    animation: connectorGlow 2s ease-out infinite;
  }
}

.comment-box {
  flex: 1;
  margin-left: 8px;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 20px;
  backdrop-filter: blur(15px);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;

  &:hover {
    background: var(--glass-bg-strong);
    border-color: var(--primary);
    transform: translateY(-3px) translateX(5px);
    box-shadow: var(--shadow-glow);
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
  color: var(--primary);
  font-weight: 500;
}

.comment-time {
  color: var(--text-secondary);
  font-size: 12px;
}

.comment-content {
  color: var(--text-primary);
  line-height: 1.6;
  margin-bottom: 16px;
  word-wrap: break-word;
}

.comment-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-top: 4px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  background: var(--surface-1);
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(
      90deg,
      transparent,
      var(--surface-1),
      transparent
    );
    transition: left 0.5s ease;
  }

  &:hover {
    background: var(--surface-2);
    border-color: var(--glass-border);
    color: var(--text-primary);
    transform: translateY(-1px);
    box-shadow: var(--shadow-medium);

    &::before {
      left: 100%;
    }
  }

  &:active {
    transform: translateY(0);
  }

  &:disabled {
    opacity: 0.4;
    cursor: not-allowed;
    transform: none;
  }

  &.active {
    background: var(--primary);
    border-color: var(--primary);
    color: white;
    box-shadow: var(--shadow-glow);
  }
}

.action-icon {
  width: 16px;
  height: 16px;
  transition: transform 0.3s ease;
}

.action-count, .action-text {
  font-weight: 600;
  min-width: 16px;
  text-align: center;
}

.like-btn {
  &.active {
    background: linear-gradient(135deg, var(--success), #45a049);
    border-color: var(--success);
    box-shadow: 0 0 15px rgba(76, 175, 80, 0.4);
  }

  &:hover:not(.active) {
    border-color: rgba(76, 175, 80, 0.5);
    color: var(--success);
  }

  &:hover .action-icon {
    transform: scale(1.1) rotate(-5deg);
  }
}

.dislike-btn {
  &.active {
    background: linear-gradient(135deg, var(--error-alert), #d32f2f);
    border-color: var(--error-alert);
    box-shadow: 0 0 15px rgba(244, 67, 54, 0.4);
  }

  &:hover:not(.active) {
    border-color: rgba(244, 67, 54, 0.5);
    color: var(--error-alert);
  }

  &:hover .action-icon {
    transform: scale(1.1) rotate(5deg);
  }
}

.delete-btn {
  color: var(--error-alert);

  &:hover {
    background: rgba(244, 67, 54, 0.1);
    border-color: var(--error-alert);
    color: var(--error-alert);
  }

  &:hover .action-icon {
    transform: scale(1.1);
  }
}

.load-more {
  text-align: center;
  margin-top: 30px;
}

.load-more-btn {
  padding: 12px 24px;
  border: 1px solid var(--primary);
  border-radius: 8px;
  background: transparent;
  color: var(--primary);
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    background: var(--primary);
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
  color: var(--text-secondary);
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
    padding-left: 40px;
  }

  .main-timeline {
    left: 15px;
  }

  .timeline-node {
    left: -22px;
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
