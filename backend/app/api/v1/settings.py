"""API 路由 - 系统设置"""
from fastapi import APIRouter
from app.config import USER_AGENTS, PROXY_LIST, DEFAULT_MIN_DELAY, DEFAULT_MAX_DELAY

router = APIRouter(prefix="/settings", tags=["系统设置"])

# 运行时可修改的设置
settings_store = {
    "min_delay": DEFAULT_MIN_DELAY,
    "max_delay": DEFAULT_MAX_DELAY,
    "user_agents": USER_AGENTS.copy(),
    "proxies": PROXY_LIST.copy(),
    "notification_webhook": "",
}


@router.get("")
async def get_settings():
    """获取系统设置"""
    return settings_store


@router.put("")
async def update_settings(data: dict):
    """更新系统设置"""
    for key in ["min_delay", "max_delay", "user_agents", "proxies", "notification_webhook"]:
        if key in data:
            settings_store[key] = data[key]
    return settings_store
