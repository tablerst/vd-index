<template>
  <div class="post-list" ref="rootRef">
    <div v-if="loading" class="loading">加载中…</div>
    <ul v-else class="list">
      <li v-for="p in topPosts" :key="p.id" class="row list-item">
        <div class="meta">
          <div class="author-info">
            <img :src="avatarUrl(p)" class="avatar" alt="avatar" />
            <span class="author">{{ displayName(p) }}</span>
          </div>
          <span class="time">{{ formatTime(p.created_at) }}</span>
        </div>
        <div class="content">{{ p.content }}</div>
        <div class="ops">
          <button class="reply-btn" @click="replyTo(p.id)">回复</button>
        </div>

        <!-- 子回复列表（单层楼中楼） -->
        <ul v-if="childrenOf(p.id).length" class="children">
          <li v-for="c in childrenOf(p.id)" :key="c.id" class="row child">
            <div class="meta">
              <div class="author-info">
                <img :src="avatarUrl(c)" class="avatar" alt="avatar" />
                <span class="author">{{ displayName(c) }}</span>
              </div>
              <span class="time">{{ formatTime(c.created_at) }}</span>
            </div>
            <div class="content">{{ c.content }}</div>
          </li>
        </ul>

        <!-- 回复输入框（复用全站 CommentInput，含匿名开关） -->
        <div v-if="replyParentId === p.id" class="reply-input">
          <CommentInput
            :member-id="0"
            :loading="submitting"
            title="回复"
            :show-anonymous-option="true"
            :anonymous-default="true"
            @submit="(text, isAnon) => submitReply(p.id, text, !!isAnon)"
            @cancel="replyParentId = null"
          />
        </div>
      </li>
      <li v-if="topPosts.length === 0 && !loading" class="empty">还没有帖子</li>
    </ul>
    <div v-if="hasMore" class="more">
      <button class="load" @click="loadMore" :disabled="loading">加载更多</button>
    </div>
  </div>
  
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useActivitiesStore } from '@/stores/activities'
import { gsap } from 'gsap'
import CommentInput from '@/components/Comment/CommentInput.vue'
import type { ActThreadPost } from '@/services/api'

const props = defineProps<{ activityId: number }>()
const store = useActivitiesStore()

const entry = computed(() => store.threadPosts[props.activityId] || { items: [], loading: false, hasMore: true })
const items = computed(() => entry.value.items)
const loading = computed(() => !!entry.value.loading)
const hasMore = computed(() => !!entry.value.hasMore)

// 顶层评论（parent_id 为空）
const topPosts = computed(() => items.value.filter(p => !p.parent_id))

const replyParentId = ref<number | null>(null)
const submitting = ref(false)

const rootRef = ref<HTMLElement | null>(null)

onMounted(() => {
  if (!items.value.length) store.fetchThreadPosts(props.activityId).catch(() => {})
  try { if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return } catch {}
  if (rootRef.value) {
    const listItems = rootRef.value.querySelectorAll('.list-item')
    if (listItems?.length) gsap.from(listItems, { opacity: 0, y: 8, duration: 0.4, ease: 'power2.out', stagger: 0.03 })
  }
})

function loadMore() {
  store.fetchThreadPosts(props.activityId, entry.value.cursor || null).catch(() => {})
}

function formatTime(iso: string) {
  const dt = new Date(iso)
  return dt.toLocaleString('zh-CN')
}

function childrenOf(parentId: number) {
  return items.value.filter(p => p.parent_id === parentId)
}

function replyTo(parentId: number) {
  replyParentId.value = parentId
}

async function submitReply(parentId: number, text: string, isAnonymous: boolean) {
  const content = (text || '').trim()
  if (!content) return
  try {
    submitting.value = true
    await store.createThreadPost(props.activityId, { content, display_anonymous: !!isAnonymous, parent_id: parentId })
    replyParentId.value = null
  } finally {
    submitting.value = false
  }
}

// 展示昵称与头像：匿名显示“匿名”+默认头像，非匿名使用 DiceBear 占位
function displayName(p: ActThreadPost) {
  if (p.display_anonymous) return '匿名'
  // 优先后端聚合昵称
  if (p.author_display_name) return p.author_display_name
  return `#${p.author_id}`
}
function avatarUrl(p: ActThreadPost) {
  if (p.display_anonymous) return '/avatars/default.jpg'
  // 优先后端聚合头像
  if (p.author_avatar_url) return p.author_avatar_url
  // 回退：使用稳定种子的 DiceBear 占位头像
  return `https://api.dicebear.com/7.x/avataaars/svg?seed=user_${p.author_id}`
}
</script>

<style scoped lang="scss">
.list { list-style: none; padding: 0; margin: 0; display: grid; gap: 10px; }
.row { background: color-mix(in srgb, var(--base-dark) 82%, rgba(0,0,0,0.15)); border: 1px solid var(--divider-color, #444); border-radius: 10px; padding: 10px; transition: transform .15s ease, background .2s ease; }
.row:hover { transform: translateY(-1px); background: color-mix(in srgb, var(--primary) 8%, transparent); border-color: var(--primary); }
.meta { color: var(--text-secondary); font-size: 12px; display: flex; gap: 8px; align-items: center; justify-content: space-between; }
.author-info { display: inline-flex; align-items: center; gap: 8px; }
.author-info .avatar { width: 24px; height: 24px; border-radius: 50%; object-fit: cover; border: 1px solid rgba(255,255,255,0.15); }
.content { margin-top: 6px; white-space: pre-wrap; line-height: 1.6; }
.ops { margin-top: 6px; display: flex; gap: 8px; }
.reply-btn { padding: 4px 8px; border: 1px solid var(--divider-color, #444); background: transparent; color: var(--text-secondary); border-radius: 8px; }
.reply-btn:hover { color: var(--primary); border-color: var(--primary); }
.children { list-style: none; padding-left: 12px; margin-top: 8px; display: grid; gap: 8px; border-left: 2px dashed rgba(255,255,255,0.08); }
.child { background: color-mix(in srgb, var(--base-dark) 88%, rgba(0,0,0,0.12)); }
.reply-input { margin-top: 8px; }
.loading, .empty { color: var(--text-secondary); }
.more { margin-top: 10px; display: flex; justify-content: center; }
.load { padding: 6px 12px; border: 1px solid var(--primary-6, var(--primary)); color: var(--primary-6, var(--primary)); background: transparent; border-radius: 8px; }
</style>


