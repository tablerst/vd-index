<template>
  <div class="login-container">
    <!-- 背景粒子效果 -->
    <div class="particles-background" ref="particlesContainer"></div>
    
    <!-- 登录表单 -->
    <div class="login-form-wrapper">
      <div class="login-form">
        <div class="login-header">
          <h1>后台管理系统</h1>
          <p>VD群成员管理平台</p>
        </div>
        
        <n-form
          ref="formRef"
          :model="loginForm"
          :rules="rules"
          size="large"
          @submit.prevent="handleLogin"
        >
          <n-form-item path="username">
            <n-input
              v-model:value="loginForm.username"
              placeholder="用户名"
              :input-props="{ autocomplete: 'username' }"
            >
              <template #prefix>
                <n-icon :component="PersonOutline" />
              </template>
            </n-input>
          </n-form-item>
          
          <n-form-item path="password">
            <n-input
              v-model:value="loginForm.password"
              type="password"
              placeholder="密码"
              show-password-on="click"
              :input-props="{ autocomplete: 'current-password' }"
            >
              <template #prefix>
                <n-icon :component="LockClosedOutline" />
              </template>
            </n-input>
          </n-form-item>
          
          <n-form-item>
            <n-button
              type="primary"
              size="large"
              :loading="loading"
              :disabled="loading"
              attr-type="submit"
              block
              strong
            >
              {{ loading ? '登录中...' : '登录' }}
            </n-button>
          </n-form-item>
        </n-form>
        
        <!-- 错误提示 -->
        <n-alert
          v-if="errorMessage"
          type="error"
          :show-icon="false"
          style="margin-top: 16px;"
        >
          {{ errorMessage }}
        </n-alert>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  NForm, 
  NFormItem, 
  NInput, 
  NButton, 
  NIcon, 
  NAlert,
  useMessage,
  type FormInst,
  type FormRules
} from 'naive-ui'
import { PersonOutline, LockClosedOutline } from '@vicons/ionicons5'
import { useAuthStore } from '@/stores/auth'
import { RevealEffect } from '@/utils/fluentEffects'

// 路由和状态管理
const router = useRouter()
const authStore = useAuthStore()
const message = useMessage()

// 表单引用和状态
const formRef = ref<FormInst | null>(null)
const loading = ref(false)
const errorMessage = ref('')
const particlesContainer = ref<HTMLElement>()

// 登录表单数据
const loginForm = reactive({
  username: '',
  password: ''
})

// 表单验证规则
const rules: FormRules = {
  username: [
    {
      required: true,
      message: '请输入用户名',
      trigger: ['input', 'blur']
    }
  ],
  password: [
    {
      required: true,
      message: '请输入密码',
      trigger: ['input', 'blur']
    }
  ]
}

// 粒子动画
let animationId: number
let particles: Array<{
  x: number
  y: number
  vx: number
  vy: number
  size: number
  opacity: number
}> = []

const initParticles = () => {
  if (!particlesContainer.value) return
  
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  particlesContainer.value.appendChild(canvas)
  
  const resizeCanvas = () => {
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight
  }
  
  resizeCanvas()
  window.addEventListener('resize', resizeCanvas)
  
  // 创建粒子
  for (let i = 0; i < 50; i++) {
    particles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.5,
      vy: (Math.random() - 0.5) * 0.5,
      size: Math.random() * 2 + 1,
      opacity: Math.random() * 0.5 + 0.2
    })
  }
  
  const animate = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    particles.forEach(particle => {
      particle.x += particle.vx
      particle.y += particle.vy
      
      if (particle.x < 0 || particle.x > canvas.width) particle.vx *= -1
      if (particle.y < 0 || particle.y > canvas.height) particle.vy *= -1
      
      ctx.beginPath()
      ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2)
      ctx.fillStyle = `rgba(170, 131, 255, ${particle.opacity})`
      ctx.fill()
    })
    
    animationId = requestAnimationFrame(animate)
  }
  
  animate()
}

