<template>
  <div class="daily-list">
    <div class="header">
      <h2 class="title">群员日常</h2>
    </div>

    <div class="masonry" ref="masonryRef">
      <DailyCard v-for="p in posts" :key="p.id" :post="p" class="masonry-item" />
      <div v-if="loading" class="loading">加载中...</div>
      <div v-if="error" class="error">{{ error }}</div>
    </div>

    <div class="footer">
      <n-pagination
        v-model:page="page"
        v-model:page-size="pageSize"
        :item-count="total"
        :page-sizes="[10, 20, 30]"
        :page-slot="7"
        size="small"
        :show-size-picker="true"
        :show-quick-jumper="true"
      >
        <template #prefix="{ itemCount }">
          共 {{ itemCount || total }} 条
        </template>
        <template #suffix="{ page, pageCount }">
          第 {{ page }} 页，共 {{ pageCount }} 页
        </template>
      </n-pagination>
    </div>
  </div>
</template>

<script setup lang="ts">
// 中文注释：/daily 列表页，分页+Masonry布局，兼容Mock模式
import { ref, onMounted, watch, nextTick, onUnmounted } from 'vue'
import DailyCard from '@/components/daily/DailyCard.vue'
import { dailyApi, type DailyPostItem } from '@/services/daily'
import { NPagination } from 'naive-ui'
import { gsap } from 'gsap'

const posts = ref<DailyPostItem[]>([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const loading = ref(false)
const error = ref('')


const masonryRef = ref<HTMLElement | null>(null)
let cleanupFns: Array<() => void> = []

function prefersReducedMotion(): boolean {
  try { return typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches } catch { return false }
}

async function fetchList() {
  loading.value = true
  error.value = ''
  try {
    const res = await dailyApi.getList(page.value, pageSize.value)
    posts.value = res.posts
    total.value = res.total
    await nextTick()
    runStagger()
  } catch (e: any) {
    error.value = e?.message || '加载失败'
  } finally {
    loading.value = false
  }
}

function runStagger() {
  if (prefersReducedMotion()) return
  const container = masonryRef.value
  if (!container) return
  const items = Array.from(container.querySelectorAll<HTMLElement>('.masonry-item'))
  if (!items.length) return
  gsap.killTweensOf(items)
  const tween = gsap.fromTo(items, { autoAlpha: 0, y: 14 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: 'power2.out', stagger: 0.05 })
  cleanupFns.push(() => tween.kill())
}

onMounted(fetchList)
watch([page, pageSize], () => { fetchList() })

onUnmounted(() => { cleanupFns.forEach(fn => { try { fn() } catch {} }); cleanupFns = [] })
</script>

<style scoped>
/* 中文注释：列表页容器与响应式布局，延续 DailyCard 暗色主题变量 */
.daily-list { padding: 24px 16px; min-height: 100vh; background: var(--base-dark, #0f0f12); }
.header { display: flex; align-items: center; justify-content: space-between; margin: 8px 0 16px; }
.title { font-size: 20px; color: var(--text-primary, #fff); font-weight: 600; }
.controls { display: flex; align-items: center; gap: 12px; }
.page-size-select { width: 120px; }

.masonry { column-gap: 16px; }
@media (max-width: 640px) { .masonry { columns: 1; } }
@media (min-width: 641px) and (max-width: 960px) { .masonry { columns: 2; } }
@media (min-width: 961px) and (max-width: 1280px) { .masonry { columns: 3; } }
@media (min-width: 1281px) and (max-width: 1600px) { .masonry { columns: 4; } }
@media (min-width: 1601px) { .masonry { columns: 5; } }
.masonry-item { break-inside: avoid; margin-bottom: 16px; display: block; }

.footer { display: flex; justify-content: center; align-items: center; padding: 16px 0 40px; }
.loading { color: var(--text-secondary, #bbb); text-align: center; padding: 16px; }
.error { color: #ff6b6b; text-align: center; padding: 16px; }
</style>

