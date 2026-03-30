<template>
  <div class="settings">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header><span class="section-title">请求频率设置</span></template>
          <el-form label-width="120px" :model="settings">
            <el-form-item label="最小延迟(秒)">
              <el-input-number v-model="settings.min_delay" :min="1" :max="30" :step="0.5" />
            </el-form-item>
            <el-form-item label="最大延迟(秒)">
              <el-input-number v-model="settings.max_delay" :min="1" :max="60" :step="0.5" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveSettings" :loading="saving">保存设置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header><span class="section-title">通知设置</span></template>
          <el-form label-width="120px" :model="settings">
            <el-form-item label="Webhook URL">
              <el-input v-model="settings.notification_webhook" placeholder="填入 Webhook 通知地址" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveSettings" :loading="saving">保存设置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header><span class="section-title">User-Agent 池</span></template>
          <div class="ua-list">
            <div v-for="(ua, index) in settings.user_agents" :key="index" class="ua-item">
              <el-input v-model="settings.user_agents[index]" size="small" />
              <el-button type="danger" size="small" link @click="settings.user_agents.splice(index, 1)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
            <el-button size="small" @click="settings.user_agents.push('')" style="margin-top: 8px;">
              <el-icon><Plus /></el-icon> 添加
            </el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header><span class="section-title">代理池</span></template>
          <div class="proxy-list">
            <div v-for="(proxy, index) in settings.proxies" :key="index" class="ua-item">
              <el-input v-model="settings.proxies[index]" size="small" placeholder="http://host:port" />
              <el-button type="danger" size="small" link @click="settings.proxies.splice(index, 1)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
            <el-button size="small" @click="settings.proxies.push('')" style="margin-top: 8px;">
              <el-icon><Plus /></el-icon> 添加代理
            </el-button>
            <el-alert
              title="代理格式示例: http://username:password@host:port"
              type="info"
              :closable="false"
              style="margin-top: 12px;"
              show-icon
            />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getSettings, updateSettings } from '@/api/stats.js'

const settings = ref({
  min_delay: 2,
  max_delay: 5,
  user_agents: [],
  proxies: [],
  notification_webhook: '',
})
const saving = ref(false)

const loadSettings = async () => {
  try {
    const data = await getSettings()
    settings.value = data
  } catch (e) {
    console.error(e)
  }
}

const saveSettings = async () => {
  saving.value = true
  try {
    await updateSettings(settings.value)
    ElMessage.success('设置已保存')
  } catch (e) {
    ElMessage.error('保存失败')
  }
  saving.value = false
}

onMounted(loadSettings)
</script>

<style scoped>
.section-title {
  font-weight: 600;
}
.ua-item {
  display: flex;
  gap: 8px;
  margin-bottom: 6px;
  align-items: center;
}
</style>
