<template>
  <div class="analysis">
    <!-- 筛选器 -->
    <el-card shadow="hover" class="filter-card">
      <el-form :inline="true">
        <el-form-item label="平台">
          <el-select v-model="siteFilter" clearable placeholder="全部平台" style="width: 140px" @change="loadAll">
            <el-option label="BOSS直聘" value="boss" />
            <el-option label="智联招聘" value="zhilian" />
            <el-option label="前程无忧" value="qianchen" />
            <el-option label="拉勾网" value="lagou" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间范围">
          <el-select v-model="daysFilter" style="width: 120px" @change="loadAll">
            <el-option label="最近7天" :value="7" />
            <el-option label="最近30天" :value="30" />
            <el-option label="最近90天" :value="90" />
          </el-select>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 图表区域 -->
    <el-row :gutter="20" style="margin-top: 16px;">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header><span class="chart-title">薪资趋势</span></template>
          <div ref="salaryRef" style="height: 350px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header><span class="chart-title">技能热度 TOP 20</span></template>
          <div ref="skillRef" style="height: 350px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header><span class="chart-title">城市职位分布</span></template>
          <div ref="cityRef" style="height: 350px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header><span class="chart-title">城市平均薪资</span></template>
          <div ref="citySalaryRef" style="height: 350px;"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { getSalaryTrend, getSkillHeatmap, getCityDistribution } from '@/api/stats.js'

const siteFilter = ref('')
const daysFilter = ref(30)

const salaryRef = ref(null)
const skillRef = ref(null)
const cityRef = ref(null)
const citySalaryRef = ref(null)

let charts = []

const initChart = (el) => {
  if (!el) return null
  const chart = echarts.init(el)
  charts.push(chart)
  return chart
}

const loadSalaryTrend = async () => {
  const data = await getSalaryTrend({ site: siteFilter.value || undefined, days: daysFilter.value })
  const chart = initChart(salaryRef.value)
  if (!chart) return

  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['平均薪资', '最低薪资', '最高薪资'] },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: data.map(d => d.date?.slice(5) || ''),
      axisLabel: { color: '#666' },
    },
    yAxis: {
      type: 'value',
      axisLabel: { formatter: v => (v / 1000).toFixed(0) + 'K', color: '#666' },
    },
    series: [
      { name: '平均薪资', type: 'line', smooth: true, data: data.map(d => d.avg_salary), lineStyle: { color: '#409EFF' }, itemStyle: { color: '#409EFF' } },
      { name: '最低薪资', type: 'line', smooth: true, data: data.map(d => d.min_salary), lineStyle: { color: '#67C23A', type: 'dashed' }, itemStyle: { color: '#67C23A' } },
      { name: '最高薪资', type: 'line', smooth: true, data: data.map(d => d.max_salary), lineStyle: { color: '#F56C6C', type: 'dashed' }, itemStyle: { color: '#F56C6C' } },
    ],
  })
}

const loadSkillHeatmap = async () => {
  const data = await getSkillHeatmap({ site: siteFilter.value || undefined, limit: 20 })
  const chart = initChart(skillRef.value)
  if (!chart) return

  const sorted = [...data].reverse()
  chart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '15%', bottom: '3%', containLabel: true },
    xAxis: { type: 'value', axisLabel: { color: '#666' } },
    yAxis: {
      type: 'category',
      data: sorted.map(d => d.skill),
      axisLabel: { color: '#333', fontSize: 12 },
    },
    series: [{
      type: 'bar',
      data: sorted.map(d => d.count),
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: '#409EFF' },
          { offset: 1, color: '#67C23A' },
        ]),
      },
      label: {
        show: true,
        position: 'right',
        formatter: '{c}',
        color: '#666',
      },
    }],
  })
}

const loadCityDist = async () => {
  const data = await getCityDistribution({ site: siteFilter.value || undefined, limit: 15 })

  // 城市职位数量
  const chart1 = initChart(cityRef.value)
  if (chart1) {
    chart1.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
      xAxis: {
        type: 'category',
        data: data.map(d => d.city),
        axisLabel: { rotate: 30, color: '#666' },
      },
      yAxis: { type: 'value', axisLabel: { color: '#666' } },
      series: [{
        type: 'bar',
        data: data.map(d => d.count),
        itemStyle: { color: '#409EFF', borderRadius: [4, 4, 0, 0] },
      }],
    })
  }

  // 城市薪资
  const chart2 = initChart(citySalaryRef.value)
  if (chart2) {
    const salaryData = data.filter(d => d.avg_salary)
    chart2.setOption({
      tooltip: { trigger: 'axis', formatter: params => `${params[0].name}: ${(params[0].value / 1000).toFixed(1)}K` },
      grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
      xAxis: {
        type: 'category',
        data: salaryData.map(d => d.city),
        axisLabel: { rotate: 30, color: '#666' },
      },
      yAxis: {
        type: 'value',
        axisLabel: { formatter: v => (v / 1000).toFixed(0) + 'K', color: '#666' },
      },
      series: [{
        type: 'bar',
        data: salaryData.map(d => d.avg_salary),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#F56C6C' },
            { offset: 1, color: '#E6A23C' },
          ]),
          borderRadius: [4, 4, 0, 0],
        },
      }],
    })
  }
}

const loadAll = async () => {
  // 清空旧图表
  charts.forEach(c => c.dispose())
  charts = []

  try {
    await Promise.all([loadSalaryTrend(), loadSkillHeatmap(), loadCityDist()])
  } catch (e) {
    console.error('加载分析数据失败:', e)
  }
}

const handleResize = () => charts.forEach(c => c.resize())

onMounted(() => {
  loadAll()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  charts.forEach(c => c.dispose())
})
</script>

<style scoped>
.chart-title {
  font-weight: 600;
  font-size: 15px;
}
.filter-card :deep(.el-card__body) {
  padding-bottom: 2px;
}
</style>
