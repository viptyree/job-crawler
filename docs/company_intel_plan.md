# 企业招聘情报第一阶段计划

## 范围

第一阶段只跑通模拟闭环：输入公司名后生成别名，按多平台模拟查询，保存公司、任务、岗位和评分，并支持前端查看和 Excel 导出。

## 已实现接口

- `GET /api/v1/company-intel/health`
- `GET /api/v1/company-intel/platforms`
- `POST /api/v1/company-intel/aliases/generate`
- `POST /api/v1/company-intel/search`
- `GET /api/v1/company-intel/queries`
- `GET /api/v1/company-intel/queries/{query_id}`
- `GET /api/v1/company-intel/queries/{query_id}/jobs`
- `GET /api/v1/company-intel/queries/{query_id}/score`
- `GET /api/v1/company-intel/companies`
- `GET /api/v1/company-intel/companies/{company_id}`
- `GET /api/v1/company-intel/companies/{company_id}/score`
- `GET /api/v1/company-intel/platform-accounts`
- `GET /api/v1/company-intel/queries/{query_id}/export`

## 第二阶段

接入真实浏览器会话、平台登录状态检测、真实搜索页面、验证码人工处理和真实岗位解析。

