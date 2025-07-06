<template>
  <div class="config-management">
    <div class="dashboard-header">
      <h1>配置管理</h1>
      <p>管理系统配置参数和设置</p>
    </div>

    <div class="management-card">
      <div class="card-header">
        <h3>配置列表</h3>
        <div class="actions">
          <n-button @click="handleExportConfigs">
            <template #icon>
              <n-icon :component="DownloadOutline" />
            </template>
            导出配置
          </n-button>
          <n-button @click="loadConfigs">
            <template #icon>
              <n-icon :component="RefreshOutline" />
            </template>
            刷新
          </n-button>
          <n-button
            v-if="canCreate"
            type="primary"
            @click="handleCreateConfig"
          >
            <template #icon>
              <n-icon :component="AddOutline" />
            </template>
            新建配置
          </n-button>
        </div>
      </div>

      <div class="filters">
        <n-space>
          <n-input
            v-model:value="searchQuery"
            placeholder="搜索配置项..."
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
        :data="filteredConfigs"
        :loading="loading"
        :pagination="pagination"
        :row-key="(row) => row.id"
        remote
        size="small"
        striped
      />
    </div>

    <!-- 创建配置模态框 -->
    <n-modal
      v-model:show="showCreateModal"
      preset="dialog"
      title="新建配置项"
      style="width: 600px;"
    >
      <template #default>
        <n-form
          ref="formRef"
          :model="formData"
          :rules="formRules"
          label-placement="left"
          label-width="100px"
        >
          <n-form-item label="配置键" path="key">
            <n-input
              v-model:value="formData.key"
              placeholder="例如: site.title, user.max_count"
            />
          </n-form-item>

          <n-form-item label="配置值" path="value">
            <n-input
              v-model:value="formData.value"
              :type="formData.type === 'json' ? 'textarea' : 'text'"
              placeholder="请输入配置值"
              :rows="formData.type === 'json' ? 4 : 1"
            />
          </n-form-item>

          <n-form-item label="配置描述" path="description">
            <n-input
              v-model:value="formData.description"
              placeholder="请输入配置项的用途描述"
            />
          </n-form-item>

          <n-form-item label="数据类型" path="type">
            <n-select
              v-model:value="formData.type"
              placeholder="选择数据类型"
              :options="typeOptions"
            />
          </n-form-item>

          <n-form-item label="启用状态" path="is_active">
            <n-switch v-model:value="formData.is_active">
              <template #checked>启用</template>
              <template #unchecked>禁用</template>
            </n-switch>
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
            创建配置
          </n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- 编辑配置模态框 -->
    <n-modal
      v-model:show="showEditModal"
      preset="dialog"
      title="编辑配置项"
      style="width: 600px;"
    >
      <template #default>
        <n-form
          v-if="editingConfig"
          ref="editFormRef"
          :model="editingConfig"
          :rules="formRules"
          label-placement="left"
          label-width="100px"
        >
          <n-form-item label="配置键" path="key">
            <n-input
              v-model:value="editingConfig.key"
              placeholder="例如: site.title, user.max_count"
              disabled
            />
          </n-form-item>

          <n-form-item label="配置值" path="value">
            <n-input
              v-model:value="editingConfig.value"
              :type="editingConfig.type === 'json' ? 'textarea' : 'text'"
              placeholder="请输入配置值"
              :rows="editingConfig.type === 'json' ? 4 : 1"
            />
          </n-form-item>

          <n-form-item label="配置描述" path="description">
            <n-input
              v-model:value="editingConfig.description"
              placeholder="请输入配置项的用途描述"
            />
          </n-form-item>

          <n-form-item label="数据类型" path="type">
            <n-select
              v-model:value="editingConfig.type"
              placeholder="选择数据类型"
              :options="typeOptions"
            />
          </n-form-item>

          <n-form-item label="启用状态" path="is_active">
            <n-switch v-model:value="editingConfig.is_active">
              <template #checked>启用</template>
              <template #unchecked>禁用</template>
            </n-switch>
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
  NSelect, NSpace, NTag, NSwitch, NPopconfirm, NText, NTooltip,
  useMessage, useDialog
} from 'naive-ui'
import {
  SearchOutline,
  AddOutline,
  CreateOutline,
  TrashOutline,
  SettingsOutline,
  RefreshOutline,
  DownloadOutline,
  CodeOutline
} from '@vicons/ionicons5'
import type { DataTableColumns } from 'naive-ui'
import {
  configApi,
  type Config,
  type ConfigCreateRequest,
  type ConfigUpdateRequest
} from '@/services/api'
import { hasPermission } from '@/router/guards'

