<template>
  <div class="daily-editor">
    <!-- 工具栏：基础文本样式与插图按钮（置顶粘性，玻璃态卡片，分组+图标） -->
    <div class="toolbar">
      <div class="toolbar-groups">
        <div class="group">
          <n-button quaternary size="small" :disabled="!editor" @click="editor?.chain().focus().toggleBold().run()"
            :type="isActive('bold') ? 'primary' : 'default'" title="加粗">
            <template #icon>
              <n-icon size="16" aria-hidden="true">
                <Bold />
              </n-icon>
            </template>
          </n-button>
          <n-button quaternary size="small" :disabled="!editor" @click="editor?.chain().focus().toggleItalic().run()"
            :type="isActive('italic') ? 'primary' : 'default'" title="斜体">
            <template #icon>
              <n-icon size="16">
                <Italic />
              </n-icon>
            </template>
          </n-button>
          <n-button quaternary size="small" :disabled="!editor" @click="editor?.chain().focus().toggleStrike().run()"
            :type="isActive('strike') ? 'primary' : 'default'" title="删除线">
            <template #icon>
              <n-icon size="16">
                <Strikethrough />
              </n-icon>
            </template>
          </n-button>
        </div>
        <div class="group">
          <n-button quaternary size="small" :disabled="!editor" @click="setHeading(2)"
            :type="isActive('heading', { level: 2 }) ? 'primary' : 'default'" title="二级标题">
            <template #icon>
              <n-icon size="16">
                <Heading2 />
              </n-icon>
            </template>
          </n-button>
          <n-button quaternary size="small" :disabled="!editor" @click="setHeading(3)"
            :type="isActive('heading', { level: 3 }) ? 'primary' : 'default'" title="三级标题">
            <template #icon>
              <n-icon size="16">
                <Heading3 />
              </n-icon>
            </template>
          </n-button>
        </div>
        <div class="group">
          <n-button quaternary size="small" :disabled="!editor"
            @click="editor?.chain().focus().toggleBulletList().run()"
            :type="isActive('bulletList') ? 'primary' : 'default'" title="无序列表">
            <template #icon>
              <n-icon size="16">
                <List />
              </n-icon>
            </template>
          </n-button>
          <n-button quaternary size="small" :disabled="!editor"
            @click="editor?.chain().focus().toggleOrderedList().run()"
            :type="isActive('orderedList') ? 'primary' : 'default'" title="有序列表">
            <template #icon>
              <n-icon size="16">
                <ListOrdered />
              </n-icon>
            </template>
          </n-button>
        </div>
        <div class="group">
          <n-button quaternary size="small" :disabled="!editor" @click="insertImage" title="插入图片">
            <template #icon>
              <n-icon size="16">
                <ImageIcon />
              </n-icon>
            </template>
          </n-button>
        </div>
      </div>
      <div class="toolbar-actions">
        <n-button size="small" @click="onCancel">取消</n-button>
        <n-button type="primary" size="small" :loading="saving" @click="onSave">保存</n-button>
      </div>
    </div>

    <!-- 编辑区域 -->
    <div class="editor-pane">
      <EditorContent :editor="editor" class="tiptap-content" />
    </div>

    <!-- 隐藏的文件选择器 -->
    <input ref="fileInputRef" type="file" accept="image/*" multiple style="display:none" @change="onFilesSelected" />
  </div>
</template>

<script setup lang="ts">
// 中文注释：独立Tiptap编辑器组件，支持基础富文本与图片插入，提供保存回调
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { NButton, NIcon, useMessage } from 'naive-ui'
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Image from '@tiptap/extension-image'
import Placeholder from '@tiptap/extension-placeholder'
import { dailyApi } from '@/services/daily'
import { Bold, Italic, Strikethrough, Heading2, Heading3, List, ListOrdered, Image as ImageIcon } from 'lucide-vue-next'
import { useThemeStore } from '@/stores/theme'
import { storeToRefs } from 'pinia'

const props = defineProps<{ autosaveKey?: string; initialContent?: Record<string, any> | null }>()
const emits = defineEmits<{ (e: 'save', json: Record<string, any>): void; (e: 'cancel'): void }>()

// 中文注释：根据主题动态决定是否启用 prose-invert（仅在深色主题下启用，避免浅色主题文字变浅灰）
const themeStore = useThemeStore()
const { isDark } = storeToRefs(themeStore)
const editorClass = computed(() => [
  'tiptap',
  'ProseMirror',
  'prose', // Tailwind Typography
  'prose-notion',
  isDark.value ? 'prose-invert' : '', // 浅色主题下不加反色类，确保文字为黑色
  'max-w-none',
  'focus:outline-none',
  // Fine-tune: headings weight, paragraph leading, list spacing, image radius/shadow
  'prose-headings:font-semibold',
  'prose-p:leading-7',
  'prose-li:my-0.5',
  'prose-img:rounded-lg',
  'prose-img:shadow-md'
].filter(Boolean).join(' '))

