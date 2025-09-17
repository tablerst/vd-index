<template>
  <div class="act-vote" ref="rootRef">
    <header class="head">
      <div class="titles">
        <h3 class="title">{{ activity.title }}</h3>
        <p v-if="activity.description" class="desc">{{ activity.description }}</p>
      </div>
      <div class="spacer" />
      <div class="admin" v-if="isAuthenticated">
        <input class="input small" v-model="newOption" placeholder="新增选项标签" :disabled="!isAuthenticated"
          @keyup.enter="addOption()" />
        <button class="btn small" @click="addOption" :disabled="!newOption.trim() || !isAuthenticated"
          title="新增选项">新增选项</button>
        <button class="btn small warn" @click="closeAct" v-if="isAdmin">关闭活动</button>
      </div>
    </header>

    <section class="grid">
      <!-- 左侧：合并的选项 + 排行列表 -->
      <div class="panel vote-combined" :data-refreshing="refreshingOptions ? 'true' : null">
        <div class="panel-header">
          <div class="chips">
            <span class="chip" :class="statusClass">{{ statusText }}</span>
            <label class="switch">
              <input type="checkbox" v-model="anonymousPreference" />
              <span class="slider" aria-hidden="true"></span>
              <span class="label">匿名展示</span>
            </label>
          </div>
          <div class="right buttons-gap">
            <span v-if="!isAuthenticated" class="hint">登录后可投票</span>
          </div>
        </div>

        <div v-if="(optionsLoading || rankingLoading) && merged.length === 0" class="loading-wrap">
          <span class="spinner" aria-hidden="true" />
          <span class="loading-text">加载中…</span>
        </div>

        <ul v-else class="vote-list" role="list" ref="voteListRef">
          <li v-for="opt in merged" :key="opt.id" class="vote-row"
            :class="{ selected: selectedOptionId === opt.id, locked: canManage && hasVotes(opt.id as number) }">
            <label class="row-main">
              <span class="radio">
                <input type="radio" :name="radioName" :value="opt.id" v-model="selectedOptionId"
                  :disabled="!isAuthenticated" />
                <span class="dot" aria-hidden="true" />
              </span>
              <div class="row-top">
                <span class="name">{{ opt.label }}</span>
                <span class="counts">{{ opt.votes }}<span class="pct">（{{ opt.pct }}%）</span></span>
              </div>
              <div class="bar">
                <div class="bar-fill" :style="{ width: `${opt.pct}%` }"></div>
              </div>
              <span class="badge" v-if="voteOfMe === opt.id">已投</span>
              <span v-if="canManage && opt.id && typeof opt.id === 'number' && voteOfMe !== opt.id" class="delete-right"
                :class="{ disabled: hasVotes(opt.id as number) }"
                :title="hasVotes(opt.id as number) ? '该选项已有投票，无法删除' : '删除选项'"
                @click.stop="confirmDelete(opt.id)">×</span>
            </label>
          </li>
          <li v-if="merged.length === 0" class="empty">暂无可投项</li>
        </ul>

        <div class="actions-bottom">
          <button class="btn small primary" @click="onVote(selectedOptionId as number)" :disabled="!canVote">投票</button>
          <button class="btn small ghost" @click="onRevoke" :disabled="revokeLoading || voteOfMe === null">{{
            revokeLoading ? '撤销中…' : '撤销投票' }}</button>
        </div>
      </div>

      <!-- 右侧：评论区（支持排序） -->
      <div class="panel comments">
        <div class="panel-title">
          <span>讨论区</span>
          <div class="seg">
            <button class="seg-btn" :class="{ active: commentSort === 'latest' }"
              @click="commentSort = 'latest'">最新</button>
            <button class="seg-btn" :class="{ active: commentSort === 'hot' }" @click="commentSort = 'hot'">最热</button>
          </div>
        </div>
        <div class="comments-body">
          <PostComposer :activity-id="activity.id" @submit="onCreatePost" />
          <div class="list-wrap" ref="commentsWrapRef">
            <PostList :activity-id="activity.id" :active="!!active" :sort="commentSort" />
          </div>
        </div>
      </div>
    </section>
  </div>

