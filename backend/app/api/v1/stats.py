"""API 路由 - 统计分析"""
import json
from datetime import datetime, timedelta, date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.database import get_db
from app.models.job import Job
from app.models.company import Company
from app.models.crawler_rule import CrawlerRule
from app.models.task import Task

router = APIRouter(prefix="/stats", tags=["统计分析"])


@router.get("/dashboard")
async def dashboard_stats(db: AsyncSession = Depends(get_db)):
    """仪表盘汇总数据"""
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())

    # 总职位数
    total_jobs = (await db.execute(select(func.count(Job.id)))).scalar() or 0

    # 今日新增
    today_new = (await db.execute(
        select(func.count(Job.id)).where(Job.crawled_at >= today_start)
    )).scalar() or 0

    # 公司总数
    total_companies = (await db.execute(select(func.count(Company.id)))).scalar() or 0
    # 如果公司表为空，用 jobs 表的去重公司名统计
    if total_companies == 0:
        total_companies = (await db.execute(
            select(func.count(func.distinct(Job.company_name))).where(Job.company_name.isnot(None))
        )).scalar() or 0

    # 活跃规则数
    active_rules = (await db.execute(
        select(func.count(CrawlerRule.id)).where(CrawlerRule.is_active == True)
    )).scalar() or 0

    # 运行中的任务
    running_tasks = (await db.execute(
        select(func.count(Task.id)).where(Task.status == "running")
    )).scalar() or 0

    # 平台分布
    site_dist_result = await db.execute(
        select(Job.source_site, func.count(Job.id))
        .group_by(Job.source_site)
    )
    site_distribution = {row[0]: row[1] for row in site_dist_result.all()}

    # 最近7天趋势
    recent_trend = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        d_start = datetime.combine(d, datetime.min.time())
        d_end = datetime.combine(d + timedelta(days=1), datetime.min.time())
        count = (await db.execute(
            select(func.count(Job.id)).where(Job.crawled_at >= d_start, Job.crawled_at < d_end)
        )).scalar() or 0
        recent_trend.append({"date": d.isoformat(), "count": count})

    return {
        "total_jobs": total_jobs,
        "today_new": today_new,
        "total_companies": total_companies,
        "active_rules": active_rules,
        "running_tasks": running_tasks,
        "site_distribution": site_distribution,
        "recent_trend": recent_trend,
    }


@router.get("/salary-trend")
async def salary_trend(
    city: str = Query(default=None),
    site: str = Query(default=None),
    days: int = Query(default=30, ge=7, le=365),
    db: AsyncSession = Depends(get_db),
):
    """薪资趋势"""
    start_date = datetime.now() - timedelta(days=days)
    query = select(
        func.date(Job.crawled_at).label("dt"),
        func.avg(Job.salary_min).label("avg_min"),
        func.avg(Job.salary_max).label("avg_max"),
        func.count(Job.id).label("cnt"),
    ).where(
        Job.crawled_at >= start_date,
        Job.salary_min.isnot(None),
    )

    if city:
        query = query.where(Job.city.contains(city))
    if site:
        query = query.where(Job.source_site == site)

    query = query.group_by(func.date(Job.crawled_at)).order_by("dt")
    result = await db.execute(query)

    return [
        {
            "date": str(row.dt),
            "avg_salary": round(((row.avg_min or 0) + (row.avg_max or 0)) / 2),
            "min_salary": round(row.avg_min or 0),
            "max_salary": round(row.avg_max or 0),
            "count": row.cnt,
        }
        for row in result.all()
    ]


@router.get("/skill-heatmap")
async def skill_heatmap(
    site: str = Query(default=None),
    limit: int = Query(default=30, ge=5, le=100),
    db: AsyncSession = Depends(get_db),
):
    """技能热度统计"""
    query = select(Job.skills, Job.salary_min, Job.salary_max).where(Job.skills.isnot(None))
    if site:
        query = query.where(Job.source_site == site)
    result = await db.execute(query)
    rows = result.all()

    skill_stats = {}
    for row in rows:
        try:
            skills = json.loads(row.skills)
        except (json.JSONDecodeError, TypeError):
            continue
        for skill in skills:
            skill = skill.strip()
            if not skill:
                continue
            if skill not in skill_stats:
                skill_stats[skill] = {"count": 0, "salary_sum": 0, "salary_cnt": 0}
            skill_stats[skill]["count"] += 1
            if row.salary_min and row.salary_max:
                avg_s = (row.salary_min + row.salary_max) / 2
                skill_stats[skill]["salary_sum"] += avg_s
                skill_stats[skill]["salary_cnt"] += 1

    items = []
    for skill, stat in skill_stats.items():
        avg_salary = None
        if stat["salary_cnt"] > 0:
            avg_salary = round(stat["salary_sum"] / stat["salary_cnt"])
        items.append({"skill": skill, "count": stat["count"], "avg_salary": avg_salary})

    items.sort(key=lambda x: x["count"], reverse=True)
    return items[:limit]


@router.get("/city-distribution")
async def city_distribution(
    site: str = Query(default=None),
    limit: int = Query(default=20),
    db: AsyncSession = Depends(get_db),
):
    """城市分布"""
    query = select(
        Job.city,
        func.count(Job.id).label("cnt"),
        func.avg(Job.salary_min).label("avg_min"),
        func.avg(Job.salary_max).label("avg_max"),
    ).where(Job.city.isnot(None))

    if site:
        query = query.where(Job.source_site == site)

    query = query.group_by(Job.city).order_by(desc("cnt")).limit(limit)
    result = await db.execute(query)

    return [
        {
            "city": row.city,
            "count": row.cnt,
            "avg_salary": round(((row.avg_min or 0) + (row.avg_max or 0)) / 2) if row.avg_min else None,
        }
        for row in result.all()
    ]
