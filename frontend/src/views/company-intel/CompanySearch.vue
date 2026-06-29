<template>
  <div class="company-intel-page">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>公司查询</span>
          <el-button :loading="loading" type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            开始查询
          </el-button>
        </div>
      </template>

      <el-form :model="form" label-width="90px" class="search-form">
        <el-form-item label="公司名称" required>
          <el-input v-model="form.company_name" placeholder="例如：广州云启未来科技有限公司" clearable @blur="loadAliases" />
        </el-form-item>
        <el-form-item label="查询平台">
          <el-checkbox-group v-model="form.platforms">
            <el-checkbox v-for="item in platforms" :key="item.value" :label="item.value">{{ item.label }}</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="城市">
          <el-input v-model="form.city" placeholder="可选，例如：广州" clearable />
        </el-form-item>
        <el-form-item label="岗位关键词">
          <el-input v-model="form.keyword" placeholder="可选，例如：销售经理" clearable />
        </el-form-item>
        <el-form-item label="查询模式">
          <el-radio-group v-model="form.search_mode">
            <el-radio-button label="mock">模拟数据</el-radio-button>
            <el-radio-button label="real_with_mock_fallback">真实优先</el-radio-button>
            <el-radio-button label="real">仅真实</el-radio-button>
          </el-radio-group>
        </el-form-item>
      </el-form>

      <el-alert v-if="aliases.length" title="搜索别名" type="info" :closable="false" class="alias-box">
        <el-tag v-for="alias in aliases" :key="alias" style="margin-right: 8px;">{{ alias }}</el-tag>
      </el-alert>
    </el-card>

    <el-row v-if="score" :gutter="16" class="result-row">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="score-box">
            <div class="score">{{ score.score }}</div>
            <el-tag :type="score.score >= 80 ? 'success' : score.score >= 50 ? 'warning' : 'info'">{{ score.level }}</el-tag>
          </div>
        </el-card>
      </el-col>
      <el-col :span="18">
        <el-card shadow="hover">
          <div class="reason">{{ score.reason_text }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card v-if="jobs.length" shadow="hover" class="result-row">
      <template #header>
        <div class="card-header">
          <span>岗位结果</span>
          <el-button @click="goReport">查看报告</el-button>
        </div>
      </template>
      <el-table :data="jobs" stripe style="width: 100%">
        <el-table-column prop="platform" label="平台" width="110" />
        <el-table-column prop="job_title" label="岗位" min-width="180" />
        <el-table-column prop="city" label="城市" width="100" />
        <el-table-column prop="salary_raw" label="薪资" width="110" />
        <el-table-column prop="experience" label="经验" width="110" />
        <el-table-column prop="education" label="学历" width="100" />
        <el-table-column prop="match_type" label="匹配" width="100" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  generateAliases,
  getCompanyIntelJobs,
  getCompanyIntelQueryScore,
  getPlatforms,
  searchCompanyIntel,
} from '@/api/companyIntel.js'

const router = useRouter()
const platforms = ref([])
const aliases = ref([])
const jobs = ref([])
const score = ref(null)
const loading = ref(false)
const lastQueryId = ref(null)
const form = ref({
  company_name: '',
  platforms: ['boss', 'zhilian', 'job51', 'lagou'],
  city: '',
    keyword: '',
    search_mode: 'mock',
})

const loadPlatforms = async () => {
  platforms.value = await getPlatforms()
}

const loadAliases = async () => {
  if (!form.value.company_name.trim()) return
  const data = await generateAliases(form.value.company_name.trim())
  aliases.value = data.aliases
}

const handleSearch = async () => {
  if (!form.value.company_name.trim()) {
    ElMessage.warning('请输入公司名称')
    return
  }
  loading.value = true
  try {
    await loadAliases()
    const result = await searchCompanyIntel({ ...form.value, company_name: form.value.company_name.trim() })
    lastQueryId.value = result.query_id
    jobs.value = await getCompanyIntelJobs(result.query_id)
    score.value = await getCompanyIntelQueryScore(result.query_id)
    ElMessage.success('查询完成')
  } finally {
    loading.value = false
  }
}

const goReport = () => {
  if (lastQueryId.value) router.push(`/company-intel/reports/${lastQueryId.value}`)
}

onMounted(loadPlatforms)
</script>

<style scoped>
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;
}
.search-form {
  max-width: 760px;
}
.alias-box,
.result-row {
  margin-top: 16px;
}
.score-box {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  min-height: 72px;
}
.score {
  font-size: 38px;
  font-weight: 700;
  color: #409eff;
}
.reason {
  min-height: 72px;
  display: flex;
  align-items: center;
  color: #606266;
  line-height: 1.7;
}
</style>