const message = useMessage()
const dialog = useDialog()

// 数据状态
const loading = ref(false)
const configs = ref<Config[]>([])
const searchQuery = ref('')
const showCreateModal = ref(false)
const showEditModal = ref(false)
const editingConfig = ref<Config | null>(null)

// 分页状态
const currentPage = ref(1)
const pageSize = ref(10)
const totalConfigs = ref(0)

// 表单数据
const formRef = ref()
const editFormRef = ref()
const formData = ref<ConfigCreateRequest>({
  key: '',
  value: '',
  description: '',
  type: 'string',
  is_active: true
})

// 权限检查
const canCreate = computed(() => hasPermission('configs:create'))
const canEdit = computed(() => hasPermission('configs:update'))
const canDelete = computed(() => hasPermission('configs:delete'))

// 表单验证规则
const formRules = {
  key: [
    {
      required: true,
      message: '请输入配置键',
      trigger: 'blur'
    },
    {
      pattern: /^[a-zA-Z][a-zA-Z0-9._]*$/,
      message: '配置键只能包含字母、数字、点和下划线，且必须以字母开头',
      trigger: 'blur'
    }
  ],
  value: {
    required: true,
    message: '请输入配置值',
    trigger: 'blur'
  },
  description: {
    required: true,
    message: '请输入配置描述',
    trigger: 'blur'
  },
  type: {
    required: true,
    message: '请选择数据类型',
    trigger: 'change'
  }
}

// 类型选项
const typeOptions = [
  {
    label: '字符串 (String)',
    value: 'string',
    icon: h(NIcon, { component: CodeOutline })
  },
  {
    label: '数字 (Number)',
    value: 'number',
    icon: h(NIcon, { component: CodeOutline })
  },
  {
    label: '布尔值 (Boolean)',
    value: 'boolean',
    icon: h(NIcon, { component: CodeOutline })
  },
  {
    label: 'JSON 对象',
    value: 'json',
    icon: h(NIcon, { component: CodeOutline })
  }
]

// 类型标签映射
const typeTagMap = {
  string: { type: 'default', text: '字符串', color: '#909399' },
  number: { type: 'info', text: '数字', color: '#409eff' },
  boolean: { type: 'success', text: '布尔值', color: '#67c23a' },
  json: { type: 'warning', text: 'JSON', color: '#e6a23c' }
}

// 表格列定义
const columns: DataTableColumns<Config> = [
  {
    title: 'ID',
    key: 'id',
    width: 80
  },
  {
    title: '配置键',
    key: 'key',
    width: 250,
    ellipsis: {
      tooltip: true
    },
    render: (row) => h(NText, {
      code: true,
      style: 'font-family: "Consolas", "Monaco", monospace; font-size: 13px;'
    }, { default: () => row.key })
  },
  {
    title: '配置值',
    key: 'value',
    width: 300,
    ellipsis: {
      tooltip: true
    },
    render: (row) => {
      const maxLength = 60
      const displayValue = row.value.length > maxLength
        ? row.value.substring(0, maxLength) + '...'
        : row.value

      return h(NTooltip, {}, {
        trigger: () => h(NText, {
          code: row.type === 'json',
          style: row.type === 'json'
            ? 'font-family: "Consolas", "Monaco", monospace; font-size: 12px;'
            : 'font-size: 13px;'
        }, { default: () => displayValue }),
        default: () => row.value
      })
    }
  },
  {
    title: '描述',
    key: 'description',
    width: 200,
    ellipsis: {
      tooltip: true
    }
  },
  {
    title: '类型',
    key: 'type',
    width: 100,
    render: (row) => {
      const config = typeTagMap[row.type]
      return h(NTag, {
        type: config.type as any,
        size: 'small'
      }, { default: () => config.text })
    }
  },
  {
    title: '状态',
    key: 'is_active',
    width: 100,
    render: (row) => {
      return h(NTag, {
        type: row.is_active ? 'success' : 'default',
        size: 'small'
      }, {
        default: () => row.is_active ? '启用' : '禁用'
      })
    }
  },
  {
    title: '更新时间',
    key: 'updated_at',
    width: 160,
    render: (row) => new Date(row.updated_at).toLocaleDateString('zh-CN')
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
          default: () => `确认删除配置项 "${row.key}" 吗？`
        })
      ].filter(Boolean)
    })
  }
]

