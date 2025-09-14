<template>
  <div class="daily-page">
    <!-- 1) 标题栏 -->
    <header class="header-bar">
      <div class="left-area">
        <n-button class="icon-circle-btn back-btn" circle type="primary" size="small" @click="goHome" title="返回"
          aria-label="返回">
          <ArrowLeft :size="18" />
        </n-button>
        <h2 class="title">群员日常</h2>
      </div>
      <div class="user-area">
        <!-- 已登录：头像+下拉 -->
        <n-dropdown v-if="isAuthenticated" trigger="click" :options="userMenuOptions" @select="handleUserMenu">
          <n-avatar round :size="avatarSize" :src="userAvatar" :fallback-src="fallbackAvatar" />
        </n-dropdown>
        <!-- 未登录：圆形灰底头像占位，点击打开登录模态 -->
        <n-avatar v-else round :size="avatarSize" class="user-avatar avatar-placeholder"
          :style="{ background: 'var(--glass-bg-strong, rgba(255,255,255,0.12))', color: 'var(--text-primary, #111)', fontSize: '12px', fontWeight: '600' }"
          title="未登录，点击登录" @click="() => { showAuth = true; authTab = 'login'; forceBindStepOnOpen = false }">未登录</n-avatar>
      </div>
    </header>

    <!-- 2) 筛选栏 -->
    <div class="filter-bar">
      <n-space :wrap="true" size="small">
        <!-- 作者筛选 -->
        <n-select class="filter-item" clearable filterable placeholder="按作者筛选" v-model:value="authorUserId"
          :options="authorOptions" :render-label="renderAuthorLabel" />
        <!-- 标签筛选（单选，对齐后端API） -->
        <n-select class="filter-item" clearable filterable placeholder="按标签筛选" v-model:value="tag"
          :options="tagOptions" />
        <!-- 日期范围筛选（前端过滤 created_at） -->
        <n-date-picker class="filter-item date-picker" v-model:value="dateRange" type="daterange" :bordered="false"
          clearable :shortcuts="dateShortcuts" :is-date-disabled="disableFutureDate" :actions="['confirm']"
          format="yyyy/MM/dd" placeholder="选择日期范围" />
      </n-space>
    </div>

    <!-- 3) 正文内容区域（可滚动，保持瀑布流） -->
    <main class="content-area">
      <n-spin :show="loading" size="large" class="masonry-spin">
        <template #description>正在加载</template>
        <div class="masonry" ref="masonryRef">
          <DailyCard v-for="p in displayedPosts" :key="p.id" :post="p" class="masonry-item" @open="goDetail" />
        </div>
      </n-spin>
      <div v-if="error" class="error">{{ error }}</div>

      <!-- 左下角浮动“+”按钮（已登录显示） -->
      <n-button class="fab icon-circle-btn" circle type="primary" size="large" @click="openEditor" title="发布日常"
        aria-label="新建日常">
        <Plus :size="22" />
      </n-button>

      <!-- 发布编辑器模态框（保留） -->
      <n-modal v-model:show="showEditor" preset="card" :title="'发布日常'" :mask-closable="false" class="daily-editor-modal"
        :style="editorModalStyle" :content-style="editorModalContentStyle">
        <DailyEditor :autosave-key="'daily_editor_autosave'" @save="handleEditorSave" @cancel="closeEditor" />
      </n-modal>


    </main>

    <!-- 4) 分页组件（底部可见） -->
    <footer class="pagination-bar">
      <n-pagination v-model:page="page" v-model:page-size="pageSize" :item-count="itemCount" :page-sizes="[10, 20, 30]"
        :page-slot="7" size="small" :show-size-picker="true" :show-quick-jumper="true" />
    </footer>

    <!-- 统一认证弹窗组件 -->
    <AuthDialog
      v-model="showAuth"
      :initial-tab="authTab"
      :force-bind-step-on-open="forceBindStepOnOpen"
      @member-bound="onMemberBound"
    />

    <!-- 修改密码模态 -->
    <n-modal v-model:show="showChangePassword" preset="dialog" title="修改密码" :mask-closable="true">
      <div class="login-modal-body">
        <n-form ref="changePwdFormRef" :model="changePwdForm" :rules="changePwdRules" label-placement="left"
          :show-require-mark="false">
          <n-form-item path="old_password" label="当前密码">
            <n-input v-model:value="changePwdForm.old_password" type="password" placeholder="请输入当前密码" />
          </n-form-item>
          <n-form-item path="new_password" label="新密码">
            <n-input v-model:value="changePwdForm.new_password" type="password" placeholder="请输入新密码(≥6位)" />
          </n-form-item>
          <n-form-item path="confirm" label="确认密码">
            <n-input v-model:value="changePwdForm.confirm" type="password" placeholder="请再次输入新密码" />
          </n-form-item>
        </n-form>
        <div v-if="changePwdError" class="error">{{ changePwdError }}</div>
        <n-button type="primary" block :loading="changePwdLoading" @click="submitChangePassword">保存</n-button>
      </div>
    </n-modal>

    <!-- 编辑个人资料模态（占位） -->
    <n-modal v-model:show="showEditProfile" preset="dialog" title="编辑个人资料" :mask-closable="true">
      <div class="login-modal-body">
        <div style="color: var(--text-secondary);">暂未开放，敬请期待。</div>
      </div>
    </n-modal>

  </div>
