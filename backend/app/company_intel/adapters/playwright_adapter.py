"""Playwright-backed real platform adapter."""
from __future__ import annotations

from bs4 import BeautifulSoup

from app.company_intel.adapters.base import CompanyIntelAdapter, CompanyIntelJobResult
from app.company_intel.browser_session import (
    ManualActionRequired,
    build_search_url,
    check_login_status,
    get_platform_config,
    get_user_data_dir,
)


class PlaywrightCompanyIntelAdapter(CompanyIntelAdapter):
    def __init__(self, platform: str):
        self.platform = platform

    async def search(self, company_name: str, aliases: list[str], city: str = "", keyword: str = "") -> list[CompanyIntelJobResult]:
        status = await check_login_status(self.platform)
        if status["status"] not in {"likely_logged_in"}:
            raise ManualActionRequired(status["note"])

        try:
            from playwright.async_api import async_playwright
        except Exception as exc:
            raise ManualActionRequired("Playwright 未安装或不可用。") from exc

        search_word = keyword or (aliases[-1] if aliases else company_name)
        url = build_search_url(self.platform, search_word, city)
        config = get_platform_config(self.platform)

        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(get_user_data_dir(self.platform)),
                headless=True,
                viewport={"width": 1280, "height": 900},
            )
            page = context.pages[0] if context.pages else await context.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            body_text = await page.locator("body").inner_text(timeout=15000)
            if "验证码" in body_text or "安全验证" in body_text:
                await context.close()
                raise ManualActionRequired("平台出现验证码或安全验证，请打开登录窗口手动处理后重试。")

            html = await page.content()
            await context.close()

        soup = BeautifulSoup(html, "html.parser")
        items = []
        for selector in config.job_selectors:
            items = soup.select(selector)
            if items:
                break

        results = [self._parse_item(item, company_name) for item in items[:20]]
        return [item for item in results if item.job_title]

    def _parse_item(self, item, company_name: str) -> CompanyIntelJobResult:
        text = item.get_text(" ", strip=True)
        link = item.select_one("a")
        href = link.get("href", "") if link else ""
        if href.startswith("/"):
            href = get_platform_config(self.platform).home_url.rstrip("/") + href

        title_el = (
            item.select_one(".job-name")
            or item.select_one(".iteminfo__line1__jobname")
            or item.select_one(".jname")
            or item.select_one(".p_top h3")
            or item.select_one("a")
        )
        salary_el = (
            item.select_one(".salary")
            or item.select_one(".iteminfo__line1__jobname__salary")
            or item.select_one(".sal")
            or item.select_one(".money")
        )
        city_el = item.select_one(".job-area") or item.select_one(".workplace") or item.select_one(".d") or item.select_one(".add")
        exp_el = item.select_one(".job-info") or item.select_one(".iteminfo__line2__jobdesc")

        return CompanyIntelJobResult(
            platform=self.platform,
            company_name_raw=company_name,
            job_title=title_el.get_text(" ", strip=True) if title_el else text[:60],
            salary_raw=salary_el.get_text(" ", strip=True) if salary_el else "",
            city=city_el.get_text(" ", strip=True) if city_el else "",
            experience=exp_el.get_text(" ", strip=True)[:80] if exp_el else "",
            education="",
            source_url=href,
            match_type="real",
        )