const message = useMessage()
const saving = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)
let autosaveTimer: number | undefined

// 初始化编辑器
const editor = useEditor({
  content: props.initialContent || '',
  extensions: [
    StarterKit,
    Image.configure({ inline: true, allowBase64: true }),
    // Placeholder: Notion-like hint text
    Placeholder.configure({
      placeholder: '输入 “/” 以插入块，或开始输入…',
      includeChildren: true
    })
  ],
  editorProps: {
    attributes: {
      // Attach typography and Notion-like classes on ProseMirror root
      class: editorClass.value
    }
  }
})

// 中文注释：主题切换时，动态更新 ProseMirror 根元素的类名，避免浅色主题文字变灰
watch(isDark, () => {
  try { editor?.value && (editor.value.view.dom.className = editorClass.value) } catch {}
})


function isActive(name: string, attrs: Record<string, any> = {}) {
  return editor?.value?.isActive(name as any, attrs) ?? false
}

function setHeading(level: 1 | 2 | 3 | 4 | 5 | 6) {
  editor?.value?.chain().focus().toggleHeading({ level }).run()
}

function insertImage() {
  fileInputRef.value?.click()
}

async function onFilesSelected(e: Event) {
  const input = e.target as HTMLInputElement
  const files = input.files ? Array.from(input.files) : []
  if (!files.length) return
  try {
    const res = await dailyApi.uploadImages(files)
    const urls = res.files.map(f => f.url).filter(Boolean)
    urls.forEach(url => editor?.value?.chain().focus().setImage({ src: url }).run())
    message.success('图片已插入')
  } catch (err: any) {
    message.error(err?.message || '图片上传失败')
  } finally {
    if (input) input.value = ''
  }
}

function onCancel() {
  emits('cancel')
}

async function onSave() {
  if (!editor?.value) return
  saving.value = true
  try {
    const json = editor.value.getJSON() as Record<string, any>
    emits('save', json)
  } finally {
    saving.value = false
  }
}

// 前端定时保存到本地（不做服务端草稿）
function doAutosave() {
  if (!props.autosaveKey || !editor?.value) return
  const json = editor.value.getJSON()
  try { localStorage.setItem(props.autosaveKey, JSON.stringify(json)) } catch { }
}

onMounted(() => {
  // 恢复本地草稿（若传入 initialContent 则优先生效）
  if (props.initialContent) {
    try { editor?.value?.commands.setContent(props.initialContent, { emitUpdate: false }) } catch { }
  } else if (props.autosaveKey) {
    try {
      const raw = localStorage.getItem(props.autosaveKey)
      if (raw) {
        const json = JSON.parse(raw)
        editor?.value?.commands.setContent(json, { emitUpdate: false })
      }
    } catch { }
  }
  autosaveTimer = window.setInterval(doAutosave, 5000)
})

onUnmounted(() => {
  if (autosaveTimer) window.clearInterval(autosaveTimer)
  editor?.value?.destroy()
})
</script>

