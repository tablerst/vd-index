<template>
  <div class="thread-panel" ref="rootRef">
    <header class="panel-header">
      <h3 class="title">{{ activity.title }}</h3>
      <p v-if="activity.description" class="desc">{{ activity.description }}</p>
    </header>

    <PostComposer :activity-id="activity.id" @submit="handleSubmit" />
    <PostList :activity-id="activity.id" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useActivitiesStore } from '@/stores/activities'
import type { ActActivity } from '@/services/api'
import PostList from './PostList.vue'
import PostComposer from './PostComposer.vue'
import { gsap } from 'gsap'

const props = defineProps<{ activity: ActActivity }>()
const store = useActivitiesStore()
const rootRef = ref<HTMLElement | null>(null)

function handleSubmit(payload: { content: string; display_anonymous: boolean }) {
  store.createThreadPost(props.activity.id, payload)
}

onMounted(() => {
  try { if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return } catch {}
  if (rootRef.value) gsap.from(rootRef.value, { opacity: 0, y: 10, duration: 0.45, ease: 'power2.out' })
})
</script>

<style scoped lang="scss">
.thread-panel { display: grid; gap: 12px; padding: 12px 16px 20px; }
.panel-header .title { font-size: 18px; font-weight: 600; color: var(--text-primary); }
.panel-header .desc { margin-top: 4px; color: var(--text-secondary); font-size: 12px; }
</style>