</template>


<script setup lang="ts">
// 中文注释：重构为四层布局（标题栏/筛选栏/内容/分页），高度严格100vh，正文区域可滚动
import { ref, onMounted, watch, nextTick, onUnmounted, computed } from 'vue'

import { useRouter } from 'vue-router'
import DailyCard from '@/components/daily/DailyCard.vue'
import DailyEditor from '@/components/daily/DailyEditor.vue'

import { dailyApi, type DailyPostItem } from '@/services/daily'
import { useAuthStore } from '@/stores/auth'

import { NPagination, NDropdown, NAvatar, NButton, NDatePicker, NSelect, NSpace, NModal, NForm, NFormItem, NInput, NSpin, useMessage } from 'naive-ui'
import type { FormInst, FormRules } from 'naive-ui'
import { gsap } from 'gsap'
import { ArrowLeft, Plus } from 'lucide-vue-next'
import { apiClient } from '@/services/api'
import AuthDialog from '@/components/auth/AuthDialog.vue'

// 列表与分页
const posts = ref<DailyPostItem[]>([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const loading = ref(false)
const error = ref('')

// 编辑器状态
const showEditor = ref(false)

// Modal 尺寸（确保不占满屏）
const editorModalStyle = { width: 'min(820px, 80vw)', maxWidth: '80vw' }
const editorModalContentStyle = { maxHeight: '60vh', overflow: 'auto' }

// 筛选（作者/标签/日期范围）
const authorUserId = ref<number | null>(null)
const tag = ref<string | null>(null)
const dateRange = ref<[number, number] | null>(null) // 时间戳(ms)数组

// Masonry 容器引用

// 中文注释：日期快捷选项（NaiveUI DatePicker Range Shortcuts）
const dateShortcuts: Record<string, [number, number] | (() => [number, number])> = {
  '最近7天': () => {
    const MS_DAY = 24 * 60 * 60 * 1000
    const end = Date.now()
    const start = end - 6 * MS_DAY
    return [start, end]
  },
  '最近30天': () => {
    const MS_DAY = 24 * 60 * 60 * 1000
    const end = Date.now()
    const start = end - 29 * MS_DAY
    return [start, end]
  },
  '本月': () => {
    const now = new Date()
    const start = new Date(now.getFullYear(), now.getMonth(), 1).getTime()
    const end = Date.now()
    return [start, end]
  }
}

const masonryRef = ref<HTMLElement | null>(null)
let cleanupFns: Array<() => void> = []

// 鉴权与用户信息
const authStore = useAuthStore()
const isAuthenticated = computed(() => authStore.isAuthenticated)

// 用户头像：优先使用绑定成员头像（若后端暂未返回member_id则回退为DiceBear）
// TODO: 后端 /auth/me 返回 member_id 后可在此优先使用 api.getAvatarUrl(member_id)
const fallbackAvatar = computed(() => `https://api.dicebear.com/7.x/avataaars/svg?seed=${authStore.user?.username || 'guest'}`)
const memberId = computed(() => authStore.user?.member_id as number | undefined)
const avatarVersion = ref(0) // 中文注释：绑定成功后递增以刷新头像缓存
const userAvatar = computed(() => {
  if (memberId.value) {
    const base = apiClient.getAvatarUrl(memberId.value)
    return avatarVersion.value ? `${base}?v=${avatarVersion.value}` : base
  }
  return fallbackAvatar.value
})

function goDetail(id: number) {
  router.push({ name: 'DailyDetail', params: { id } })
}

// 统一用户头像尺寸
const avatarSize = 36

// 用户下拉菜单（未绑定时动态增加“绑定成员”）
const isBound = computed(() => Boolean(authStore.user?.member_id))
const userMenuOptions = computed(() => {
  const options = [
    { label: '修改密码', key: 'change-password' },
    { label: '编辑个人资料', key: 'edit-profile' },
    { label: '退出登录', key: 'logout' }
  ] as Array<{ label: string; key: string }>
  if (!isBound.value) {
    options.unshift({ label: '绑定成员', key: 'bind-member' })
  }
  return options
})

// 修改密码弹窗与表单（先在本页用 Modal 完成交互）
const showChangePassword = ref(false)
const showEditProfile = ref(false)
const changePwdFormRef = ref<FormInst | null>(null)
const changePwdForm = ref({ old_password: '', new_password: '', confirm: '' })
const changePwdLoading = ref(false)
const changePwdError = ref('')
const changePwdRules: FormRules = {
  old_password: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { validator: (_r, v) => (v && String(v).length >= 6), message: '新密码至少6位', trigger: ['blur', 'input'] }
  ],
  confirm: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: (_r, v) => v === changePwdForm.value.new_password, message: '两次输入的新密码不一致', trigger: ['blur', 'input'] }
  ]
}

