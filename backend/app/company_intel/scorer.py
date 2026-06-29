"""Recruiting activity scoring."""
import json
from app.company_intel.models import IntelJob, IntelScore


def score_jobs(query_id: int, company_id: int, jobs: list[IntelJob]) -> IntelScore:
    job_count = len(jobs)
    platforms = {job.platform for job in jobs if job.platform}
    cities = {job.city for job in jobs if job.city}
    titles = {job.job_title for job in jobs if job.job_title}
    salaries = [job for job in jobs if job.salary_raw]

    count_score = min(30, job_count * 5)
    platform_score = min(20, len(platforms) * 5)
    city_score = min(10, len(cities) * 5)
    recent_score = min(20, job_count * 4)
    title_score = min(10, len(titles) * 2)
    salary_score = 10 if job_count and len(salaries) == job_count else min(10, len(salaries) * 2)
    total = count_score + platform_score + city_score + recent_score + title_score + salary_score

    if total >= 80:
        level = "高活跃"
        reason = "该公司在多个平台存在招聘信息，岗位数量较多，近期可能处于扩张阶段。"
    elif total >= 50:
        level = "中活跃"
        reason = "该公司存在稳定招聘信息，可继续观察岗位变化和平台覆盖。"
    else:
        level = "低活跃"
        reason = "当前发现的招聘信息较少，建议后续接入真实平台后再次确认。"

    detail = {
        "job_count_score": count_score,
        "platform_score": platform_score,
        "city_score": city_score,
        "recent_score": recent_score,
        "title_score": title_score,
        "salary_score": salary_score,
        "job_count": job_count,
        "platform_count": len(platforms),
        "city_count": len(cities),
    }
    return IntelScore(
        query_id=query_id,
        company_id=company_id,
        score=total,
        level=level,
        reason_text=reason,
        detail_json=json.dumps(detail, ensure_ascii=False),
    )

