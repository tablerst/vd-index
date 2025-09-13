<template>
  <div class="activity-carousel" ref="rootRef">
    <div class="header">
      <h2 class="title title-accent">活动</h2>
      <span class="subtitle">左右滑动浏览不同活动</span>
      <div class="spacer" />
      <div class="actions">
        <template v-if="isAuthenticated">
          <button class="btn" @click="openCreate('vote')">新建投票</button>
          <button class="btn" @click="openCreate('thread')">新建讨论</button>
        </template>
        <template v-else>
          <button class="btn ghost" @click="openLogin">登录后发起或投票</button>
        </template>
      </div>
    </div>

    <div class="carousel" ref="scrollRef">
      <div v-for="act in activities" :key="act.id" class="slide">
        <component :is="act.type === 'thread' ? ActivityPanelThread : ActivityPanelVote" :activity="act" />
      </div>
      <div v-if="!loading && activities.length === 0" class="empty">
        暂无活动
      </div>
    </div>

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

    <!-- 登录 Modal（非管理员场景使用） -->
    <div v-if="showLogin" class="modal" ref="loginBackdropRef" @click.self="closeLoginWithAnim">
      <div class="modal-body" ref="loginModalRef" role="dialog" aria-modal="true" aria-label="登录">
        <h3 class="modal-title">登录</h3>
        <div class="form-grid">
          <label class="field">
            <span class="label">用户名</span>
            <input v-model="loginForm.username" class="input" placeholder="请输入用户名" autocomplete="username" />
          </label>
          <label class="field">
            <span class="label">密码</span>
            <input v-model="loginForm.password" class="input" placeholder="请输入密码" type="password" autocomplete="current-password" />
          </label>
          <div v-if="loginError" class="error">{{ loginError }}</div>
        </div>
        <div class="modal-actions">
          <button class="btn primary" :disabled="loginLoading" @click="handleLogin">{{ loginLoading ? '登录中…' : '登录' }}</button>
          <button class="btn ghost" :disabled="loginLoading" @click="closeLoginWithAnim">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, computed, nextTick } from 'vue'
import { useActivitiesStore } from '@/stores/activities'
import { useAuthStore } from '@/stores/auth'
import ActivityPanelVote from './ActivityPanelVote_back.vue'
import ActivityPanelThread from './ActivityPanelThread.vue'
import { useRouter } from 'vue-router'
import { gsap } from 'gsap'

const store = useActivitiesStore()
const auth = useAuthStore()
const router = useRouter()

const activities = computed(() => store.activities)
const loading = computed(() => store.loading.activities)
const isAuthenticated = computed(() => auth.isAuthenticated)
const scrollRef = ref<HTMLDivElement | null>(null)
const rootRef = ref<HTMLDivElement | null>(null)

const showCreate = ref(false)
const createType = ref<'vote' | 'thread'>('vote')
const form = ref<{ title: string; description?: string; allow_change?: boolean; anonymous_allowed?: boolean }>({ title: '', description: '', allow_change: true, anonymous_allowed: true })

const backdropRef = ref<HTMLElement | null>(null)
const modalRef = ref<HTMLElement | null>(null)
const titleInputRef = ref<HTMLInputElement | null>(null)
let escHandler: ((e: KeyboardEvent) => void) | null = null

// Login modal state
const showLogin = ref(false)
const loginBackdropRef = ref<HTMLElement | null>(null)
const loginModalRef = ref<HTMLElement | null>(null)
const loginForm = ref({ username: '', password: '' })
const loginLoading = ref(false)
const loginError = ref('')
let escLoginHandler: ((e: KeyboardEvent) => void) | null = null

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

function openLogin() {
  showLogin.value = true
  nextTick(() => {
    animateOpen(loginBackdropRef.value, loginModalRef.value)
    escLoginHandler = (e: KeyboardEvent) => { if (e.key === 'Escape') closeLoginWithAnim() }
    window.addEventListener('keydown', escLoginHandler)
  })
}

function closeLoginWithAnim() {
  const finish = () => { showLogin.value = false; window.removeEventListener('keydown', escLoginHandler as any); }
  animateClose(loginBackdropRef.value, loginModalRef.value, finish)
}

async function handleLogin() {
  if (!loginForm.value.username || !loginForm.value.password) { loginError.value = '请输入用户名和密码'; return }
  loginLoading.value = true
  loginError.value = ''
  try {
    // 设置 redirect 到当前页面，避免登录后跳到 /settings
    const current = router.currentRoute.value.fullPath || '/'
    if (router.currentRoute.value.query.redirect !== current) {
      await router.replace({ path: router.currentRoute.value.path, query: { ...router.currentRoute.value.query, redirect: current } })
    }
    const ok = await auth.login({ username: loginForm.value.username, password: loginForm.value.password })
    if (ok) {
      closeLoginWithAnim()
    } else {
      loginError.value = '登录失败，请检查用户名与密码'
    }
  } catch (e: any) {
    loginError.value = e?.message || '登录失败'
  } finally {
    loginLoading.value = false
  }
}

function reduced() {
  try { return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches } catch { return false }
}

onMounted(() => {
  // 初始化加载活动列表
  store.fetchActivities().catch(() => {/* 静默失败，UI优雅降级 */})
  store.startRankingPolling()

  if (reduced()) return
  // Header & slides entrance
  if (rootRef.value) {
    const header = rootRef.value.querySelector('.header')
    if (header) gsap.from(header, { y: -12, opacity: 0, duration: 0.6, ease: 'power2.out' })
    const slides = rootRef.value.querySelectorAll('.slide')
    if (slides?.length) gsap.from(slides, { opacity: 0, y: 12, duration: 0.5, ease: 'power2.out', stagger: 0.06 })
  }
})

onUnmounted(() => {
  store.stopRankingPolling()
  if (escHandler) window.removeEventListener('keydown', escHandler)
  if (escLoginHandler) window.removeEventListener('keydown', escLoginHandler)
})
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
.subtitle { color: var(--text-secondary); font-size: 12px; }
.spacer { flex: 1; }
.actions { display: flex; gap: 8px; }
.btn { padding: 6px 10px; border: 1px solid var(--primary-6, var(--primary)); color: var(--primary-6, var(--primary)); background: color-mix(in srgb, var(--primary) 6%, transparent); border-radius: 8px; }
.btn:hover { background: color-mix(in srgb, var(--primary) 12%, transparent); }
.btn.ghost { border-color: var(--divider-color, #444); color: var(--text-secondary); background: transparent; }
.btn.primary { border-color: var(--primary); color: white; background: var(--primary); }

.carousel {
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: 100%;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
}
.slide {
  scroll-snap-align: start;
  padding: 0 8px;
}
.empty {
  width: 100%;
  height: 50vh;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
}

.modal { position: fixed; inset: 0; background: color-mix(in srgb, var(--base-dark) 60%, rgba(0,0,0,0.5)); backdrop-filter: blur(4px); display: grid; place-items: center; }
.modal-body { background: var(--panel-bg, var(--base-dark)); border: 1px solid var(--divider-color, #444); border-radius: 14px; padding: 16px; width: min(520px, 92vw); box-shadow: 0 10px 35px rgba(0,0,0,.45); }
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
</style>

