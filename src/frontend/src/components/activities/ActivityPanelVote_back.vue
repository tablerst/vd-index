<template>
  <div class="activity-panel" ref="rootRef">
    <header class="panel-header">
      <h3 class="title">{{ activity.title }}</h3>
      <p v-if="activity.description" class="desc">{{ activity.description }}</p>
      <div class="spacer" />
      <div class="admin" v-if="isAuthenticated">
        <input class="input small" v-model="newOption" placeholder="新增选项标签" />
        <button class="btn small" @click="addOption" :disabled="!newOption.trim()">新增选项</button>
        <button class="btn small warn" @click="closeAct">关闭活动</button>
      </div>
    </header>

    <section class="ranking-section">
      <div v-if="rankingLoading" class="loading">加载中…</div>
      <ul v-else class="list">
        <li v-for="(r, i) in entries" :key="r.option_id" class="row list-item">
          <span class="rank">{{ i + 1 }}</span>
          <span class="label">{{ r.label }}</span>
          <span class="votes">{{ r.votes }}</span>
        </li>
      </ul>
    </section>

    <section class="options-section">
      <div class="toolbar">
        <label class="anon">
          <input type="checkbox" v-model="anonymousPreference" />
          <span>匿名展示</span>
        </label>
        <button class="revoke" @click="onRevoke" :disabled="rankingLoading">撤销投票</button>
        <span v-if="!isAuthenticated" class="hint">登录后可投票</span>
      </div>
      <div class="options">
        <button
          v-for="opt in options"
          :key="opt.id"
          class="vote"
          @click="onVote(opt.id)"
          :disabled="!isAuthenticated"
        >为 {{ opt.label }} 投票</button>
        <div v-if="!optionsLoading && options.length === 0" class="empty">暂无可投项</div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useActivitiesStore } from '@/stores/activities'
import { useAuthStore } from '@/stores/auth'
import type { ActActivity, ActRankingEntry, ActVoteOption } from '@/services/api'
import { gsap } from 'gsap'

const props = defineProps<{ activity: ActActivity }>()
const store = useActivitiesStore()
const auth = useAuthStore()

const entries = computed<ActRankingEntry[]>(() => store.ranking[props.activity.id] || [])
const options = computed<ActVoteOption[]>(() => store.options[props.activity.id]?.items || [])
const rankingLoading = computed(() => !!store.loading.ranking[props.activity.id])
const optionsLoading = computed(() => !!store.loading.options[props.activity.id])
const anonymousPreference = computed({
  get: () => store.anonymousPreference,
  set: (v: boolean) => { store.anonymousPreference = v }
})
const isAuthenticated = computed(() => auth.isAuthenticated)

const newOption = ref('')
const rootRef = ref<HTMLElement | null>(null)

onMounted(() => {
  store.fetchRankingTop(props.activity.id).catch(() => {})
  store.fetchOptions(props.activity.id).catch(() => {})

  try {
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
  } catch {}
  if (rootRef.value) {
    const items = rootRef.value.querySelectorAll('.list-item')
    if (items?.length) gsap.from(items, { opacity: 0, y: 8, duration: 0.4, ease: 'power2.out', stagger: 0.04 })
  }
})

function onVote(optionId: number) {
  store.submitVote(props.activity.id, optionId, store.anonymousPreference).catch(() => {})
}

function onRevoke() {
  store.revokeVote(props.activity.id).catch(() => {})
}

async function addOption() {
  const label = newOption.value.trim()
  if (!label) return
  await store.createOption(props.activity.id, label)
  newOption.value = ''
}

async function closeAct() {
  await store.closeActivity(props.activity.id)
}
</script>

<style scoped lang="scss">
.activity-panel { display: grid; gap: 12px; padding: 12px 16px 20px; }
.panel-header { display: flex; align-items: center; gap: 8px; }
.panel-header .title { font-size: 18px; font-weight: 600; color: var(--text-primary); }
.panel-header .desc { margin-top: 4px; color: var(--text-secondary); font-size: 12px; }
.spacer { flex: 1; }
.admin { display: flex; align-items: center; gap: 6px; }
.input.small { padding: 6px 8px; width: 160px; background: transparent; color: var(--text-primary); border: 1px solid var(--divider-color, #444); border-radius: 8px; }
.btn.small { padding: 6px 8px; border: 1px solid var(--primary-6, var(--primary)); color: var(--primary-6, var(--primary)); background: color-mix(in srgb, var(--primary) 6%, transparent); border-radius: 8px; }
.btn.small:hover { background: color-mix(in srgb, var(--primary) 12%, transparent); }
.btn.small.warn { border-color: var(--accent-red, #f7768e); color: var(--accent-red, #f7768e); }
.loading { color: var(--text-secondary); }
.list { list-style: none; margin: 0; padding: 0; display: grid; gap: 6px; }
.row { display: grid; grid-template-columns: 28px 1fr 60px; gap: 8px; align-items: center; background: color-mix(in srgb, var(--panel-bg, #0f0f14) 60%, transparent); border: 1px solid var(--divider-color, #444); border-radius: 10px; padding: 8px 10px; }
.rank { color: var(--text-secondary); }
.options .vote { margin: 6px 6px 0 0; padding: 6px 10px; border: 1px solid var(--primary-6, var(--primary)); color: var(--primary-6, var(--primary)); background: transparent; border-radius: 8px; transition: background .2s ease; }
.options .vote:hover { background: color-mix(in srgb, var(--primary) 10%, transparent); }
.empty { color: var(--text-secondary); padding: 6px 0; }
.toolbar { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.hint { color: var(--text-secondary); font-size: 12px; }
</style>


