"""Company intelligence application service."""
import json
from datetime import datetime
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.company_intel.alias_generator import generate_aliases
from app.company_intel.browser_session import ManualActionRequired
from app.company_intel.models import IntelCompany, IntelCompanyAlias, IntelJob, IntelQuery, IntelScore
from app.company_intel.platform_registry import get_adapters, get_real_adapters
from app.company_intel.scorer import score_jobs


async def get_or_create_company(db: AsyncSession, company_name: str, aliases: list[str]) -> IntelCompany:
    result = await db.execute(select(IntelCompany).where(IntelCompany.name == company_name))
    company = result.scalar_one_or_none()
    if company is None:
        company = IntelCompany(name=company_name)
        db.add(company)
        await db.flush()

    existing = await db.execute(select(IntelCompanyAlias.alias).where(IntelCompanyAlias.company_id == company.id))
    existing_aliases = set(existing.scalars().all())
    for alias in aliases:
        if alias not in existing_aliases:
            db.add(IntelCompanyAlias(company_id=company.id, alias=alias))
    await db.flush()
    return company


async def run_company_search(
    db: AsyncSession,
    company_name: str,
    platforms: list[str],
    city: str = "",
    keyword: str = "",
    search_mode: str = "mock",
) -> tuple[IntelQuery, IntelScore]:
    aliases = generate_aliases(company_name)
    company = await get_or_create_company(db, company_name, aliases)
    query = IntelQuery(
        company_id=company.id,
        company_name=company_name,
        platforms=json.dumps(platforms, ensure_ascii=False),
        city=city,
        keyword=keyword,
        status="running",
    )
    db.add(query)
    await db.flush()

    saved_jobs: list[IntelJob] = []
    platform_messages: list[str] = []
    try:
        use_real = search_mode in {"real", "real_with_mock_fallback"}
        adapters = get_real_adapters(platforms) if use_real else get_adapters(platforms)
        for adapter in adapters:
            try:
                results = await adapter.search(company_name=company_name, aliases=aliases, city=city, keyword=keyword)
            except ManualActionRequired as exc:
                platform_messages.append(f"{adapter.platform}: {exc}")
                if search_mode == "real_with_mock_fallback":
                    mock_adapter = get_adapters([adapter.platform])[0]
                    results = await mock_adapter.search(company_name=company_name, aliases=aliases, city=city, keyword=keyword)
                else:
                    results = []
            for item in results:
                job = IntelJob(
                    query_id=query.id,
                    company_id=company.id,
                    platform=item.platform,
                    company_name_raw=item.company_name_raw,
                    job_title=item.job_title,
                    salary_raw=item.salary_raw,
                    city=item.city,
                    experience=item.experience,
                    education=item.education,
                    source_url=item.source_url,
                    match_type=item.match_type,
                )
                db.add(job)
                saved_jobs.append(job)
        query.status = "success"
        query.total_count = len(saved_jobs)
        query.error_message = "\n".join(platform_messages)
        query.finished_at = datetime.now()
    except Exception as exc:
        query.status = "failed"
        query.error_message = str(exc)
        query.finished_at = datetime.now()
        raise
    finally:
        await db.flush()

    score = score_jobs(query.id, company.id, saved_jobs)
    db.add(score)
    await db.flush()
    return query, score


async def list_companies(db: AsyncSession) -> list[IntelCompany]:
    result = await db.execute(select(IntelCompany).order_by(desc(IntelCompany.updated_at)))
    return list(result.scalars().all())


async def list_queries(db: AsyncSession) -> list[IntelQuery]:
    result = await db.execute(select(IntelQuery).order_by(desc(IntelQuery.created_at)))
    return list(result.scalars().all())
