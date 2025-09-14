<template>
  <div class="activity-carousel" ref="rootRef">
    <div class="header">
      <div class="title-wrap">
        <h2 class="title title-accent">活动</h2>
        <span v-if="activeActivity" class="badge">{{ (activeActivity as any).type === 'vote' ? '投票' : '讨论' }}</span>
        <span v-if="activities.length" class="count">{{ activeIndex + 1 }}/{{ totalPages }}</span>
      </div>
      <div class="spacer" />
      <div class="actions">
        <template v-if="isAuthenticated">
          <button class="btn" @click="openCreate('vote')">新建投票</button>
          <button class="btn" @click="openCreate('thread')">新建讨论</button>
          <button
            v-if="activeActivity && canManageActive"
            class="btn warn outline"
            @click="deleteActive"
            title="删除当前活动（不可恢复）"
          >删除活动</button>
        </template>
        <template v-else>
          <button class="btn ghost" @click="openLogin">登录后发起或投票</button>
        </template>
      </div>
    </div>

    <div class="carousel">
      <swiper
        :modules="[Navigation]"
        :slides-per-view="1"
        :space-between="0"
        :keyboard="{ enabled: true }"
        :speed="700"
        :allow-touch-move="true"
        @slide-change="onSlideChange"
        @swiper="onSwiperInit"
        class="activity-swiper"
      >
        <swiper-slide v-for="act in activities" :key="act.id" class="activity-slide">
          <div class="slide-inner">
            <component
              :is="act.type === 'thread' ? ActivityPanelThread : ActivityPanelVote"
              :activity="act"
              :active="activeActivity && (act.id === (activeActivity as any).id)"
            />
          </div>
        </swiper-slide>
      </swiper>
      <div v-if="!loading && activities.length === 0" class="empty">暂无活动</div>
    </div>

    <PaginationArrows
      v-if="activities.length > 0"
      :current-page="activeIndex + 1"
      :total-pages="totalPages"
      @prev-page="goToPrevPage"
      @next-page="goToNextPage"
    />

    <!-- 创建活动 Modal -->
    <div v-if="showCreate" class="modal" ref="backdropRef" @click.self="closeWithAnim">
      <div class="modal-body" ref="modalRef" role="dialog" aria-modal="true" :aria-label="createType === 'vote' ? '创建投票' : '创建讨论'">
        <h3 class="modal-title">创建{{ createType === 'vote' ? '投票' : '讨论' }}</h3>

        <div class="form-grid">
          <label class="field">
            <span class="label">标题</span>
            <input v-model="form.title" ref="titleInputRef" class="input" :placeholder="`给你的${createType === 'vote' ? '投票' : '讨论'}起个标题`" />
          </label>

          <label class="field">
            <span class="label">描述</span>
            <textarea v-model="form.description" class="textarea" rows="3" placeholder="可选：补充背景、规则等"></textarea>
          </label>

          <div class="field" v-if="createType === 'vote'">
            <span class="label">选项</span>
            <div class="hints">创建后可在面板中继续添加投票选项</div>
          </div>

          <div class="field two-col" v-if="createType === 'vote'">
            <label class="checkbox"><input type="checkbox" v-model="form.allow_change" /><span>允许改票/撤销</span></label>
            <label class="checkbox"><input type="checkbox" v-model="form.anonymous_allowed" /><span>允许匿名展示</span></label>
          </div>
        </div>

        <div class="modal-actions">
          <button class="btn primary" @click="submitCreate">创建</button>
          <button class="btn ghost" @click="closeWithAnim">取消</button>
        </div>
      </div>
    </div>

    <!-- 统一认证弹窗组件 -->
    <AuthDialog v-model="showLogin" :initial-tab="'login'" @success="onAuthSuccess" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, computed, nextTick, watch } from 'vue'