</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch, inject } from 'vue'
import { useActivitiesStore } from '@/stores/activities'
import { useAuthStore } from '@/stores/auth'
import { storeToRefs } from 'pinia'
import type { ActActivity, ActRankingEntry, ActVoteOption } from '@/services/api'
import PostComposer from './PostComposer.vue'
import PostList from './PostList.vue'
import { gsap } from 'gsap'
// no theme dependency now

const props = defineProps<{ activity: ActActivity; active?: boolean }>()
const store = useActivitiesStore()
const auth = useAuthStore()
const { user, isAuthenticated } = storeToRefs(auth)

const entries = computed<ActRankingEntry[]>(() => store.ranking[props.activity.id] || [])
const options = computed<ActVoteOption[]>(() => store.options[props.activity.id]?.items || [])
const rankingLoading = computed(() => !!store.loading.ranking[props.activity.id])
const optionsLoading = computed(() => !!store.loading.options[props.activity.id])
const voteOfMe = computed(() => store.myVotes[props.activity.id] ?? null)
const revokeLoading = computed(() => !!store.loading.revoke?.[props.activity.id])
const anonymousPreference = computed({
  get: () => store.anonymousPreference,
  set: (v: boolean) => { store.anonymousPreference = v }
})
// 直接使用 Ref，避免双层 computed
const isAdmin = computed(() => user.value?.role === 'admin')
const isCreator = computed(() => {
  const uid = Number(user.value?.id ?? 0)
  const creator = Number((props.activity as any)?.creator_id ?? 0)
  return !!uid && creator === uid
})
const canManage = computed(() => isAdmin.value || isCreator.value)

const newOption = ref('')
const rootRef = ref<HTMLElement | null>(null)
// 内部可滚动容器引用：投票列表与评论列表
const voteListRef = ref<HTMLElement | null>(null)
const commentsWrapRef = ref<HTMLElement | null>(null)
// 删除模式已移除，改为每个选项独立删除按钮
const refreshingOptions = computed(() => options.value.length > 0 && optionsLoading.value)

// Map option_id -> votes for quick lookup in delete mode
const votesByOption = computed<Map<number, number>>(() => {
  const m = new Map<number, number>()
  for (const e of entries.value) {
    const id = (e as any).option_id
    if (typeof id === 'number') m.set(id, (e as any).votes || 0)
  }
  return m
})

function hasVotes(optionId: number): boolean {
  return (votesByOption.value.get(optionId) || 0) > 0
}

function ensureInit() {
  store.fetchRankingTop(props.activity.id).catch(() => { })
  store.fetchOptions(props.activity.id).catch(() => { })
  store.fetchMyVote(props.activity.id).catch(() => { })
}

onMounted(async () => {
  if (props.active) ensureInit()

  try { if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return } catch { }
  if (rootRef.value) {
    const rank = rootRef.value.querySelectorAll('.rank-item')
    if (rank?.length) gsap.from(rank, { opacity: 0, y: 8, duration: 0.4, ease: 'power2.out', stagger: 0.04 })
  }
  // 绑定内部滚动守卫
  attachScrollableGuards(voteListRef.value)
  attachScrollableGuards(commentsWrapRef.value)
})

watch(() => props.active, (v) => { if (v) ensureInit() })

onUnmounted(() => {
  // 卸载时移除事件并恢复全局滚轮
  detachScrollableGuards(voteListRef.value)
  detachScrollableGuards(commentsWrapRef.value)
  setWheelListenerDisabled?.(false)
})

// 百分比在图表构建中计算，此处函数已不再使用

function onVote(optionId: number) {
  if (!optionId) return
  store.submitVote(props.activity.id, optionId, store.anonymousPreference).catch(() => { })
}

function onRevoke() {
  store.revokeVote(props.activity.id).catch(() => { })
}

function onCreatePost(payload: { content: string; display_anonymous: boolean }) {
  store.createThreadPost(props.activity.id, payload)
}

async function addOption() {
  const label = newOption.value.trim()
  if (!label) return
  try {
    await store.createOption(props.activity.id, label)
    newOption.value = ''
  } catch (e: any) {
    // 后端会做权限判断：管理员或活动发起者
    const msg = e?.message || e?.detail || ''
    if (msg.includes('permissions') || msg.includes('403')) {
      alert('新增选项失败：需要管理员或活动发起者权限')
    } else {
      alert('新增选项失败：' + (msg || '未知错误'))
    }
  }
}