<style scoped>
/* 中文注释：编辑器容器采用垂直布局，工具栏与主体分离 */
.daily-editor {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 顶部工具栏：更明显的分隔与层次（玻璃态、粘性、阴影） */
.toolbar {
  position: sticky;
  top: 0;
  z-index: 2;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 10px;
  /* 中文注释：iOS 刘海/安全区适配，防止 sticky 工具栏顶边被遮挡 */
  padding-top: calc(8px + env(safe-area-inset-top));
  border-radius: var(--radius-md);
  border: 1px solid var(--glass-border);
  background: linear-gradient(180deg, color-mix(in oklch, var(--glass-bg) 85%, transparent) 0%, var(--glass-bg) 100%);
  box-shadow:
    0 6px 20px rgba(0, 0, 0, 0.18),
    0 0 0 1px rgba(255, 255, 255, 0.04) inset;
  backdrop-filter: saturate(120%) blur(6px);
}

/* 分组容器：左侧功能分区更显著 */
.toolbar-groups {
  display: flex;
  align-items: center;
  gap: 8px;
}

.group {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 6px;
  border-radius: var(--radius-md);
  border: 1px solid var(--glass-border);
  background: linear-gradient(180deg, color-mix(in oklch, var(--glass-bg) 82%, transparent) 0%, var(--glass-bg) 100%);
  box-shadow: 0 2px 10px rgba(0, 0, 0, .18) inset;
}

.group :deep(.n-button) {
  --btn-radius: 8px;
}

.toolbar-actions {
  display: flex;
  gap: 8px;
}

/* 统一图标盒尺寸，避免不同 SVG 视觉高度不一致 */
.toolbar :deep(.n-button .n-button__icon) {
  width: 20px;
  height: 20px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.toolbar :deep(.n-button .n-button__icon svg) {
  width: 18px !important;
  height: 18px !important;
  display: block;
}

/* 编辑区域：柔和边框+光晕，契合主题 */
.editor-pane {
  min-height: 260px;
  max-height: 52vh;
  /* 中文注释：仅允许纵向滚动，禁止横向溢出以避免移动端偏移 */
  overflow-x: hidden;
  overflow-y: auto;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  padding: 12px;
  box-shadow:
    0 0 0 1px color-mix(in oklch, var(--glass-border) 70%, transparent) inset,
    0 8px 24px rgba(0, 0, 0, 0.25);
  transition: border-color .2s ease, box-shadow .2s ease, background .2s ease;
}

.editor-pane:hover {
  background: var(--glass-bg-strong);
  border-color: var(--border-focus);
}

.editor-pane:focus-within {
  box-shadow:
    0 0 0 2px color-mix(in oklch, var(--primary) 35%, transparent),
    0 0 18px color-mix(in oklch, var(--primary) 22%, transparent),
    0 0 0 1px color-mix(in oklch, var(--glass-border) 70%, transparent) inset;
  /* 兼容性备用（不支持 color-mix 的浏览器）：*/
  /* box-shadow: 0 0 0 2px rgba(170,131,255,.35), 0 0 18px rgba(170,131,255,.2); */
}

.tiptap-content {
  color: var(--text-primary);
}

.tiptap-content :deep(p) {
  margin: 0.5em 0;
}

.tiptap-content {
  display: flex;
  justify-content: center;
}

.tiptap-content :deep(.ProseMirror) {
  width: 100%;
  max-width: 720px;
  margin: 0 auto;
  line-height: 1.75;
  font-size: 15px;
}

/* 中文注释：移动端防止超长URL/英文导致横向溢出 */
.tiptap-content :deep(.ProseMirror) {
  overflow-wrap: anywhere;
  word-break: break-word;
}


.tiptap-content :deep(h1, h2, h3) {
  line-height: 1.25;
  font-weight: 700;
}

.tiptap-content :deep(h1) {
  font-size: 28px;
  margin: 1.2em 0 .6em;
}

.tiptap-content :deep(h2) {
  font-size: 22px;
  margin: 1.1em 0 .5em;
}

.tiptap-content :deep(h3) {
  font-size: 18px;
  margin: 1em 0 .4em;
}

.tiptap-content :deep(blockquote) {
  margin: .8em 0;
  padding: .6em .9em;
  border-left: 3px solid color-mix(in oklch, var(--primary) 40%, white);
  background: color-mix(in oklch, var(--glass-bg) 88%, transparent);
  border-radius: 8px;
}

.tiptap-content :deep(hr) {
  border: none;
  height: 1px;
  background: color-mix(in oklch, var(--glass-border) 80%, transparent);
  margin: 1.2em 0;
}

.tiptap-content :deep(p, ul, ol, blockquote, h1, h2, h3) {
  position: relative;
}

.tiptap-content :deep(p:hover, ul:hover, ol:hover, blockquote:hover, h1:hover, h2:hover, h3:hover)::before {
  content: '⋮⋮';
  position: absolute;
  left: -24px;
  top: .1em;
  font-size: 14px;
  opacity: .35;
  cursor: grab;
  user-select: none;
}

.tiptap-content :deep(ul) {
  list-style: disc outside;
  padding-left: 1.5rem;
  margin: .5em 0;
}

.tiptap-content :deep(ol) {
  list-style: decimal outside;
  padding-left: 1.5rem;
  margin: .5em 0;
}

.tiptap-content :deep(li) {
  margin: .25em 0;
}

.tiptap-content :deep(.ProseMirror:focus),
.tiptap-content :deep(.ProseMirror-focused) {
  outline: none;
}

/* 中文注释：移动端隐藏块级“⋮⋮”拖拽手柄，避免 left:-24px 造成横向溢出；平板缩短偏移 */
@media (max-width: 640px) {
  .tiptap-content :deep(p:hover, ul:hover, ol:hover, blockquote:hover, h1:hover, h2:hover, h3:hover)::before {
    display: none;
  }
}
@media (min-width: 641px) and (max-width: 960px) {
  .tiptap-content :deep(p:hover, ul:hover, ol:hover, blockquote:hover, h1:hover, h2:hover, h3:hover)::before {
    left: -12px;
  }
}

/* 中文注释：占位符样式（Notion 风格的淡色提示） */
.tiptap-content :deep(p.is-editor-empty:first-child::before) {
  content: attr(data-placeholder);
  color: color-mix(in oklch, var(--text-primary) 45%, transparent);
  pointer-events: none;
  height: 0;
  float: left;
}
</style>