import { useActivitiesStore } from '@/stores/activities'
import { useAuthStore } from '@/stores/auth'
import ActivityPanelVote from './ActivityPanelVote.vue'
import ActivityPanelThread from './ActivityPanelThread.vue'
// import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { gsap } from 'gsap'
import { Swiper, SwiperSlide } from 'swiper/vue'
import { Navigation } from 'swiper/modules'
import PaginationArrows from '@/components/PaginationArrows.vue'
import AuthDialog from '@/components/auth/AuthDialog.vue'

const store = useActivitiesStore()
const auth = useAuthStore()
// const router = useRouter()

const activities = computed(() => store.activities)
const loading = computed(() => store.loading.activities)
// 通过 storeToRefs 获取 Ref，确保响应式正确
const { user, isAuthenticated } = storeToRefs(auth)
const rootRef = ref<HTMLDivElement | null>(null)
const activeIndex = computed(() => store.currentIndex)
const totalPages = computed(() => activities.value.length)
const swiperRef = ref<any>(null)
const activeActivity = computed(() => activities.value[activeIndex.value] || null)
const isAdmin = computed(() => user.value?.role === 'admin')
const canManageActive = computed(() => {
  const uid = Number(user.value?.id ?? 0)
  const creator = Number((activeActivity.value as any)?.creator_id ?? 0)
  return !!uid && (isAdmin.value || creator === uid)
})

const showCreate = ref(false)
const createType = ref<'vote' | 'thread'>('vote')
const form = ref<{ title: string; description?: string; allow_change?: boolean; anonymous_allowed?: boolean }>({ title: '', description: '', allow_change: true, anonymous_allowed: true })

const backdropRef = ref<HTMLElement | null>(null)
const modalRef = ref<HTMLElement | null>(null)
const titleInputRef = ref<HTMLInputElement | null>(null)
let escHandler: ((e: KeyboardEvent) => void) | null = null

// Login modal state (unified)
const showLogin = ref(false)

function openCreate(type: 'vote' | 'thread') {
  createType.value = type
  showCreate.value = true
  nextTick(() => {
    animateOpen(backdropRef.value, modalRef.value)
    titleInputRef.value?.focus()
    escHandler = (e: KeyboardEvent) => { if (e.key === 'Escape') closeWithAnim() }
    window.addEventListener('keydown', escHandler)
  })
}

function animateOpen(backdropEl?: HTMLElement | null, modalEl?: HTMLElement | null) {
  try { if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return } catch {}
  if (backdropEl && modalEl) {
    gsap.fromTo(backdropEl, { opacity: 0 }, { opacity: 1, duration: 0.18, ease: 'power1.out' })
    gsap.fromTo(modalEl, { opacity: 0, y: 14, scale: 0.96 }, { opacity: 1, y: 0, scale: 1, duration: 0.28, ease: 'power3.out' })
  }
}

function animateClose(backdropEl: HTMLElement | null | undefined, modalEl: HTMLElement | null | undefined, onDone: () => void) {
  try { if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) { onDone(); return } } catch {}
  if (backdropEl && modalEl) {
    gsap.to(modalEl, { opacity: 0, y: 10, scale: 0.97, duration: 0.2, ease: 'power2.in' })
    gsap.to(backdropEl, { opacity: 0, duration: 0.18, ease: 'power1.in', onComplete: onDone })
  } else {
    onDone()
  }
}

function closeWithAnim() {
  const finish = () => { showCreate.value = false; window.removeEventListener('keydown', escHandler as any); }
  animateClose(backdropRef.value, modalRef.value, finish)
}

async function submitCreate() {
  if (!form.value.title.trim()) return
  await store.createActivity({
    type: createType.value,
    title: form.value.title.trim(),
    description: form.value.description?.trim() || undefined,
    allow_change: form.value.allow_change,
    anonymous_allowed: form.value.anonymous_allowed,
  })
  form.value.title = ''
  form.value.description = ''
  closeWithAnim()
}

function openLogin() { showLogin.value = true }
function onAuthSuccess() { /* stay on current page */ }

function reduced() {
  try { return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches } catch { return false }
}

function clamp(n: number, min: number, max: number) {
  return Math.max(min, Math.min(max, n))
}

