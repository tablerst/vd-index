<template>
  <div class="daily-detail-page">
    <header class="detail-header">
      <n-button
        class="icon-circle-btn back-btn"
        circle
        type="primary"
        size="small"
        @click="goBack"
        title="返回"
        aria-label="返回"
      >
        <ArrowLeft :size="18" />
      </n-button>
      <div class="meta">
        <img v-if="post?.author_avatar_url" :src="post.author_avatar_url" class="avatar" alt="avatar" />
        <div class="author">
          <div class="name">{{ post?.author_display_name || `用户${post?.author_user_id || ''}` }}</div>
          <div class="time" v-if="post">{{ formatTime(post.created_at) }}</div>
        </div>
      </div>
    </header>

    <main class="detail-content">
      <n-spin :show="loading" size="large" class="detail-spin">
        <template #description>加载中…</template>
        <div v-if="error" class="error">{{ error }}</div>
        <template v-else>
          <DailyEditor
            v-if="isAuthor(post?.author_user_id)"
            class="detail-editor"
            :initial-content="post?.content_jsonb || undefined"
            :autosave-key="post ? `daily_edit_${post.id}` : undefined"
            @save="saveDetail"
            @cancel="goBack"
          />
          <TiptapViewer v-else :doc="post?.content_jsonb || null" />

          <!-- 内容与评论的视觉分割线 -->
          <div class="content-divider" aria-hidden="true"></div>

          <!-- 新增：评论区 -->
          <section class="comments-section" v-if="post">
            <DailyComments :post-id="post.id" />
          </section>
        </template>
      </n-spin>
    </main>
  </div>
</template>

<script setup lang="ts">
// 中文注释：路由详情页；作者可编辑，非作者只读
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DailyEditor from '@/components/daily/DailyEditor.vue'
import TiptapViewer from '@/components/daily/TiptapViewer.vue'
import DailyComments from '@/components/daily/DailyComments.vue'
import { NSpin, NButton } from 'naive-ui'
import { ArrowLeft } from 'lucide-vue-next'
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
.meta { display:flex; align-items:center; gap:12px; }
.detail-content { padding: 12px 16px; }
.detail-editor { margin: 0 auto; max-width: 880px; }
.comments-section { margin: 16px auto; max-width: 880px; }
.avatar { width:32px; height:32px; border-radius:50%; object-fit: cover; }
.author { display:flex; flex-direction:column; }
.name { font-weight:600; }
.time { font-size:12px; color: var(--text-secondary); }
.detail-content { padding: 16px; min-height: 50vh; }

  /* 内容与评论的视觉分割线样式 */
  .content-divider {
    /* 上下间距加大，明确分区 */
    margin: 28px auto 20px;
    max-width: 880px;
    height: 2px;
    /* 渐变 + 主题混合，提升在深浅主题下的可见性 */
    background: linear-gradient(90deg,
      transparent,
      color-mix(in oklch, var(--primary) 75%, #ffffff) 15%,
      color-mix(in oklch, var(--primary) 85%, #000000) 50%,
      color-mix(in oklch, var(--primary) 75%, #ffffff) 85%,
      transparent
    );
    border: none;
    filter: drop-shadow(0 0 4px color-mix(in oklch, var(--primary) 35%, transparent));
    opacity: .9;
    border-radius: 2px;
  }

/* 中文注释：让 NSpin 居中显示加载动画与描述文案 */
.detail-spin { display: block; width: 100%; }
.detail-spin :deep(.n-spin-body) { min-height: 260px; display: flex; align-items: center; justify-content: center; }
.detail-spin :deep(.n-spin-content) { width: 100%; }

/* 中文注释：作者编辑模式下，提升编辑器可视高度 */
.detail-editor :deep(.editor-pane) { min-height: 360px; max-height: 70vh; }

/* 中文注释：圆形主题按钮动效（与列表页一致） */
.icon-circle-btn :deep(.n-button__content) {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.icon-circle-btn.n-button--primary-type {
  background: var(--primary) !important;
  border: none !important;
  color: var(--text-inverse) !important;
}
.icon-circle-btn.n-button--primary-type:hover {
  background: var(--primary-hover) !important;
  box-shadow: 0 8px 22px rgba(170, 131, 255, 0.25);
  transform: translateY(-1px);
}
.icon-circle-btn.n-button--primary-type:active {
  background: var(--primary-pressed) !important;
  transform: translateY(0);
}
.icon-circle-btn svg { color: var(--text-inverse); }

.error { color: #ff6b6b; text-align: center; padding: 16px; }
</style>