async function closeAct() {
  await store.closeActivity(props.activity.id)
}

// 删除操作统一在 ActivityCarousel 顶部进行

function confirmDelete(optionId: number) {
  if (voteOfMe.value === optionId) { alert('你已投该选项，不能删除该选项'); return }
  if (hasVotes(optionId)) { alert('该选项已有投票，无法删除'); return }
  if (!confirm('确定删除该选项吗？此操作不可恢复')) return
  store.deleteOption(props.activity.id, optionId).catch((e: any) => {
    const msg = e?.message || e?.detail || '删除失败'
    alert(msg)
  })
}

// 删除模式已移除

// -------- 合并选项与排行的数据视图 --------
const totalVotes = computed(() => entries.value.reduce((s, e) => s + (e.votes || 0), 0))

const merged = computed(() => {
  const list = (options.value || []).map(o => {
    const votes = votesByOption.value.get(o.id as number) || 0
    const ratio = totalVotes.value > 0 ? votes / totalVotes.value : 0
    const pct = Math.round(ratio * 100)
    return { id: o.id as number, label: o.label, votes, pct, ratio }
  })
  // 保持与排行一致的降序
  return list.sort((a, b) => b.votes - a.votes)
})

// 活动状态展示
const statusText = computed(() => {
  const s = (props.activity as any).status as string
  if (s === 'draft') return '未开始'
  if (s === 'closed') return '已结束'
  return '进行中'
})
const statusClass = computed(() => {
  const s = (props.activity as any).status as string
  return s === 'draft' ? 'chip-draft' : (s === 'closed' ? 'chip-closed' : 'chip-ongoing')
})

// 评论排序
const commentSort = ref<'latest' | 'hot'>('latest')

// 交互：单选 + 底部按钮
const selectedOptionId = ref<number | null>(null)
const radioName = `act-radio-${Math.random().toString(36).slice(2)}`
const canVote = computed(() => isAuthenticated.value && selectedOptionId.value !== null && selectedOptionId.value !== voteOfMe.value)

// ---- 分屏滚动干扰处理：在内部滚动区域禁用全局 wheel 监听 ----
const setWheelListenerDisabled = inject<((disabled: boolean) => void) | undefined>('setWheelListenerDisabled', undefined)

// 保留逻辑可用于后续精准判断滚动方向（当前不使用，避免误触发子屏幕）
// function canScrollInDirection(el: HTMLElement, deltaY: number): boolean {
//   const tolerance = 1
//   const scrollTop = el.scrollTop
//   const maxScrollTop = el.scrollHeight - el.clientHeight
//   if (el.scrollHeight <= el.clientHeight + tolerance) return false
//   if (deltaY > 0) {
//     // 向下滚动
//     return scrollTop < maxScrollTop - tolerance
//   } else if (deltaY < 0) {
//     // 向上滚动
//     return scrollTop > tolerance
//   }
//   return false
// }

function onScrollableWheel(e: WheelEvent) {
  const el = e.currentTarget as HTMLElement | null
  if (!el) return
  // 始终在进入滚动容器后禁用全局分屏滚动
  setWheelListenerDisabled?.(true)
  // 当容器无法继续滚动时，保持禁用以允许继续点击/交互，例如“加载更多”按钮
  // 仅阻止冒泡，避免触发父级 snap 的 wheel 监听
  e.stopPropagation()
}

function onScrollableEnter() { setWheelListenerDisabled?.(true) }
function onScrollableLeave() { setWheelListenerDisabled?.(false) }

function attachScrollableGuards(el: HTMLElement | null) {
  if (!el) return
  el.addEventListener('mouseenter', onScrollableEnter)
  el.addEventListener('mouseleave', onScrollableLeave)
  el.addEventListener('wheel', onScrollableWheel, { passive: true })
}

function detachScrollableGuards(el: HTMLElement | null) {
  if (!el) return
  el.removeEventListener('mouseenter', onScrollableEnter)
  el.removeEventListener('mouseleave', onScrollableLeave)
  el.removeEventListener('wheel', onScrollableWheel as EventListener)
}

