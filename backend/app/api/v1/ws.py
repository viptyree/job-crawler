"""WebSocket 实时推送"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import json

router = APIRouter(tags=["WebSocket"])

# 连接管理
connections: dict[int, list[WebSocket]] = {}


async def broadcast_task_update(task_id: int, data: dict):
    """向指定任务的所有连接推送更新"""
    if task_id in connections:
        for ws in connections[task_id]:
            try:
                await ws.send_json(data)
            except Exception:
                pass


@router.websocket("/ws/task/{task_id}")
async def task_ws(websocket: WebSocket, task_id: int):
    """任务实时日志 WebSocket"""
    await websocket.accept()

    if task_id not in connections:
        connections[task_id] = []
    connections[task_id].append(websocket)

    try:
        while True:
            # 保持连接，等待客户端消息或断开
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        connections[task_id].remove(websocket)
        if not connections[task_id]:
            del connections[task_id]
