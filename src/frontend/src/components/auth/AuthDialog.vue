<template>
  <n-modal
    v-model:show="visible"
    preset="dialog"
    title="账号"
    :mask-closable="allowCloseDuringBind || registerStep !== 2"
    :close-on-esc="allowCloseDuringBind || registerStep !== 2"
    :closable="allowCloseDuringBind || registerStep !== 2"
    :style="{ width: 'min(520px, 86vw)' }"
  >
    <div class="auth-dialog-body">
      <n-tabs v-model:value="authTab" type="line">
        <n-tab-pane name="login" tab="登录">
          <div class="pane">
            <n-form ref="loginFormRef" :model="loginForm" :rules="loginRules" label-placement="left" label-align="right" :label-width="formLabelWidth" :show-require-mark="false">
              <n-form-item path="username" label="用户名">
                <n-input v-model:value="loginForm.username" placeholder="请输入用户名" autocomplete="username" />
              </n-form-item>
              <n-form-item path="password" label="密码">
                <n-input v-model:value="loginForm.password" type="password" placeholder="请输入密码" autocomplete="current-password" />
              </n-form-item>
            </n-form>
            <div v-if="loginError" class="error">{{ loginError }}</div>
            <n-button type="primary" block :loading="loginLoading" @click="handleLogin">登录</n-button>
          </div>
        </n-tab-pane>
        <n-tab-pane name="register" tab="注册">
          <div v-if="registerStep === 1" class="pane">
            <n-form ref="registerFormRef" :model="registerForm" :rules="registerRules" label-placement="left" label-align="right" :label-width="formLabelWidth" :show-require-mark="false">
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

          <div v-else class="pane">
            <n-form ref="bindFormRef" :model="bindForm" :rules="bindRules" label-placement="left" label-align="right" :label-width="formLabelWidth" :show-require-mark="false">
              <n-form-item path="member_id" label="选择成员">
                <n-select
                  v-model:value="bindForm.member_id"
                  v-model:show="bindableSelectOpen"
                  :options="bindableMemberOptions"
                  placeholder="选择要绑定的成员"
                  filterable
                  :virtual-scroll="true"
                  :loading="bindableLoading"
                  :reset-menu-on-options-change="false"
                  @update:show="onBindableShowChange"
                >
                  <template #action>
                    <div style="padding: 8px 12px; text-align: center;">
                      <n-button
                        type="primary"
                        round
                        size="small"
                        :loading="bindableLoading"
                        :disabled="!bindableHasMore || bindableLoading"
                        style="min-width: 120px;"
                        @mousedown.prevent
                        @click.stop="handleLoadMoreBindable"
                      >
                        {{ bindableHasMore ? (bindableLoading ? '加载中...' : '加载更多') : (bindableMemberOptions.length === 0 ? '暂无可绑定成员' : '已全部加载') }}
                      </n-button>
                    </div>
                  </template>
                </n-select>
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
</template>

<script setup lang="ts">
// English comments only inside code.
import { ref, watch, onMounted, computed, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { apiClient } from '@/services/api'
import { NModal, NForm, NFormItem, NInput, NButton, NSelect, NTabs, NTabPane, useMessage } from 'naive-ui'
import type { FormInst, FormRules } from 'naive-ui'
// unified label width for aligned forms
const formLabelWidth = 80

interface Props {
  modelValue?: boolean
  initialTab?: 'login' | 'register'
  allowCloseDuringBind?: boolean
  redirectToCurrent?: boolean
  forceBindStepOnOpen?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: false,
  initialTab: 'login',
  allowCloseDuringBind: false,
  redirectToCurrent: true,
  forceBindStepOnOpen: false,
})

const emit = defineEmits<{
  (e: 'update:show', v: boolean): void
  (e: 'update:modelValue', v: boolean): void
  (e: 'closed'): void
  (e: 'success', type: 'login' | 'register'): void
  (e: 'member-bound', memberId: number): void
}>()

// v-model compatibility
const visible = computed({
  get: () => props.modelValue ?? false,
  set: (v: boolean) => {
    emit('update:modelValue', v)
    emit('update:show', v)
    if (!v) emit('closed')
  }
})

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const message = useMessage()

// tabs and steps
const authTab = ref<'login' | 'register'>(props.initialTab)
const registerStep = ref<1 | 2>(1)

