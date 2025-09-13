<template>
  <div class="post-list" ref="rootRef">
    <div v-if="loading" class="loading">加载中…</div>
    <ul v-else class="list">
      <li v-for="p in items" :key="p.id" class="row list-item">
        <div class="meta">
          <span class="author">{{ p.display_anonymous ? '匿名用户' : ('#' + p.author_id) }}</span>
          <span class="time">{{ formatTime(p.created_at) }}</span>
        </div>
        <div class="content">{{ p.content }}</div>
      </li>
      <li v-if="items.length === 0 && !loading" class="empty">还没有帖子</li>
    </ul>
    <div v-if="hasMore" class="more">
      <button class="load" @click="loadMore" :disabled="loading">加载更多</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useActivitiesStore } from '@/stores/activities'
import { gsap } from 'gsap'

const props = defineProps<{ activityId: number }>()
const store = useActivitiesStore()

const entry = computed(() => store.threadPosts[props.activityId] || { items: [], loading: false, hasMore: true })
const items = computed(() => entry.value.items)
const loading = computed(() => !!entry.value.loading)
const hasMore = computed(() => !!entry.value.hasMore)

const rootRef = ref<HTMLElement | null>(null)

onMounted(() => {
  if (!items.value.length) store.fetchThreadPosts(props.activityId).catch(() => {})
  try { if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return } catch {}
  if (rootRef.value) {
    const listItems = rootRef.value.querySelectorAll('.list-item')
    if (listItems?.length) gsap.from(listItems, { opacity: 0, y: 8, duration: 0.4, ease: 'power2.out', stagger: 0.03 })
  }
})

function loadMore() {
  store.fetchThreadPosts(props.activityId, entry.value.cursor || null).catch(() => {})
}

function formatTime(iso: string) {
  const dt = new Date(iso)
  return dt.toLocaleString('zh-CN')
}
</script>

<style scoped lang="scss">
.list { list-style: none; padding: 0; margin: 0; display: grid; gap: 10px; }
.row { background: color-mix(in srgb, var(--panel-bg, #0f0f14) 65%, transparent); border: 1px solid var(--divider-color, #444); border-radius: 10px; padding: 10px; transition: transform .15s ease, background .2s ease; }
.row:hover { transform: translateY(-1px); background: color-mix(in srgb, var(--panel-bg, #0f0f14) 80%, transparent); }
.meta { color: var(--text-secondary); font-size: 12px; display: flex; gap: 8px; }
.content { margin-top: 6px; white-space: pre-wrap; line-height: 1.6; }
.loading, .empty { color: var(--text-secondary); }
.more { margin-top: 10px; display: flex; justify-content: center; }
.load { padding: 6px 12px; border: 1px solid var(--primary-6, var(--primary)); color: var(--primary-6, var(--primary)); background: transparent; border-radius: 8px; }
</style>


