"""FastAPI 应用入口"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.config import CORS_ORIGINS
from app.database import init_db
from app.api.v1 import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化数据库和调度器"""
    await init_db()
    # 初始化调度器
    from app.crawler.scheduler import start_scheduler
    await start_scheduler()
    yield


app = FastAPI(
    title="招聘信息爬虫管理系统",
    description="可配置化的招聘网站爬虫平台，支持 BOSS直聘、智联招聘、前程无忧、拉勾网",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 API 路由
app.include_router(api_router)


# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "job-crawler"}


# 尝试挂载前端静态文件（生产模式）
frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
