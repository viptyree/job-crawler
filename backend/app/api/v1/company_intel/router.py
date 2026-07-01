"""API routes for company intelligence."""
import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.company_intel.alias_generator import generate_aliases
from app.company_intel.browser_session import check_login_status, get_platform_config, open_login_window
from app.company_intel.exporter import build_query_export
from app.company_intel.models import IntelCompany, IntelJob, IntelPlatformAccount, IntelQuery, IntelScore
from app.company_intel.platform_registry import list_platforms
from app.company_intel.schemas import AliasGenerateRequest, CompanySearchRequest
from app.company_intel.service import list_companies, list_queries, run_company_search
from app.database import get_db

router = APIRouter(prefix="/company-intel", tags=["企业招聘情报"])


def query_to_dict(query: IntelQuery) -> dict:
    return {
        "id": query.id,
        "company_id": query.company_id,
        "company_name": query.company_name,
        "platforms": json.loads(query.platforms or "[]"),
        "city": query.city or "",
        "keyword": query.keyword or "",
        "status": query.status,
        "total_count": query.total_count,
        "error_message": query.error_message or "",
        "created_at": query.created_at,
        "finished_at": query.finished_at,
    }


def job_to_dict(job: IntelJob) -> dict:
    return {
        "id": job.id,
        "query_id": job.query_id,
        "company_id": job.company_id,
        "platform": job.platform,
        "company_name_raw": job.company_name_raw,
        "job_title": job.job_title,
        "salary_raw": job.salary_raw,
        "city": job.city,
        "experience": job.experience,
        "education": job.education,
        "source_url": job.source_url,
        "match_type": job.match_type,
        "created_at": job.created_at,
    }


def score_to_dict(score: IntelScore) -> dict:
    return {
        "id": score.id,
        "query_id": score.query_id,
        "company_id": score.company_id,
        "score": score.score,
        "level": score.level,
        "reason_text": score.reason_text,
        "detail": json.loads(score.detail_json or "{}"),
        "created_at": score.created_at,
    }


@router.get("/health")
async def health():
    return {"status": "ok", "module": "company_intel"}


@router.get("/platforms")
async def platforms():
    return list_platforms()


@router.post("/aliases/generate")
async def aliases_generate(data: AliasGenerateRequest):
    aliases = generate_aliases(data.company_name)
    if not aliases:
        raise HTTPException(status_code=400, detail="公司名称不能为空")
    return {"aliases": aliases}


@router.post("/search")
async def search(data: CompanySearchRequest, db: AsyncSession = Depends(get_db)):
    query, _score = await run_company_search(
        db=db,
        company_name=data.company_name.strip(),
        platforms=data.platforms,
        city=data.city.strip(),
        keyword=data.keyword.strip(),
        search_mode=data.search_mode,
    )
    return {
        "query_id": query.id,
        "company_id": query.company_id,
        "status": query.status,
        "total_count": query.total_count,
        "error_message": query.error_message or "",
    }


@router.get("/queries")
async def queries(db: AsyncSession = Depends(get_db)):
    return [query_to_dict(query) for query in await list_queries(db)]


@router.get("/queries/{query_id}")
async def query_detail(query_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IntelQuery).where(IntelQuery.id == query_id))
    query = result.scalar_one_or_none()
    if not query:
        raise HTTPException(status_code=404, detail="查询任务不存在")
    return query_to_dict(query)


@router.get("/queries/{query_id}/jobs")
async def query_jobs(query_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IntelJob).where(IntelJob.query_id == query_id).order_by(IntelJob.id.desc()))
    return [job_to_dict(job) for job in result.scalars().all()]


@router.get("/queries/{query_id}/score")
async def query_score(query_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IntelScore).where(IntelScore.query_id == query_id).order_by(desc(IntelScore.created_at)).limit(1))
    score = result.scalar_one_or_none()
    if not score:
        raise HTTPException(status_code=404, detail="评分不存在")
    return score_to_dict(score)


@router.get("/companies")
async def companies(db: AsyncSession = Depends(get_db)):
    items = []
    for company in await list_companies(db):
        score_result = await db.execute(select(IntelScore).where(IntelScore.company_id == company.id).order_by(desc(IntelScore.created_at)).limit(1))
        score = score_result.scalar_one_or_none()
        items.append({
            "id": company.id,
            "name": company.name,
            "created_at": company.created_at,
            "updated_at": company.updated_at,
            "latest_score": score_to_dict(score) if score else None,
        })
    return items