function onSwiperInit(swiper: any) { swiperRef.value = swiper }
function onSlideChange(swiper: any) {
  const previous = store.currentIndex
  store.setCurrentIndex(swiper.activeIndex)
  animateSlideTransition(previous, swiper.activeIndex)
}

function goTo(index: number) {
  const target = clamp(index, 0, Math.max(0, activities.value.length - 1))
  if (swiperRef.value) swiperRef.value.slideTo(target)
}

function goToPrevPage() { if (swiperRef.value) swiperRef.value.slidePrev() }
function goToNextPage() { if (swiperRef.value) swiperRef.value.slideNext() }

async function deleteActive() {
  if (!activeActivity.value) return
  if (!confirm('确定删除该活动吗？此操作会移除相关数据且不可恢复。')) return
  await store.deleteActivity(activeActivity.value.id)
}

// 根据反馈：移除滚轮/触摸/键盘切换，仅保留箭头按钮触发

onMounted(() => {
  // 初始化加载活动列表
  store.fetchActivities().catch(() => {/* 静默失败，UI优雅降级 */})

  if (reduced()) return
  // Header & slides entrance
  if (rootRef.value) {
    const header = rootRef.value.querySelector('.header')
    if (header) gsap.from(header, { y: -12, opacity: 0, duration: 0.6, ease: 'power2.out' })
    const slides = rootRef.value.querySelectorAll('.slide')
    if (slides?.length) gsap.from(slides, { opacity: 0, y: 12, duration: 0.5, ease: 'power2.out', stagger: 0.06 })
  }
  // 供帖子编辑器触发登录弹窗
  window.addEventListener('open-login-modal', openLogin as any)
})

onUnmounted(() => {
  if (escHandler) window.removeEventListener('keydown', escHandler)
  window.removeEventListener('open-login-modal', openLogin as any)
})

watch(() => activities.value.length, (len) => {
  if (len === 0) { store.setCurrentIndex(0); return }
  const idx = clamp(store.currentIndex, 0, Math.max(0, len - 1))
  if (idx !== store.currentIndex) store.setCurrentIndex(idx)
  nextTick(() => goTo(idx))
})

watch(() => store.currentIndex, (idx) => {
  nextTick(() => goTo(idx))
})

// Slide transition animation with GSAP (simplified, mirrors MembersCircle style)
function animateSlideTransition(fromIndex: number, toIndex: number) {
  if (fromIndex === toIndex) return
  const slides = document.querySelectorAll('.activity-slide .slide-inner') as NodeListOf<HTMLElement>
  const current = slides[toIndex]
  const previous = slides[fromIndex]

  const tl = gsap.timeline({ defaults: { ease: 'power2.out' } })
  if (previous) {
    tl.to(previous, { opacity: 0, scale: 0.98, duration: 0.2 }, 0)
  }
  if (current) {
    gsap.set(current, { opacity: 0, y: 16, scale: 0.98 })
    tl.to(current, { opacity: 1, y: 0, scale: 1, duration: 0.35 }, 0.05)
  }
}

// -------- 仅对当前可见面板进行轮询刷新（投票/讨论） --------
const activePollingHandle = ref<number | null>(null)

function stopActivePolling() {
  if (activePollingHandle.value) {
    clearInterval(activePollingHandle.value)
    activePollingHandle.value = null
  }
}

function tickActive() {
  const act = activeActivity.value as any
  if (!act) return
  if (document.visibilityState === 'hidden') return
  if (act.type === 'vote') {
    store.fetchRankingTop(act.id).catch(() => {})
    // 选项变化频率较低，仍按无感刷新，避免首次后出现加载条
    store.fetchOptions(act.id).catch(() => {})
  } else if (act.type === 'thread') {
    // 静默刷新：不触发骨架屏
    store.fetchThreadPosts(act.id, null, 20, { silent: true }).catch(() => {})
  }
}

function startActivePolling() {
  stopActivePolling()
  tickActive()
  activePollingHandle.value = window.setInterval(() => {
    tickActive()
  }, store.pollingIntervalMs)
}

