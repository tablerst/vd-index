<template>
  <div class="activity-management">
    <div class="dashboard-header">
      <h1>活动管理</h1>
      <p>管理系统中的所有活动信息</p>
    </div>

    <div class="management-card">
      <div class="card-header">
        <h3>活动列表</h3>
        <div class="actions">
          <n-button @click="handleExportActivities">
            <template #icon>
              <n-icon :component="DownloadOutline" />
            </template>
            导出数据
          </n-button>
          <n-button @click="loadActivities">
            <template #icon>
              <n-icon :component="RefreshOutline" />
            </template>
            刷新
          </n-button>
          <n-button
            v-if="canCreate"
            type="primary"
            @click="handleCreateActivity"
          >
            <template #icon>
              <n-icon :component="AddOutline" />
            </template>
            新建活动
          </n-button>
        </div>
      </div>

      <div class="filters">
        <n-space>
          <n-input
            v-model:value="searchQuery"
            placeholder="搜索活动..."
            clearable
            style="width: 200px;"
            @input="handleSearch"
          >
            <template #prefix>
              <n-icon :component="SearchOutline" />
            </template>
          </n-input>
        </n-space>
      </div>

      <n-data-table
        :columns="columns"
        :data="filteredActivities"
        :loading="loading"
        :pagination="pagination"
        :row-key="(row) => row.id"
        remote
        size="small"
        striped
      />
    </div>

    <!-- 创建活动模态框 -->
    <n-modal
      v-model:show="showCreateModal"
      preset="dialog"
      title="新建活动"
      style="width: 700px;"
    >
      <template #default>
        <n-form
          ref="formRef"
          :model="formData"
          :rules="formRules"
          label-placement="left"
          label-width="100px"
        >
          <n-form-item label="活动标题" path="title">
            <n-input
              v-model:value="formData.title"
              placeholder="请输入活动标题"
            />
          </n-form-item>

          <n-form-item label="活动描述" path="description">
            <n-input
              v-model:value="formData.description"
              type="textarea"
              placeholder="请输入活动描述"
              :rows="4"
            />
          </n-form-item>

          <n-form-item label="活动日期" path="date">
            <n-date-picker
              v-model:value="createDateValue"
              type="date"
              placeholder="选择活动日期"
              style="width: 100%"
              format="yyyy-MM-dd"
              value-format="yyyy-MM-dd"
            />
          </n-form-item>

          <n-form-item label="活动标签" path="tags">
            <n-dynamic-tags
              v-model:value="formData.tags"
              placeholder="添加标签"
            />
          </n-form-item>

          <n-form-item label="参与成员" path="participant_ids">
            <n-transfer
              v-model:value="formData.participant_ids"
              :options="availableParticipants"
              source-title="可选成员"
              target-title="已选成员"
              style="width: 100%"
            />
          </n-form-item>
        </n-form>
      </template>

      <template #action>
        <n-space>
          <n-button @click="showCreateModal = false">取消</n-button>
          <n-button
            type="primary"
            :loading="loading"
            @click="handleCreateSubmit"
          >
            创建活动
          </n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- 编辑活动模态框 -->
    <n-modal
      v-model:show="showEditModal"
      preset="dialog"
      title="编辑活动"
      style="width: 700px;"
    >
      <template #default>
        <n-form
          v-if="editingActivity"
          ref="editFormRef"
          :model="editingActivity"
          :rules="formRules"
          label-placement="left"
          label-width="100px"
        >
          <n-form-item label="活动标题" path="title">
            <n-input
              v-model:value="editingActivity.title"
              placeholder="请输入活动标题"
            />
          </n-form-item>

          <n-form-item label="活动描述" path="description">
            <n-input
              v-model:value="editingActivity.description"
              type="textarea"
              placeholder="请输入活动描述"
              :rows="4"
            />
          </n-form-item>

          <n-form-item label="活动日期" path="date">
            <n-date-picker
              v-model:value="editDateValue"
              type="date"
              placeholder="选择活动日期"
              style="width: 100%"
              format="yyyy-MM-dd"
              value-format="yyyy-MM-dd"
            />
          </n-form-item>

          <n-form-item label="活动标签" path="tags">
            <n-dynamic-tags
              v-model:value="editingActivity.tags"
              placeholder="添加标签"
            />
          </n-form-item>

          <n-form-item label="参与成员" path="participant_ids">
            <n-transfer
              v-model:value="editParticipantIds"
              :options="availableParticipants"
              source-title="可选成员"
              target-title="已选成员"
              style="width: 100%"
            />
          </n-form-item>
        </n-form>
      </template>

      <template #action>
        <n-space>
          <n-button @click="showEditModal = false">取消</n-button>
          <n-button
            type="primary"
            :loading="loading"
            @click="handleEditSubmit"
          >
            保存修改
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h } from 'vue'
import {
  NDataTable, NInput, NButton, NIcon, NModal, NForm, NFormItem,
  NDatePicker, NSpace, NTag, NPopconfirm, NTransfer, NText,
  NTooltip, NDynamicTags, useMessage
} from 'naive-ui'
import {
  SearchOutline,
  AddOutline,
  CreateOutline,
  TrashOutline,
  PeopleOutline,
  RefreshOutline,
  DownloadOutline
} from '@vicons/ionicons5'
import type { DataTableColumns } from 'naive-ui'
import {
  activityApi,
  memberApi,
  type Activity,
  type ActivityCreateRequest,
  type ActivityUpdateRequest,
  type Member
} from '@/services/api'
import { hasPermission } from '@/router/guards'