// 监听 ref 变化（例如数据加载后渲染出的列表），动态绑定/解绑
watch(voteListRef, (el, prev) => { if (prev) detachScrollableGuards(prev); attachScrollableGuards(el) })
watch(commentsWrapRef, (el, prev) => { if (prev) detachScrollableGuards(prev); attachScrollableGuards(el) })
</script>

<style scoped lang="scss">
.act-vote {
  display: grid;
  gap: 16px;
  padding: 14px 18px 22px;
  color: var(--text-primary);
  /* 让面板根据内容自适应高度，避免被父级强行拉伸 */
  min-height: 0;
  max-width: 100vw;
  grid-template-rows: auto auto;
  /* 子屏高度与左右列表占比可调整 */
  --vote-panel-max-h: clamp(460px, 68vh, 760px);
  /* 移动端：投票列表按视口高度自适应上限，避免过长 */
  --vote-list-max-pct: clamp(220px, 52vh, 560px);
  --comment-list-max-pct: 100%;
  overflow-x: hidden;
}

.head {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.titles {
  display: grid;
  gap: 4px;
}

.title {
  font-size: 18px;
  font-weight: 700;
}

.desc {
  color: var(--text-secondary);
  font-size: 12px;
}

.spacer {
  flex: 1;
}

.admin {
  display: flex;
  align-items: center;
  gap: 6px;
}

.input.small {
  padding: 6px 8px;
  width: 160px;
  background: transparent;
  color: var(--text-primary);
  border: 1px solid var(--divider-color, #444);
  border-radius: 8px;
}

/* 移动端：登录后管理控件换行，避免撑破宽度 */
@media (max-width: 959px) {
  .head .admin {
    width: 100%;
    justify-content: flex-start;
    flex-wrap: wrap;
    row-gap: 6px;
  }

  .head .titles {
    min-width: 0;
  }

  .head .spacer {
    display: none;
  }

  .head .admin .input.small {
    width: auto;
    flex: 1 1 180px;
    min-width: 0;
    max-width: 100%;
  }
}

.btn.small {
  padding: 6px 8px;
  border: 1px solid var(--primary-6, var(--primary));
  color: var(--primary-6, var(--primary));
  background: color-mix(in srgb, var(--primary) 6%, transparent);
  border-radius: 8px;
}

.btn.small.warn {
  border-color: var(--accent-red, #f7768e);
  color: var(--accent-red, #f7768e);
}

.btn.small.warn.outline {
  background: transparent;
}

.btn.small.warn.outline[aria-pressed="true"] {
  background: color-mix(in srgb, var(--accent-red, #f7768e) 22%, transparent);
  color: #fff;
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--accent-red, #f7768e) 35%, transparent) inset;
}

.grid {
  display: grid;
  gap: 12px;
  grid-template-columns: 1fr;
  /* 让子卡片根据内容自高，不再强制拉满 */
  align-items: start;
  min-height: 0;
}

@media (min-width: 960px) {
  .grid {
    grid-template-columns: 1.4fr 1fr;
    align-items: stretch;
  }
}

@media (min-width: 960px) {
  .act-vote {
    /* 桌面端：列表占满面板可用空间 */
    --vote-list-max-pct: 100%;
  }
}

.panel {
  background: color-mix(in srgb, var(--base-dark) 85%, rgba(0, 0, 0, 0.2));
  /* 移除外部大边框，保持卡片化阴影 */
  border: none;
  border-radius: 14px;
  padding: 12px;
  /* 收紧并分层阴影，避免大片弥漫 */
  box-shadow:
    0 1px 2px rgba(0,0,0,.28),
    0 6px 14px rgba(0,0,0,.20),
    inset 0 0 0 1px rgba(255,255,255,.04);
  /* 让容器高度自适应，同时限定最大高度 */
  max-height: var(--vote-panel-max-h);
  overflow: hidden;
}

@media (max-width: 959px) {
  .panel {
    padding-left: 10px;
    padding-right: 10px;
  }
}

.panel.options.managing {
  border-color: var(--error-alert, #f7768e);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--error-alert, #f7768e) 30%, transparent) inset, 0 6px 24px rgba(0, 0, 0, .35);
}

.panel-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: var(--text-secondary);
  font-size: 12px;
  margin-bottom: 8px;
}

.anon {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.hint {
  color: var(--text-secondary);
  font-size: 12px;
  margin-left: 8px;
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 2px 8px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--primary) 10%, transparent);
  color: var(--text-secondary);
  margin-right: 8px;
}

.chip.danger {
  background: color-mix(in srgb, var(--error-alert, #f7768e) 25%, transparent);
  color: #fff;
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--error-alert, #f7768e) 50%, transparent) inset;
}

.buttons-gap {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

/* 左侧合并面板 */
.vote-combined {
  display: grid;
  grid-template-rows: auto 1fr auto;
  min-height: 0;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
  color: var(--text-secondary);
  font-size: 12px;
}

@media (max-width: 959px) {
  .panel-header {
    flex-wrap: wrap;
    gap: 8px;
  }
}

.chips {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.switch {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.switch input {
  width: 0;
  height: 0;
  opacity: 0;
  position: absolute;
}

.switch .slider {
  width: 34px;
  height: 18px;
  background: color-mix(in srgb, var(--base-dark) 70%, rgba(0, 0, 0, 0.2));
  border-radius: 999px;
  border: 1px solid var(--divider-color, #444);
  position: relative;
  transition: background .2s ease, border-color .2s ease;
}

.switch .slider::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 2px;
  transform: translateY(-50%);
  width: 14px;
  height: 14px;
  background: #fff;
  border-radius: 50%;
  transition: left .2s ease;
}

.switch input:checked+.slider {
  background: var(--primary);
  border-color: var(--primary);
}

.switch input:checked+.slider::after {
  left: 18px;
}

.switch .label {
  white-space: nowrap;
}

.vote-list {
  list-style: none;
  padding: 6px 0 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
  overflow: auto;
  min-height: 0;
  align-content: flex-start;
  max-height: var(--vote-list-max-pct);
}

.vote-row {
  position: relative;
  /* 缩窄整体视觉宽度并居中 */
  width: min(98%, 1120px);
  max-width: 100%;
  margin-inline: auto;
}

.row-main {
  width: 100%;
  text-align: left;
  background: color-mix(in srgb, var(--base-dark) 82%, rgba(0, 0, 0, 0.15));
  /* 去掉描边，使用卡片阴影提升层次 */
  border: none;
  border-radius: 12px;
  padding: 10px 48px 10px 10px;
  color: var(--text-primary);
  /* 更聚焦的多层阴影，减小模糊半径，避免“弥漫感” */
  box-shadow:
    0 1px 2px rgba(0,0,0,.28),
    0 4px 8px rgba(0,0,0,.18),
    inset 0 0 0 1px rgba(255,255,255,.04);
  transition: transform .15s ease, background .2s ease, box-shadow .2s ease;
  display: grid;
  grid-template-columns: auto 1fr;
  column-gap: 8px;
  position: relative;
}

.row-main:hover {
  transform: translateY(-1px);
  background: color-mix(in srgb, var(--primary) 8%, transparent);
  box-shadow:
    0 2px 6px rgba(0,0,0,.32),
    0 8px 20px rgba(0,0,0,.22),
    inset 0 0 0 1px color-mix(in srgb, var(--primary) 28%, transparent);
}

.row-main:disabled {
  opacity: .55;
  cursor: not-allowed;
}

.row-top {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 8px;
}

.radio {
  display: inline-grid;
  width: 18px;
  height: 18px;
  place-items: center;
}

.radio input {
  appearance: none;
  width: 0;
  height: 0;
  opacity: 0;
  position: absolute;
}

.radio .dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid var(--divider-color, #555);
  background: transparent;
  transition: all .2s ease;
}

.vote-row.selected .radio .dot,
.radio input:checked+.dot {
  border-color: var(--primary);
  background: var(--primary);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--primary) 20%, transparent) inset;
}

.vote-row.selected .row-main {
  background: color-mix(in srgb, var(--primary) 22%, transparent);
  box-shadow:
    0 2px 8px rgba(0,0,0,.28),
    0 10px 22px rgba(0,0,0,.24),
    0 0 0 2px color-mix(in srgb, var(--primary) 30%, transparent) inset;
}

.actions-bottom {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  padding-top: 8px;
}

.btn.primary {
  border-color: var(--primary);
  background: var(--primary);
  color: #fff;
}

.row-top .name {
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.row-top .counts {
  color: var(--text-secondary);
}

.row-top .pct {
  margin-left: 2px;
  font-size: 12px;
}

.bar {
  position: relative;
  margin-top: 6px;
  height: 12px;
  background: color-mix(in srgb, var(--secondary-light) 55%, rgba(0, 0, 0, 0.25));
  /* 去掉描边，靠背景与圆角区分层次 */
  border: none;
  border-radius: 999px;
  overflow: hidden;
  grid-column: 1 / -1;
}

.bar-fill {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 0%;
  background: linear-gradient(90deg, var(--secondary) 0%, var(--primary) 100%);
  box-shadow: 0 0 8px color-mix(in srgb, var(--primary) 45%, transparent);
  transition: width .35s var(--ease-hover);
}

.vote-row .badge {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 2px 6px;
  font-size: 12px;
  border-radius: 999px;
  background: var(--primary);
  color: #fff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, .3);
}

.vote-row .delete-right {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 22px;
  height: 22px;
  display: grid;
  place-items: center;
  border-radius: 6px;
  background: color-mix(in srgb, var(--error-alert, #f7768e) 30%, transparent);
  color: #fff;
  font-weight: 700;
  cursor: pointer;
  opacity: .9;
  transition: background .2s ease;
}

.vote-row .delete-right:hover {
  background: var(--error-alert, #f7768e);
}

.vote-row .delete-right.disabled {
  opacity: .45;
  cursor: not-allowed;
  filter: grayscale(0.35);
}

.vote-row.locked .row-main {
  background: color-mix(in srgb, #444 12%, transparent);
}

.empty {
  color: var(--text-secondary);
  padding: 6px 0;
}

/* 状态 Chip */
.chip-ongoing {
  background: color-mix(in srgb, var(--primary) 18%, transparent);
  color: var(--text-secondary);
}

.chip-draft {
  background: color-mix(in srgb, #ffd166 30%, transparent);
  color: #111;
}

.chip-closed {
  background: color-mix(in srgb, var(--error-alert, #f7768e) 25%, transparent);
  color: #fff;
}

/* 评论区布局：占满剩余高度并内部滚动 */
.panel.comments {
  display: grid;
  grid-template-rows: auto 1fr;
  min-height: 0;
}

.panel.comments .panel-title {
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.comments-body {
  display: grid;
  gap: 8px;
  grid-template-rows: auto 1fr;
  min-height: 0;
}

.list-wrap {
  overflow: auto;
  min-height: 0;
  max-height: var(--comment-list-max-pct);
}

.seg {
  display: inline-flex;
  background: color-mix(in srgb, var(--base-dark) 82%, rgba(0, 0, 0, 0.15));
  border: 1px solid var(--divider-color, #3a3a3a);
  border-radius: 8px;
  overflow: hidden;
}

.seg-btn {
  padding: 4px 10px;
  font-size: 12px;
  color: var(--text-secondary);
  background: transparent;
  border: none;
  cursor: pointer;
  transition: background .2s ease, color .2s ease;
}

.seg-btn:hover {
  background: color-mix(in srgb, var(--primary) 12%, transparent);
  color: var(--text-primary);
}

.seg-btn.active {
  color: #fff;
  background: var(--primary);
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--primary) 35%, transparent) inset;
}

/* 独立加载样式，避免文字跟着旋转 */
.loading-wrap {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, .25);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 选项面板无感刷新：右上角小圆圈，不遮挡内容 */
.vote-combined {
  position: relative;
}

.vote-combined[data-refreshing="true"]::before {
  content: '';
  position: absolute;
  top: 10px;
  right: 10px;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, .25);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* 评论区布局微调 */
.panel.comments {
  padding-top: 10px;
}

.panel.comments .panel-title {
  margin-bottom: 8px;
}
</style>