watch(activeActivity, (val) => { if (val) startActivePolling(); else stopActivePolling() }, { immediate: true })
document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible') tickActive() })

onUnmounted(() => { stopActivePolling() })
</script>

<style scoped lang="scss">
.activity-carousel {
  /* 参考 DailyWall：为顶部标题/导航留出安全距离 */
  padding-top: calc(24px + var(--top-safe-offset, 56px));
  padding-bottom: 24px;
  color: var(--text-primary);
}
.header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 24px 12px;
}
.title { font-size: 20px; font-weight: 700; letter-spacing: .2px; }
.title-accent { background: var(--mixed-gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; text-shadow: var(--shadow-glow); }
.title-wrap { display: inline-flex; align-items: baseline; gap: 8px; }
.badge { padding: 2px 8px; font-size: 12px; border-radius: 999px; background: color-mix(in srgb, var(--primary) 12%, transparent); color: var(--text-secondary); }
.count { color: var(--text-secondary); font-size: 12px; }
.spacer { flex: 1; }
.actions { display: flex; gap: 8px; }
.btn { padding: 6px 10px; border: 1px solid var(--primary-6, var(--primary)); color: var(--primary-6, var(--primary)); background: color-mix(in srgb, var(--primary) 6%, transparent); border-radius: 8px; }
.btn:hover { background: color-mix(in srgb, var(--primary) 12%, transparent); }
.btn.ghost { border-color: var(--divider-color, #444); color: var(--text-secondary); background: transparent; }
.btn.primary { border-color: var(--primary); color: white; background: var(--primary); }
.btn.warn { border-color: var(--accent-red, #f7768e); color: var(--accent-red, #f7768e); }
.btn.warn.outline { background: transparent; }

.activity-swiper { width: 100%; }
.activity-slide { width: 100%; }
.slide-inner { padding: 0 8px; }
@media (min-width: 1024px) {
  /* 中文注释：仅为左右分页箭头预留安全边距（按钮60px+少量间距），避免覆盖主内容 */
  .slide-inner { padding-left: clamp(60px, 4vw, 84px); padding-right: clamp(60px, 4vw, 84px); }
}
.empty {
  width: 100%;
  height: 50vh;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
}

.modal { position: fixed; inset: 0; background: color-mix(in srgb, var(--base-dark) 60%, rgba(0,0,0,0.5)); backdrop-filter: blur(4px); display: grid; place-items: center; z-index: 1000; }
.modal-body { background: var(--panel-bg, var(--base-dark)); border: 1px solid var(--divider-color, #444); border-radius: 14px; padding: 16px; width: min(520px, 92vw); box-shadow: 0 10px 35px rgba(0,0,0,.45); z-index: 1001; }
.modal-title { font-size: 16px; font-weight: 700; margin-bottom: 12px; }

.form-grid { display: grid; gap: 10px; }
.field { display: grid; gap: 6px; }
.field.two-col { grid-template-columns: 1fr 1fr; align-items: center; gap: 10px; }
.label { color: var(--text-secondary); font-size: 12px; }
.hints { color: var(--text-secondary); font-size: 12px; }
.input, .textarea { width: 100%; padding: 10px 12px; background: transparent; color: var(--text-primary); border: 1px solid var(--divider-color, #444); border-radius: 10px; }
.checkbox { display: flex; align-items: center; gap: 6px; }

.modal-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 10px; }
.error { color: #ff6b6b; font-size: 12px; }

.nav { position: relative; display: flex; justify-content: center; align-items: center; gap: 8px; padding: 8px 0 0; }
.arrow { width: 32px; height: 32px; display: grid; place-items: center; border-radius: 999px; border: 1px solid var(--divider-color, #444); background: color-mix(in srgb, var(--base-dark) 75%, rgba(0,0,0,0.2)); color: var(--text-primary); box-shadow: 0 4px 14px rgba(0,0,0,.25); }
.arrow:hover { background: color-mix(in srgb, var(--primary) 14%, transparent); border-color: var(--primary); }
.arrow:disabled { opacity: .5; cursor: not-allowed; }
</style>

