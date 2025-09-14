<template>
  <div class="act-vote" ref="rootRef">
    <header class="head">
      <div class="titles">
        <h3 class="title">{{ activity.title }}</h3>
        <p v-if="activity.description" class="desc">{{ activity.description }}</p>
      </div>
      <div class="spacer" />
      <div class="admin" v-if="isAuthenticated">
        <input
          class="input small"
          v-model="newOption"
          placeholder="新增选项标签"
          :disabled="!isAuthenticated"
          @keyup.enter="addOption()"
        />
        <button class="btn small" @click="addOption" :disabled="!newOption.trim() || !isAuthenticated" :title="(!isAdmin && !isCreator) ? '若无权限将提示' : ''">新增选项</button>
        <button class="btn small warn" @click="closeAct" v-if="isAdmin">关闭活动</button>
      </div>
    </header>

    <section class="grid">
      <div class="panel ranking">
        <div class="panel-title">排行榜</div>
        <div v-if="entries.length === 0 && rankingLoading" class="loading-wrap">
          <span class="spinner" aria-hidden="true" />
          <span class="loading-text">加载中…</span>
        </div>
        <div v-else-if="entries.length > 0" class="rank-chart-wrap" :class="{ syncing: rankingLoading }">
          <div ref="rankChartRef" class="rank-chart"></div>
        </div>
        <div v-else class="empty">暂无排行</div>
      </div>

      <div class="panel options" :data-refreshing="refreshingOptions ? 'true' : null">
        <div class="panel-title">
          <div class="left">
            <label class="anon">
              <input type="checkbox" v-model="anonymousPreference" />
              <span>匿名展示</span>
            </label>
          </div>
          <div class="right buttons-gap">
            <button class="btn ghost small" @click="onRevoke" :disabled="revokeLoading">{{ revokeLoading ? '撤销中…' : '撤销投票' }}</button>
            <span v-if="!isAuthenticated" class="hint">登录后可投票</span>
          </div>
        </div>

        <div v-if="optionsLoading && options.length === 0" class="loading-wrap">
          <span class="spinner" aria-hidden="true" />
          <span class="loading-text">加载选项…</span>
        </div>

        <div v-else class="option-grid">
          <button
            v-for="opt in options"
            :key="opt.id"
            class="vote-card"
            :class="{ locked: canManage && hasVotes(opt.id as number) }"
            @click="onVote(opt.id)"
            :disabled="!isAuthenticated"
          >
            <span
              v-if="canManage && opt.id && typeof opt.id === 'number' && voteOfMe !== opt.id"
              class="delete-right"
              :class="{ disabled: hasVotes(opt.id as number) }"
              :title="hasVotes(opt.id as number) ? '该选项已有投票，无法删除' : '删除选项'"
              @click.stop="confirmDelete(opt.id)"
            >×</span>
            <span class="label">{{ opt.label }}</span>
            <span class="badge" v-if="voteOfMe === opt.id">已投</span>
          </button>
          <div v-if="options.length === 0" class="empty">暂无可投项</div>
        </div>
      </div>
    </section>
  </div>
  
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch, nextTick } from 'vue'
import { useActivitiesStore } from '@/stores/activities'
import { useAuthStore } from '@/stores/auth'
import { storeToRefs } from 'pinia'
import type { ActActivity, ActRankingEntry, ActVoteOption } from '@/services/api'
import { gsap } from 'gsap'
import { useThemeStore } from '@/stores/theme'
import * as echarts from 'echarts/core'
import type { ECharts } from 'echarts/core'
import { BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([BarChart, GridComponent, TooltipComponent, CanvasRenderer])

const props = defineProps<{ activity: ActActivity; active?: boolean }>()
const store = useActivitiesStore()
const auth = useAuthStore()
const { user, isAuthenticated } = storeToRefs(auth)

const entries = computed<ActRankingEntry[]>(() => store.ranking[props.activity.id] || [])
const options = computed<ActVoteOption[]>(() => store.options[props.activity.id]?.items || [])
const rankingLoading = computed(() => !!store.loading.ranking[props.activity.id])
const optionsLoading = computed(() => !!store.loading.options[props.activity.id])
const voteOfMe = computed(() => store.myVotes[props.activity.id] ?? null)
const revokeLoading = computed(() => !!store.loading.revoke?.[props.activity.id])
const anonymousPreference = computed({
  get: () => store.anonymousPreference,
  set: (v: boolean) => { store.anonymousPreference = v }
})
// 直接使用 Ref，避免双层 computed
const isAdmin = computed(() => user.value?.role === 'admin')
const isCreator = computed(() => {
  const uid = Number(user.value?.id ?? 0)
  const creator = Number((props.activity as any)?.creator_id ?? 0)
  return !!uid && creator === uid
})
const canManage = computed(() => isAdmin.value || isCreator.value)

const newOption = ref('')
const rootRef = ref<HTMLElement | null>(null)
const rankChartRef = ref<HTMLDivElement | null>(null)
// 删除模式已移除，改为每个选项独立删除按钮
const refreshingOptions = computed(() => options.value.length > 0 && optionsLoading.value)

let chart: ECharts | null = null
let resizeObserver: ResizeObserver | null = null

// Map option_id -> votes for quick lookup in delete mode
const votesByOption = computed<Map<number, number>>(() => {
  const m = new Map<number, number>()
  for (const e of entries.value) {
    const id = (e as any).option_id
    if (typeof id === 'number') m.set(id, (e as any).votes || 0)
  }
  return m
})

function hasVotes(optionId: number): boolean {
  return (votesByOption.value.get(optionId) || 0) > 0
}

function ensureInit() {
  store.fetchRankingTop(props.activity.id).catch(() => {})
  store.fetchOptions(props.activity.id).catch(() => {})
  store.fetchMyVote(props.activity.id).catch(() => {})
}

onMounted(async () => {
  if (props.active) ensureInit()

  try { if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return } catch {}
  if (rootRef.value) {
    const rank = rootRef.value.querySelectorAll('.rank-item')
    if (rank?.length) gsap.from(rank, { opacity: 0, y: 8, duration: 0.4, ease: 'power2.out', stagger: 0.04 })
  }

  await nextTick()
  initOrUpdateChart()
})

watch(() => props.active, (v) => { if (v) ensureInit() })

onUnmounted(() => {
  // 释放 ECharts 实例与观察器
  if (resizeObserver && rankChartRef.value) {
    try { resizeObserver.unobserve(rankChartRef.value) } catch {}
  }
  resizeObserver = null
  if (chart) {
    try { chart.dispose() } catch {}
  }
  chart = null
})

// 百分比在图表构建中计算，此处函数已不再使用

function onVote(optionId: number) {
  store.submitVote(props.activity.id, optionId, store.anonymousPreference).catch(() => {})
}

function onRevoke() {
  store.revokeVote(props.activity.id).catch(() => {})
}

async function addOption() {
  const label = newOption.value.trim()
  if (!label) return
  try {
    await store.createOption(props.activity.id, label)
    newOption.value = ''
  } catch (e: any) {
    // 后端会做权限判断：管理员或活动发起者
    const msg = e?.message || e?.detail || ''
    if (msg.includes('permissions') || msg.includes('403')) {
      alert('新增选项失败：需要管理员或活动发起者权限')
    } else {
      alert('新增选项失败：' + (msg || '未知错误'))
    }
  }
}

async function closeAct() {
  await store.closeActivity(props.activity.id)
}

// 删除操作统一在 ActivityCarousel 顶部进行

function confirmDelete(optionId: number) {
  if (voteOfMe.value === optionId) { alert('你已投该选项，不能删除该选项'); return }
  if (hasVotes(optionId)) { alert('该选项已有投票，无法删除'); return }
  if (!confirm('确定删除该选项吗？此操作不可恢复')) return
  store.deleteOption(props.activity.id, optionId).catch((e: any) => {
    const msg = e?.message || e?.detail || '删除失败'
    alert(msg)
  })
}

// 删除模式已移除

// ---------------- ECharts 排行榜 ----------------
const themeStore = useThemeStore()

function getCssVar(name: string, fallback: string): string {
  try {
    const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim()
    return v || fallback
  } catch {
    return fallback
  }
}

function buildChartOption(sorted: ActRankingEntry[]) {
  const primary = getCssVar('--primary', '#3F7DFB')
  const textPrimary = getCssVar('--text-primary', '#E6E6E6')
  const textSecondary = getCssVar('--text-secondary', '#A0A0A0')
  const divider = getCssVar('--divider', 'rgba(255,255,255,0.12)')
  const total = sorted.reduce((s, e) => s + (e.votes || 0), 0)

  return {
    grid: { left: 8, right: 12, top: 8, bottom: 8, containLabel: true },
    tooltip: {
      trigger: 'item',
      formatter: (p: any) => {
        const votes = p.value ?? 0
        const pct = total > 0 ? Math.round((votes / total) * 100) : 0
        return `${p.name}<br/>票数：${votes}（${pct}%）`
      }
    },
    xAxis: {
      type: 'value',
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: textSecondary },
      splitLine: { show: true, lineStyle: { color: divider } }
    },
    yAxis: {
      type: 'category',
      data: sorted.map(e => e.label),
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: textPrimary }
    },
    series: [
      {
        type: 'bar',
        data: sorted.map(e => e.votes || 0),
        barWidth: '60%',
        itemStyle: { color: primary },
        emphasis: { focus: 'series' },
        label: {
          show: true,
          position: 'right',
          color: textPrimary,
          formatter: (p: any) => {
            const votes = p.value ?? 0
            const pct = total > 0 ? Math.round((votes / total) * 100) : 0
            return `${votes}（${pct}%）`
          }
        },
        animationDurationUpdate: 300
      }
    ]
  } as any
}

