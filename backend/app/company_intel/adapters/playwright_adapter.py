"""Playwright-backed real platform adapter."""
from __future__ import annotations

from bs4 import BeautifulSoup

from app.company_intel.adapters.base import CompanyIntelAdapter, CompanyIntelJobResult
from app.company_intel.browser_session import (
    ManualActionRequired,
    build_search_url,
    get_platform_config,
    get_platform_lock,
    launch_persistent_context,
)


class PlaywrightCompanyIntelAdapter(CompanyIntelAdapter):
    def __init__(self, platform: str):
        self.platform = platform

    async def search(self, company_name: str, aliases: list[str], city: str = "", keyword: str = "") -> list[CompanyIntelJobResult]:
        try:
            from playwright.async_api import async_playwright
        except Exception as exc:
            raise ManualActionRequired("Playwright 未安装或不可用。") from exc

        company_word = aliases[-1] if aliases else company_name
        search_word = f"{company_word} {keyword}".strip() if keyword else company_word
        url = build_search_url(self.platform, search_word, city)
        config = get_platform_config(self.platform)

        async with get_platform_lock(self.platform):
            async with async_playwright() as p:
                context = await launch_persistent_context(
                    p,
                    self.platform,
                    headless=False,
                    viewport={"width": 1280, "height": 900},
                )
                page = context.pages[0] if context.pages else await context.new_page()
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    await page.wait_for_timeout(2500)
                    body_text = await page.locator("body").inner_text(timeout=15000)
                    current_url = page.url
                    clean_text = body_text.strip()
                    if "_security_check" in current_url or "验证码" in clean_text or "安全验证" in clean_text:
                        raise ManualActionRequired("平台出现验证码或安全验证，请打开登录窗口手动处理后重试。")
                    if not clean_text:
                        raise ManualActionRequired("平台页面为空白，可能被安全校验拦截，请打开登录窗口确认后重试。")
                    html = await page.content()
                finally:
                    await context.close()

        soup = BeautifulSoup(html, "html.parser")
        items = []
        for selector in config.job_selectors:
            items = soup.select(selector)
            if items:
                break

        if not items and self._looks_blocked(soup):
            raise ManualActionRequired("平台未返回岗位列表，可能需要重新登录或处理安全验证。")

        results = [self._parse_item(item, company_name) for item in items[:20]]
        return [item for item in results if item.job_title]

    def _looks_blocked(self, soup: BeautifulSoup) -> bool:
        text = soup.get_text(" ", strip=True)
        block_words = ("验证码", "安全验证", "扫码登录", "请登录", "访问异常", "稍后重试")
        return not text or any(word in text for word in block_words)

    def _parse_item(self, item, company_name: str) -> CompanyIntelJobResult:
        text = item.get_text(" ", strip=True)
        link = item.select_one("a")
        href = link.get("href", "") if link else ""
        if href.startswith("/"):
            href = get_platform_config(self.platform).home_url.rstrip("/") + href

        title_el = (
            item.select_one(".job-name")
            or item.select_one(".job-title")
            or item.select_one(".iteminfo__line1__jobname")
            or item.select_one(".jname")
            or item.select_one(".p_top h3")
            or item.select_one("a")
        )
        salary_el = (
            item.select_one(".salary")
            or item.select_one(".job-salary")
            or item.select_one(".iteminfo__line1__jobname__salary")
            or item.select_one(".sal")
            or item.select_one(".money")
        )
        city_el = (
            item.select_one(".job-area")
            or item.select_one(".job-location")
            or item.select_one(".workplace")
            or item.select_one(".d")
            or item.select_one(".add")
        )
        exp_el = item.select_one(".job-info") or item.select_one(".tag-list") or item.select_one(".iteminfo__line2__jobdesc")

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