async function submitChangePassword() {
  if (!changePwdFormRef.value) return
  try {
    await changePwdFormRef.value.validate()
    changePwdLoading.value = true
    changePwdError.value = ''
    await apiClient.changePassword({ old_password: changePwdForm.value.old_password, new_password: changePwdForm.value.new_password })
    message.success('密码修改成功')
    showChangePassword.value = false
    changePwdForm.value = { old_password: '', new_password: '', confirm: '' }
  } catch (e: any) {
    changePwdError.value = e?.message || '修改失败'
  } finally {
    changePwdLoading.value = false
  }
}

function handleUserMenu(key: string) {
  if (key === 'bind-member') {
    // 中文注释：未绑定时从菜单进入绑定步骤
    showAuth.value = true
    authTab.value = 'register'
    forceBindStepOnOpen.value = true
    return
  }
  if (key === 'change-password') {
    showChangePassword.value = true
    return
  }
  if (key === 'edit-profile') {
    showEditProfile.value = true
    return
  }
  if (key === 'logout') {
    authStore.logout()
    message.success('已退出登录')
    return
  }
}

// 作者与标签选项（从当前结果聚合，避免额外接口）
const authorOptions = computed(() => {
  const map = new Map<number, string>()
  posts.value.forEach(p => { map.set(p.author_user_id, p.author_display_name || `用户${p.author_user_id}`) })
  return Array.from(map.entries()).map(([value, label]) => ({ label, value }))
})
const tagOptions = computed(() => {
  const set = new Set<string>()
  posts.value.forEach(p => p.tags?.forEach(t => set.add(t)))
  return Array.from(set.values()).map(t => ({ label: t, value: t }))
})
const renderAuthorLabel = (option: any) => option.label

function disableFutureDate(ts: number) { return ts > Date.now() }

function prefersReducedMotion(): boolean {
  try { return typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches } catch { return false }
}