@router.get("/companies/{company_id}")
async def company_detail(company_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IntelCompany).where(IntelCompany.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="公司不存在")
    queries_result = await db.execute(select(IntelQuery).where(IntelQuery.company_id == company_id).order_by(desc(IntelQuery.created_at)))
    return {
        "id": company.id,
        "name": company.name,
        "created_at": company.created_at,
        "updated_at": company.updated_at,
        "queries": [query_to_dict(query) for query in queries_result.scalars().all()],
    }


@router.get("/companies/{company_id}/score")
async def company_score(company_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IntelScore).where(IntelScore.company_id == company_id).order_by(desc(IntelScore.created_at)).limit(1))
    score = result.scalar_one_or_none()
    if not score:
        raise HTTPException(status_code=404, detail="评分不存在")
    return score_to_dict(score)


@router.get("/platform-accounts")
async def platform_accounts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IntelPlatformAccount).order_by(IntelPlatformAccount.platform))
    accounts = {account.platform: account for account in result.scalars().all()}
    rows = []
    for platform in list_platforms():
        account = accounts.get(platform["value"])
        rows.append({
            "platform": platform["value"],
            "label": platform["label"],
            "status": account.status if account else "not_configured",
            "note": account.note if account else "点击打开登录，在平台窗口中手动登录后再进行真实查询。",
            "updated_at": account.updated_at if account else None,
        })
    return rows


@router.post("/platform-accounts/open-all-logins")
async def open_all_platform_logins(db: AsyncSession = Depends(get_db)):
    opened = []
    for platform in list_platforms():
        platform_value = platform["value"]
        config = get_platform_config(platform_value)
        await open_login_window(platform_value)
        result = await db.execute(select(IntelPlatformAccount).where(IntelPlatformAccount.platform == platform_value))
        account = result.scalar_one_or_none()
        if account is None:
            account = IntelPlatformAccount(platform=platform_value)
            db.add(account)
        account.status = "login_window_opened"
        account.note = f"已打开 {config.label} 登录窗口，请完成登录或验证码处理，登录后关闭窗口。"
        opened.append({"platform": platform_value, "label": config.label, "login_url": config.login_url})
    await db.flush()
    return {"status": "opened", "items": opened}


@router.post("/platform-accounts/{platform}/open-login")
async def open_platform_login(platform: str, db: AsyncSession = Depends(get_db)):
    config = get_platform_config(platform)
    await open_login_window(platform)
    result = await db.execute(select(IntelPlatformAccount).where(IntelPlatformAccount.platform == platform))
    account = result.scalar_one_or_none()
    if account is None:
        account = IntelPlatformAccount(platform=platform)
        db.add(account)
    account.status = "login_window_opened"
    account.note = f"已打开 {config.label} 登录窗口，请完成登录或验证码处理，登录后关闭窗口。"
    await db.flush()
    return {"platform": platform, "status": account.status, "note": account.note, "login_url": config.login_url}


@router.post("/platform-accounts/{platform}/check")
async def check_platform_login(platform: str, db: AsyncSession = Depends(get_db)):
    get_platform_config(platform)
    status = await check_login_status(platform)
    result = await db.execute(select(IntelPlatformAccount).where(IntelPlatformAccount.platform == platform))
    account = result.scalar_one_or_none()
    if account is None:
        account = IntelPlatformAccount(platform=platform)
        db.add(account)
    account.status = status["status"]
    account.note = status["note"]
    await db.flush()
    return {"platform": platform, **status}


@router.get("/queries/{query_id}/export")
async def export_query(query_id: int, db: AsyncSession = Depends(get_db)):
    query_result = await db.execute(select(IntelQuery).where(IntelQuery.id == query_id))
    query = query_result.scalar_one_or_none()
    if not query:
        raise HTTPException(status_code=404, detail="查询任务不存在")
    jobs_result = await db.execute(select(IntelJob).where(IntelJob.query_id == query_id).order_by(IntelJob.id))
    output = build_query_export(query, list(jobs_result.scalars().all()))
    filename = f"company_intel_query_{query_id}.xlsx"
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
