<template>
  <div class="composer">
    <textarea v-model="content" class="input" rows="3" placeholder="说点什么…" />
    <div class="toolbar">
      <label class="switch">
        <input type="checkbox" v-model="anonymous" />
        <span class="slider" aria-hidden="true"></span>
        <span class="label">匿名</span>
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
  // v2：必须登录才能发表评论（匿名仅影响展示）
  if (!auth.isAuthenticated) {
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
.switch { position: relative; display: inline-flex; align-items: center; gap: 6px; }
.switch input { width: 0; height: 0; opacity: 0; position: absolute; }
.switch .slider { width: 34px; height: 18px; background: color-mix(in srgb, var(--base-dark) 70%, rgba(0,0,0,0.2)); border-radius: 999px; border: 1px solid var(--divider-color, #444); position: relative; transition: background .2s ease, border-color .2s ease; }
.switch .slider::after { content: ''; position: absolute; top: 50%; left: 2px; transform: translateY(-50%); width: 14px; height: 14px; background: #fff; border-radius: 50%; transition: left .2s ease; }
.switch input:checked + .slider { background: var(--primary); border-color: var(--primary); }
.switch input:checked + .slider::after { left: 18px; }
.switch .label { white-space: nowrap; }
.btn { padding: 6px 12px; border: 1px solid var(--primary-6, var(--primary)); color: var(--primary-6, var(--primary)); background: color-mix(in srgb, var(--primary) 6%, transparent); border-radius: 8px; }
.btn:disabled { opacity: .5; cursor: not-allowed; }
.btn:not(:disabled):hover { background: color-mix(in srgb, var(--primary) 12%, transparent); }
</style>


