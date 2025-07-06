<template>
  <div class="activity-management">
    <div class="page-header">
      <h1>活动管理</h1>
      <p>管理系统中的所有活动信息</p>
    </div>

    <div class="toolbar">
      <div class="search-section">
        <n-input
          v-model:value="searchQuery"
          placeholder="搜索活动..."
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <n-icon :component="SearchOutline" />
          </template>
        </n-input>
      </div>

      <div class="action-section">
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

    <n-card class="table-card">
      <n-data-table
        :columns="columns"
        :data="filteredActivities"
        :loading="loading"
        :pagination="pagination"
        :row-key="(row) => row.id"
        remote
        striped
      />
    </n-card>

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
              v-model:formatted-value="formData.date"
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
              v-model:formatted-value="editingActivity.date"
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
              :value="editingActivity.participants.map(p => p.id)"
              :options="availableParticipants"
              source-title="可选成员"
              target-title="已选成员"
              style="width: 100%"
              @update:value="handleParticipantsChange"
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
  NCard, NDataTable, NInput, NButton, NIcon, NModal, NForm, NFormItem,
  NDatePicker, NSelect, NSpace, NTag, NPopconfirm, NTransfer, NText,
  NAvatar, NTooltip, NDynamicTags, useMessage, useDialog
} from 'naive-ui'
import {
  SearchOutline,
  AddOutline,
  CreateOutline,
  TrashOutline,
  CalendarOutline,
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
const dialog = useDialog()

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
const formData = ref<ActivityCreateRequest>({
  title: '',
  description: '',
  date: '',
  tags: [],
  participant_ids: []
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
            trigger: () => h(NTag, { size: 'small', type: 'default' }, {
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
    date: '',
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
  showEditModal.value = true
}

// 处理参与者变化
const handleParticipantsChange = (value: number[]) => {
  if (editingActivity.value) {
    // 更新参与者列表
    editingActivity.value.participants = members.value
      .filter(member => value.includes(member.id))
      .map(member => ({
        id: member.id,
        name: member.name,
        avatar_url: member.avatar_url
      }))
  }
}

// 处理编辑提交
const handleEditSubmit = async () => {
  if (!editingActivity.value) return

  try {
    const updateData: ActivityUpdateRequest = {
      title: editingActivity.value.title,
      description: editingActivity.value.description,
      date: editingActivity.value.date,
      tags: editingActivity.value.tags,
      participant_ids: editingActivity.value.participants.map(p => p.id)
    }

    await activityApi.updateActivity(editingActivity.value.id, updateData)
    message.success('活动更新成功')
    showEditModal.value = false
    editingActivity.value = null
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
  max-width: 1400px;
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

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  gap: 24px;
  padding: 20px 24px;
  @include fluent-acrylic(0.9, 20px);
  border-radius: $fluent-border-radius-medium;
  border: 1px solid $fluent-stroke-surface;

  .search-section {
    flex: 1;
    max-width: 400px;
  }

  .action-section {
    display: flex;
    gap: 12px;
    align-items: center;
  }
}

.table-card {
  @include fluent-acrylic(0.9, 30px);
  border-radius: $fluent-border-radius-large;
  border: 1px solid $fluent-stroke-surface;
  @include fluent-depth-shadow(8);
  transition: all $fluent-duration-normal $fluent-easing-standard;

  &:hover {
    @include fluent-depth-shadow(16);
  }

  :deep(.n-card__content) {
    padding: 0;
  }

  :deep(.n-data-table) {
    border-radius: $fluent-border-radius-large;
    overflow: hidden;

    .n-data-table-wrapper {
      border-radius: $fluent-border-radius-large;
    }

    .n-data-table-thead {
      background: $fluent-fill-subtle;
    }

    .n-data-table-th {
      background: $fluent-fill-subtle;
      color: $fluent-text-primary;
      font-weight: 600;
      border-bottom: 1px solid $fluent-stroke-surface;
      font-family: $fluent-font-family;
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
    @include fluent-acrylic(0.95, 40px);
    @include fluent-depth-shadow(32);
  }
}

:deep(.n-tag) {
  border-radius: $fluent-border-radius-small;
  font-weight: 500;
}

:deep(.n-transfer) {
  .n-transfer-list {
    border-radius: $fluent-border-radius-medium;
    border: 1px solid $fluent-stroke-surface;

    .n-transfer-list-header {
      background: $fluent-fill-subtle;
      border-bottom: 1px solid $fluent-stroke-surface;
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
