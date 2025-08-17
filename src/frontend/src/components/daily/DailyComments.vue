<template>
  <div class="daily-comments">
    <!-- 输入区（需登录） -->
    <div class="input-card" v-if="authed">
      <!-- 复用全站评论输入样式组件 -->
      <CommentInput
        :member-id="currentMemberId"
        :loading="submitting"
        title="发表评论"
        :show-anonymous-option="false"
        @submit="onSubmitFromInput"
        @cancel="onCancelInput"
      />
    </div>

    <!-- 无权限提示 -->
    <div v-else class="signin-hint">
      <n-button type="primary" quaternary disabled>登录后参与讨论</n-button>
    </div>


    <!-- 评论列表：卡片式，支持楼中楼 -->
    <div class="list">
      <div v-for="c in data.top_comments" :key="c.id" class="comment-card">
        <div class="meta">
          <div class="author-info">
            <img :src="avatarUrl(c)" class="avatar" alt="avatar" />
            <span class="name">{{ displayName(c) }}</span>
          </div>
          <span class="time">{{ formatTime(c.created_at) }}</span>
        </div>
        <div class="content">{{ c.content }}</div>
        <div class="ops">
          <n-button text @click="like(c.id)">👍 {{ c.likes }}</n-button>
          <n-button text @click="dislike(c.id)">👎 {{ c.dislikes }}</n-button>
          <n-button text @click="replyTo(c.id)">回复</n-button>
          <n-popconfirm v-if="canDelete(c)" @positive-click="remove(c.id)">
            <template #trigger>
              <n-button text>删除</n-button>
            </template>
            确认删除此评论？
          </n-popconfirm>
        </div>

        <!-- 子回复 -->
        <div v-if="childrenOf(c.id).length" class="children">
          <div v-for="rc in childrenOf(c.id)" :key="rc.id" class="reply-card">
            <div class="meta">
              <div class="author-info">
                <img :src="avatarUrl(rc)" class="avatar" alt="avatar" />
                <span class="name">{{ displayName(rc) }}</span>
              </div>
              <span class="time">{{ formatTime(rc.created_at) }}</span>
            </div>
            <div class="content">{{ rc.content }}</div>
            <div class="ops">
              <n-button text @click="like(rc.id)">👍 {{ rc.likes }}</n-button>
              <n-button text @click="dislike(rc.id)">👎 {{ rc.dislikes }}</n-button>
              <n-popconfirm v-if="canDelete(rc)" @positive-click="remove(rc.id)">
                <template #trigger>
                  <n-button text>删除</n-button>
                </template>
                确认删除此评论？
              </n-popconfirm>
            </div>
          </div>
        </div>

        <!-- 回复输入：统一使用 CommentInput 样式 -->
        <div v-if="replyParentId === c.id && authed" class="reply-input">
          <CommentInput
            :member-id="currentMemberId"
            :loading="submitting"
            title="回复评论"
            :show-anonymous-option="false"
            @submit="(text)=>submitReply(c.id, text)"
            @cancel="replyParentId = null"
          />
        </div>
      </div>

      <!-- 分页 -->
      <div class="pager" v-if="data.total_pages > 1">
        <n-pagination
          :page="page"
          :page-size="pageSize"
          :page-count="data.total_pages"
          @update:page="(p:number)=>{ page = p; load(); }"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 中文注释：日常帖下的简易卡片式评论，支持楼中楼（单层）
import { ref, onMounted, computed } from 'vue'
import { NButton, NPagination, NPopconfirm, useMessage } from 'naive-ui'
import { dailyApi, type DailyCommentListResponse, type DailyCommentItem } from '@/services/daily'
import { useAuthStore } from '@/stores/auth'
import CommentInput from '@/components/Comment/CommentInput.vue'

const props = defineProps<{ postId: number }>()

const msg = useMessage()
const auth = useAuthStore()
const authed = computed(() => !!auth.user)

const data = ref<DailyCommentListResponse>({ top_comments: [], children_map: {}, total: 0, page: 1, page_size: 20, total_pages: 1 })
const pageSize = 20
let page = 1

const submitting = ref(false)

// 头像与昵称展示：优先使用后端聚合字段；回退到 DiceBear + UID
function displayName(c: DailyCommentItem) {
  return c.author_display_name || `用户${c.author_user_id}`
}
function avatarUrl(c: DailyCommentItem) {
  if (c.author_avatar_url) return c.author_avatar_url
  // 使用用户名种子回退（仅用于占位）
  return `https://api.dicebear.com/7.x/avataaars/svg?seed=user_${c.author_user_id}`
}

