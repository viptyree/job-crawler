"""API 路由 - 任务管理"""
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database import get_db, async_session
from app.models.task import Task
from app.models.crawler_rule import CrawlerRule
from app.schemas.task import TaskCreate, TaskResponse

router = APIRouter(prefix="/tasks", tags=["任务管理"])

# 全局任务状态跟踪
running_tasks: dict[int, bool] = {}


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    status: str = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """获取任务列表"""
    query = select(Task).order_by(desc(Task.id)).limit(limit)
    if status:
        query = query.where(Task.status == status)
    result = await db.execute(query)
    tasks = result.scalars().all()

    out = []
    for t in tasks:
        # 获取关联规则信息
        rule_result = await db.execute(select(CrawlerRule).where(CrawlerRule.id == t.rule_id))
        rule = rule_result.scalar_one_or_none()
        resp = TaskResponse(
            id=t.id, rule_id=t.rule_id, status=t.status,
            started_at=t.started_at, finished_at=t.finished_at,
            total_count=t.total_count, success_count=t.success_count,
            error_count=t.error_count, log_text=t.log_text, error_msg=t.error_msg,
            rule_name=rule.name if rule else None,
            rule_site=rule.site if rule else None,
        )
        out.append(resp)
    return out


@router.post("", response_model=TaskResponse)
async def create_task(
    data: TaskCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """手动触发爬取任务"""
    # 验证规则存在
    result = await db.execute(select(CrawlerRule).where(CrawlerRule.id == data.rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")

    # 创建任务记录
    task = Task(
        rule_id=data.rule_id,
        status="pending",
        started_at=datetime.now(),
    )
    db.add(task)
    await db.flush()
    await db.refresh(task)

    task_id = task.id

    # 后台执行爬虫任务
    background_tasks.add_task(run_crawler_task, task_id, data.rule_id)

    return TaskResponse(
        id=task.id, rule_id=task.rule_id, status=task.status,
        started_at=task.started_at,
        rule_name=rule.name, rule_site=rule.site,
    )


@router.post("/{task_id}/stop")
async def stop_task(task_id: int, db: AsyncSession = Depends(get_db)):
    """停止任务"""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    running_tasks[task_id] = False
    task.status = "stopped"
    task.finished_at = datetime.now()
    await db.flush()
    return {"message": "任务已停止"}


@router.get("/{task_id}/logs")
async def get_task_logs(task_id: int, db: AsyncSession = Depends(get_db)):
    """获取任务日志"""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return {"task_id": task_id, "logs": task.log_text or "", "status": task.status}


async def run_crawler_task(task_id: int, rule_id: int):
    """后台执行爬虫任务"""
    from app.crawler.engine import CrawlerEngine

    running_tasks[task_id] = True

    async with async_session() as db:
        try:
            # 更新状态为运行中
            result = await db.execute(select(Task).where(Task.id == task_id))
            task = result.scalar_one()
            task.status = "running"
            task.started_at = datetime.now()
            await db.commit()

            # 获取规则
            result = await db.execute(select(CrawlerRule).where(CrawlerRule.id == rule_id))
            rule = result.scalar_one()

            # 执行爬虫
            engine = CrawlerEngine()
            stats = await engine.run(
                rule=rule,
                task_id=task_id,
                stop_flag=lambda: not running_tasks.get(task_id, False),
                db_session=db,
            )

            # 更新任务结果
            result = await db.execute(select(Task).where(Task.id == task_id))
            task = result.scalar_one()
            task.status = "success"
            task.finished_at = datetime.now()
            task.total_count = stats.get("total", 0)
            task.success_count = stats.get("success", 0)
            task.error_count = stats.get("errors", 0)
            task.log_text = stats.get("log", "")
            await db.commit()

        except Exception as e:
            result = await db.execute(select(Task).where(Task.id == task_id))
            task = result.scalar_one()
            task.status = "failed"
            task.finished_at = datetime.now()
            task.error_msg = str(e)
            await db.commit()
        finally:
            running_tasks.pop(task_id, None)