watch(() => props.initialTab, (tab) => { authTab.value = tab })
watch(() => props.modelValue, (show) => {
  if (show) {
    // when opened by parent request to jump directly to bind step
    if (props.forceBindStepOnOpen) {
      authTab.value = 'register'
      registerStep.value = 2
      // lazy-load bindable members on open
      nextTick(() => { if (bindableMemberOptions.value.length === 0) loadBindableMembers(true) })
    } else {
      registerStep.value = 1
    }
  }
})

// login
const loginFormRef = ref<FormInst | null>(null)
const loginForm = ref({ username: '', password: '' })
const loginLoading = ref(false)
const loginError = ref('')
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
    if (props.redirectToCurrent) {
      const redirect = route.fullPath || '/'
      if (route.query.redirect !== redirect) {
        await router.replace({ path: route.path, query: { ...route.query, redirect } })
      }
    }
    const ok = await auth.login({ username: loginForm.value.username, password: loginForm.value.password })
    if (ok) {
      emit('success', 'login')
      visible.value = false
      message.success('登录成功')
    } else {
      loginError.value = '登录失败，请检查用户名和密码'
    }
  } catch (e: any) {
    loginError.value = e?.message || '登录失败'
  } finally {
    loginLoading.value = false
  }
}

// register
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
    const ok = await auth.register({ username: registerForm.value.username, password: registerForm.value.password })
    if (ok) {
      emit('success', 'register')
      message.success('注册成功，请完成成员绑定')
      registerStep.value = 2
      await loadBindableMembers(true)
    } else {
      registerError.value = '注册失败，请稍后再试'
    }
  } catch (e: any) {
    registerError.value = e?.message || '注册失败'
  } finally {
    registerLoading.value = false
  }
}

// bind member
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

const bindableMemberOptions = ref<Array<{ label: string; value: number }>>([])
const bindablePage = ref(1)
const bindablePageSize: number = 50
const bindableLoading = ref(false)
const bindableHasMore = ref(true)
const bindableTotalPages = ref(1)
const bindableSelectOpen = ref(false)

function onBindableShowChange(show: boolean) {
  bindableSelectOpen.value = show
  if (show) {
    if (bindableMemberOptions.value.length === 0) {
      loadBindableMembers(true)
    }
  }
}

async function handleLoadMoreBindable(e?: MouseEvent) {
  try { e?.stopPropagation() } catch {}
  if (!bindableLoading.value && bindableHasMore.value) {
    await loadBindableMembers(false)
    await nextTick()
    bindableSelectOpen.value = true
  }
}

async function loadBindableMembers(reset = false) {
  try {
    if (bindableLoading.value) return
    if (reset) {
      bindablePage.value = 1
      bindableHasMore.value = true
      bindableTotalPages.value = 1
      bindableMemberOptions.value = []
    } else {
      if (!bindableHasMore.value) return
    }
    bindableLoading.value = true
    const res = await apiClient.getBindableMembers(bindablePage.value, bindablePageSize)
    const existed = new Set(bindableMemberOptions.value.map(o => o.value))
    const newOptions = res.members
      .map(m => ({ label: m.display_name, value: m.id }))
      .filter(o => !existed.has(o.value))
    bindableMemberOptions.value = [...bindableMemberOptions.value, ...newOptions]
    bindableTotalPages.value = res.total_pages || Math.ceil((res.total || 0) / (res.page_size || bindablePageSize))
    const nowPage = res.page || bindablePage.value
    const nextPage = nowPage + 1
    bindablePage.value = nextPage
    bindableHasMore.value = nextPage <= bindableTotalPages.value
  } catch (e: any) {
    console.error('Failed to load bindable members', e)
    if (reset) bindableMemberOptions.value = []
    bindError.value = '加载可绑定成员失败，请稍后重试'
  } finally {
    bindableLoading.value = false
  }
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
      try { await auth.validateToken() } catch { /* ignore */ }
      const mid = Number(auth.user?.member_id || bindForm.value.member_id || 0)
      emit('member-bound', mid)
      visible.value = false
      // reset internal states
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

onMounted(() => {
  // If already logged in and not bound, parent may open bind step directly.
})
</script>

<style scoped>
.auth-dialog-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.pane {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.pane :deep(.n-form-item-label) {
  /* align labels on the same vertical baseline */
  padding-right: 8px;
}
.pane :deep(.n-input),
.pane :deep(.n-select) {
  /* unify input control widths and visuals */
  width: 100%;
}
.pane :deep(.n-input .n-input-wrapper) {
  border-radius: var(--radius-md, 10px);
}
.error {
  color: #ff6b6b;
  text-align: left;
}
</style>


