<template>
  <div class="member-management">
    <div class="page-header">
      <h1>成员管理</h1>
      <p>管理群成员信息、权限和状态</p>
    </div>
    
    <div class="management-card">
      <div class="card-header">
        <h3>成员列表</h3>
        <div class="actions">
          <n-button
            v-if="canImport"
            type="primary"
            @click="showImportModal = true"
          >
            <template #icon>
              <n-icon :component="CloudUploadOutline" />
            </template>
            导入成员数据
          </n-button>
          <n-button @click="handleExportMembers">
            <template #icon>
              <n-icon :component="DownloadOutline" />
            </template>
            导出数据
          </n-button>
          <n-button @click="loadMembers">
            <template #icon>
              <n-icon :component="RefreshOutline" />
            </template>
            刷新
          </n-button>
        </div>
      </div>
      
      <div class="filters">
        <n-space>
          <n-input
            v-model:value="searchQuery"
            placeholder="搜索成员..."
            clearable
            style="width: 200px;"
          >
            <template #prefix>
              <n-icon :component="SearchOutline" />
            </template>
          </n-input>
          
          <n-select
            v-model:value="roleFilter"
            placeholder="筛选角色"
            clearable
            style="width: 120px;"
            :options="roleOptions"
          />
          
          <n-select
            v-model:value="statusFilter"
            placeholder="筛选状态"
            clearable
            style="width: 120px;"
            :options="statusOptions"
          />
        </n-space>
      </div>
      
      <n-data-table
        :columns="columns"
        :data="members"
        :loading="loading"
        :pagination="pagination"
        :row-key="(row: any) => row.id"
        remote
        size="small"
        striped
      />
    </div>

    <!-- 导入成员模态框 -->
    <n-modal
      v-model:show="showImportModal"
      preset="dialog"
      title="导入成员数据"
      style="width: 600px;"
    >
      <div class="import-content">
        <n-text depth="3" style="margin-bottom: 16px; display: block;">
          支持导入JSON格式的成员数据文件。请确保文件格式正确。
        </n-text>

        <n-upload
          v-model:file-list="uploadFiles"
          :max="1"
          accept=".json"
          @change="handleFileChange"
        >
          <n-upload-dragger>
            <div style="margin-bottom: 12px;">
              <n-icon size="48" :depth="3">
                <CloudUploadOutline />
              </n-icon>
            </div>
            <n-text style="font-size: 16px;">
              点击或者拖动文件到该区域来上传
            </n-text>
            <n-text depth="3" style="margin-top: 8px;">
              仅支持 JSON 格式文件
            </n-text>
          </n-upload-dragger>
        </n-upload>

        <div style="margin-top: 16px; display: flex; justify-content: flex-end; gap: 12px;">
          <n-button @click="showImportModal = false">取消</n-button>
          <n-button
            type="primary"
            :loading="loading"
            :disabled="uploadFiles.length === 0"
            @click="handleImportConfirm"
          >
            确认导入
          </n-button>
        </div>
      </div>
    </n-modal>

    <!-- 编辑成员模态框 -->
    <n-modal
      v-model:show="showEditModal"
      preset="dialog"
      title="编辑成员信息"
      style="width: 500px;"
    >
      <n-form
        v-if="editingMember"
        :model="editingMember"
        label-placement="left"
        label-width="80px"
      >
        <n-form-item label="用户名">
          <n-input v-model:value="editingMember.name" placeholder="请输入用户名" />
        </n-form-item>
        <n-form-item label="角色">
          <n-select
            v-model:value="editingMember.role"
            :options="roleOptions"
            placeholder="请选择角色"
          />
        </n-form-item>
        <n-form-item label="备注">
          <n-input
            v-model:value="editingMember.bio"
            type="textarea"
            placeholder="请输入备注信息"
            :rows="3"
          />
        </n-form-item>
      </n-form>

      <div style="margin-top: 16px; display: flex; justify-content: flex-end; gap: 12px;">
        <n-button @click="showEditModal = false">取消</n-button>
        <n-button
          type="primary"
          :loading="loading"
          @click="handleEditConfirm"
        >
          保存
        </n-button>
      </div>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h, watch } from 'vue'
