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

onMounted(() => {
  initParticles()
})

onUnmounted(() => {
  if (animationId) {
    cancelAnimationFrame(animationId)
  }
})
</script>

<style scoped>
.login-container {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  overflow: hidden;
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
  max-width: 400px;
  padding: 20px;
}

.login-form {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-header h1 {
  font-size: 28px;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px 0;
}

.login-header p {
  font-size: 14px;
  color: #666;
  margin: 0;
}

:deep(.n-input) {
  border-radius: 8px;
}

:deep(.n-button) {
  border-radius: 8px;
  height: 44px;
}

:deep(.n-form-item) {
  margin-bottom: 20px;
}

:deep(.n-form-item:last-child) {
  margin-bottom: 0;
}
</style>
