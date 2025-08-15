<template>
  <div class="daily-card" role="button" tabindex="0" @click="emit('open', post.id)"
    @keydown.enter.prevent="emit('open', post.id)" @keydown.space.prevent="emit('open', post.id)">
    <!-- 主图区域 -->
    <div class="cover">
      <img v-if="firstImage" :src="firstImage" alt="cover" loading="lazy" decoding="async" />
    </div>

    <!-- 信息条：头像+昵称+时间 -->
    <div class="meta">
      <img v-if="post.author_avatar_url" class="avatar" :src="post.author_avatar_url" alt="avatar" loading="lazy"
        decoding="async" />
      <div class="author">
        <div class="name">{{ post.author_display_name || '未知作者' }}</div>
        <div class="time">{{ formatTime(post.created_at) }}</div>
      </div>
    </div>

    <!-- 正文摘要 -->
    <div v-if="post.content" class="content" :title="post.content">{{ post.content }}</div>

    <!-- 底部条：标签与统计 -->
    <div class="footer">
      <div class="tags">
        <span v-for="(t, i) in post.tags.slice(0, 3)" :key="i" class="tag">#{{ t }}</span>
      </div>
      <div class="stats">
        <span class="stat">❤ {{ post.likes_count }}</span>
        <span class="stat">💬 {{ post.comments_count }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 中文注释：展示单条 DailyPost 卡片，支持点击/键盘打开详情
import { computed } from 'vue'
import type { DailyPostItem } from '@/services/daily'

const props = defineProps<{ post: DailyPostItem }>()
const emit = defineEmits<{ (e: 'open', id: number): void }>()
const firstImage = computed(() => props.post.images?.[0] || '')

function formatTime(iso: string) {
  const d = new Date(iso)
  const now = new Date()
  const diff = (now.getTime() - d.getTime()) / 1000
  if (diff < 60) return '刚刚'
  if (diff < 3600) return `${Math.floor(diff / 60)} 分钟前`
  if (diff < 86400) return `${Math.floor(diff / 3600)} 小时前`
  return d.toLocaleDateString('zh-CN', { year: 'numeric', month: 'short', day: 'numeric' })
}
</script>

<style scoped>
/* 中文注释：颜色使用主题变量，卡片有轻微内阴影，暗色适配；可点击指针 */
.daily-card {
  background: var(--glass-bg);
  color: var(--text-primary);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--shadow-soft) inset;
  display: flex;
  flex-direction: column;
  transition: transform .25s ease, box-shadow .25s ease, opacity .25s ease;
  cursor: pointer;
}

.daily-card:hover {
  transform: scale(1.02);
  box-shadow: var(--shadow-medium);
}

.daily-card:focus-within {
  transform: scale(1.015);
  outline: none;
  box-shadow: 0 0 0 2px color-mix(in oklch, var(--primary) 28%, transparent);
}

.cover {
  position: relative;
  width: 100%;
  overflow: hidden;
}

.cover img {
  width: 100%;
  display: block;
  object-fit: cover;
}

.meta {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.author {
  display: flex;
  flex-direction: column;
}

.name {
  font-weight: 600;
  color: var(--text-primary);
}

.time {
  font-size: 12px;
  color: var(--text-secondary);
}

.content {
  padding: 0 12px 12px;
  color: var(--text-primary);
  line-height: 1.5;
  max-height: 3.0em;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-top: 1px solid var(--border-secondary);
}

.tags {
  display: flex;
  gap: 8px;
  flex-wrap: nowrap;
  overflow: hidden;
}

.tag {
  background: var(--surface-pressed);
  color: var(--text-secondary);
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  white-space: nowrap;
}

.stats {
  display: flex;
  gap: 12px;
  color: var(--text-secondary, #bbb);
  font-size: 12px;
}
</style>
