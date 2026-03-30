<template>
  <div class="task-manager">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>任务管理</span>
          <div class="header-actions">
            <el-select v-model="statusFilter" placeholder="筛选状态" clearable style="width: 150px; margin-right: 12px;">
              <el-option label="运行中" value="running" />
              <el-option label="成功" value="success" />
              <el-option label="失败" value="failed" />
              <el-option label="已停止" value="stopped" />
            </el-select>
            <el-button @click="loadTasks" :loading="loading">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="tasks" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column label="规则" min-width="180">
          <template #default="{ row }">
            <div>
              <strong>{{ row.rule_name || '-' }}</strong>
              <el-tag size="small" :type="siteTagType(row.rule_site)" style="margin-left: 6px;">
                {{ siteNameMap[row.rule_site] || row.rule_site || '-' }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" effect="dark" size="small">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="进度" width="200">
          <template #default="{ row }">
            <div class="progress-info">
              <span class="count-text">
                <span style="color: #67C23A">{{ row.success_count }}</span> 成功
                /
                <span style="color: #F56C6C">{{ row.error_count }}</span> 失败
                /
                {{ row.total_count }} 总计
              </span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="开始时间" width="170">
          <template #default="{ row }">
            {{ row.started_at ? new Date(row.started_at).toLocaleString('zh-CN') : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="结束时间" width="170">
          <template #default="{ row }">
            {{ row.finished_at ? new Date(row.finished_at).toLocaleString('zh-CN') : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'running'"
              type="danger"
              size="small"
              link
              @click="handleStop(row.id)"
            >停止</el-button>
            <el-button type="primary" size="small" link @click="viewLogs(row)">日志</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 日志弹窗 -->
    <el-dialog v-model="logDialogVisible" title="任务日志" width="700px">
      <div class="log-container">
        <pre class="log-text">{{ logContent || '暂无日志' }}</pre>
      </div>
      <div v-if="logError" class="error-msg">
        <el-alert :title="logError" type="error" :closable="false" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { getTasks, stopTask, getTaskLogs } from '@/api/tasks.js'

const tasks = ref([])
const loading = ref(false)
const statusFilter = ref(null)
const logDialogVisible = ref(false)
const logContent = ref('')
const logError = ref('')

const siteNameMap = { boss: 'BOSS直聘', zhilian: '智联招聘', qianchen: '前程无忧', lagou: '拉勾网' }
const siteTagType = (site) => ({ boss: '', zhilian: 'success', qianchen: 'warning', lagou: 'danger' }[site] || 'info')

const statusType = (s) => ({
  pending: 'info', running: 'warning', success: 'success', failed: 'danger', stopped: 'info',
}[s] || 'info')
const statusLabel = (s) => ({
  pending: '等待中', running: '运行中', success: '成功', failed: '失败', stopped: '已停止',
}[s] || s)

const loadTasks = async () => {
  loading.value = true
  try {
    const params = {}
    if (statusFilter.value) params.status = statusFilter.value
    tasks.value = await getTasks(params)
  } catch (e) {
    console.error(e)
  }
  loading.value = false
}

const handleStop = async (taskId) => {
  try {
    await stopTask(taskId)
    ElMessage.success('任务已停止')
    await loadTasks()
  } catch (e) {
    console.error(e)
  }
}

const viewLogs = async (row) => {
  logContent.value = row.log_text || ''
  logError.value = row.error_msg || ''

  try {
    const data = await getTaskLogs(row.id)
    logContent.value = data.logs || '暂无日志'
  } catch { /* use existing */ }

  logDialogVisible.value = true
}

watch(statusFilter, loadTasks)
onMounted(loadTasks)
</script>

<style scoped>
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;
}
.header-actions {
  display: flex;
  align-items: center;
}
.count-text {
  font-size: 13px;
  color: #606266;
}
.log-container {
  max-height: 400px;
  overflow-y: auto;
  background: #1e1e1e;
  border-radius: 6px;
  padding: 16px;
}
.log-text {
  color: #d4d4d4;
  font-family: 'Fira Code', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
}
.error-msg {
  margin-top: 12px;
}
</style>