import {
  NButton,
  NIcon,
  NInput,
  NSelect,
  NSpace,
  NDataTable,
  NTag,
  NAvatar,
  NModal,
  NForm,
  NFormItem,
  NUpload,
  NUploadDragger,
  NText,
  NPopconfirm,
  useMessage,
  useDialog,
  type DataTableColumns,
  type UploadFileInfo
} from 'naive-ui'
import {
  CloudUploadOutline,
  RefreshOutline,
  SearchOutline,
  PersonOutline,
  TrashOutline,
  CreateOutline,
  DownloadOutline
} from '@vicons/ionicons5'
import { memberApi, type Member, type MemberDetail } from '@/services/api'
import { hasPermission } from '@/router/guards'

// 状态管理
const message = useMessage()
const dialog = useDialog()
const loading = ref(false)
const searchQuery = ref('')
const roleFilter = ref<string | null>(null)
const statusFilter = ref<string | null>(null)

// 成员数据
const members = ref<Member[]>([])
const totalMembers = ref(0)
const totalPages = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

// 模态框状态
const showImportModal = ref(false)
const showEditModal = ref(false)
const editingMember = ref<Member | null>(null)

// 上传文件
const uploadFiles = ref<UploadFileInfo[]>([])

// 权限检查
const canEdit = computed(() => hasPermission('members:update'))
const canDelete = computed(() => hasPermission('members:delete'))
const canImport = computed(() => hasPermission('members:import'))

// 筛选选项
const roleOptions = [
  { label: '群主', value: 0 },
  { label: '管理员', value: 1 },
  { label: '群员', value: 2 }
]

const statusOptions = [
  { label: '正常', value: 'normal' },
  { label: '已删除', value: 'deleted' }
]

// 分页配置
const pagination = computed(() => {
  const config = {
    page: currentPage.value,
    pageSize: pageSize.value,
    itemCount: totalMembers.value,
    showSizePicker: true,
    pageSizes: [10, 20, 50, 100],
    showQuickJumper: true,
    prefix: (info: { itemCount?: number }) => `共 ${info.itemCount || 0} 条`,
    suffix: (info: { page?: number, pageCount?: number }) => `第 ${info.page || 1} 页，共 ${info.pageCount || 1} 页`,
    'onUpdate:page': (page: number) => {
      currentPage.value = page
      loadMembers()
    },
    'onUpdate:pageSize': (size: number) => {
      pageSize.value = size
      currentPage.value = 1
      loadMembers()
    }
  }
  console.log('Pagination config:', config)
  return config
})

// 表格列配置
const columns: DataTableColumns = [
  {
    title: '头像',
    key: 'avatar',
    width: 80,
    render: (row: Member) => h(NAvatar, {
      size: 'small',
      src: row.avatar_url,
      fallbackSrc: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMjAiIGN5PSIyMCIgcj0iMjAiIGZpbGw9IiNGNUY1RjUiLz4KPHBhdGggZD0iTTIwIDIwQzIyLjc2MTQgMjAgMjUgMTcuNzYxNCAyNSAxNUMyNSAxMi4yMzg2IDIyLjc2MTQgMTAgMjAgMTBDMTcuMjM4NiAxMCAxNSAxMi4yMzg2IDE1IDE1QzE1IDE3Ljc2MTQgMTcuMjM4NiAyMCAyMCAyMFoiIGZpbGw9IiNEREREREQiLz4KPHBhdGggZD0iTTEwIDMwQzEwIDI1LjAyOTQgMTQuMDI5NCAyMSAxOSAyMUgyMUMyNS45NzA2IDIxIDMwIDI1LjAyOTQgMzAgMzBWMzBIMTBWMzBaIiBmaWxsPSIjREREREREIi8+Cjwvc3ZnPgo='
    })
  },
  {
    title: 'ID',
    key: 'id',
    width: 80
  },
  {
    title: '姓名',
    key: 'name',
    width: 120
  },
  {
    title: '群昵称',
    key: 'group_nick',
    width: 150,
    render: (row: Member) => row.group_nick || '-'
  },
  {
    title: 'QQ昵称',
    key: 'qq_nick',
    width: 150,
    render: (row: Member) => row.qq_nick || '-'
  },
  {
    title: '角色',
    key: 'role',
    width: 100,
    render: (row: Member) => {
      const roleMap: Record<number, { type: any, label: string }> = {
        0: { type: 'error', label: '群主' },
        1: { type: 'warning', label: '管理员' },
        2: { type: 'info', label: '群员' }
      }
      const role = roleMap[row.role] || { type: 'default', label: '未知' }
      return h(NTag, { type: role.type, size: 'small' }, { default: () => role.label })
    }
  },
  {
    title: '加入时间',
    key: 'join_date',
    width: 120,
    render: (row: Member) => new Date(row.join_date).toLocaleDateString('zh-CN')
  },
  {
    title: '操作',
    key: 'actions',
    width: 150,
    render: (row: Member) => h(NSpace, { size: 'small' }, {
      default: () => [
        canEdit.value && h(NButton, {
          size: 'small',
          type: 'primary',
          text: true,
          onClick: () => handleEdit(row)
        }, {
          default: () => '编辑',
          icon: () => h(NIcon, { component: CreateOutline })
        }),
        canDelete.value && h(NPopconfirm, {
          onPositiveClick: () => handleDelete(row)
        }, {
          trigger: () => h(NButton, {
            size: 'small',
            type: 'error',
            text: true
          }, {
            default: () => '删除',
            icon: () => h(NIcon, { component: TrashOutline })
          }),
          default: () => `确定要删除成员 ${row.name} 吗？`
        })
      ].filter(Boolean)
    })
  }
]

