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
          <n-button type="primary" @click="handleImportMembers">
            <template #icon>
              <n-icon :component="CloudUploadOutline" />
            </template>
            导入成员数据
          </n-button>
          <n-button @click="handleRefresh">
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
        :data="filteredMembers"
        :loading="loading"
        :pagination="pagination"
        :row-key="(row: any) => row.id"
        size="small"
        striped
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h } from 'vue'
import {
  NButton,
  NIcon,
  NInput,
  NSelect,
  NSpace,
  NDataTable,
  NTag,
  NAvatar,
  useMessage,
  type DataTableColumns
} from 'naive-ui'
import {
  CloudUploadOutline,
  RefreshOutline,
  SearchOutline,
  PersonOutline
} from '@vicons/ionicons5'

// 状态管理
const message = useMessage()
const loading = ref(false)
const searchQuery = ref('')
const roleFilter = ref<string | null>(null)
const statusFilter = ref<string | null>(null)

// 模拟成员数据
const members = ref([
  {
    id: 1,
    uin: '123456789',
    username: 'Alice',
    nickname: 'Alice Chen',
    role: 'admin',
    status: 'active',
    joinTime: '2024-01-15',
    lastActive: '2024-07-06'
  },
  {
    id: 2,
    uin: '987654321',
    username: 'Bob',
    nickname: 'Bob Wang',
    role: 'member',
    status: 'active',
    joinTime: '2024-02-20',
    lastActive: '2024-07-05'
  },
  {
    id: 3,
    uin: '456789123',
    username: 'Charlie',
    nickname: 'Charlie Li',
    role: 'member',
    status: 'inactive',
    joinTime: '2024-03-10',
    lastActive: '2024-06-20'
  }
])

// 筛选选项
const roleOptions = [
  { label: '管理员', value: 'admin' },
  { label: '成员', value: 'member' },
  { label: '访客', value: 'guest' }
]

const statusOptions = [
  { label: '活跃', value: 'active' },
  { label: '非活跃', value: 'inactive' },
  { label: '已禁用', value: 'disabled' }
]

// 分页配置
const pagination = {
  page: 1,
  pageSize: 10,
  showSizePicker: true,
  pageSizes: [10, 20, 50],
  showQuickJumper: true,
  prefix: ({ itemCount }: { itemCount: number }) => `共 ${itemCount} 条`
}

// 表格列配置
const columns: DataTableColumns = [
  {
    title: '头像',
    key: 'avatar',
    width: 80,
    render: (row: any) => h(NAvatar, {
      size: 'small',
      src: `https://api.dicebear.com/7.x/avataaars/svg?seed=${row.uin}`,
      fallbackSrc: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMjAiIGN5PSIyMCIgcj0iMjAiIGZpbGw9IiNGNUY1RjUiLz4KPHBhdGggZD0iTTIwIDIwQzIyLjc2MTQgMjAgMjUgMTcuNzYxNCAyNSAxNUMyNSAxMi4yMzg2IDIyLjc2MTQgMTAgMjAgMTBDMTcuMjM4NiAxMCAxNSAxMi4yMzg2IDE1IDE1QzE1IDE3Ljc2MTQgMTcuMjM4NiAyMCAyMCAyMFoiIGZpbGw9IiNEREREREQiLz4KPHBhdGggZD0iTTEwIDMwQzEwIDI1LjAyOTQgMTQuMDI5NCAyMSAxOSAyMUgyMUMyNS45NzA2IDIxIDMwIDI1LjAyOTQgMzAgMzBWMzBIMTBWMzBaIiBmaWxsPSIjREREREREIi8+Cjwvc3ZnPgo='
    })
  },
  {
    title: 'UIN',
    key: 'uin',
    width: 120
  },
  {
    title: '用户名',
    key: 'username',
    width: 120
  },
  {
    title: '昵称',
    key: 'nickname',
    width: 150
  },
  {
    title: '角色',
    key: 'role',
    width: 100,
    render: (row: any) => {
      const roleMap: Record<string, { type: any, label: string }> = {
        admin: { type: 'success', label: '管理员' },
        member: { type: 'info', label: '成员' },
        guest: { type: 'default', label: '访客' }
      }
      const role = roleMap[row.role] || { type: 'default', label: '未知' }
      return h(NTag, { type: role.type, size: 'small' }, { default: () => role.label })
    }
  },
  {
    title: '状态',
    key: 'status',
    width: 100,
    render: (row: any) => {
      const statusMap: Record<string, { type: any, label: string }> = {
        active: { type: 'success', label: '活跃' },
        inactive: { type: 'warning', label: '非活跃' },
        disabled: { type: 'error', label: '已禁用' }
      }
      const status = statusMap[row.status] || { type: 'default', label: '未知' }
      return h(NTag, { type: status.type, size: 'small' }, { default: () => status.label })
    }
  },
  {
    title: '加入时间',
    key: 'joinTime',
    width: 120
  },
  {
    title: '最后活跃',
    key: 'lastActive',
    width: 120
  },
  {
    title: '操作',
    key: 'actions',
    width: 120,
    render: (row: any) => h(NSpace, { size: 'small' }, {
      default: () => [
        h(NButton, { 
          size: 'small', 
          type: 'primary', 
          text: true,
          onClick: () => handleEdit(row)
        }, { default: () => '编辑' }),
        h(NButton, { 
          size: 'small', 
          type: 'error', 
          text: true,
          onClick: () => handleDelete(row)
        }, { default: () => '删除' })
      ]
    })
  }
]

// 筛选后的成员列表
const filteredMembers = computed(() => {
  let result = members.value
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(member => 
      member.username.toLowerCase().includes(query) ||
      member.nickname.toLowerCase().includes(query) ||
      member.uin.includes(query)
    )
  }
  
  if (roleFilter.value) {
    result = result.filter(member => member.role === roleFilter.value)
  }
  
  if (statusFilter.value) {
    result = result.filter(member => member.status === statusFilter.value)
  }
  
  return result
})

// 处理导入成员
const handleImportMembers = () => {
  message.info('导入成员功能开发中...')
}

// 处理刷新
const handleRefresh = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    message.success('数据已刷新')
  } catch (error) {
    message.error('刷新失败')
  } finally {
    loading.value = false
  }
}

// 处理编辑
const handleEdit = (member: any) => {
  message.info(`编辑成员: ${member.username}`)
}

// 处理删除
const handleDelete = (member: any) => {
  message.warning(`删除成员: ${member.username}`)
}

onMounted(() => {
  // 初始化数据
})
</script>

<style scoped>
.member-management {
  max-width: 1200px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #333;
}

.page-header p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.management-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.actions {
  display: flex;
  gap: 12px;
}

.filters {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

:deep(.n-data-table) {
  border-radius: 8px;
}

:deep(.n-button) {
  border-radius: 6px;
}

:deep(.n-input) {
  border-radius: 6px;
}

:deep(.n-select) {
  border-radius: 6px;
}
</style>
