"""Mock adapter used to complete the first-stage closed loop."""
from app.company_intel.adapters.base import CompanyIntelAdapter, CompanyIntelJobResult


class MockCompanyIntelAdapter(CompanyIntelAdapter):
    platform = "mock"

    async def search(self, company_name: str, aliases: list[str], city: str = "", keyword: str = "") -> list[CompanyIntelJobResult]:
        target_city = city or "广州"
        base_titles = [keyword or "销售经理", "运营专员", "客户成功经理"]
        alias = aliases[-1] if aliases else company_name
        return [
            CompanyIntelJobResult(
                platform=self.platform,
                company_name_raw=company_name,
                job_title=title,
                salary_raw=salary,
                city=target_city if index != 2 else "深圳",
                experience=experience,
                education=education,
                source_url=f"https://example.com/{self.platform}/jobs/{index + 1}?q={alias}",
                match_type="mock",
            )
            for index, (title, salary, experience, education) in enumerate([
                (base_titles[0], "8-13K", "1-3年", "大专"),
                (base_titles[1], "10-18K", "3-5年", "本科"),
                (base_titles[2], "12-20K", "经验不限", "本科"),
            ])
        ]

