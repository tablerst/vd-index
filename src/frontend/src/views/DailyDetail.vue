<template>
  <div class="daily-detail-page">
    <header class="detail-header">
      <button class="back" @click="goBack">← 返回</button>
      <div class="meta">
        <img v-if="post?.author_avatar_url" :src="post.author_avatar_url" class="avatar" alt="avatar" />
        <div class="author">
          <div class="name">{{ post?.author_display_name || `用户${post?.author_user_id || ''}` }}</div>
          <div class="time" v-if="post">{{ formatTime(post.created_at) }}</div>
        </div>
      </div>
    </header>

    <main class="detail-content">
      <div v-if="loading" class="loading">加载中…</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <template v-else>
        <DailyEditor
          v-if="isAuthor(post?.author_user_id)"
          :initial-content="post?.content_jsonb || undefined"
          :autosave-key="post ? `daily_edit_${post.id}` : undefined"
          @save="saveDetail"
          @cancel="goBack"
        />
        <TiptapViewer v-else :doc="post?.content_jsonb || null" />
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
// 中文注释：路由详情页；作者可编辑，非作者只读
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DailyEditor from '@/components/daily/DailyEditor.vue'
import TiptapViewer from '@/components/daily/TiptapViewer.vue'
import { dailyApi, type DailyPostItem } from '@/services/daily'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const id = computed(() => Number(route.params.id))
const post = ref<DailyPostItem | null>(null)
const loading = ref(false)
const error = ref('')

function isAuthor(authorUserId?: number | null) {
  const uid = authStore.user?.id
  return !!uid && !!authorUserId && uid === authorUserId
}

async function fetchDetail() {
  loading.value = true
  error.value = ''
  try {
    post.value = await dailyApi.getDetail(id.value)
  } catch (e: any) {
    error.value = e?.message || '加载失败'
  } finally {
    loading.value = false
  }
}

async function saveDetail(json: Record<string, any>) {
  if (!post.value) return
  try {
    const updated = await dailyApi.updatePost(post.value.id, { content_jsonb: json })
    post.value = updated
    // 保存后返回列表
    goBack()
  } catch (e: any) {
    error.value = e?.message || '保存失败'
  }
}

function goBack() {
  router.back()
}

function formatTime(iso: string) {
  const d = new Date(iso)
  const now = new Date()
  const diff = (now.getTime() - d.getTime()) / 1000
  if (diff < 60) return '刚刚'
  if (diff < 3600) return `${Math.floor(diff / 60)} 分钟前`
  if (diff < 86400) return `${Math.floor(diff / 3600)} 小时前`
  return d.toLocaleDateString('zh-CN', { year: 'numeric', month: 'short', day: 'numeric' })
}

onMounted(fetchDetail)
</script>

<style scoped>
/* 中文注释：路由详情页的布局与样式（与列表页风格一致） */
.daily-detail-page { min-height: 100vh; background: var(--base-dark, #0f0f12); color: var(--text-primary); }
.detail-header { display:flex; align-items:center; justify-content:space-between; padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,.06); }
.back { background: transparent; border:1px solid var(--glass-border); color: var(--text-primary); border-radius: 8px; padding: 6px 10px; cursor: pointer; }
.meta { display:flex; align-items:center; gap:12px; }
.avatar { width:32px; height:32px; border-radius:50%; object-fit: cover; }
.author { display:flex; flex-direction:column; }
.name { font-weight:600; }
.time { font-size:12px; color: var(--text-secondary); }
.detail-content { padding: 16px; }
.loading { padding: 16px; color: var(--text-secondary); }
.error { color: #ff6b6b; text-align: center; padding: 16px; }
</style>

