<template>
  <div class="composer">
    <textarea v-model="content" class="input" rows="3" placeholder="说点什么…" />
    <div class="toolbar">
      <label class="anon">
        <input type="checkbox" v-model="anonymous" />
        <span class="anon-text">匿名</span>
      </label>
      <div class="actions">
        <button class="btn" @click="onSubmit" :disabled="!canSubmit">发布</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

defineProps<{ activityId: number }>()
const emit = defineEmits<{ (e: 'submit', payload: { content: string; display_anonymous: boolean }): void }>()

const content = ref('')
const anonymous = ref(true)
const auth = useAuthStore()
const canSubmit = computed(() => content.value.trim().length > 0 && content.value.length <= 500)

function onSubmit() {
  if (!canSubmit.value) return
  // 若未登录且未勾选匿名 -> 需要登录；若未登录但勾选匿名 -> 允许匿名提交
  if (!auth.isAuthenticated && !anonymous.value) {
    try { window.dispatchEvent(new CustomEvent('open-login-modal')) } catch {}
    return
  }
  emit('submit', { content: content.value.trim(), display_anonymous: anonymous.value })
  content.value = ''
}
</script>

<style scoped lang="scss">
.composer { display: grid; gap: 8px; }
.input { width: 100%; padding: 10px 12px; background: transparent; color: var(--text-primary); border: 1px solid var(--divider-color, #444); border-radius: 10px; }
.toolbar { display: flex; align-items: center; justify-content: space-between; }
.anon { display: inline-flex; align-items: center; gap: 6px; }
.anon input { margin: 0; }
.anon-text { line-height: 1; transform: translateY(0.5px); }
.btn { padding: 6px 12px; border: 1px solid var(--primary-6, var(--primary)); color: var(--primary-6, var(--primary)); background: color-mix(in srgb, var(--primary) 6%, transparent); border-radius: 8px; }
.btn:disabled { opacity: .5; cursor: not-allowed; }
.btn:not(:disabled):hover { background: color-mix(in srgb, var(--primary) 12%, transparent); }
</style>