async function fetchList() {
  loading.value = true
  error.value = ''
  try {
    const res = await dailyApi.getList(page.value, pageSize.value, tag.value ?? undefined, authorUserId.value ?? undefined)
    // 服务端分页数据
    let list = res.posts
    total.value = res.total

    // 前端日期范围过滤（若设置）
    if (dateRange.value && dateRange.value.length === 2) {
      const [start, end] = dateRange.value
      list = list.filter(p => {
        const t = new Date(p.created_at).getTime()
        return t >= start && t <= end
      })
    }
    posts.value = list

    await nextTick()
    runStagger()
  } catch (e: any) {
    error.value = e?.message || '加载失败'
  } finally {
    loading.value = false
  }
}

// 展示用数据与计数
const displayedPosts = computed(() => posts.value)
const itemCount = computed(() => (dateRange.value ? posts.value.length : total.value))

function runStagger() {
  if (prefersReducedMotion()) return
  const container = masonryRef.value
  if (!container) return
  const items = Array.from(container.querySelectorAll<HTMLElement>('.masonry-item'))
  if (!items.length) return
  gsap.killTweensOf(items)
  const tween = gsap.fromTo(items, { autoAlpha: 0, y: 14 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: 'power2.out', stagger: 0.05 })
  cleanupFns.push(() => tween.kill())
}


// 中文注释：返回主界面按钮
function goHome() {
  router.push('/')
}

const router = useRouter()
// const route = useRoute()
const message = useMessage()

// 统一认证弹窗控制
const showAuth = ref(false)
const authTab = ref<'login' | 'register'>('login')
const forceBindStepOnOpen = ref(false)

async function waitForAvatarReady(memberId: number, retries = 5, delayMs = 800): Promise<boolean> {
  // 中文注释：轮询头像是否可用（HEAD 200），用于绑定后后端生成头像存在延迟的情况
  for (let i = 0; i < retries; i++) {
    try {
      const url = apiClient.getAvatarUrl(memberId) + `?t=${Date.now()}`
      const res = await fetch(url, { method: 'HEAD', cache: 'no-store' })
      if (res.ok) return true
    } catch (_) {
      // 忽略网络错误，继续重试
    }
    await new Promise(resolve => setTimeout(resolve, delayMs))
  }
  return false
}

async function onMemberBound(mid?: number) {
  const m = Number(mid || memberId.value || 0)
  if (m) {
    await waitForAvatarReady(m, 6, 800)
    avatarVersion.value++
  }
}

// 监听筛选与分页
watch([page, pageSize], () => { fetchList() })
watch([authorUserId, tag, dateRange], () => { page.value = 1; fetchList() })


onMounted(fetchList)

// 打开/关闭编辑器
function openEditor() {
  if (!isAuthenticated.value) {
    message.info('请先登录')
    showAuth.value = true
    authTab.value = 'login'
    forceBindStepOnOpen.value = false
    return
  }
  showEditor.value = true
}
function closeEditor() { showEditor.value = false }

// 处理保存
async function handleEditorSave(json: Record<string, any>) {
  try {
    await dailyApi.createPost({ content_jsonb: json, published: true })
    message.success('发布成功')
    // 清除本地草稿
    try { localStorage.removeItem('daily_editor_autosave') } catch { }
    showEditor.value = false
    // 刷新列表
    await fetchList()
  } catch (e: any) {
    message.error(e?.message || '发布失败')
  }
}
onUnmounted(() => { cleanupFns.forEach(fn => { try { fn() } catch { } }); cleanupFns = [] })
</script>

<style scoped lang="scss">
/* 中文注释：总体使用列布局，严格限制在100vh；正文区域滚动，底部分页常驻可见 */
.daily-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--base-dark, #0f0f12);
  /* 中文注释：防止子元素因伪元素/超长内容导致页面级横向滚动 */
  overflow-x: hidden;
}


