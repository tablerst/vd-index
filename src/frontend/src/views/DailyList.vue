<template>
  <div class="daily-page">
    <!-- 1) 标题栏 -->
    <header class="header-bar">
      <h2 class="title">群员日常</h2>
      <div class="user-area">
        <!-- 已登录：头像+下拉 -->
        <n-dropdown v-if="isAuthenticated" trigger="click" :options="userMenuOptions" @select="handleUserMenu">
          <n-avatar round :size="avatarSize" :src="userAvatar" :fallback-src="fallbackAvatar" />
        </n-dropdown>
        <!-- 未登录：圆形灰底头像占位，点击打开登录模态 -->
        <n-avatar v-else round :size="avatarSize" class="user-avatar avatar-placeholder"
          @click="showLoginModal = true">未登录</n-avatar>
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
          <DailyCard v-for="p in displayedPosts" :key="p.id" :post="p" class="masonry-item" />
        </div>
      </n-spin>
      <div v-if="error" class="error">{{ error }}</div>
    </main>

    <!-- 4) 分页组件（底部可见） -->
    <footer class="pagination-bar">
      <n-pagination v-model:page="page" v-model:page-size="pageSize" :item-count="itemCount" :page-sizes="[10, 20, 30]"
        :page-slot="7" size="small" :show-size-picker="true" :show-quick-jumper="true">
        <template #prefix="{ itemCount }">
          共 {{ itemCount }} 条
        </template>
        <template #suffix="{ page, pageCount }">
          第 {{ page }} 页，共 {{ pageCount }} 页
        </template>
      </n-pagination>
    </footer>

    <!-- 登录模态（内置表单，不跳转页面） -->
    <n-modal v-model:show="showLoginModal" preset="dialog" title="登录" :mask-closable="true">
      <div class="login-modal-body">
        <n-form ref="loginFormRef" :model="loginForm" :rules="loginRules" label-placement="left"
          :show-require-mark="false">
          <n-form-item path="username" label="用户名">
            <n-input v-model:value="loginForm.username" placeholder="请输入用户名" />
          </n-form-item>
          <n-form-item path="password" label="密码">
            <n-input v-model:value="loginForm.password" type="password" placeholder="请输入密码" />
          </n-form-item>
        </n-form>
        <div v-if="loginError" class="error">{{ loginError }}</div>
        <n-button type="primary" block :loading="loginLoading" @click="handleLogin">登录</n-button>
      </div>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
// 中文注释：重构为四层布局（标题栏/筛选栏/内容/分页），高度严格100vh，正文区域可滚动
import { ref, onMounted, watch, nextTick, onUnmounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import DailyCard from '@/components/daily/DailyCard.vue'
import { dailyApi, type DailyPostItem } from '@/services/daily'
import { useAuthStore } from '@/stores/auth'

import { NPagination, NDropdown, NAvatar, NButton, NDatePicker, NSelect, NSpace, NModal, NForm, NFormItem, NInput, NSpin, useMessage } from 'naive-ui'
import type { FormInst, FormRules } from 'naive-ui'
import { gsap } from 'gsap'

// 列表与分页
const posts = ref<DailyPostItem[]>([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const loading = ref(false)
const error = ref('')

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
const userAvatar = computed(() => fallbackAvatar.value)

// 统一用户头像尺寸
const avatarSize = 36

// 用户下拉菜单
const userMenuOptions = [
  { label: '修改密码', key: 'change-password' },
  { label: '编辑个人信息', key: 'edit-profile' }
]
function handleUserMenu(key: string) {
  // 中文注释：此处可根据路由实现具体页面；当前跳转到后台设置首页
  if (key === 'change-password' || key === 'edit-profile') router.push('/settings')
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

const router = useRouter()
const route = useRoute()

// 登录模态显隐与表单
const showLoginModal = ref(false)
const loginFormRef = ref<FormInst | null>(null)
const loginForm = ref({ username: '', password: '' })
const loginLoading = ref(false)
const loginError = ref('')
const message = useMessage()
const loginRules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

async function handleLogin() {
  if (!loginFormRef.value) return
  try {
    await loginFormRef.value.validate()
    loginLoading.value = true
    loginError.value = ''
    // 设置redirect到当前页，避免跳转到/settings
    const redirect = route.fullPath || '/daily'
    if (route.query.redirect !== redirect) {
      await router.replace({ path: route.path, query: { ...route.query, redirect } })
    }
    const ok = await authStore.login({ username: loginForm.value.username, password: loginForm.value.password })
    if (ok) {
      showLoginModal.value = false
      message.success('登录成功')
      // 留在当前页（authStore.login 会读取上面设置的 redirect）
    } else {
      loginError.value = '登录失败，请检查用户名和密码'
    }
  } catch (e: any) {
    loginError.value = e?.message || '登录失败'
  } finally {
    loginLoading.value = false
  }
}

// 监听筛选与分页
watch([page, pageSize], () => { fetchList() })
watch([authorUserId, tag, dateRange], () => { page.value = 1; fetchList() })


onMounted(fetchList)
onUnmounted(() => { cleanupFns.forEach(fn => { try { fn() } catch { } }); cleanupFns = [] })
</script>

<style scoped lang="scss">
/* 中文注释：总体使用列布局，严格限制在100vh；正文区域滚动，底部分页常驻可见 */
.daily-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--base-dark, #0f0f12);
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
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
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
  min-height: 200px; /* 中文注释：当使用 NSpin 包裹时，给容器一个最小高度，便于加载器在中间居中 */
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
  overflow: hidden; /* 防止内部方形层在圆角外露 */
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
</style>
