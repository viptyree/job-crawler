<template>
  <el-card shadow="hover">
    <template #header>
      <div class="card-header">
        <span>平台账号</span>
        <el-button :loading="loading" @click="loadAccounts">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </template>
    <el-table :data="accounts" stripe v-loading="loading" style="width: 100%">
      <el-table-column prop="label" label="平台" width="140" />
      <el-table-column label="状态" width="150">
        <template #default="{ row }">
          <el-tag type="info">{{ statusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="note" label="说明" min-width="260" />
      <el-table-column label="更新时间" width="180">
        <template #default="{ row }">{{ formatTime(row.updated_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="210" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" size="small" link @click="handleOpenLogin(row)">打开登录</el-button>
          <el-button size="small" link @click="handleCheck(row)">检测</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { checkPlatformLogin, getPlatformAccounts, openPlatformLogin } from '@/api/companyIntel.js'

const accounts = ref([])
const loading = ref(false)
const formatTime = (value) => value ? new Date(value).toLocaleString('zh-CN') : '-'
const statusLabel = (status) => ({
  not_configured: '未配置',
  login_window_opened: '已打开登录',
  likely_logged_in: '可能已登录',
  not_logged_in: '未登录',
  browser_missing: '缺浏览器',
  check_failed: '检测失败',
  expired: '已失效',
}[status] || status)

const loadAccounts = async () => {
  loading.value = true
  try {
    accounts.value = await getPlatformAccounts()
  } finally {
    loading.value = false
  }
}

const handleOpenLogin = async (row) => {
  const result = await openPlatformLogin(row.platform)
  ElMessage.success(result.note)
  await loadAccounts()
}

const handleCheck = async (row) => {
  const result = await checkPlatformLogin(row.platform)
  ElMessage.info(result.note)
  await loadAccounts()
}

onMounted(loadAccounts)
</script>

<style scoped>
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;
}
</style>