// 复用样式化输入组件的回调
const currentMemberId = 0 // Daily评论不基于memberId，此处占位但不使用
async function onSubmitFromInput(text: string, _isAnonymous?: boolean) {
  if (!text.trim()) return
  try {
    submitting.value = true
    await dailyApi.createComment(props.postId, text)
    await load()
    msg.success('已发布')
  } catch (e: any) {
    msg.error(e?.message || '发布失败')
  } finally {
    submitting.value = false
  }
}
function onCancelInput() {
  // 无特殊逻辑
}

const replyParentId = ref<number | null>(null)

function childrenOf(id: number): DailyCommentItem[] {
  return data.value.children_map[id] || []
}

function formatTime(iso: string) {
  const d = new Date(iso)
  return d.toLocaleString()
}

async function load() {
  try {
    const res = await dailyApi.getComments(props.postId, page, pageSize)
    data.value = res
  } catch (e: any) {
    msg.error(e?.message || '加载评论失败')
  }
}


function replyTo(id: number) {
  // 中文注释：显示统一样式的回复输入框
  replyParentId.value = id
}

async function submitReply(parentId: number, text: string) {
  const content = (text || '').trim()
  if (!content) return
  try {
    submitting.value = true
    await dailyApi.createComment(props.postId, content, parentId)
    replyParentId.value = null
    await load()
    msg.success('已回复')
  } catch (e: any) {
    msg.error(e?.message || '回复失败')
  } finally {
    submitting.value = false
  }
}

async function like(id: number) {
  try { await dailyApi.likeComment(id); await load() } catch { /* ignore */ }
}
async function dislike(id: number) {
  try { await dailyApi.dislikeComment(id); await load() } catch { /* ignore */ }
}
async function remove(id: number) {
  try { await dailyApi.deleteComment(id); await load(); msg.success('已删除') } catch { msg.error('删除失败') }
}

function canDelete(c: DailyCommentItem): boolean {
  const userId = auth.user?.id
  return !!userId && (userId === c.author_user_id || auth.user?.role === 'admin')
}

onMounted(load)
</script>

<style scoped lang="scss">
.daily-comments {
  .input-card {
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    padding: 16px;
    margin-bottom: 16px;
    box-shadow: var(--shadow-soft);

    /* 放大输入区整体尺寸，和页面其他元素一致 */
    :deep(.comment-input) { max-width: 880px; }
    :deep(.input-title) { font-size: 20px; }
    :deep(.comment-textarea) { min-height: 140px; font-size: 15px; }
    :deep(.input-container) { border-radius: 16px; }
  }

  .list { margin-top: 8px; }

  /* 隐藏匿名相关元素（在 Daily 评论中不展示匿名区块） */
  :deep(.anonymous-badge),
  :deep(.anonymous-toggle) { display: none !important; }

  .actions { margin-top: 8px; display: flex; justify-content: flex-end; gap: 8px; }

  /* 卡片化样式，增加景深与悬浮交互 */
  .comment-card, .reply-card {
    background: var(--surface-1);
    border: 1px solid var(--glass-border);
    border-radius: 14px;
    padding: 12px 14px;
    margin-bottom: 12px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.18);
    transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease;
  }
  .comment-card:hover { transform: translateY(-2px); box-shadow: 0 10px 24px rgba(0,0,0,0.22); border-color: var(--primary-alpha, rgba(170,131,255,.35)); }
  .reply-card { background: var(--surface-2); }

  .comment-card .meta, .reply-card .meta {
    font-size: 12px;
    color: var(--text-secondary);
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
  }
  .author-info { display: flex; align-items: center; gap: 8px; }
  .author-info .avatar { width: 24px; height: 24px; border-radius: 50%; object-fit: cover; border: 1px solid rgba(255,255,255,0.15); }
  .author-info .name { color: var(--text-primary); font-weight: 600; }

  .comment-card .content, .reply-card .content { margin: 8px 0; color: var(--text-primary); line-height: 1.7; }
  .ops { display: flex; gap: 6px; }

  .children { margin-left: 14px; border-left: 2px dashed rgba(255,255,255,0.06); padding-left: 12px; }
  .pager { display: flex; justify-content: center; margin-top: 12px; }

  /* 主题兼容的按钮颜色（文本按钮） */
  :deep(.n-button--text-type) { color: var(--text-secondary); }
  :deep(.n-button--text-type:hover) { color: var(--primary); }

  .signin-hint { margin: 12px 0; display: flex; justify-content: center; }
}

</style>

