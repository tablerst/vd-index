<template>
  <div class="daily-page">
    <!-- 1) 标题栏 -->
    <header class="header-bar">
      <div class="left-area">
        <n-button size="small" tertiary @click="goHome">返回</n-button>
        <h2 class="title">群员日常</h2>
      </div>
      <div class="user-area">
        <!-- 已登录：头像+下拉 -->
        <n-dropdown v-if="isAuthenticated" trigger="click" :options="userMenuOptions" @select="handleUserMenu">
          <n-avatar round :size="avatarSize" :src="userAvatar" :fallback-src="fallbackAvatar" />
        </n-dropdown>
        <!-- 未登录：圆形灰底头像占位，点击打开登录模态 -->
        <n-avatar
          v-else
          round
          :size="avatarSize"
          class="user-avatar avatar-placeholder"
          :style="{ background: 'var(--glass-bg-strong, rgba(255,255,255,0.12))', color: 'var(--text-primary, #111)', fontSize: '12px', fontWeight: '600' }"
          title="未登录，点击登录"
          @click="showLoginModal = true"
        >未登录</n-avatar>
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
      <n-button
        class="fab"
        circle
        type="primary"
        size="large"
        @click="openEditor"
        title="发布日常"
        aria-label="新建日常"
      >+
      </n-button>

      <!-- 发布编辑器模态框（保留） -->
      <n-modal
        v-model:show="showEditor"
        preset="card"
        :title="'发布日常'"
        :mask-closable="false"
        class="daily-editor-modal"
        :style="editorModalStyle"
        :content-style="editorModalContentStyle"
      >
        <DailyEditor :autosave-key="'daily_editor_autosave'" @save="handleEditorSave" @cancel="closeEditor" />
      </n-modal>


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

    <!-- 登录/注册模态（内置表单，不跳转页面） -->
    <n-modal v-model:show="showLoginModal" preset="dialog" title="账号" :mask-closable="registerStep !== 2" :close-on-esc="registerStep !== 2" :closable="registerStep !== 2">
      <div class="login-modal-body">
        <n-tabs v-model:value="authTab" type="line">
          <n-tab-pane name="login" tab="登录">
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
          </n-tab-pane>
          <n-tab-pane name="register" tab="注册">
            <div v-if="registerStep === 1" class="login-modal-body">
              <n-form ref="registerFormRef" :model="registerForm" :rules="registerRules" label-placement="left"
                :show-require-mark="false">
                <n-form-item path="username" label="用户名">
                  <n-input v-model:value="registerForm.username" placeholder="设置用户名" />
                </n-form-item>
                <n-form-item path="password" label="密码">
                  <n-input v-model:value="registerForm.password" type="password" placeholder="设置密码(≥6位)" />
                </n-form-item>
                <n-form-item path="confirm" label="确认密码">
                  <n-input v-model:value="registerForm.confirm" type="password" placeholder="再次输入密码" />
                </n-form-item>
              </n-form>
              <div v-if="registerError" class="error">{{ registerError }}</div>
              <n-button type="primary" block :loading="registerLoading" @click="handleRegister">下一步</n-button>
            </div>
            <div v-else class="login-modal-body">
              <n-form ref="bindFormRef" :model="bindForm" :rules="bindRules" label-placement="left"
                :show-require-mark="false">
                <n-form-item path="member_id" label="选择成员">
                  <n-select v-model:value="bindForm.member_id" :options="bindableMemberOptions" placeholder="选择要绑定的成员" filterable />
                </n-form-item>
                <n-form-item path="uin" label="成员UIN">
                  <n-input v-model:value="bindForm.uin" placeholder="请输入该成员的QQ号用于验证" />
                </n-form-item>
              </n-form>
              <div v-if="bindError" class="error">{{ bindError }}</div>
              <n-button type="primary" block :loading="bindLoading" @click="handleBind">完成绑定</n-button>
            </div>
          </n-tab-pane>
        </n-tabs>
      </div>
    </n-modal>

    <!-- 修改密码模态 -->
    <n-modal v-model:show="showChangePassword" preset="dialog" title="修改密码" :mask-closable="true">
      <div class="login-modal-body">
        <n-form ref="changePwdFormRef" :model="changePwdForm" :rules="changePwdRules" label-placement="left" :show-require-mark="false">
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
import { useRouter, useRoute } from 'vue-router'
import DailyCard from '@/components/daily/DailyCard.vue'
import DailyEditor from '@/components/daily/DailyEditor.vue'

import { dailyApi, type DailyPostItem } from '@/services/daily'
import { useAuthStore } from '@/stores/auth'

