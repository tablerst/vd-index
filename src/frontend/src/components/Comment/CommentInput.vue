<template>
  <div class="comment-input">
    <div class="input-container">
      <div class="input-header">
        <h3 class="input-title">{{ title }}</h3>
        <div class="anonymous-badge" v-if="!showAnonymousOption && isAnonymous">
          <i class="icon-anonymous"></i>
          <span>匿名</span>
        </div>
        <div class="anonymous-toggle" v-else>
          <label class="toggle-label">
            <input type="checkbox" v-model="isAnonymous" />
            <span>匿名</span>
          </label>
        </div>
      </div>

      <div class="input-body">
        <textarea
          v-model="content"
          class="comment-textarea"
          placeholder="说点什么吧... (最多500字)"
          :maxlength="500"
          :disabled="loading"
          @input="handleInput"
          @keydown="handleKeydown"
        ></textarea>

        <div class="input-footer">
          <div class="char-count">
            <span :class="{ warning: content.length > 450, error: content.length >= 500 }">
              {{ content.length }}/500
            </span>
          </div>

          <div class="input-actions">
            <button
              class="cancel-btn"
              @click="handleCancel"
              :disabled="loading"
              v-if="content.length > 0"
            >
              取消
            </button>

            <button
              class="submit-btn"
              @click="handleSubmit"
              :disabled="!canSubmit || loading"
            >
              <span v-if="loading" class="loading-spinner"></span>
              {{ loading ? '发布中...' : '发布评论' }}
            </button>
          </div>
        </div>
      </div>

      <!-- 输入提示 -->
      <div v-if="showTips" class="input-tips">
        <div class="tip-item" v-if="showAnonTip">
          <i class="icon-tip"></i>
          <span>评论将以匿名形式发布，请文明发言</span>
        </div>
        <div class="tip-item">
          <i class="icon-tip"></i>
          <span>支持 Ctrl+Enter 快速发布</span>
        </div>
      </div>

      <!-- 错误提示 -->
      <div v-if="error" class="error-message">
        <i class="icon-error"></i>
        <span>{{ error }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { commentApi } from '@/services/api'

interface Props {
  memberId: number
  loading?: boolean
  placeholder?: string
  title?: string
  showAnonymousOption?: boolean
  anonymousDefault?: boolean
}

interface Emits {
  (e: 'submit', content: string, isAnonymous?: boolean): void
  (e: 'cancel'): void
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  placeholder: '说点什么吧... (最多500字)',
  title: '发表匿名评论',
  showAnonymousOption: false,
  anonymousDefault: true
})

const emit = defineEmits<Emits>()

// 响应式数据
const content = ref('')
const error = ref('')
const showTips = ref(false)
const isAnonymous = ref<boolean>(props.anonymousDefault)


// 中文注释：只有在显示匿名开关且已开启匿名时，才展示匿名相关提示
const showAnonTip = computed(() => props.showAnonymousOption && isAnonymous.value)

// 派生展示标题
const title = props.title
const showAnonymousOption = props.showAnonymousOption

// 计算属性
const canSubmit = computed(() => {
  const validation = commentApi.validateContent(content.value)
  return validation.valid && !props.loading
})

// 处理输入
const handleInput = () => {
  error.value = ''

  // 显示提示（首次输入时）
  if (content.value.length > 0 && !showTips.value) {
    showTips.value = true
  }
}

// 处理键盘事件
const handleKeydown = (event: KeyboardEvent) => {
  // Ctrl+Enter 快速发布
  if (event.ctrlKey && event.key === 'Enter') {
    event.preventDefault()
    handleSubmit()
  }
}

// 提交评论
const handleSubmit = async () => {
  if (!canSubmit.value) return

  const validation = commentApi.validateContent(content.value)
  if (!validation.valid) {
    error.value = validation.message || '评论内容无效'
    return
  }

  try {
    emit('submit', content.value.trim(), isAnonymous.value)
    // 成功后清空内容
    content.value = ''
    showTips.value = false
    error.value = ''
  } catch (err) {
    error.value = '发布失败，请重试'
  }
}

