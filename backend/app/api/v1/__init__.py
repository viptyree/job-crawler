"""API v1 路由注册"""
from fastapi import APIRouter

from app.api.v1 import rules, tasks, jobs, stats, settings, ws

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(rules.router)
api_router.include_router(tasks.router)
api_router.include_router(jobs.router)
api_router.include_router(stats.router)
api_router.include_router(settings.router)
api_router.include_router(ws.router)