// 处理登录
const handleLogin = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    loading.value = true
    errorMessage.value = ''

    const success = await authStore.login({
      username: loginForm.username,
      password: loginForm.password
    })

    if (success) {
      message.success('登录成功')
      // 路由跳转已在authStore.login中处理
    } else {
      errorMessage.value = authStore.error || '登录失败，请检查用户名和密码'
      message.error(errorMessage.value)
    }
  } catch (error: any) {
    console.error('登录失败:', error)
    errorMessage.value = error.response?.data?.detail || '登录失败，请检查用户名和密码'
    message.error(errorMessage.value)
  } finally {
    loading.value = false
  }
}

// Reveal 效果
let revealEffect: RevealEffect | null = null

onMounted(() => {
  initParticles()

  // 为登录表单添加 Reveal 效果
  setTimeout(() => {
    const loginForm = document.querySelector('.login-form') as HTMLElement
    if (loginForm) {
      revealEffect = new RevealEffect(loginForm)
    }
  }, 100)
})

onUnmounted(() => {
  if (animationId) {
    cancelAnimationFrame(animationId)
  }
  if (revealEffect) {
    revealEffect.destroy()
  }
})
</script>

<style scoped lang="scss">
@import '@/styles/fluent-theme.scss';

.login-container {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--fluent-primary) 0%, #764ba2 100%);
  overflow: hidden;
  font-family: var(--fluent-font-family);
}

.particles-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.particles-background canvas {
  position: absolute;
  top: 0;
  left: 0;
}

.login-form-wrapper {
  position: relative;
  z-index: 2;
  width: 100%;
  max-width: 420px;
  padding: var(--fluent-spacing-xl);
}

.login-form {
  @include fluent-acrylic(0.95, 30px);
  border-radius: var(--fluent-radius-xlarge);
  padding: var(--fluent-spacing-xxxl);
  @include fluent-depth(16);
  border: 1px solid rgba(255, 255, 255, 0.2);
  @include fluent-motion();

  // Reveal 效果
  @include fluent-reveal();

  &:hover {
    @include fluent-depth(64);
  }
}

.login-header {
  text-align: center;
  margin-bottom: var(--fluent-spacing-xxxl);

  h1 {
    @include fluent-typography(large-title);
    color: var(--fluent-text-primary);
    margin: 0 0 var(--fluent-spacing-sm) 0;
  }

  p {
    @include fluent-typography(body);
    color: var(--fluent-text-secondary);
    margin: 0;
  }
}

// Naive UI 组件样式覆盖
:deep(.n-input) {
  border-radius: var(--fluent-radius-medium);
  @include fluent-motion();

  .n-input__input-el {
    @include fluent-typography(body);
  }

  &:hover {
    @include fluent-depth(2);
  }

  &:focus-within {
    @include fluent-depth(4);
  }
}

:deep(.n-button) {
  border-radius: var(--fluent-radius-medium);
  height: 44px;
  font-weight: var(--fluent-font-weight-semibold);
  @include fluent-motion();

  &:hover {
    @include fluent-depth(8);
    transform: translateY(-1px);
  }

  &:active {
    @include fluent-depth(2);
    transform: translateY(0);
  }
}

:deep(.n-form-item) {
  margin-bottom: var(--fluent-spacing-xl);

  &:last-child {
    margin-bottom: 0;
  }
}

:deep(.n-alert) {
  border-radius: var(--fluent-radius-medium);
  @include fluent-motion();
}

// 图标样式
:deep(.n-icon) {
  color: var(--fluent-text-tertiary);
  @include fluent-motion();
}

:deep(.n-input:focus-within .n-icon) {
  color: var(--fluent-primary);
}

// 响应式设计
@media (max-width: 480px) {
  .login-form-wrapper {
    max-width: 100%;
    padding: var(--fluent-spacing-lg);
  }

  .login-form {
    padding: var(--fluent-spacing-xxl);
  }

  .login-header h1 {
    @include fluent-typography(title);
  }
}

// 加载状态动画
:deep(.n-button--loading) {
  .n-button__icon {
    animation: fluent-spin 1s linear infinite;
  }
}

@keyframes fluent-spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

// 表单验证错误样式
:deep(.n-form-item--feedback-error) {
  .n-input {
    border-color: var(--fluent-error);

    &:hover {
      border-color: var(--fluent-error);
    }
  }
}

// 粒子颜色调整
.particles-background canvas {
  opacity: 0.6;
}
</style>