// 取消输入
const handleCancel = () => {
  content.value = ''
  showTips.value = false
  error.value = ''
  emit('cancel')
}

// 聚焦到输入框
const focus = async () => {
  await nextTick()
  const textarea = document.querySelector('.comment-textarea') as HTMLTextAreaElement
  if (textarea) {
    textarea.focus()
  }
}

// 暴露方法
defineExpose({
  focus,
  clear: handleCancel
})
</script>

<style scoped lang="scss">
.comment-input {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.input-container {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 20px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;

  &:focus-within {
    border-color: var(--primary);
    box-shadow: var(--shadow-glow);
  }
}

.input-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.input-title {
  color: var(--text-primary);
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.anonymous-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  background: rgba(170, 131, 255, 0.2);
  border: 1px solid rgba(170, 131, 255, 0.3);
  border-radius: 20px;
  color: var(--primary-color, #AA83FF);
  font-size: 12px;
  font-weight: 500;
}
.anonymous-toggle .toggle-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
}
.anonymous-toggle input[type='checkbox'] {
  width: 16px;
  height: 16px;
}

.input-body {
  position: relative;
}

.comment-textarea {
  width: 100%;
  min-height: 120px;
  max-height: 300px;
  padding: 16px;
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  background: var(--surface-1);
  color: var(--text-primary);
  font-size: 14px;
  line-height: 1.6;
  resize: vertical;
  transition: all 0.3s ease;

  &::placeholder {
    color: var(--text-tertiary);
  }

  &:focus {
    outline: none;
    border-color: var(--primary);
    background: var(--surface-2);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
}

.input-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.char-count {
  font-size: 12px;
  color: var(--text-secondary);

  .warning {
    color: var(--warning);
  }

  .error {
    color: var(--error-alert);
  }
}

.input-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.cancel-btn,
.submit-btn {
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.cancel-btn {
  border: 1px solid var(--glass-border);
  background: transparent;
  color: var(--text-secondary);

  &:hover:not(:disabled) {
    background: var(--surface-2);
    color: var(--text-primary);
  }
}

.submit-btn {
  border: 1px solid var(--primary);
  background: var(--primary);
  color: var(--text-inverse);
  display: flex;
  align-items: center;
  gap: 8px;

  &:hover:not(:disabled) {
    background: var(--primary-hover);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px color-mix(in oklch, var(--primary) 30%, transparent);
  }

  &:disabled {
    background: color-mix(in oklch, var(--primary) 60%, transparent);
    border-color: color-mix(in oklch, var(--primary) 60%, transparent);
  }
}

.loading-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid color-mix(in oklch, var(--text-inverse) 30%, transparent);
  border-top: 2px solid var(--text-inverse);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.input-tips {
  margin-top: 16px;
  padding: 12px;
  background: color-mix(in oklch, var(--primary) 12%, transparent);
  border: 1px solid color-mix(in oklch, var(--primary) 22%, transparent);
  border-radius: 8px;
  animation: fadeInUp 0.3s ease-out;
}

.tip-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
  font-size: 12px;
  margin-bottom: 4px;

  &:last-child {
    margin-bottom: 0;
  }
}

.error-message {
  margin-top: 12px;
  padding: 12px;
  background: color-mix(in oklch, var(--error-alert) 12%, transparent);
  border: 1px solid color-mix(in oklch, var(--error-alert) 30%, transparent);
  border-radius: 8px;
  color: var(--error-alert);
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  animation: shake 0.5s ease-in-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

/* 图标样式 */
.icon-anonymous::before { content: '🎭'; }
.icon-tip::before { content: '💡'; }
.icon-error::before { content: '⚠️'; }

/* 响应式设计 */
@media (max-width: 768px) {
  .comment-input {
    padding: 10px;
  }

  .input-container {
    padding: 16px;
  }

  .input-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .input-title {
    font-size: 16px;
  }

  .comment-textarea {
    min-height: 100px;
    padding: 12px;
    font-size: 13px;
  }

  .input-footer {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .input-actions {
    justify-content: flex-end;
  }

  .cancel-btn,
  .submit-btn {
    padding: 10px 16px;
    font-size: 13px;
  }
}
</style>
