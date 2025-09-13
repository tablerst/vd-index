<template>
  <div class="composer">
    <textarea v-model="content" class="input" rows="3" placeholder="说点什么…" />
    <div class="toolbar">
      <label class="anon">
        <input type="checkbox" v-model="anonymous" />
        <span>匿名</span>
      </label>
      <div class="actions">
        <button class="btn" @click="onSubmit" :disabled="!canSubmit">发布</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

defineProps<{ activityId: number }>()
const emit = defineEmits<{ (e: 'submit', payload: { content: string; display_anonymous: boolean }): void }>()

const content = ref('')
const anonymous = ref(true)
const canSubmit = computed(() => content.value.trim().length > 0 && content.value.length <= 500)

function onSubmit() {
  if (!canSubmit.value) return
  emit('submit', { content: content.value.trim(), display_anonymous: anonymous.value })
  content.value = ''
}
</script>

<style scoped lang="scss">
.composer { display: grid; gap: 8px; }
.input { width: 100%; padding: 10px 12px; background: transparent; color: var(--text-primary); border: 1px solid var(--divider-color, #444); border-radius: 10px; }
.toolbar { display: flex; align-items: center; justify-content: space-between; }
.btn { padding: 6px 12px; border: 1px solid var(--primary-6, var(--primary)); color: var(--primary-6, var(--primary)); background: color-mix(in srgb, var(--primary) 6%, transparent); border-radius: 8px; }
.btn:disabled { opacity: .5; cursor: not-allowed; }
.btn:not(:disabled):hover { background: color-mix(in srgb, var(--primary) 12%, transparent); }
</style>


