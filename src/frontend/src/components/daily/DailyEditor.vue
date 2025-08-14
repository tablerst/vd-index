<template>
  <div class="daily-editor">
    <!-- 工具栏：基础文本样式与插图按钮（置顶粘性，玻璃态卡片，分组+图标） -->
    <div class="toolbar">
      <div class="toolbar-groups">
        <div class="group">
          <n-button quaternary size="small" :disabled="!editor" @click="editor?.chain().focus().toggleBold().run()"
            :type="isActive('bold') ? 'primary' : 'default'" title="加粗">
            <template #icon>
              <n-icon size="16" aria-hidden="true"><svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
                  <path d="M7 5h6a4 4 0 1 1 0 8H7V5zm0 10h7a4 4 0 1 1 0 8H7v-8z" />
                </svg></n-icon>
            </template>
          </n-button>
          <n-button quaternary size="small" :disabled="!editor" @click="editor?.chain().focus().toggleItalic().run()"
            :type="isActive('italic') ? 'primary' : 'default'" title="斜体">
            <template #icon>
              <n-icon size="16"><svg viewBox="0 0 24 20" width="16" height="16" fill="currentColor">
                  <path d="M10 5v2h2.58l-3.16 10H7v2h7v-2h-2.58l3.16-10H17V5z" />
                </svg></n-icon>
            </template>
          </n-button>
          <n-button quaternary size="small" :disabled="!editor" @click="editor?.chain().focus().toggleStrike().run()"
            :type="isActive('strike') ? 'primary' : 'default'" title="删除线">
            <template #icon>
              <n-icon size="16"><svg viewBox="0 0 24 18" width="16" height="16" fill="currentColor">
                  <path
                    d="M4 12h16v2H4zM7 8c0-2.21 2.46-3 5-3 1.73 0 3.41.41 4.5 1.17l-1.5 1.5C13.99 7.25 12.64 7 12 7c-1.81 0-3 .5-3 1 0 .53.56.92 1.76 1.34L9.5 11H7V8zM15 13l-1.5 3H17v-2c0-.76-.86-1.4-2-1z" />
                </svg></n-icon>
            </template>
          </n-button>
        </div>
        <div class="group">
          <n-button quaternary size="small" :disabled="!editor" @click="setHeading(2)"
            :type="isActive('heading', { level: 2 }) ? 'primary' : 'default'" title="二级标题">
            <template #icon>
              <n-icon size="16"><svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
                  <path
                    d="M4 5h2v6h6V5h2v14h-2v-6H6v6H4zM18 19h4v-2h-2.6c.22-.5.84-.92 1.6-1.5.78-.6 1.5-1.34 1.5-2.5 0-1.65-1.35-3-3-3-1.2 0-2.23.67-2.72 1.64l1.78.92c.21-.46.6-.76.94-.76.56 0 1 .45 1 1 0 .54-.52.95-1.22 1.5-.95.75-2.28 1.8-2.28 3.2V19z" />
                </svg></n-icon>
            </template>
          </n-button>
          <n-button quaternary size="small" :disabled="!editor" @click="setHeading(3)"
            :type="isActive('heading', { level: 3 }) ? 'primary' : 'default'" title="三级标题">
            <template #icon>
              <n-icon size="16"><svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
                  <path
                    d="M4 5h2v6h6V5h2v14h-2v-6H6v6H4zM18.5 11c-1.38 0-2.5 1.12-2.5 2.5h2a.5.5 0 1 1 1 0c0 .28-.22.5-.5.5H18v2h.5c.28 0 .5.22.5.5a.5.5 0 1 1-1 0h-2A2.5 2.5 0 1 0 21 14.5 2.5 2.5 0 0 0 18.5 11z" />
                </svg></n-icon>
            </template>
          </n-button>
        </div>
        <div class="group">
          <n-button quaternary size="small" :disabled="!editor"
            @click="editor?.chain().focus().toggleBulletList().run()"
            :type="isActive('bulletList') ? 'primary' : 'default'" title="无序列表">
            <template #icon>
              <n-icon size="16"><svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
                  <path d="M4 7h2v2H4V7zm4 0h12v2H8V7zm-4 6h2v2H4v-2zm4 0h12v2H8v-2zm-4 6h2v2H4v-2zm4 0h12v2H8v-2z" />
                </svg></n-icon>
            </template>
          </n-button>
          <n-button quaternary size="small" :disabled="!editor"
            @click="editor?.chain().focus().toggleOrderedList().run()"
            :type="isActive('orderedList') ? 'primary' : 'default'" title="有序列表">
            <template #icon>
              <n-icon size="16"><svg viewBox="0 0 24 20" width="16" height="16" fill="currentColor">
                  <path
                    d="M4 6h2V4H3v1h1v1zm0 6h2v-2H3v1h1v1zm0 6h2v-2H3v1h1v1zM8 5h12v2H8V5zm0 6h12v2H8v-2zm0 6h12v2H8v-2z" />
                </svg></n-icon>
            </template>
          </n-button>
        </div>
        <div class="group">
          <n-button quaternary size="small" :disabled="!editor" @click="insertImage" title="插入图片">
            <template #icon>
              <n-icon size="16"><svg viewBox="0 0 24 22" width="16" height="16" fill="currentColor">
                  <path d="M21 19V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v14h18zM5 5h14v8l-3-3-4 5-3-4-4 5V5z" />
                </svg></n-icon>
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
import { ref, onMounted, onUnmounted } from 'vue'
import { NButton, NIcon, useMessage } from 'naive-ui'
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Image from '@tiptap/extension-image'
import { dailyApi } from '@/services/daily'

const props = defineProps<{ autosaveKey?: string }>()
const emits = defineEmits<{ (e: 'save', json: Record<string, any>): void; (e: 'cancel'): void }>()

const message = useMessage()
const saving = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)
let autosaveTimer: number | undefined

// 初始化编辑器
const editor = useEditor({
  content: '<p>分享你的日常…</p>',
  extensions: [
    StarterKit,
    Image.configure({ inline: true, allowBase64: true })
  ],
  editorProps: {
    attributes: { class: 'prose prose-invert focus:outline-none' }
  }
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
  // 恢复本地草稿
  if (props.autosaveKey) {
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
  overflow: auto;
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
</style>
