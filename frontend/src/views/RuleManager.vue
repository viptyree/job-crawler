<template>
  <div class="rule-manager">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>爬虫规则管理</span>
          <el-button type="primary" @click="showAddDialog">
            <el-icon><Plus /></el-icon>
            新增规则
          </el-button>
        </div>
      </template>

      <el-table :data="rules" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="规则名称" min-width="160" />
        <el-table-column prop="site" label="平台" width="120">
          <template #default="{ row }">
            <el-tag :type="siteTagType(row.site)">{{ siteNameMap[row.site] || row.site }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="keywords" label="关键词" min-width="160">
          <template #default="{ row }">
            <el-tag v-for="kw in (row.keywords || [])" :key="kw" size="small" class="kw-tag">{{ kw }}</el-tag>
            <span v-if="!row.keywords?.length" class="text-muted">未设置</span>
          </template>
        </el-table-column>
        <el-table-column prop="cities" label="城市" width="140">
          <template #default="{ row }">
            <span>{{ (row.cities || []).join(', ') || '全国' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="schedule" label="调度" width="120">
          <template #default="{ row }">
            <span>{{ row.schedule || '手动触发' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-switch v-model="row.is_active" @change="toggleActive(row)" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" link @click="editRule(row)">编辑</el-button>
            <el-button type="success" size="small" link @click="runRule(row)">执行</el-button>
            <el-button type="warning" size="small" link @click="testRuleAction(row)">测试</el-button>
            <el-popconfirm title="确定删除此规则？" @confirm="removeRule(row.id)">
              <template #reference>
                <el-button type="danger" size="small" link>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 编辑/新增弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑规则' : '新增规则'" width="700px" destroy-on-close>
      <el-form :model="form" label-width="100px" label-position="top">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="规则名称" required>
              <el-input v-model="form.name" placeholder="如：BOSS直聘-Python岗位" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="目标平台" required>
              <el-select v-model="form.site" placeholder="选择平台" style="width: 100%">
                <el-option label="BOSS直聘" value="boss" />
                <el-option label="智联招聘" value="zhilian" />
                <el-option label="前程无忧" value="qianchen" />
                <el-option label="拉勾网" value="lagou" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="搜索关键词">
          <el-select
            v-model="form.keywords"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="输入关键词后回车添加"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="目标城市">
          <el-select
            v-model="form.cities"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="输入城市后回车添加"
            style="width: 100%"
          >
            <el-option v-for="c in commonCities" :key="c" :label="c" :value="c" />
          </el-select>
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="定时调度 (Cron)">
              <el-input v-model="form.schedule" placeholder="如: 0 9 * * * (每天9点)" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="是否启用">
              <el-switch v-model="form.is_active" />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 切换模式 -->
        <el-form-item>
          <div class="mode-switch">
            <span>高级配置</span>
            <el-switch v-model="showAdvanced" />
          </div>
        </el-form-item>

        <el-form-item v-if="showAdvanced" label="爬取规则 (JSON)">
          <el-input
            v-model="ruleConfigStr"
            type="textarea"
            :rows="12"
            placeholder="自定义爬取规则配置..."
            style="font-family: monospace;"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveRule" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getRules, createRule, updateRule, deleteRule, testRule } from '@/api/rules.js'
import { createTask } from '@/api/tasks.js'

const rules = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const saving = ref(false)
const showAdvanced = ref(false)
const ruleConfigStr = ref('{}')

const siteNameMap = { boss: 'BOSS直聘', zhilian: '智联招聘', qianchen: '前程无忧', lagou: '拉勾网' }
const siteTagType = (site) => ({ boss: '', zhilian: 'success', qianchen: 'warning', lagou: 'danger' }[site] || 'info')
const commonCities = ['北京', '上海', '广州', '深圳', '杭州', '成都', '南京', '武汉', '西安', '苏州', '长沙', '天津', '重庆']

const defaultForm = () => ({
  id: null,
  name: '',
  site: 'boss',
  keywords: [],
  cities: [],
  rule_config: {},
  schedule: '',
  is_active: true,
})
const form = ref(defaultForm())

const loadRules = async () => {
  loading.value = true
  try {
    rules.value = await getRules()
  } catch (e) {
    console.error(e)
  }
  loading.value = false
}

const showAddDialog = () => {
  isEdit.value = false
  form.value = defaultForm()
  ruleConfigStr.value = '{}'
  showAdvanced.value = false
  dialogVisible.value = true
}

const editRule = (row) => {
  isEdit.value = true
  form.value = { ...row }
  ruleConfigStr.value = JSON.stringify(row.rule_config || {}, null, 2)
  showAdvanced.value = Object.keys(row.rule_config || {}).length > 0
  dialogVisible.value = true
}

const saveRule = async () => {
  saving.value = true
  try {
    let ruleConfig = {}
    try {
      ruleConfig = JSON.parse(ruleConfigStr.value || '{}')
    } catch { /* ignore */ }

    const data = { ...form.value, rule_config: ruleConfig }

    if (isEdit.value) {
      await updateRule(form.value.id, data)
      ElMessage.success('规则已更新')
    } else {
      await createRule(data)
      ElMessage.success('规则已创建')
    }
    dialogVisible.value = false
    await loadRules()
  } catch (e) {
    console.error(e)
  }
  saving.value = false
}

const toggleActive = async (row) => {
  try {
    await updateRule(row.id, { is_active: row.is_active })
    ElMessage.success(row.is_active ? '已启用' : '已停用')
  } catch (e) {
    row.is_active = !row.is_active
  }
}

const removeRule = async (id) => {
  await deleteRule(id)
  ElMessage.success('已删除')
  await loadRules()
}

const runRule = async (row) => {
  try {
    await createTask({ rule_id: row.id })
    ElMessage.success(`任务已创建，规则 "${row.name}" 开始执行`)
  } catch (e) {
    console.error(e)
  }
}

const testRuleAction = async (row) => {
  try {
    const result = await testRule(row.id)
    ElMessage.info(result.message || '测试完成')
  } catch (e) {
    console.error(e)
  }
}

onMounted(loadRules)
</script>

<style scoped>
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;
}

.kw-tag {
  margin-right: 4px;
  margin-bottom: 2px;
}

.text-muted {
  color: #c0c4cc;
  font-size: 13px;
}

.mode-switch {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #606266;
}
</style>
