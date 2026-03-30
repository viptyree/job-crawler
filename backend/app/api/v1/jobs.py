"""API 路由 - 职位数据查询"""
import json
from io import BytesIO
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, or_

from app.database import get_db
from app.models.job import Job
from app.schemas.job import JobResponse

router = APIRouter(prefix="/jobs", tags=["职位数据"])


@router.get("")
async def list_jobs(
    keyword: str = Query(default=None, description="关键词搜索"),
    site: str = Query(default=None, description="来源平台"),
    city: str = Query(default=None, description="城市"),
    salary_min: int = Query(default=None, description="最低月薪"),
    salary_max: int = Query(default=None, description="最高月薪"),
    experience: str = Query(default=None, description="经验要求"),
    education: str = Query(default=None, description="学历要求"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """职位列表（支持多条件筛选）"""
    query = select(Job)

    if keyword:
        query = query.where(
            or_(
                Job.title.contains(keyword),
                Job.company_name.contains(keyword),
                Job.description.contains(keyword),
            )
        )
    if site:
        query = query.where(Job.source_site == site)
    if city:
        query = query.where(Job.city.contains(city))
    if salary_min is not None:
        query = query.where(Job.salary_min >= salary_min)
    if salary_max is not None:
        query = query.where(Job.salary_max <= salary_max)
    if experience:
        query = query.where(Job.experience.contains(experience))
    if education:
        query = query.where(Job.education.contains(education))

    # 总数
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # 分页
    query = query.order_by(desc(Job.crawled_at)).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    jobs = result.scalars().all()

    items = []
    for j in jobs:
        items.append({
            "id": j.id,
            "source_site": j.source_site,
            "source_id": j.source_id,
            "title": j.title,
            "company_name": j.company_name,
            "city": j.city,
            "district": j.district,
            "salary_raw": j.salary_raw,
            "salary_min": j.salary_min,
            "salary_max": j.salary_max,
            "experience": j.experience,
            "education": j.education,
            "job_type": j.job_type,
            "skills": json.loads(j.skills) if j.skills else [],
            "description": j.description,
            "url": j.url,
            "crawled_at": j.crawled_at.isoformat() if j.crawled_at else None,
        })

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items,
    }


@router.get("/export")
async def export_jobs(
    site: str = Query(default=None),
    city: str = Query(default=None),
    keyword: str = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    """导出职位数据为 Excel"""
    import openpyxl

    query = select(Job)
    if keyword:
        query = query.where(Job.title.contains(keyword))
    if site:
        query = query.where(Job.source_site == site)
    if city:
        query = query.where(Job.city.contains(city))
    query = query.order_by(desc(Job.crawled_at)).limit(5000)

    result = await db.execute(query)
    jobs = result.scalars().all()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "职位数据"
    headers = ["ID", "来源", "职位", "公司", "城市", "薪资", "经验", "学历", "技能", "链接", "爬取时间"]
    ws.append(headers)

    for j in jobs:
        ws.append([
            j.id, j.source_site, j.title, j.company_name, j.city,
            j.salary_raw, j.experience, j.education,
            ", ".join(json.loads(j.skills) if j.skills else []),
            j.url,
            j.crawled_at.strftime("%Y-%m-%d %H:%M") if j.crawled_at else "",
        ])

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=jobs_export.xlsx"},
    )
