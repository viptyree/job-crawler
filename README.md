# 🕷 招聘爬虫管理系统

一个可配置化的招聘信息爬虫管理系统，支持 **BOSS直聘、智联招聘、前程无忧、拉勾网** 4 大平台，帮助你持续关注行业动态，持续学习进步。

![dashboard](https://img.shields.io/badge/Vue3-前端-42b883?logo=vue.js)
![backend](https://img.shields.io/badge/FastAPI-后端-009688?logo=fastapi)
![db](https://img.shields.io/badge/SQLite-数据库-003B57?logo=sqlite)
![crawler](https://img.shields.io/badge/httpx-爬虫-2E8B57)

---

## ✨ 功能特性

| 模块 | 功能 |
|------|------|
| **仪表盘** | 总职位数、今日新增、活跃任务数；平台分布饼图；7天数据趋势折线图 |
| **规则管理** | 可视化爬虫规则编辑（表单模式 + JSON 高级模式）；一键执行/测试 |
| **任务管理** | 任务列表（状态、进度、耗时）；实时日志查看；任务停止 |
| **数据中心** | 职位搜索/多条件筛选；分页展示；详情抽屉；Excel 批量导出 |
| **行业分析** | 薪资趋势折线图；技能热度 TOP20 横向柱状图；城市分布；城市薪资对比 |
| **系统设置** | 请求延迟配置；User-Agent 池管理；代理池；Webhook 通知 |

---

## 🏗 系统架构

```
Vue3 前端 (5173)
    ↓ HTTP + WebSocket (Vite Dev Proxy)
FastAPI 后端 (8000)
    ├── API 层：规则/任务/职位/统计/设置
    ├── 爬虫引擎：httpx + BeautifulSoup
    │   ├── BOSS直聘 适配器
    │   ├── 智联招聘 适配器
    │   ├── 前程无忧 适配器
    │   └── 拉勾网   适配器
    ├── 数据清洗 Pipeline（薪资解析、城市归一化、技能提取）
    ├── 定时调度器（APScheduler，Cron 表达式）
    └── SQLite 数据库（5张表）
```

---

## 📁 项目结构

```
job-crawler/
├── backend/                     # FastAPI 后端
│   ├── requirements.txt
│   ├── seed_data.py             # 示例数据脚本
│   └── app/
│       ├── main.py              # 应用入口
│       ├── database.py          # 数据库引擎（SQLAlchemy 异步）
│       ├── config.py            # 全局配置
│       ├── models/              # ORM 数据模型（5张表）
│       ├── schemas/             # Pydantic 校验模式
│       ├── api/v1/              # RESTful 接口（规则/任务/职位/统计/设置/WebSocket）
│       └── crawler/
│           ├── engine.py        # 爬虫引擎基类
│           ├── pipeline.py      # 数据清洗管道
│           ├── anti_crawl.py    # 反爬策略（UA 轮换、随机延迟、代理）
│           ├── scheduler.py     # 定时任务调度
│           ├── rule_parser.py   # JSON 规则解析器
│           └── sites/           # 4 大平台适配器
│               ├── boss.py
│               ├── zhilian.py
│               ├── qianchen.py
│               └── lagou.py
└── frontend/                    # Vue3 前端
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── main.js
        ├── App.vue
        ├── router/              # Vue Router 路由
        ├── api/                 # Axios 封装
        └── views/               # 6 个页面
            ├── Dashboard.vue
            ├── RuleManager.vue
            ├── TaskManager.vue
            ├── DataCenter.vue
            ├── Analysis.vue
            └── Settings.vue
```

---

## 🚀 本地部署启动流程

### 环境要求

| 工具 | 版本要求 |
|------|----------|
| Python | 3.10+ |
| Node.js | 18+ |
| pnpm / npm | 任意新版本 |

---

### 第一步：克隆项目

```bash
git clone https://github.com/tengx7/job-crawler.git
cd job-crawler
```

---

### 第二步：启动后端

```bash
# 进入后端目录
cd backend

# 安装 Python 依赖
pip install -r requirements.txt

# 启动 FastAPI 服务（默认端口 8000）
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

> 首次启动会自动创建 `data/job_crawler.db` 数据库文件并初始化所有表结构。

**（可选）插入示例数据，快速体验效果：**

```bash
python seed_data.py
# 将插入 300 条模拟职位 + 25 家公司 + 4 条爬虫规则
```

后端启动成功后，访问 API 文档：
- Swagger UI：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

---

### 第三步：启动前端

**新开一个终端窗口**，然后：

```bash
# 回到项目根目录
cd job-crawler/frontend

# 安装前端依赖（任选其一）
pnpm install
# 或
npm install

# 启动开发服务器（默认端口 5173）
pnpm dev
# 或
npm run dev
```

前端启动成功后，打开浏览器访问：**http://localhost:5173**

> 前端已配置 Vite 代理，`/api` 请求自动转发到 `http://localhost:8000`，无需手动配置跨域。

---

### 第四步：配置爬虫规则并执行

1. 访问 http://localhost:5173
2. 点击左侧菜单「**规则管理**」
3. 点击「**新增规则**」，填写：
   - **规则名称**：如 `BOSS直聘-Python开发`
   - **目标平台**：选择 `BOSS直聘`
   - **搜索关键词**：输入 `Python` 后回车
   - **目标城市**：选择 `北京`、`上海` 等
   - **定时调度**（可选）：填写 Cron 表达式，如 `0 9 * * *`（每天早9点）
4. 保存后，点击规则列表中的「**执行**」按钮，立即触发爬取
5. 切换到「**任务管理**」查看执行状态和日志
6. 切换到「**数据中心**」查看已爬取的职位数据

---

## ⚙️ 规则配置说明

每条爬虫规则支持 JSON 高级配置（在规则编辑页面开启「高级配置」开关）：

```json
{
  "list_page": {
    "item_selector": ".job-card-wrapper",
    "max_pages": 10
  },
  "anti_crawl": {
    "min_delay": 2,
    "max_delay": 5,
    "use_proxy": false
  }
}
```

| 字段 | 说明 |
|------|------|
| `item_selector` | 职位列表项的 CSS 选择器 |
| `max_pages` | 最大翻页数（默认 10）|
| `min_delay` / `max_delay` | 请求间隔范围（秒），默认 2~5 秒 |
| `use_proxy` | 是否使用代理池（需在系统设置中配置代理地址）|

---

## 📊 数据库设计

| 表名 | 说明 |
|------|------|
| `crawler_rules` | 爬虫规则配置（关键词、城市、规则JSON、Cron调度） |
| `tasks` | 任务执行记录（状态、成功/失败数、日志） |
| `jobs` | 职位信息（唯一键：source_site + source_id，自动去重） |
| `companies` | 公司信息（行业、规模、融资阶段） |
| `trends` | 行业趋势聚合缓存（薪资/技能/城市按日统计） |

---

## 🛡 免责声明

本项目仅供个人学习和研究使用，爬取的数据不得用于商业目的。使用时请：

- 遵守各平台的 `robots.txt` 规则
- 控制请求频率（系统默认 2~5 秒间隔）
- 仅访问公开可见的招聘信息
- 遵守相关法律法规

---

## 📄 License

MIT License