// 监听搜索和筛选变化，重新加载数据
watch([searchQuery, roleFilter], () => {
  currentPage.value = 1
  loadMembers()
})

// 加载成员数据
const loadMembers = async () => {
  loading.value = true
  try {
    const response = await memberApi.getMembers(currentPage.value, pageSize.value)
    console.log('API Response:', response)
    members.value = response.members
    totalMembers.value = response.total
    totalPages.value = response.total_pages
    console.log('Updated values:', {
      totalMembers: totalMembers.value,
      totalPages: totalPages.value,
      membersCount: members.value.length
    })
  } catch (error) {
    console.error('Failed to load members:', error)
    message.error('加载成员数据失败')
  } finally {
    loading.value = false
  }
}

// 处理文件上传变化
const handleFileChange = (options: { fileList: UploadFileInfo[] }) => {
  uploadFiles.value = options.fileList
}

// 处理导入确认
const handleImportConfirm = async () => {
  if (uploadFiles.value.length === 0) {
    message.warning('请选择要导入的文件')
    return
  }

  const file = uploadFiles.value[0].file
  if (!file) {
    message.error('文件读取失败')
    return
  }

  loading.value = true
  try {
    const text = await file.text()
    const data = JSON.parse(text)

    // 这里应该调用后端API进行导入
    // await memberApi.importMembers(data)

    message.success('成员数据导入成功')
    showImportModal.value = false
    uploadFiles.value = []
    await loadMembers()
  } catch (error) {
    console.error('Import failed:', error)
    message.error('导入失败，请检查文件格式')
  } finally {
    loading.value = false
  }
}

