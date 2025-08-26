<template>
  <div class="danmaku" :title="comment.content">
    <!-- 左侧头像 -->
    <img v-if="comment.author_avatar_url" class="avatar" :src="comment.author_avatar_url" alt="avatar" loading="lazy" decoding="async" />
    <div v-else class="avatar placeholder" aria-hidden="true">🙂</div>
    <!-- 右侧气泡内容 -->
    <div class="bubble">
      <div class="line">
        <span class="name">{{ displayName }}</span>
        <span class="time">· {{ formatTime(comment.created_at) }}</span>
      </div>
      <div class="content">{{ comment.content }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 中文注释：单条弹幕评论组件，左侧头像，右侧内容气泡，主题变量适配暗/亮色
import { computed } from 'vue'
import type { DailyCommentItem } from '@/services/daily'

const props = defineProps<{ comment: DailyCommentItem }>()

const displayName = computed(() => props.comment.author_display_name || `UID ${props.comment.author_user_id}`)

function formatTime(iso: string) {
  // 中文注释：简易相对时间显示（分钟/小时/日期）
  const d = new Date(iso)
  const now = new Date()
  const diff = (now.getTime() - d.getTime()) / 1000
  if (!isFinite(diff)) return ''
  if (diff < 60) return '刚刚'
  if (diff < 3600) return `${Math.floor(diff / 60)} 分钟前`
  if (diff < 86400) return `${Math.floor(diff / 3600)} 小时前`
  return d.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}
</script>

<style scoped>
/* 中文注释：采用主题色，玻璃拟态背景；宽度自适应以适配跑马灯 */
.danmaku {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: transparent; /* 由父级轨道控制背景 */
  color: var(--text-primary);
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  object-fit: cover;
  box-shadow: var(--shadow-soft);
  flex: 0 0 auto;
}
.avatar.placeholder {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--glass-bg);
  color: var(--text-secondary);
  font-size: 14px;
}

.bubble {
  max-width: min(48vw, 520px);
  min-width: 180px;
  padding: 8px 12px;
  border-radius: 12px;
  background: var(--glass-bg);
  box-shadow: var(--shadow-soft) inset;
}

.line {
  display: flex;
  gap: 6px;
  align-items: baseline;
  margin-bottom: 4px;
}
.name { font-weight: 600; color: var(--text-primary); }
.time { font-size: 12px; color: var(--text-secondary); }
.content { color: var(--text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
</style>

