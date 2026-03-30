<template>
  <div class="data-center">
    <!-- 搜索过滤 -->
    <el-card shadow="hover" class="filter-card">
      <el-form :inline="true" :model="filters">
        <el-form-item label="关键词">
          <el-input v-model="filters.keyword" placeholder="职位/公司名称" clearable style="width: 180px" @keyup.enter="search" />
        </el-form-item>
        <el-form-item label="平台">
          <el-select v-model="filters.site" clearable placeholder="全部" style="width: 130px">
            <el-option label="BOSS直聘" value="boss" />
            <el-option label="智联招聘" value="zhilian" />
            <el-option label="前程无忧" value="qianchen" />
            <el-option label="拉勾网" value="lagou" />
          </el-select>
        </el-form-item>
        <el-form-item label="城市">
          <el-input v-model="filters.city" placeholder="城市" clearable style="width: 120px" />
        </el-form-item>
        <el-form-item label="薪资范围">
          <el-input-number v-model="filters.salary_min" :min="0" :step="1000" placeholder="最低" style="width: 120px" />
          <span style="margin: 0 4px;">-</span>
          <el-input-number v-model="filters.salary_max" :min="0" :step="1000" placeholder="最高" style="width: 120px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="search">
            <el-icon><Search /></el-icon> 搜索
          </el-button>
          <el-button @click="resetFilters">重置</el-button>
          <el-button type="success" @click="handleExport">
            <el-icon><Download /></el-icon> 导出
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据表格 -->
    <el-card shadow="hover" style="margin-top: 16px;">
      <template #header>
        <div class="card-header">
          <span>职位数据 (共 {{ total }} 条)</span>
        </div>
      </template>

      <el-table :data="jobs" stripe v-loading="loading" style="width: 100%" @row-click="showDetail">
        <el-table-column prop="title" label="职位" min-width="200">
          <template #default="{ row }">
            <div class="job-title">
              <a :href="row.url" target="_blank" @click.stop>{{ row.title }}</a>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="company_name" label="公司" min-width="150" />
        <el-table-column prop="salary_raw" label="薪资" width="130">
          <template #default="{ row }">
            <span class="salary">{{ row.salary_raw || '面议' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="city" label="城市" width="100" />
        <el-table-column prop="experience" label="经验" width="100" />
        <el-table-column prop="education" label="学历" width="80" />
        <el-table-column prop="source_site" label="来源" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="siteTagType(row.source_site)">
              {{ siteNameMap[row.source_site] || row.source_site }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="技能" min-width="200">
          <template #default="{ row }">
            <el-tag v-for="s in (row.skills || []).slice(0, 4)" :key="s" size="small" type="info" class="skill-tag">
              {{ s }}
            </el-tag>
            <span v-if="(row.skills || []).length > 4" class="more-skills">+{{ row.skills.length - 4 }}</span>
          </template>
        </el-table-column>
        <el-table-column label="时间" width="110">
          <template #default="{ row }">
            <span class="time-text">{{ row.crawled_at?.slice(0, 10) || '-' }}</span>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="filters.page"
          v-model:page-size="filters.page_size"
          :total="total"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="search"
          @current-change="search"
        />
      </div>
    </el-card>

    <!-- 详情抽屉 -->
    <el-drawer v-model="detailVisible" title="职位详情" size="45%">
      <div v-if="detailJob" class="job-detail">
        <h2>{{ detailJob.title }}</h2>
        <div class="detail-meta">
          <el-tag>{{ detailJob.company_name }}</el-tag>
          <el-tag type="success">{{ detailJob.salary_raw || '面议' }}</el-tag>
          <el-tag type="warning">{{ detailJob.city }}</el-tag>
          <el-tag type="info">{{ detailJob.experience }}</el-tag>
          <el-tag type="info">{{ detailJob.education }}</el-tag>
        </div>
        <el-divider />
        <h4>技能要求</h4>
        <div class="skill-list">
          <el-tag v-for="s in (detailJob.skills || [])" :key="s" size="default" class="skill-tag">{{ s }}</el-tag>
          <span v-if="!detailJob.skills?.length" style="color: #c0c4cc;">无</span>
        </div>
        <el-divider />
        <h4>职位描述</h4>
        <pre class="description">{{ detailJob.description || '暂无描述' }}</pre>
        <el-divider />
        <a :href="detailJob.url" target="_blank" class="source-link">
          <el-button type="primary">查看原文</el-button>
        </a>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getJobs, exportJobs } from '@/api/jobs.js'

const jobs = ref([])
const total = ref(0)
const loading = ref(false)
const detailVisible = ref(false)
const detailJob = ref(null)

const siteNameMap = { boss: 'BOSS直聘', zhilian: '智联招聘', qianchen: '前程无忧', lagou: '拉勾网' }
const siteTagType = (site) => ({ boss: '', zhilian: 'success', qianchen: 'warning', lagou: 'danger' }[site] || 'info')

const filters = ref({
  keyword: '',
  site: '',
  city: '',
  salary_min: null,
  salary_max: null,
  page: 1,
  page_size: 20,
})

const search = async () => {
  loading.value = true
  try {
    const params = {}
    for (const [k, v] of Object.entries(filters.value)) {
      if (v !== null && v !== '' && v !== undefined) params[k] = v
    }
    const data = await getJobs(params)
    jobs.value = data.items || []
    total.value = data.total || 0
  } catch (e) {
    console.error(e)
  }
  loading.value = false
}

const resetFilters = () => {
  filters.value = { keyword: '', site: '', city: '', salary_min: null, salary_max: null, page: 1, page_size: 20 }
  search()
}

const showDetail = (row) => {
  detailJob.value = row
  detailVisible.value = true
}

const handleExport = async () => {
  try {
    const params = {}
    if (filters.value.keyword) params.keyword = filters.value.keyword
    if (filters.value.site) params.site = filters.value.site
    if (filters.value.city) params.city = filters.value.city

    const response = await exportJobs(params)
    const url = window.URL.createObjectURL(new Blob([response]))
    const link = document.createElement('a')
    link.href = url
    link.download = 'jobs_export.xlsx'
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (e) {
    ElMessage.error('导出失败')
  }
}

onMounted(search)
</script>

<style scoped>
.filter-card :deep(.el-card__body) {
  padding-bottom: 2px;
}
.card-header {
  font-weight: 600;
}
.job-title a {
  color: #409eff;
  text-decoration: none;
}
.job-title a:hover {
  text-decoration: underline;
}
.salary {
  color: #F56C6C;
  font-weight: 600;
}
.skill-tag {
  margin: 2px;
}
.more-skills {
  color: #909399;
  font-size: 12px;
}
.time-text {
  font-size: 13px;
  color: #909399;
}
.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
.job-detail h2 {
  margin-bottom: 16px;
  color: #303133;
}
.detail-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.skill-list {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin: 8px 0;
}
.description {
  white-space: pre-wrap;
  word-break: break-all;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.8;
  color: #606266;
}
</style>