function initOrUpdateChart() {
  if (!props.active) return
  if (!rankChartRef.value) return
  const container = rankChartRef.value

  // 动态高度：每项 36px，最小 220 最大 520
  const itemCount = entries.value.length
  const targetHeight = Math.max(220, Math.min(520, 36 * itemCount + 60))
  if (container.style.height !== `${targetHeight}px`) {
    container.style.height = `${targetHeight}px`
  }

  // 排序（票数降序）
  const sorted = [...entries.value].sort((a, b) => (b.votes || 0) - (a.votes || 0))

  if (!chart) {
    chart = echarts.init(container)
    // 监听容器尺寸变化
    try {
      resizeObserver = new ResizeObserver(() => { try { chart && chart.resize() } catch {} })
      resizeObserver.observe(container)
    } catch {
      window.addEventListener('resize', () => { try { chart && chart.resize() } catch {} }, { passive: true })
    }
  }

  const option = buildChartOption(sorted)
  try { chart.setOption(option, true) } catch {}
}

// 数据与主题变化时更新
watch(entries, async () => {
  // 等 DOM 根据 v-if/v-else-if 切换出图表容器后再初始化
  await nextTick()
  initOrUpdateChart()
}, { deep: true, flush: 'post' })
watch(() => themeStore.currentTheme, () => {
  // 主题切换时重建配置
  initOrUpdateChart()
})
</script>

