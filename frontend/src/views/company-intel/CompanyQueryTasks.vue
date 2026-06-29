<template>
  <el-card shadow="hover">
    <template #header>
      <div class="card-header">
        <span>查询任务</span>
        <el-button :loading="loading" @click="loadQueries">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </template>
    <el-table :data="queries" stripe v-loading="loading" style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="company_name" label="公司" min-width="220" />
      <el-table-column prop="platforms" label="平台" min-width="180">
        <template #default="{ row }">{{ row.platforms.join(', ') }}</template>
      </el-table-column>
      <el-table-column prop="city" label="城市" width="100" />
      <el-table-column prop="keyword" label="关键词" width="130" />
      <el-table-column prop="total_count" label="岗位数" width="90" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'success' ? 'success' : row.status === 'failed' ? 'danger' : 'warning'">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" width="180">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="$router.push(`/company-intel/reports/${row.id}`)">查看结果</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { getCompanyIntelQueries } from '@/api/companyIntel.js'

const queries = ref([])
const loading = ref(false)
const formatTime = (value) => value ? new Date(value).toLocaleString('zh-CN') : '-'

const loadQueries = async () => {
  loading.value = true
  try {
    queries.value = await getCompanyIntelQueries()
  } finally {
    loading.value = false
  }
}

onMounted(loadQueries)
</script>

<style scoped>
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;
}
</style>