.header-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.title {
  font-size: 18px;
  color: var(--text-primary, #fff);
  font-weight: 600;
}

.left-area {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* 中文注释：圆形图标按钮（主题填充 + 微动效），用于返回与新增 */
.icon-circle-btn :deep(.n-button__content) {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.icon-circle-btn.n-button--primary-type {
  /* 主题色填充背景 */
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

/* 中文注释：lucide 图标颜色也用主题色的反色，确保明暗主题可见 */
.icon-circle-btn svg {
  color: var(--text-inverse);
}

.user-area {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-avatar {
  cursor: pointer;
  box-shadow: 0 0 0 1px var(--border-secondary) inset;
}

.avatar-placeholder {
  /* 使用更强的玻璃态背景，保证深浅主题下都有对比度 */
  background: var(--glass-bg-strong, rgba(255, 255, 255, 0.12));
  /* 文字颜色采用主题主文本色，避免浅色主题下看不见 */
  color: var(--text-primary, #111);
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  user-select: none;
}

.filter-bar {
  padding: 8px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.filter-item {
  width: 200px;
  max-width: 40vw;
}

.filter-item.date-picker {
  width: 320px;
  max-width: 50vw;
}

.content-area {
  flex: 1 1 auto;
  overflow: auto;
  padding: 12px 16px;
}

.masonry {
  column-gap: 16px;
  min-height: 200px;
  /* 中文注释：当使用 NSpin 包裹时，给容器一个最小高度，便于加载器在中间居中 */
}

/* 中文注释：确保 NSpin 作为块级元素占满可用宽度，内部加载器可居中 */
.masonry-spin {
  display: block;
  width: 100%;
}

@media (max-width: 640px) {
  .masonry {
    columns: 1;
  }

  .filter-item {
    width: 160px;
  }

  .filter-item.date-picker {
    width: 200px;
    max-width: 70vw;
  }

  /* 中文注释：移动端上移“新增日常”悬浮按钮，避免遮挡底部分页 */
  .fab {
    /* 中文注释：进一步上移，确保不与分页组件重叠 */
    bottom: calc(64px + env(safe-area-inset-bottom));
  }

  /* 中文注释：为分页区域留出更多竖向空间，增强可读性 */
  .pagination-bar {
    padding: 12px 0 18px;
  }
}

@media (min-width: 641px) and (max-width: 960px) {
  .masonry {
    columns: 2;
  }
}

@media (min-width: 961px) and (max-width: 1280px) {
  .masonry {
    columns: 3;
  }
}

@media (min-width: 1281px) and (max-width: 1600px) {
  .masonry {
    columns: 4;
  }
}

@media (min-width: 1601px) {
  .masonry {
    columns: 5;
  }
}

.masonry-item {
  break-inside: avoid;
  margin-bottom: 16px;
  display: block;
}

.pagination-bar {
  flex: 0 0 auto;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 10px 0 14px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}



/* 中文注释：统一日期选择器外观，沿用项目玻璃态/圆角/文本色体系 */
:deep(.n-date-picker) {
  .n-input {

    /* 中文注释：拉伸内部输入占位范围，保证展示完整的起止日期 */
    .n-input__input-el,
    .n-input__input {
      /* 避免内容被压缩隐藏，允许更长文本 */
      min-width: 0;
    }

    border-radius: var(--radius-md);
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    color: var(--text-primary);

    transition: border-color var(--transition-base),
    box-shadow var(--transition-base),
    background var(--transition-base);

    &:hover {
      background: var(--glass-bg-strong);
      border-color: var(--border-focus);
    }

    &.n-input--focus {
      box-shadow: 0 0 0 2px rgba(170, 131, 255, 0.25);
      border-color: var(--primary);
    }

    .n-input__placeholder {
      color: var(--text-tertiary);
    }
  }
}

:deep(.n-date-panel) {
  border-radius: var(--radius-lg);
  background: var(--glass-bg);
  color: var(--text-primary);
  box-shadow: var(--shadow-soft);
  border: 1px solid var(--glass-border);

  .n-date-panel-header {
    border-bottom: 1px solid var(--divider);
  }

  .n-date-panel-weekdays {
    border-bottom: 1px solid var(--divider);
  }

  .n-date-panel-dates {
    .n-date-panel-date {
      border-radius: var(--radius-md);

      &:not(.n-date-panel-date--disabled):hover {
        background-color: var(--surface-hover);

        /* 中文注释：DatePicker 使用 n-input（pair），隐藏其内置边框层并对齐高度 */

      }

      &.n-date-panel-date--selected {
        color: var(--text-inverse);

        &::after {
          background-color: var(--primary);
        }
      }

      &.n-date-panel-date--current {
        .n-date-panel-date__sup {
          background-color: var(--primary);
        }
      }
    }
  }

  .n-date-panel-actions {
    border-top: 1px solid var(--divider);
  }
}

@media (max-width: 640px) {
  :deep(.n-date-picker) {
    max-width: 220px;
  }
}


/* 中文注释：让外层容器也使用一致圆角，并裁剪内部方形边框 */
:deep(.n-date-picker) {
  border-radius: var(--radius-md);
  overflow: hidden;
  /* 防止内部方形层在圆角外露 */
}

/* 中文注释：DatePicker（range）使用 n-input，统一高度与去重边框 */
:deep(.n-date-picker .n-input) {
  height: 34px;
  min-height: 34px;
  line-height: 34px;
  box-sizing: border-box;
  border-radius: var(--radius-md);
  background: var(--glass-bg);
}

/* 中文注释：确保 DatePicker 使用 wrapper 的背景与边框，移除黑底 */
:deep(.n-date-picker .n-input .n-input-wrapper) {
  background-color: var(--glass-bg) !important;
  /* 统一玻璃态背景，去掉黑底 */
  border: 1px solid var(--glass-border) !important;
  border-radius: var(--radius-md) !important;
}

/* 悬停/聚焦时改变 wrapper 的样式 */
:deep(.n-date-picker .n-input:hover .n-input-wrapper) {
  background-color: var(--glass-bg-strong) !important;
  border-color: var(--border-focus) !important;
}

:deep(.n-date-picker .n-input:focus-within .n-input-wrapper) {
  box-shadow: 0 0 0 2px rgba(124, 58, 237, .25) !important;
  border-color: var(--primary) !important;
}

/* 清理内部节点背景，避免再次出现内层底色 */
:deep(.n-date-picker .n-input__input-el),
:deep(.n-date-picker .n-input__input),
:deep(.n-date-picker .n-input__separator) {
  background: transparent !important;
}


:deep(.n-date-picker .n-input:hover) {
  border-color: var(--border-focus);
  background: var(--glass-bg-strong);
}

:deep(.n-date-picker .n-input--focus) {
  box-shadow: 0 0 0 2px rgba(124, 58, 237, .25);
  border-color: var(--primary);
}

/* 去掉 n-input 内部状态边框，避免和外层主题边框叠加 */
:deep(.n-date-picker .n-input__border),
:deep(.n-date-picker .n-input__state-border) {
  display: none;
}

/* 子结构行高与分隔符高度对齐 */
:deep(.n-date-picker .n-input__input) {
  height: 32px;
  line-height: 32px;
}

:deep(.n-date-picker .n-input__separator) {
  height: 32px;
  align-self: center;
}


.error {
  color: #ff6b6b;
  text-align: center;
  padding: 16px;
}

.login-modal-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.login-tip {
  color: var(--text-secondary, #bbb);
  margin: 0 0 4px;
}
.fab {
  position: fixed;
  right: 20px;
  bottom: 20px;
  z-index: 50;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  box-shadow: 0 8px 24px rgba(0,0,0,0.3);
}
.fab svg { color: var(--text-inverse); }


/* 中文注释：为了保证覆盖顺序，移动端下在文件末端再次提升 FAB 的 bottom 值 */
@media (max-width: 640px) {
  .fab {
    bottom: calc(64px + env(safe-area-inset-bottom));
  }
}

/* DailyEditor modal 尺寸与滚动控制 */
.daily-editor-modal :deep(.n-card) {
  width: min(800px, 80vw);
  max-width: 80vw;
}
.daily-editor-modal :deep(.n-card__content) {
  max-height: 60vh;
  overflow: auto;
}

</style>
