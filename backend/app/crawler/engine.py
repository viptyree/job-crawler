"""爬虫引擎核心 - 基于 Playwright 的可配置爬虫"""
import json
import asyncio
import random
import logging
from datetime import datetime
from typing import Callable, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.sqlite import insert as sqlite_upsert
from sqlalchemy import select

from app.models.crawler_rule import CrawlerRule
from app.models.job import Job
from app.models.company import Company
from app.crawler.pipeline import DataPipeline
from app.crawler.anti_crawl import AntiCrawl

logger = logging.getLogger("crawler.engine")


class CrawlerEngine:
    """可配置化爬虫引擎"""

    def __init__(self):
        self.pipeline = DataPipeline()
        self.anti_crawl = AntiCrawl()

    async def run(
        self,
        rule: CrawlerRule,
        task_id: int,
        stop_flag: Callable[[], bool],
        db_session: AsyncSession,
    ) -> dict:
        """执行爬虫任务"""
        stats = {"total": 0, "success": 0, "errors": 0, "log": ""}
        logs = []

        try:
            rule_config = json.loads(rule.rule_config or "{}")
            keywords = json.loads(rule.keywords or "[]")
            cities = json.loads(rule.cities or "[]")

            if not keywords:
                keywords = [""]
            if not cities:
                cities = [""]

            site = rule.site
            logs.append(f"[{datetime.now():%H:%M:%S}] 开始爬取 {rule.name} (平台: {site})")

            # 根据平台选择适配器
            adapter = self._get_adapter(site)
            if not adapter:
                logs.append(f"[{datetime.now():%H:%M:%S}] 未找到平台 {site} 的适配器，使用通用模式")

            # 使用 httpx 模拟请求（轻量级方案，不依赖浏览器启动）
            import httpx

            anti_config = rule_config.get("anti_crawl", {})
            min_delay = anti_config.get("min_delay", 2)
            max_delay = anti_config.get("max_delay", 5)

            for keyword in keywords:
                for city in cities:
                    if stop_flag():
                        logs.append(f"[{datetime.now():%H:%M:%S}] 任务被停止")
                        break

                    logs.append(f"[{datetime.now():%H:%M:%S}] 搜索: keyword={keyword}, city={city}")

                    # 使用适配器获取数据
                    if adapter:
                        try:
                            items = await adapter.fetch(keyword, city, rule_config, self.anti_crawl)
                            stats["total"] += len(items)

                            # 清洗并存储
                            for item in items:
                                try:
                                    cleaned = self.pipeline.process(item, site)
                                    await self._save_job(cleaned, db_session)
                                    stats["success"] += 1
                                except Exception as e:
                                    stats["errors"] += 1
                                    logger.warning(f"保存数据失败: {e}")

                            logs.append(f"[{datetime.now():%H:%M:%S}] 获取 {len(items)} 条数据")
                        except Exception as e:
                            stats["errors"] += 1
                            logs.append(f"[{datetime.now():%H:%M:%S}] 爬取失败: {e}")

                    # 请求间隔
                    delay = random.uniform(min_delay, max_delay)
                    await asyncio.sleep(delay)

            logs.append(f"[{datetime.now():%H:%M:%S}] 爬取完成: 成功 {stats['success']}, 失败 {stats['errors']}")

        except Exception as e:
            logs.append(f"[{datetime.now():%H:%M:%S}] 引擎异常: {e}")
            stats["errors"] += 1

        stats["log"] = "\n".join(logs)
        return stats

    def _get_adapter(self, site: str):
        """获取平台适配器"""
        from app.crawler.sites import get_site_adapter
        return get_site_adapter(site)

    async def _save_job(self, data: dict, db: AsyncSession):
        """保存职位数据（upsert）"""
        # 检查是否存在
        result = await db.execute(
            select(Job).where(
                Job.source_site == data["source_site"],
                Job.source_id == data["source_id"],
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            # 更新
            for key, value in data.items():
                if hasattr(existing, key) and value is not None:
                    setattr(existing, key, value)
        else:
            # 新增
            job = Job(**data)
            db.add(job)

        await db.flush()

        # 同时更新公司表
        if data.get("company_name"):
            company_result = await db.execute(
                select(Company).where(Company.name == data["company_name"])
            )
            if not company_result.scalar_one_or_none():
                company = Company(name=data["company_name"])
                db.add(company)
                await db.flush()