const message = useMessage()
// const dialog = useDialog()

// 数据状态
const loading = ref(false)
const activities = ref<Activity[]>([])
const members = ref<Member[]>([])
const searchQuery = ref('')
const showCreateModal = ref(false)
const showEditModal = ref(false)
const editingActivity = ref<Activity | null>(null)

// 分页状态
const currentPage = ref(1)
const pageSize = ref(10)
const totalActivities = ref(0)

// 表单数据
const formRef = ref()
const editFormRef = ref()
const formData = ref<ActivityCreateRequest>({
  title: '',
  description: '',
  date: '',
  tags: [],
  participant_ids: []
})

// 编辑表单的参与者ID列表
const editParticipantIds = ref<(string | number)[]>([])

// 创建表单的日期值（用于日期选择器）
const createDateValue = computed({
  get: () => {
    return formData.value.date ? new Date(formData.value.date).getTime() : null
  },
  set: (value: number | null) => {
    if (value) {
      formData.value.date = new Date(value).toISOString().split('T')[0]
    } else {
      formData.value.date = ''
    }
  }
})

// 编辑表单的日期值（用于日期选择器）
const editDateValue = computed({
  get: () => {
    return editingActivity.value?.date ? new Date(editingActivity.value.date).getTime() : null
  },
  set: (value: number | null) => {
    if (editingActivity.value) {
      if (value) {
        editingActivity.value.date = new Date(value).toISOString().split('T')[0]
      } else {
        editingActivity.value.date = ''
      }
    }
  }
})

// 参与者选择
const availableParticipants = computed(() =>
  members.value.map(member => ({
    label: member.name,
    value: member.id,
    disabled: false
  }))
)

// 权限检查
const canCreate = computed(() => hasPermission('activities:create'))
const canEdit = computed(() => hasPermission('activities:update'))
const canDelete = computed(() => hasPermission('activities:delete'))

// 表单验证规则
const formRules = {
  title: {
    required: true,
    message: '请输入活动标题',
    trigger: 'blur'
  },
  description: {
    required: true,
    message: '请输入活动描述',
    trigger: 'blur'
  },
  date: {
    required: true,
    message: '请选择活动日期',
    trigger: 'blur'
  }
}

// 表格列定义
const columns: DataTableColumns<Activity> = [
  {
    title: 'ID',
    key: 'id',
    width: 80
  },
  {
    title: '活动标题',
    key: 'title',
    ellipsis: {
      tooltip: true
    }
  },
  {
    title: '活动描述',
    key: 'description',
    ellipsis: {
      tooltip: true
    },
    width: 200
  },
  {
    title: '活动日期',
    key: 'date',
    width: 120,
    render: (row) => activityApi.formatDate(row.date)
  },
  {
    title: '标签',
    key: 'tags',
    width: 150,
    render: (row) => h(NSpace, { size: 'small' }, {
      default: () => row.tags.slice(0, 2).map(tag =>
        h(NTag, { size: 'small', type: 'info' }, { default: () => tag })
      ).concat(
        row.tags.length > 2 ? [
          h(NTooltip, {}, {
            trigger: () => h(NTag, {
              size: 'small',
              type: 'warning',
              class: 'tag-more'
            }, {
              default: () => `+${row.tags.length - 2}`
            }),
            default: () => row.tags.slice(2).join(', ')
          })
        ] : []
      )
    })
  },
  {
    title: '参与人数',
    key: 'participants_total',
    width: 100,
    render: (row) => h(NSpace, { size: 'small', align: 'center' }, {
      default: () => [
        h(NIcon, { component: PeopleOutline, size: 16 }),
        h(NText, {}, { default: () => row.participants_total })
      ]
    })
  },
  {
    title: '创建时间',
    key: 'created_at',
    width: 120,
    render: (row) => new Date(row.created_at).toLocaleDateString('zh-CN')
  },
  {
    title: '操作',
    key: 'actions',
    width: 150,
    render: (row) => h(NSpace, { size: 'small' }, {
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
          onPositiveClick: () => handleDelete(row.id)
        }, {
          trigger: () => h(NButton, {
            size: 'small',
            type: 'error',
            text: true
          }, {
            default: () => '删除',
            icon: () => h(NIcon, { component: TrashOutline })
          }),
          default: () => `确认删除活动 "${row.title}" 吗？`
        })
      ].filter(Boolean)
    })
  }
]

