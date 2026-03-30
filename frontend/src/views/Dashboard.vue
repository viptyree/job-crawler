<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="6" v-for="card in statCards" :key="card.label">
        <el-card shadow="hover" class="stat-card" :body-style="{ padding: '20px' }">
          <div class="stat-card-inner">
            <div class="stat-info">
              <div class="stat-label">{{ card.label }}</div>
              <div class="stat-value" :style="{ color: card.color }">{{ card.value }}</div>
            </div>
            <div class="stat-icon" :style="{ backgroundColor: card.color + '15' }">
              <el-icon :size="28" :style="{ color: card.color }"><component :is="card.icon" /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表行 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="16">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>最近7天数据趋势</span>
              <el-tag size="small" type="info">日新增职位</el-tag>
            </div>
          </template>
          <div ref="trendChartRef" style="height: 320px;"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>平台分布</span>
            </div>
          </template>
          <div ref="pieChartRef" style="height: 320px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快捷操作 -->
    <el-row :gutter="20" class="quick-actions">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>快捷操作</span>
            </div>
          </template>
          <div class="action-buttons">
            <el-button type="primary" size="large" @click="$router.push('/rules')">
              <el-icon><Setting /></el-icon>
              配置爬虫规则
            </el-button>
            <el-button type="success" size="large" @click="$router.push('/tasks')">
              <el-icon><VideoPlay /></el-icon>
              查看任务状态
            </el-button>
            <el-button type="warning" size="large" @click="$router.push('/data')">
              <el-icon><Coin /></el-icon>
              浏览职位数据
            </el-button>
            <el-button type="danger" size="large" @click="$router.push('/analysis')">
              <el-icon><TrendCharts /></el-icon>
              行业分析报告
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { getDashboard } from '@/api/stats.js'
import * as echarts from 'echarts'

const stats = ref({
  total_jobs: 0,
  today_new: 0,
  total_companies: 0,
  active_rules: 0,
  running_tasks: 0,
  site_distribution: {},
  recent_trend: [],
})

const statCards = computed(() => [
  { label: '总职位数', value: stats.value.total_jobs.toLocaleString(), icon: 'Coin', color: '#409EFF' },
  { label: '今日新增', value: stats.value.today_new.toLocaleString(), icon: 'Plus', color: '#67C23A' },
  { label: '公司总数', value: stats.value.total_companies.toLocaleString(), icon: 'OfficeBuilding', color: '#E6A23C' },
  { label: '活跃规则', value: stats.value.active_rules, icon: 'Setting', color: '#F56C6C' },
])

const trendChartRef = ref(null)
const pieChartRef = ref(null)
let trendChart = null
let pieChart = null

const siteNameMap = {
  boss: 'BOSS直聘',
  zhilian: '智联招聘',
  qianchen: '前程无忧',
  lagou: '拉勾网',
}

const initCharts = () => {
  // 趋势图
  if (trendChartRef.value) {
    trendChart = echarts.init(trendChartRef.value)
    const trend = stats.value.recent_trend || []
    trendChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        data: trend.map(d => d.date?.slice(5) || ''),
        axisLine: { lineStyle: { color: '#ddd' } },
        axisLabel: { color: '#666' },
      },
      yAxis: {
        type: 'value',
        axisLine: { show: false },
        splitLine: { lineStyle: { color: '#f0f0f0' } },
        axisLabel: { color: '#666' },
      },
      series: [{
        name: '新增职位',
        type: 'line',
        smooth: true,
        data: trend.map(d => d.count || 0),
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64,158,255,0.3)' },
            { offset: 1, color: 'rgba(64,158,255,0.02)' },
          ]),
        },
        lineStyle: { color: '#409EFF', width: 2 },
        itemStyle: { color: '#409EFF' },
      }],
    })
  }

  // 饼图
  if (pieChartRef.value) {
    pieChart = echarts.init(pieChartRef.value)
    const dist = stats.value.site_distribution || {}
    const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399']
    const data = Object.entries(dist).map(([key, val], i) => ({
      name: siteNameMap[key] || key,
      value: val,
      itemStyle: { color: colors[i % colors.length] },
    }))
    // 如果没数据，显示占位
    const chartData = data.length > 0 ? data : [
      { name: 'BOSS直聘', value: 0, itemStyle: { color: '#409EFF' } },
      { name: '智联招聘', value: 0, itemStyle: { color: '#67C23A' } },
      { name: '前程无忧', value: 0, itemStyle: { color: '#E6A23C' } },
      { name: '拉勾网', value: 0, itemStyle: { color: '#F56C6C' } },
    ]
    pieChart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
      legend: { bottom: '5%', left: 'center' },
      series: [{
        type: 'pie',
        radius: ['40%', '65%'],
        center: ['50%', '45%'],
        avoidLabelOverlap: true,
        label: { show: false },
        emphasis: {
          label: { show: true, fontSize: 14, fontWeight: 'bold' },
        },
        data: chartData,
      }],
    })
  }
}

const loadData = async () => {
  try {
    const data = await getDashboard()
    stats.value = data
    initCharts()
  } catch (e) {
    console.error('加载仪表盘数据失败:', e)
    initCharts()
  }
}

const handleResize = () => {
  trendChart?.resize()
  pieChart?.resize()
}

onMounted(() => {
  loadData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  pieChart?.dispose()
})
</script>

<style scoped>
.stat-cards {
  margin-bottom: 20px;
}

.stat-card {
  border-radius: 8px;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-card-inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;
}

.chart-row {
  margin-bottom: 20px;
}

.action-buttons {
  display: flex;
  gap: 16px;
  justify-content: center;
  padding: 10px 0;
}
</style>
