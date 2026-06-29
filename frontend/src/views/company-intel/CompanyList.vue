<template>
  <el-card shadow="hover">
    <template #header>
      <div class="card-header">
        <span>公司档案</span>
        <el-button :loading="loading" @click="loadCompanies">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </template>
    <el-table :data="companies" stripe v-loading="loading" style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="公司名称" min-width="220" />
      <el-table-column label="最新评分" width="150">
        <template #default="{ row }">
          <el-tag v-if="row.latest_score" :type="row.latest_score.score >= 80 ? 'success' : 'warning'">
            {{ row.latest_score.score }} / {{ row.latest_score.level }}
          </el-tag>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column label="更新时间" width="180">
        <template #default="{ row }">{{ formatTime(row.updated_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="$router.push(`/company-intel/companies/${row.id}`)">查看</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { getCompanyIntelCompanies } from '@/api/companyIntel.js'

const companies = ref([])
const loading = ref(false)
const formatTime = (value) => value ? new Date(value).toLocaleString('zh-CN') : '-'

const loadCompanies = async () => {
  loading.value = true
  try {
    companies.value = await getCompanyIntelCompanies()
  } finally {
    loading.value = false
  }
}

onMounted(loadCompanies)
</script>

<style scoped>
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;
}
</style>