<style scoped lang="scss">
.act-vote { display: grid; gap: 16px; padding: 14px 18px 22px; color: var(--text-primary); }
.head { display: flex; align-items: center; gap: 10px; }
.titles { display: grid; gap: 4px; }
.title { font-size: 18px; font-weight: 700; }
.desc { color: var(--text-secondary); font-size: 12px; }
.spacer { flex: 1; }
.admin { display: flex; align-items: center; gap: 6px; }
.input.small { padding: 6px 8px; width: 160px; background: transparent; color: var(--text-primary); border: 1px solid var(--divider-color, #444); border-radius: 8px; }
.btn.small { padding: 6px 8px; border: 1px solid var(--primary-6, var(--primary)); color: var(--primary-6, var(--primary)); background: color-mix(in srgb, var(--primary) 6%, transparent); border-radius: 8px; }
.btn.small.warn { border-color: var(--accent-red, #f7768e); color: var(--accent-red, #f7768e); }
.btn.small.warn.outline { background: transparent; }
.btn.small.warn.outline[aria-pressed="true"] { background: color-mix(in srgb, var(--accent-red, #f7768e) 22%, transparent); color: #fff; box-shadow: 0 0 0 2px color-mix(in srgb, var(--accent-red, #f7768e) 35%, transparent) inset; }

.grid { display: grid; gap: 12px; grid-template-columns: 1fr; }
@media (min-width: 960px) { .grid { grid-template-columns: 3fr 1fr; align-items: start; } }

.panel { background: color-mix(in srgb, var(--base-dark) 85%, rgba(0,0,0,0.2)); border: 1px solid color-mix(in srgb, var(--divider-color, #3a3a3a) 60%, rgba(255,255,255,0.08)); border-radius: 14px; padding: 12px; box-shadow: 0 6px 24px rgba(0,0,0,.35); }
.panel.options.managing { border-color: var(--error-alert, #f7768e); box-shadow: 0 0 0 2px color-mix(in srgb, var(--error-alert, #f7768e) 30%, transparent) inset, 0 6px 24px rgba(0,0,0,.35); }
.panel-title { display: flex; align-items: center; justify-content: space-between; color: var(--text-secondary); font-size: 12px; margin-bottom: 8px; }
.anon { display: inline-flex; align-items: center; gap: 6px; }
.hint { color: var(--text-secondary); font-size: 12px; margin-left: 8px; }
.chip { display: inline-flex; align-items: center; gap: 6px; padding: 2px 8px; border-radius: 999px; background: color-mix(in srgb, var(--primary) 10%, transparent); color: var(--text-secondary); margin-right: 8px; }
.chip.danger { background: color-mix(in srgb, var(--error-alert, #f7768e) 25%, transparent); color: #fff; box-shadow: 0 0 0 1px color-mix(in srgb, var(--error-alert, #f7768e) 50%, transparent) inset; }

.buttons-gap { display: inline-flex; align-items: center; gap: 8px; }

/* 排行 */
.rank-list { list-style: none; margin: 0; padding: 0; display: grid; gap: 8px; }
.rank-list.syncing .bar-fill { transition: width .25s ease; }
/* 中文注释：PC 端采用 3:1 区域（标签:票数），移动端上下布局 */
.rank-item { display: grid; grid-template-columns: 28px 1fr; gap: 8px; align-items: center; }
.rank-item.first .bar-fill { background: linear-gradient(90deg, var(--primary) 0%, #a77bff 100%); }
.rank-item.second .bar-fill { background: linear-gradient(90deg, #6aa9ff, #7cc3ff); }
.rank-item.third .bar-fill { background: linear-gradient(90deg, #6fe3b5, #7ff1c2); }
.order { color: var(--text-secondary); font-weight: 700; }
.bar { position: relative; background: color-mix(in srgb, var(--panel-bg, #0f0f14) 80%, transparent); border: 1px solid var(--divider-color, #333); border-radius: 10px; overflow: hidden; }
.bar-fill { position: absolute; inset: 0; width: 0%; background: color-mix(in srgb, var(--primary) 26%, transparent); transition: width .35s ease; }
.bar-label { position: relative; display: grid; grid-template-columns: 3fr 1fr; align-items: center; padding: 6px 10px; column-gap: 8px; }
.bar-label .name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; min-width: 0; }
.bar-label .votes { justify-self: end; }
.bar-label .pct { color: var(--text-secondary); margin-left: 2px; font-size: 12px; }
@media (max-width: 768px) {
  .rank-item { grid-template-columns: 22px 1fr; align-items: stretch; }
  .bar-label { grid-template-columns: 1fr; row-gap: 4px; }
  .bar-label .votes { justify-self: start; }
}

/* ECharts 容器样式 */
.rank-chart-wrap { width: 100%; }
.rank-chart { width: 100%; height: 260px; }

/* 选项 */
.option-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 10px; }
.vote-card { position: relative; padding: 12px 40px 12px 12px; border: 1px solid var(--divider-color, #3a3a3a); border-radius: 12px; background: color-mix(in srgb, var(--base-dark) 82%, rgba(0,0,0,0.15)); color: var(--text-primary); text-align: left; transition: transform .15s ease, background .2s ease, border-color .2s ease, box-shadow .2s ease; }
.vote-card:hover { transform: translateY(-2px); background: color-mix(in srgb, var(--primary) 8%, transparent); border-color: var(--primary); }
.vote-card:disabled { opacity: 0.55; }
.vote-card.disabled { cursor: not-allowed; }
.vote-card[disabled] { cursor: not-allowed; }
.vote-card .badge { position: absolute; top: 8px; right: 8px; padding: 2px 6px; font-size: 12px; border-radius: 999px; background: var(--primary); color: #fff; box-shadow: 0 2px 10px rgba(0,0,0,.3); }
.vote-card .label { display: block; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
.vote-card .delete-right { position: absolute; right: 8px; top: 50%; transform: translateY(-50%); width: 22px; height: 22px; display: grid; place-items: center; border-radius: 6px; background: color-mix(in srgb, var(--error-alert, #f7768e) 30%, transparent); color: #fff; font-weight: 700; cursor: pointer; opacity: .9; transition: background .2s ease; }
.vote-card .delete-right:hover { background: var(--error-alert, #f7768e); }
.vote-card .delete-right.disabled { opacity: .45; cursor: not-allowed; filter: grayscale(0.35); }
.vote-card.locked { border-color: color-mix(in srgb, var(--divider-color, #3a3a3a) 80%, rgba(255,255,255,0.08)); background: color-mix(in srgb, #444 12%, transparent); }
.empty { color: var(--text-secondary); padding: 6px 0; }

/* 独立加载样式，避免文字跟着旋转 */
.loading-wrap { display: inline-flex; align-items: center; gap: 8px; color: var(--text-secondary); }
.spinner { width: 16px; height: 16px; border: 2px solid rgba(255,255,255,.25); border-top-color: var(--primary); border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* 选项面板无感刷新：右上角小圆圈，不遮挡内容 */
.panel.options { position: relative; }
.panel.options[data-refreshing="true"]::before {
  content: '';
  position: absolute; top: 10px; right: 10px; width: 14px; height: 14px;
  border: 2px solid rgba(255,255,255,.25); border-top-color: var(--primary); border-radius: 50%;
  animation: spin 1s linear infinite;
}
</style>