// 分页配置
const pagination = computed(() => ({
  page: currentPage.value,
  pageSize: pageSize.value,
  itemCount: totalActivities.value,
  showSizePicker: true,
  pageSizes: [10, 20, 50],
  showQuickJumper: true,
  prefix: (info: any) => `共 ${info.itemCount} 条`,
  suffix: (info: { page?: number, pageCount?: number }) => `第 ${info.page || 1} 页，共 ${info.pageCount || 1} 页`,
  'onUpdate:page': (page: number) => {
    currentPage.value = page
    loadActivities()
  },
  'onUpdate:pageSize': (size: number) => {
    pageSize.value = size
    currentPage.value = 1
    loadActivities()
  }
}))

// 过滤后的活动列表
const filteredActivities = computed(() => {
  if (!searchQuery.value) return activities.value

  return activities.value.filter(activity =>
    activity.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    activity.description.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    activity.tags.some(tag => tag.toLowerCase().includes(searchQuery.value.toLowerCase()))
  )
})

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1
  loadActivities()
}

// 加载活动列表
const loadActivities = async () => {
  loading.value = true
  try {
    const response = await activityApi.getActivities(currentPage.value, pageSize.value)
    activities.value = response.activities
    totalActivities.value = response.total
  } catch (error) {
    console.error('Failed to load activities:', error)
    message.error('加载活动列表失败')
  } finally {
    loading.value = false
  }
}

// 加载成员列表
const loadMembers = async () => {
  try {
    members.value = await memberApi.getAllMembers()
  } catch (error) {
    console.error('Failed to load members:', error)
    message.error('加载成员列表失败')
  }
}

// 处理创建活动
const handleCreateActivity = () => {
  formData.value = {
    title: '',
    description: '',
    date: '', // 空字符串，通过计算属性转换为null
    tags: [],
    participant_ids: []
  }
  showCreateModal.value = true
}

// 处理创建提交
const handleCreateSubmit = async () => {
  try {
    await formRef.value?.validate()

    await activityApi.createActivity(formData.value)
    message.success('活动创建成功')
    showCreateModal.value = false
    await loadActivities()
  } catch (error) {
    console.error('Create activity failed:', error)
    message.error('创建活动失败')
  }
}

// 处理编辑活动
const handleEdit = (activity: Activity) => {
  editingActivity.value = { ...activity }
  // 设置编辑表单的参与者ID列表
  editParticipantIds.value = activity.participants.map(p => p.id)
  showEditModal.value = true
}

// 处理编辑提交
const handleEditSubmit = async () => {
  if (!editingActivity.value) return

  try {
    await editFormRef.value?.validate()

    const updateData: ActivityUpdateRequest = {
      title: editingActivity.value.title,
      description: editingActivity.value.description,
      date: editingActivity.value.date,
      tags: editingActivity.value.tags,
      participant_ids: editParticipantIds.value.map(id => Number(id))
    }

    await activityApi.updateActivity(editingActivity.value.id, updateData)
    message.success('活动更新成功')
    showEditModal.value = false
    editingActivity.value = null
    editParticipantIds.value = []
    await loadActivities()
  } catch (error) {
    console.error('Update activity failed:', error)
    message.error('更新活动失败')
  }
}

// 处理删除活动
const handleDelete = async (id: number) => {
  try {
    await activityApi.deleteActivity(id)
    message.success('活动删除成功')
    await loadActivities()
  } catch (error) {
    console.error('Delete activity failed:', error)
    message.error('删除活动失败')
  }
}

