# 企业招聘情报 API

## 生成公司别名

`POST /api/v1/company-intel/aliases/generate`

```json
{
  "company_name": "广州云启未来科技有限公司"
}
```

## 发起查询

`POST /api/v1/company-intel/search`

```json
{
  "company_name": "广州云启未来科技有限公司",
  "platforms": ["boss", "zhilian", "job51", "lagou"],
  "city": "广州",
  "keyword": "销售经理",
  "search_mode": "real_with_mock_fallback"
}
```

`search_mode` 可选值：

- `mock`
- `real_with_mock_fallback`
- `real`

## 平台账号

- `POST /api/v1/company-intel/platform-accounts/{platform}/open-login`
- `POST /api/v1/company-intel/platform-accounts/{platform}/check`

## 查询结果

- `GET /api/v1/company-intel/queries/{query_id}`
- `GET /api/v1/company-intel/queries/{query_id}/jobs`
- `GET /api/v1/company-intel/queries/{query_id}/score`
- `GET /api/v1/company-intel/queries/{query_id}/export`
