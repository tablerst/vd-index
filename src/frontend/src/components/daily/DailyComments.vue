<template>
  <div class="daily-comments">
    <!-- 输入区（需登录） -->
    <div class="input-card" v-if="authed">
      <n-input
        v-model:value="content"
        type="textarea"
        :autosize="{ minRows: 2, maxRows: 5 }"
        placeholder="写下你的评论..."
      />
      <div class="actions">
        <n-button type="primary" :loading="submitting" @click="submit">发布</n-button>
      </div>
    </div>

    <!-- 评论列表：卡片式，支持楼中楼 -->
    <div class="list">
      <div v-for="c in data.top_comments" :key="c.id" class="comment-card">
        <div class="meta">
          <span class="author">UID {{ c.author_user_id }}</span>
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
              <span class="author">UID {{ rc.author_user_id }}</span>
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

        <!-- 回复输入 -->
        <div v-if="replyParentId === c.id && authed" class="reply-input">
          <n-input
            v-model:value="replyContent"
            type="textarea"
            :autosize="{ minRows: 2, maxRows: 4 }"
            placeholder="回复内容..."
          />
          <div class="actions">
            <n-button size="small" :loading="submitting" @click="submitReply(c.id)">回复</n-button>
            <n-button size="small" quaternary @click="replyParentId = null">取消</n-button>
          </div>
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
import { NInput, NButton, NPagination, NPopconfirm, useMessage } from 'naive-ui'
import { dailyApi, type DailyCommentListResponse, type DailyCommentItem } from '@/services/daily'
import { useAuthStore } from '@/stores/auth'

const props = defineProps<{ postId: number }>()

const msg = useMessage()
const auth = useAuthStore()
const authed = computed(() => !!auth.user)

const data = ref<DailyCommentListResponse>({ top_comments: [], children_map: {}, total: 0, page: 1, page_size: 20, total_pages: 1 })
const pageSize = 20
let page = 1

const content = ref('')
const submitting = ref(false)

const replyParentId = ref<number | null>(null)
const replyContent = ref('')

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

async function submit() {
  if (!content.value.trim()) return
  try {
    submitting.value = true
    await dailyApi.createComment(props.postId, content.value)
    content.value = ''
    await load()
    msg.success('已发布')
  } catch (e: any) {
    msg.error(e?.message || '发布失败')
  } finally {
    submitting.value = false
  }
}

function replyTo(id: number) {
  replyParentId.value = id
  replyContent.value = ''
}

async function submitReply(parentId: number) {
  if (!replyContent.value.trim()) return
  try {
    submitting.value = true
    await dailyApi.createComment(props.postId, replyContent.value, parentId)
    replyContent.value = ''
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
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 12px;
  }
  .actions {
    margin-top: 8px;
    display: flex;
    justify-content: flex-end;
    gap: 8px;
  }
  .comment-card, .reply-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px;
    padding: 10px 12px;
    margin-bottom: 10px;
  }
  .comment-card .meta, .reply-card .meta {
    font-size: 12px;
    color: var(--text-secondary);
    display: flex;
    justify-content: space-between;
  }
  .comment-card .content, .reply-card .content {
    margin: 6px 0;
    color: var(--text-primary);
  }
  .ops { display: flex; gap: 8px; }
  .children { margin-left: 12px; border-left: 2px dashed rgba(255,255,255,0.06); padding-left: 10px; }
  .pager { display: flex; justify-content: center; margin-top: 8px; }
}
</style>

