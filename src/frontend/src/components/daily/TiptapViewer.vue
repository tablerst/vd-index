<template>
  <div class="tiptap-viewer">
    <!-- 中文注释：只读模式下，隐藏工具栏，仅渲染内容 -->
    <EditorContent v-if="editor" :editor="editor" class="tiptap-content" />
  </div>
</template>

<script setup lang="ts">
// 中文注释：Tiptap 只读渲染组件，接受 JSON 文档渲染
import { onUnmounted, watch, toRef } from 'vue'
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Image from '@tiptap/extension-image'

const props = defineProps<{ doc: Record<string, any> | null | undefined }>()
const jsonRef = toRef(props, 'doc')

// 初始化只读编辑器
const editor = useEditor({
  editable: false,
  content: props.doc || '',
  extensions: [StarterKit, Image.configure({ inline: true })],
  editorProps: {
    attributes: {
      class: [
        'tiptap', 'ProseMirror', 'prose', 'prose-notion', 'prose-invert',
        'max-w-none', 'focus:outline-none'
      ].join(' ')
    }
  }
})

// 当外部 doc 变化时更新内容
watch(jsonRef, (val) => {
  if (!editor?.value) return
  if (val) editor.value.commands.setContent(val, { emitUpdate: false })
  else editor.value.commands.setContent('', { emitUpdate: false })
})

onUnmounted(() => { editor?.value?.destroy() })
</script>

<style scoped>
/* 中文注释：沿用编辑器的内容样式，但不显示占位符/拖拽句柄等编辑态样式 */
.tiptap-content { display:flex; justify-content:center; }
.tiptap-content :deep(.ProseMirror){ width:100%; max-width:720px; margin:0 auto; line-height:1.75; font-size:15px; }
.tiptap-content :deep(h1,h2,h3){ line-height:1.25; font-weight:700; }
.tiptap-content :deep(h1){ font-size:28px; margin:1.2em 0 .6em; }
.tiptap-content :deep(h2){ font-size:22px; margin:1.1em 0 .5em; }
.tiptap-content :deep(h3){ font-size:18px; margin:1em 0 .4em; }
.tiptap-content :deep(blockquote){ margin:.8em 0; padding:.6em .9em; border-left:3px solid color-mix(in oklch, var(--primary) 40%, white); background: color-mix(in oklch, var(--glass-bg) 88%, transparent); border-radius:8px; }
.tiptap-content :deep(ul){ list-style: disc outside; padding-left:1.5rem; margin:.5em 0; }
.tiptap-content :deep(ol){ list-style: decimal outside; padding-left:1.5rem; margin:.5em 0; }
.tiptap-content :deep(li){ margin:.25em 0; }
.tiptap-content :deep(.ProseMirror-focused){ outline: none; }
</style>

