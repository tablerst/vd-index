<template>
  <div class="thread-panel">
    <!-- v2: 该组件已废弃，保留占位避免路由/引用报错；请改用 ActivityPanelVote -->
    <div class="deprecated">该活动类型已合并为投票 + 评论，请使用投票面板。</div>
  </div>
</template>

<script setup lang="ts">
// noop
</script>

<style scoped lang="scss">
.deprecated { color: var(--text-secondary); font-size: 12px; padding: 12px; border: 1px dashed var(--divider-color, #444); border-radius: 8px; }
</style>

