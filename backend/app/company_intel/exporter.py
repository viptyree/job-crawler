"""Excel exporter for company intelligence query jobs."""
from io import BytesIO
import openpyxl

from app.company_intel.models import IntelJob, IntelQuery


def build_query_export(query: IntelQuery, jobs: list[IntelJob]) -> BytesIO:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "企业招聘情报"
    ws.append(["公司名称", "平台", "岗位名称", "城市", "薪资", "经验", "学历", "原始链接", "匹配方式", "查询时间"])
    for job in jobs:
        ws.append([
            query.company_name,
            job.platform,
            job.job_title,
            job.city,
            job.salary_raw,
            job.experience,
            job.education,
            job.source_url,
            job.match_type,
            query.created_at.strftime("%Y-%m-%d %H:%M:%S") if query.created_at else "",
        ])
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output

