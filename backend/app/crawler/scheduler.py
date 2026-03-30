"""任务调度器 - 基于 APScheduler"""
import json
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.database import async_session
from app.models.crawler_rule import CrawlerRule
from app.models.task import Task
from sqlalchemy import select
from datetime import datetime

logger = logging.getLogger("crawler.scheduler")

scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")


async def start_scheduler():
    """启动调度器并加载所有活跃规则"""
    try:
        # 加载所有活跃规则
        async with async_session() as db:
            result = await db.execute(
                select(CrawlerRule).where(CrawlerRule.is_active == True)
            )
            rules = result.scalars().all()

            for rule in rules:
                if rule.schedule:
                    try:
                        add_schedule_job(rule.id, rule.schedule, rule.name)
                    except Exception as e:
                        logger.warning(f"添加调度任务失败 [{rule.name}]: {e}")

        scheduler.start()
        logger.info(f"调度器已启动，已加载 {len(rules)} 个定时任务")
    except Exception as e:
        logger.error(f"调度器启动失败: {e}")


def add_schedule_job(rule_id: int, cron_expr: str, name: str = ""):
    """添加定时任务"""
    job_id = f"rule_{rule_id}"

    # 移除旧的同ID任务
    existing = scheduler.get_job(job_id)
    if existing:
        scheduler.remove_job(job_id)

    # 解析 cron 表达式 (分 时 日 月 周)
    parts = cron_expr.strip().split()
    if len(parts) == 5:
        trigger = CronTrigger(
            minute=parts[0],
            hour=parts[1],
            day=parts[2],
            month=parts[3],
            day_of_week=parts[4],
        )
    else:
        trigger = CronTrigger(hour=9, minute=0)  # 默认每天9点

    scheduler.add_job(
        scheduled_crawl,
        trigger=trigger,
        id=job_id,
        name=name or f"Rule {rule_id}",
        args=[rule_id],
        replace_existing=True,
    )
    logger.info(f"已添加定时任务: {name} ({cron_expr})")


def remove_schedule_job(rule_id: int):
    """移除定时任务"""
    job_id = f"rule_{rule_id}"
    existing = scheduler.get_job(job_id)
    if existing:
        scheduler.remove_job(job_id)


async def scheduled_crawl(rule_id: int):
    """定时爬取任务"""
    from app.crawler.engine import CrawlerEngine

    async with async_session() as db:
        try:
            result = await db.execute(select(CrawlerRule).where(CrawlerRule.id == rule_id))
            rule = result.scalar_one_or_none()
            if not rule or not rule.is_active:
                return

            # 创建任务记录
            task = Task(rule_id=rule_id, status="running", started_at=datetime.now())
            db.add(task)
            await db.commit()
            await db.refresh(task)

            # 执行爬虫
            engine = CrawlerEngine()
            stats = await engine.run(
                rule=rule,
                task_id=task.id,
                stop_flag=lambda: False,
                db_session=db,
            )

            # 更新结果
            task.status = "success"
            task.finished_at = datetime.now()
            task.total_count = stats.get("total", 0)
            task.success_count = stats.get("success", 0)
            task.error_count = stats.get("errors", 0)
            task.log_text = stats.get("log", "")
            await db.commit()

            logger.info(f"定时任务完成 [rule_id={rule_id}]: 成功 {stats.get('success', 0)} 条")

        except Exception as e:
            logger.error(f"定时任务失败 [rule_id={rule_id}]: {e}")
            try:
                task.status = "failed"
                task.error_msg = str(e)
                task.finished_at = datetime.now()
                await db.commit()
            except Exception:
                pass
