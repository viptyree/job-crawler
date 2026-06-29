<template>
  <div>
    <el-page-header @back="$router.back()" :content="company?.name || '公司详情'" />
    <el-card shadow="hover" class="profile-card" v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>{{ company?.name || '-' }}</span>
          <el-button type="primary" @click="$router.push('/company-intel/search')">继续查询</el-button>
        </div>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="公司ID">{{ company?.id }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatTime(company?.created_at) }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card shadow="hover" class="profile-card">
      <template #header>历史查询</template>
      <el-table :data="company?.queries || []" stripe style="width: 100%">
        <el-table-column prop="id" label="任务ID" width="90" />
        <el-table-column prop="platforms" label="平台" min-width="180">
          <template #default="{ row }">{{ row.platforms.join(', ') }}</template>
        </el-table-column>
        <el-table-column prop="city" label="城市" width="100" />
        <el-table-column prop="keyword" label="关键词" width="130" />
        <el-table-column prop="total_count" label="岗位数" width="90" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }"><el-tag type="success">{{ row.status }}</el-tag></template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" link @click="$router.push(`/company-intel/reports/${row.id}`)">报告</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { getCompanyIntelCompany } from '@/api/companyIntel.js'

const route = useRoute()
const company = ref(null)
const loading = ref(false)
const formatTime = (value) => value ? new Date(value).toLocaleString('zh-CN') : '-'

const loadCompany = async () => {
  loading.value = true
  try {
    company.value = await getCompanyIntelCompany(route.params.id)
  } finally {
    loading.value = false
  }
}

onMounted(loadCompany)
</script>

<style scoped>
.profile-card {
  margin-top: 16px;
}
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;
}
</style>