// 分页配置
const pagination = computed(() => ({
  page: currentPage.value,
  pageSize: pageSize.value,
  itemCount: totalConfigs.value,
  showSizePicker: true,
  pageSizes: [10, 20, 50],
  showQuickJumper: true,
  prefix: (info: any) => `共 ${info.itemCount} 条`,
  suffix: (info: { page?: number, pageCount?: number }) => `第 ${info.page || 1} 页，共 ${info.pageCount || 1} 页`,
  'onUpdate:page': (page: number) => {
    currentPage.value = page
    loadConfigs()
  },
  'onUpdate:pageSize': (size: number) => {
    pageSize.value = size
    currentPage.value = 1
    loadConfigs()
  }
}))

// 过滤后的配置列表
const filteredConfigs = computed(() => {
  if (!searchQuery.value) return configs.value

  return configs.value.filter(config =>
    config.key.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    config.description.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    config.value.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1
  loadConfigs()
}

// 加载配置列表
const loadConfigs = async () => {
  loading.value = true
  try {
    const response = await configApi.getConfigs(currentPage.value, pageSize.value)
    configs.value = response.configs
    totalConfigs.value = response.total
  } catch (error) {
    console.error('Failed to load configs:', error)
    message.error('加载配置列表失败')
  } finally {
    loading.value = false
  }
}

// 处理创建配置
const handleCreateConfig = () => {
  formData.value = {
    key: '',
    value: '',
    description: '',
    type: 'string',
    is_active: true
  }
  showCreateModal.value = true
}

// 处理创建提交
const handleCreateSubmit = async () => {
  try {
    await formRef.value?.validate()

    // 验证JSON格式
    if (formData.value.type === 'json') {
      try {
        JSON.parse(formData.value.value)
      } catch {
        message.error('JSON格式不正确，请检查语法')
        return
      }
    }

    await configApi.createConfig(formData.value)
    message.success('配置创建成功')
    showCreateModal.value = false
    await loadConfigs()
  } catch (error) {
    console.error('Create config failed:', error)
    message.error('创建配置失败')
  }
}

// 处理编辑配置
const handleEdit = (config: Config) => {
  editingConfig.value = { ...config }
  showEditModal.value = true
}

// 处理编辑提交
const handleEditSubmit = async () => {
  if (!editingConfig.value) return

  try {
    await editFormRef.value?.validate()

    // 验证JSON格式
    if (editingConfig.value.type === 'json') {
      try {
        JSON.parse(editingConfig.value.value)
      } catch {
        message.error('JSON格式不正确，请检查语法')
        return
      }
    }

    const updateData: ConfigUpdateRequest = {
      value: editingConfig.value.value,
      description: editingConfig.value.description,
      type: editingConfig.value.type,
      is_active: editingConfig.value.is_active
    }

    await configApi.updateConfig(editingConfig.value.id, updateData)
    message.success('配置更新成功')
    showEditModal.value = false
    editingConfig.value = null
    await loadConfigs()
  } catch (error) {
    console.error('Update config failed:', error)
    message.error('更新配置失败')
  }
}

// 处理删除配置
const handleDelete = async (id: number) => {
  try {
    await configApi.deleteConfig(id)
    message.success('配置删除成功')
    await loadConfigs()
  } catch (error) {
    console.error('Delete config failed:', error)
    message.error('删除配置失败')
  }
}

// 处理导出配置
const handleExportConfigs = async () => {
  try {
    const allConfigs = await configApi.getAllConfigs()
    const dataStr = JSON.stringify(allConfigs, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })

    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `configs_${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)

    message.success('配置数据导出成功')
  } catch (error) {
    console.error('Export failed:', error)
    message.error('导出失败')
  }
}

onMounted(() => {
  loadConfigs()
})
</script>

<style scoped lang="scss">
@import '@/styles/fluent-theme.scss';

.config-management {
  padding: 24px;
}

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

:deep(.n-switch) {
  .n-switch__rail {
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
    font-family: "Consolas", "Monaco", monospace;
    font-size: 12px;
    max-width: 400px;
    word-break: break-all;
  }
}

// 代码样式
:deep(.n-text) {
  &[code] {
    background: $fluent-fill-subtle;
    border: 1px solid $fluent-stroke-surface;
    border-radius: $fluent-border-radius-small;
    padding: 2px 6px;
    font-family: "Consolas", "Monaco", "Courier New", monospace;
  }
}
</style>