import { NPagination, NDropdown, NAvatar, NButton, NDatePicker, NSelect, NSpace, NModal, NForm, NFormItem, NInput, NSpin, NTabs, NTabPane, useMessage } from 'naive-ui'
import type { FormInst, FormRules } from 'naive-ui'
import { gsap } from 'gsap'
import { apiClient } from '@/services/api'

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
    showLoginModal.value = true
    authTab.value = 'register'
    registerStep.value = 2
    bindError.value = ''
    bindForm.value = { member_id: null, uin: '' }
    loadBindableMembers()
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

// 登录/注册切换与注册-绑定流程状态
const authTab = ref<'login' | 'register'>('login')
const registerStep = ref<1 | 2>(1)

// 注册表单
const registerFormRef = ref<FormInst | null>(null)
const registerForm = ref({ username: '', password: '', confirm: '' })
const registerLoading = ref(false)
const registerError = ref('')
const registerRules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { validator: (_r, v) => (v && String(v).length >= 6), message: '密码至少6位', trigger: ['blur', 'input'] }
  ],
  confirm: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: (_r, v) => v === registerForm.value.password, message: '两次输入的密码不一致', trigger: ['blur', 'input'] }
  ]
}

async function handleRegister() {
  if (!registerFormRef.value) return
  try {
    await registerFormRef.value.validate()
    registerLoading.value = true
    registerError.value = ''
    const ok = await authStore.register({ username: registerForm.value.username, password: registerForm.value.password })
    if (ok) {
      // 进入绑定步骤并加载可绑定成员
      registerStep.value = 2
      await loadBindableMembers()
      message.success('注册成功，请完成成员绑定')
    } else {
      registerError.value = '注册失败，请稍后再试'
    }
  } catch (e: any) {
    registerError.value = e?.message || '注册失败'
  } finally {
    registerLoading.value = false
  }
}

// 绑定成员表单
const bindFormRef = ref<FormInst | null>(null)
const bindForm = ref<{ member_id: number | null; uin: string }>({ member_id: null, uin: '' })
const bindLoading = ref(false)
const bindError = ref('')
const bindRules: FormRules = {
  member_id: [{ required: true, type: 'number', message: '请选择成员', trigger: 'change' }],
  uin: [
    { required: true, message: '请输入成员UIN', trigger: 'blur' },
    { validator: (_r, v) => /^\d{5,}$/.test(String(v || '')), message: 'UIN格式不正确', trigger: ['blur', 'input'] }
  ]
}

// 可绑定成员选项
const bindableMemberOptions = ref<Array<{ label: string; value: number }>>([])

async function loadBindableMembers() {
  try {
    const res = await apiClient.getBindableMembers(1, 50)
    bindableMemberOptions.value = res.members.map(m => ({ label: m.display_name, value: m.id }))
  } catch (e: any) {
    console.error('Failed to load bindable members', e)
    bindableMemberOptions.value = []
    // 中文注释：若后端路由注册顺序不当，/members/bindable 可能被 /members/{member_id} 吞掉导致422
    bindError.value = '加载可绑定成员失败：请确认后端已将 users_bind 路由在 members 之前注册（/api/router.py）'
    message.error('无法加载可绑定成员，请稍后重试')
  }
}

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

async function handleBind() {
  if (!bindFormRef.value) return
  try {
    await bindFormRef.value.validate()
    bindLoading.value = true
    bindError.value = ''
    const payload = { member_id: Number(bindForm.value.member_id), uin: Number(bindForm.value.uin) }
    const res = await apiClient.bindMember(payload)
    if (res?.success) {
      message.success('绑定成功')
      // 绑定成功后刷新用户信息，确保拿到最新 member_id
      try {
        await authStore.validateToken()
      } catch (e) {
        console.warn('刷新用户信息失败，但继续后续流程', e)
      }
      // 若后端异步生成头像文件，等待头像可用（HEAD 200）再强制刷新
      if (memberId.value) {
        await waitForAvatarReady(memberId.value, 6, 800)
        avatarVersion.value++
      }
      showLoginModal.value = false
      // 重置注册流程，方便下次打开
      authTab.value = 'login'
      registerStep.value = 1
      registerForm.value = { username: '', password: '', confirm: '' }
      bindForm.value = { member_id: null, uin: '' }
    } else {
      bindError.value = '绑定失败，请检查UIN是否正确'
    }
  } catch (e: any) {
    bindError.value = e?.message || '绑定失败'
  } finally {
    bindLoading.value = false
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
    showLoginModal.value = true
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
    try { localStorage.removeItem('daily_editor_autosave') } catch {}
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
.fab {
  position: fixed;
  right: 20px;
  bottom: 20px;
  z-index: 50;
  width: 44px;
  height: 44px;
  font-size: 24px;
  border-radius: 50%;
  box-shadow: 0 8px 24px rgba(0,0,0,0.3);
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