// 处理导出活动
const handleExportActivities = async () => {
  try {
    const allActivities = await activityApi.getAllActivities()
    const dataStr = JSON.stringify(allActivities, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })

    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `activities_${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)

    message.success('活动数据导出成功')
  } catch (error) {
    console.error('Export failed:', error)
    message.error('导出失败')
  }
}

onMounted(async () => {
  await Promise.all([
    loadActivities(),
    loadMembers()
  ])
})
</script>

<style scoped lang="scss">
@import '@/styles/fluent-theme.scss';

.activity-management {
  padding: 24px;

  .dashboard-header {
    margin-bottom: 24px;

    h1 {
      margin: 0 0 8px 0;
      font-size: 28px;
      font-weight: 600;
      color: #FFFFFF;
    }

    p {
      margin: 0;
      color: rgba(255, 255, 255, 0.7);
      font-size: 16px;
    }
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
    color: #FFFFFF; // 修复深色主题下的文字颜色
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

// Fluent Design 组件样式覆盖
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

  // 表格操作按钮样式优化
  &.n-button--small-type {
    min-width: 60px; // 增加最小宽度
    padding: 0 12px; // 增加内边距

    &.n-button--text-type {
      min-width: 50px;
      padding: 0 8px;
    }
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

:deep(.n-date-picker) {
  border-radius: $fluent-border-radius-small;

  .n-input {
    border-radius: $fluent-border-radius-small;
  }
}

:deep(.n-modal) {
  .n-dialog {
    border-radius: $fluent-border-radius-large;
    @include fluent-modal-acrylic(0.15, 24px);
    @include fluent-depth-shadow(32);

    // 确保文字可读性
    color: rgba(255, 255, 255, 0.95) !important;

    .n-dialog__title {
      color: rgba(255, 255, 255, 0.95) !important;
      font-weight: 600;
    }

    .n-dialog__content {
      color: rgba(255, 255, 255, 0.9) !important;
    }
  }

  // 增强遮罩层
  .n-modal-mask {
    background-color: rgba(0, 0, 0, 0.6) !important;
  }
}

:deep(.n-tag) {
  border-radius: 6px;
  font-weight: 500;

  // 确保所有标签都使用深色主题
  &:not(.tag-more) {
    background: rgba(255, 255, 255, 0.1) !important;
    color: rgba(255, 255, 255, 0.9) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;

    &:hover {
      background: rgba(255, 255, 255, 0.15) !important;
      color: rgba(255, 255, 255, 0.95) !important;
      border-color: rgba(255, 255, 255, 0.3) !important;
    }
  }

  // 省略标签样式优化
  &.tag-more {
    background: rgba(255, 255, 255, 0.1) !important;
    color: rgba(255, 255, 255, 0.8) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;

    &:hover {
      background: rgba(255, 255, 255, 0.15) !important;
      color: rgba(255, 255, 255, 0.9) !important;
      border-color: rgba(255, 255, 255, 0.3) !important;
    }
  }

  // 特定类型标签的深色主题适配
  &.n-tag--info-type {
    background: rgba(63, 125, 251, 0.2) !important;
    color: #3F7DFB !important;
    border: 1px solid rgba(63, 125, 251, 0.4) !important;
  }

  &.n-tag--warning-type {
    background: rgba(255, 176, 32, 0.2) !important;
    color: #FFB020 !important;
    border: 1px solid rgba(255, 176, 32, 0.4) !important;
  }

  &.n-tag--success-type {
    background: rgba(212, 222, 199, 0.2) !important;
    color: #D4DEC7 !important;
    border: 1px solid rgba(212, 222, 199, 0.4) !important;
  }

  &.n-tag--error-type {
    background: rgba(255, 65, 80, 0.2) !important;
    color: #FF4150 !important;
    border: 1px solid rgba(255, 65, 80, 0.4) !important;
  }
}

:deep(.n-transfer) {
  .n-transfer-list {
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    background: rgba(255, 255, 255, 0.08) !important;

    .n-transfer-list-header {
      background: rgba(255, 255, 255, 0.12) !important;
      border-bottom: 1px solid rgba(255, 255, 255, 0.15) !important;
      color: rgba(255, 255, 255, 0.9) !important;
    }

    .n-transfer-list-body {
      background: transparent !important;
    }

    .n-transfer-list-item {
      color: rgba(255, 255, 255, 0.8) !important;

      &:hover {
        background: rgba(255, 255, 255, 0.08) !important;
      }

      &.n-transfer-list-item--pending {
        background: rgba(170, 131, 255, 0.1) !important;
        color: rgba(255, 255, 255, 0.9) !important;
      }
    }
  }

  .n-transfer-list-gap {
    .n-button {
      background: rgba(255, 255, 255, 0.08) !important;
      border: 1px solid rgba(255, 255, 255, 0.15) !important;
      color: rgba(255, 255, 255, 0.7) !important;

      &:hover {
        background: rgba(255, 255, 255, 0.12) !important;
        color: rgba(255, 255, 255, 0.9) !important;
      }
    }
  }
}

:deep(.n-dynamic-tags) {
  .n-dynamic-tags-input {
    border-radius: $fluent-border-radius-small;
  }
}

:deep(.n-popconfirm) {
  .n-popover {
    border-radius: $fluent-border-radius-medium;
    @include fluent-acrylic(0.95, 20px);
    @include fluent-depth-shadow(16);
  }
}

:deep(.n-tooltip) {
  .n-tooltip__content {
    border-radius: $fluent-border-radius-small;
    @include fluent-acrylic(0.95, 10px);
  }
}
</style>
