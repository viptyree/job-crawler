# 企业招聘情报开发台账

## 2026-06-29

- 确认项目结构：后端入口 `backend/app/main.py`，前端入口 `frontend/src/main.js`，数据库文件 `backend/data/job_crawler.db`。
- 新增后端 `company_intel` 模块，不修改原有 crawler / tasks / jobs / rules 主流程。
- 新增 SQLite 表：`company_intel_companies`、`company_intel_aliases`、`company_intel_queries`、`company_intel_jobs`、`company_intel_platform_accounts`、`company_intel_scores`。
- 新增模拟平台适配器：BOSS、智联、前程无忧、拉勾。
- 新增别名生成、查询任务、岗位保存、活跃度评分、Excel 导出接口。
- 新增前端企业招聘情报菜单和页面：公司查询、公司档案、公司详情、查询任务、招聘报告、平台账号。
- 第二阶段新增 Playwright 浏览器会话、平台登录窗口、登录状态检测、真实优先查询模式和验证码/未登录人工处理提示。
