<template>
  <div>
    <el-page-header @back="$router.back()" content="招聘报告" />
    <el-row :gutter="16" class="report-row">
      <el-col :span="8">
        <el-card shadow="hover" v-loading="loading">
          <template #header>任务信息</template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="公司">{{ query?.company_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="平台">{{ query?.platforms?.join(', ') || '-' }}</el-descriptions-item>
            <el-descriptions-item label="城市">{{ query?.city || '-' }}</el-descriptions-item>
            <el-descriptions-item label="岗位数">{{ query?.total_count ?? '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
      <el-col :span="16">
        <el-card shadow="hover" v-loading="loading">
          <template #header>
            <div class="card-header">
              <span>活跃度评分</span>
              <el-button type="primary" @click="exportCompanyIntelQuery(queryId)">
                <el-icon><Download /></el-icon>
                导出 Excel
              </el-button>
            </div>
          </template>
          <div v-if="score" class="score-line">
            <span class="score">{{ score.score }}</span>
            <el-tag :type="score.score >= 80 ? 'success' : score.score >= 50 ? 'warning' : 'info'">{{ score.level }}</el-tag>
            <span class="reason">{{ score.reason_text }}</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="hover" class="report-row">
      <template #header>岗位明细</template>
      <el-table :data="jobs" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="platform" label="平台" width="110" />
        <el-table-column prop="job_title" label="岗位" min-width="180" />
        <el-table-column prop="city" label="城市" width="100" />
        <el-table-column prop="salary_raw" label="薪资" width="110" />
        <el-table-column prop="experience" label="经验" width="110" />
        <el-table-column prop="education" label="学历" width="100" />
        <el-table-column prop="source_url" label="链接" min-width="220" show-overflow-tooltip />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import {
  exportCompanyIntelQuery,
  getCompanyIntelJobs,
  getCompanyIntelQuery,
  getCompanyIntelQueryScore,
} from '@/api/companyIntel.js'

const route = useRoute()
const queryId = route.params.queryId
const query = ref(null)
const jobs = ref([])
const score = ref(null)
const loading = ref(false)

const loadReport = async () => {
  loading.value = true
  try {
    query.value = await getCompanyIntelQuery(queryId)
    jobs.value = await getCompanyIntelJobs(queryId)
    score.value = await getCompanyIntelQueryScore(queryId)
  } finally {
    loading.value = false
  }
}

onMounted(loadReport)
</script>

<style scoped>
.report-row {
  margin-top: 16px;
}
.card-header,
.score-line {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}
.card-header {
  font-weight: 600;
}
.score {
  font-size: 36px;
  font-weight: 700;
  color: #409eff;
}
.reason {
  flex: 1;
  color: #606266;
}
</style>

