<template>
  <div class="thread-panel" ref="rootRef">
    <header class="panel-header">
      <h3 class="title">{{ activity.title }}</h3>
      <p v-if="activity.description" class="desc">{{ activity.description }}</p>
      <div class="spacer" />
      <div class="admin" v-if="isAuthenticated"></div>
    </header>

    <PostComposer :activity-id="activity.id" @submit="handleSubmit" />
    <PostList :activity-id="activity.id" :active="!!active" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useActivitiesStore } from '@/stores/activities'
import type { ActActivity } from '@/services/api'
import PostList from './PostList.vue'
import PostComposer from './PostComposer.vue'
import { gsap } from 'gsap'
import { useAuthStore } from '@/stores/auth'
import { storeToRefs } from 'pinia'

const props = defineProps<{ activity: ActActivity; active?: boolean }>()
const store = useActivitiesStore()
const auth = useAuthStore()
const { isAuthenticated } = storeToRefs(auth)
const rootRef = ref<HTMLElement | null>(null)

function handleSubmit(payload: { content: string; display_anonymous: boolean }) {
  store.createThreadPost(props.activity.id, payload)
}

// 直接使用 Ref，避免二次 computed
// 角色信息在本组件未使用，保留 user 以供子组件发帖鉴权

// 删除操作统一在 ActivityCarousel 顶部进行

let hasAnimated = false

function animateIn() {
  if (hasAnimated) return
  hasAnimated = true
  try { if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return } catch {}
  if (!rootRef.value) return
  const header = rootRef.value.querySelector('.panel-header')
  const composer = rootRef.value.querySelector('.composer')
  const tl = gsap.timeline({ defaults: { ease: 'power2.out' } })
  if (header) tl.fromTo(header, { opacity: 0 }, { opacity: 1, duration: 0.26 }, 0)
  if (composer) tl.fromTo(composer, { opacity: 0 }, { opacity: 1, duration: 0.26 }, 0.05)
}

onMounted(() => {
  if (props.active) animateIn()
})

watch(() => props.active, (v) => { if (v) animateIn() })
</script>

<style scoped lang="scss">
.thread-panel { display: grid; gap: 12px; padding: 12px 16px 20px; }
.panel-header .title { font-size: 18px; font-weight: 600; color: var(--text-primary); }
.panel-header .desc { margin-top: 4px; color: var(--text-secondary); font-size: 12px; }
.panel-header { display: flex; align-items: center; gap: 10px; }
.spacer { flex: 1; }
.admin { display: flex; align-items: center; gap: 6px; }
.btn.small { padding: 6px 8px; border: 1px solid var(--primary-6, var(--primary)); color: var(--primary-6, var(--primary)); background: color-mix(in srgb, var(--primary) 6%, transparent); border-radius: 8px; }
.btn.small.warn { border-color: var(--accent-red, #f7768e); color: var(--accent-red, #f7768e); }
.btn.small.warn.outline { background: transparent; }
</style>