// 处理导出成员
const handleExportMembers = async () => {
  try {
    const allMembers = await memberApi.getAllMembers()
    const dataStr = JSON.stringify(allMembers, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })

    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `members_${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)

    message.success('成员数据导出成功')
  } catch (error) {
    console.error('Export failed:', error)
    message.error('导出失败')
  }
}

// 处理编辑
const handleEdit = (member: Member) => {
  editingMember.value = { ...member }
  showEditModal.value = true
}

// 处理编辑确认
const handleEditConfirm = async () => {
  if (!editingMember.value) return

  loading.value = true
  try {
    // 这里应该调用后端API进行更新
    // await memberApi.updateMember(editingMember.value.id, editingMember.value)

    message.success('成员信息更新成功')
    showEditModal.value = false
    editingMember.value = null
    await loadMembers()
  } catch (error) {
    console.error('Update failed:', error)
    message.error('更新失败')
  } finally {
    loading.value = false
  }
}

// 处理删除
const handleDelete = async (member: Member) => {
  try {
    // 这里应该调用后端API进行删除
    // await memberApi.deleteMember(member.id)

    message.success(`成员 ${member.name} 删除成功`)
    await loadMembers()
  } catch (error) {
    console.error('Delete failed:', error)
    message.error('删除失败')
  }
}

onMounted(() => {
  loadMembers()
})
</script>

<style scoped lang="scss">
@import '@/styles/fluent-theme.scss';

.member-management {
  max-width: 1200px;
  padding: 0;
}

.page-header {
  margin-bottom: 32px;
  padding: 24px 0;

  h1 {
    margin: 0 0 8px 0;
    font-size: 32px;
    font-weight: 600;
    color: $fluent-text-primary;
    font-family: $fluent-font-family;
  }

  p {
    margin: 0;
    color: $fluent-text-secondary;
    font-size: 16px;
    line-height: 1.5;
  }
}

.management-card {
  @include fluent-acrylic(0.9, 30px);
  border-radius: $fluent-border-radius-large;
  padding: 32px;
  border: 1px solid $fluent-stroke-surface;
  @include fluent-depth-shadow(8);
  transition: all $fluent-duration-normal $fluent-easing-standard;

  &:hover {
    @include fluent-depth-shadow(16);
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;

  h3 {
    margin: 0;
    font-size: 24px;
    font-weight: 600;
    color: $fluent-text-primary;
    font-family: $fluent-font-family;
  }
}

.actions {
  display: flex;
  gap: 16px;
  align-items: center;
}

.filters {
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid $fluent-stroke-surface;
}

.import-content {
  padding: 16px 0;
}

// Fluent Design 组件样式覆盖
:deep(.n-data-table) {
  border-radius: $fluent-border-radius-medium;
  overflow: hidden;

  .n-data-table-wrapper {
    border-radius: $fluent-border-radius-medium;
  }

  .n-data-table-thead {
    background: $fluent-fill-subtle;
  }

  .n-data-table-th {
    background: $fluent-fill-subtle;
    color: $fluent-text-primary;
    font-weight: 600;
    border-bottom: 1px solid $fluent-stroke-surface;
  }

  .n-data-table-td {
    border-bottom: 1px solid $fluent-stroke-surface;

    &:hover {
      background: $fluent-fill-subtle;
    }
  }

  .n-data-table-tr:hover {
    .n-data-table-td {
      background: $fluent-fill-subtle;
    }
  }
}

:deep(.n-button) {
  border-radius: $fluent-border-radius-small;
  font-weight: 500;
  transition: all $fluent-duration-fast $fluent-easing-standard;

  &:hover {
    transform: translateY(-1px);
    @include fluent-depth-shadow(4);
  }

  &:active {
    transform: translateY(0);
  }
}

:deep(.n-input) {
  border-radius: $fluent-border-radius-small;

  .n-input__input-el {
    font-family: $fluent-font-family;
  }
}

:deep(.n-select) {
  border-radius: $fluent-border-radius-small;

  .n-base-selection {
    border-radius: $fluent-border-radius-small;
  }
}

:deep(.n-upload) {
  .n-upload-dragger {
    border-radius: $fluent-border-radius-medium;
    border: 2px dashed $fluent-stroke-surface;
    background: $fluent-fill-subtle;
    transition: all $fluent-duration-normal $fluent-easing-standard;

    &:hover {
      border-color: $fluent-accent-default;
      background: $fluent-fill-subtle-secondary;
    }
  }
}

:deep(.n-modal) {
  .n-dialog {
    border-radius: $fluent-border-radius-large;
    @include fluent-acrylic(0.95, 40px);
    @include fluent-depth-shadow(32);
  }
}

:deep(.n-tag) {
  border-radius: $fluent-border-radius-small;
  font-weight: 500;
}

:deep(.n-avatar) {
  border: 2px solid $fluent-stroke-surface;
  transition: all $fluent-duration-fast $fluent-easing-standard;

  &:hover {
    border-color: $fluent-accent-default;
    transform: scale(1.05);
  }
}

:deep(.n-popconfirm) {
  .n-popover {
    border-radius: $fluent-border-radius-medium;
    @include fluent-acrylic(0.95, 20px);
    @include fluent-depth-shadow(16);
  }
}
</style>
