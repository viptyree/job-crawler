"""Playwright browser session helpers for real platform searches."""
from __future__ import annotations

import asyncio
import os
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

from app.config import DATA_DIR


SESSION_ROOT = DATA_DIR / "company_intel_sessions"
SESSION_ROOT.mkdir(exist_ok=True)
PLAYWRIGHT_LOCKS: dict[str, asyncio.Lock] = {}


class BrowserSessionError(RuntimeError):
    """Raised when a browser session cannot be opened or checked."""


class ManualActionRequired(RuntimeError):
    """Raised when a platform needs user action such as login or captcha."""


@dataclass(frozen=True)
class PlatformConfig:
    platform: str
    label: str
    login_url: str
    home_url: str
    search_url_template: str
    logged_out_texts: tuple[str, ...]
    job_selectors: tuple[str, ...]


PLATFORM_CONFIGS: dict[str, PlatformConfig] = {
    "boss": PlatformConfig(
        platform="boss",
        label="BOSS直聘",
        login_url="https://www.zhipin.com/web/user/?ka=header-login",
        home_url="https://www.zhipin.com/",
        search_url_template="https://www.zhipin.com/web/geek/job?query={keyword}&city={city_code}",
        logged_out_texts=("登录", "扫码登录", "验证码"),
        job_selectors=(".job-card-wrapper", ".job-list-box .job-card-wrapper"),
    ),
    "zhilian": PlatformConfig(
        platform="zhilian",
        label="智联招聘",
        login_url="https://passport.zhaopin.com/login",
        home_url="https://www.zhaopin.com/",
        search_url_template="https://sou.zhaopin.com/?kw={keyword}&jl={city}",
        logged_out_texts=("登录", "扫码登录", "验证码"),
        job_selectors=(".joblist-box__item", ".positionlist .joblist-box__item"),
    ),
    "job51": PlatformConfig(
        platform="job51",
        label="前程无忧",
        login_url="https://login.51job.com/login.php",
        home_url="https://www.51job.com/",
        search_url_template="https://search.51job.com/list/{city_code},000000,0000,00,9,99,{keyword},2,1.html",
        logged_out_texts=("登录", "验证码", "会员名"),
        job_selectors=(".j_joblist .e", ".joblist-item", ".el"),
    ),
    "lagou": PlatformConfig(
        platform="lagou",
        label="拉勾网",
        login_url="https://passport.lagou.com/login/login.html",
        home_url="https://www.lagou.com/",
        search_url_template="https://www.lagou.com/wn/zhaopin?kd={keyword}&city={city}",
        logged_out_texts=("登录", "验证码", "扫码"),
        job_selectors=(".item__10RTO", ".con_list_item", ".position-list li"),
    ),
}

BOSS_CITY_CODES = {
    "全国": "100010000", "北京": "101010100", "上海": "101020100",
    "广州": "101280100", "深圳": "101280600", "杭州": "101210100",
    "成都": "101270100", "南京": "101190100", "武汉": "101200100",
}

JOB51_CITY_CODES = {
    "全国": "000000", "北京": "010000", "上海": "020000", "广州": "030200",
    "深圳": "040000", "杭州": "080200", "成都": "090200", "南京": "070200",
    "武汉": "180200",
}


def get_platform_config(platform: str) -> PlatformConfig:
    if platform not in PLATFORM_CONFIGS:
        raise BrowserSessionError(f"不支持的平台：{platform}")
    return PLATFORM_CONFIGS[platform]


def get_user_data_dir(platform: str) -> Path:
    path = SESSION_ROOT / platform
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_platform_lock(platform: str) -> asyncio.Lock:
    if platform not in PLAYWRIGHT_LOCKS:
        PLAYWRIGHT_LOCKS[platform] = asyncio.Lock()
    return PLAYWRIGHT_LOCKS[platform]


async def launch_persistent_context(playwright, platform: str, *, headless: bool, viewport: dict):
    """Launch a persistent browser context, preferring installed Google Chrome when available."""
    options = {
        "user_data_dir": str(get_user_data_dir(platform)),
        "headless": headless,
        "viewport": viewport,
    }
    try:
        return await playwright.chromium.launch_persistent_context(channel="chrome", **options)
    except Exception:
        return await playwright.chromium.launch_persistent_context(**options)


def build_search_url(platform: str, keyword: str, city: str) -> str:
    config = get_platform_config(platform)
    encoded_keyword = quote(keyword or "", safe="")
    city_name = quote(city or "全国", safe="")
    return config.search_url_template.format(
        keyword=encoded_keyword,
        city=city_name,
        city_code=BOSS_CITY_CODES.get(city, BOSS_CITY_CODES["全国"]) if platform == "boss" else JOB51_CITY_CODES.get(city, "000000"),
    )


async def open_login_window(platform: str) -> None:
    """Open the platform login page in the user's default browser."""
    config = get_platform_config(platform)

    def _open_url() -> None:
        if os.name == "nt":
            os.startfile(config.login_url)  # type: ignore[attr-defined]
            return
        if not webbrowser.open(config.login_url, new=2):
            raise BrowserSessionError(f"无法打开登录页：{config.login_url}")

    try:
        await asyncio.to_thread(_open_url)
    except Exception as exc:
        raise BrowserSessionError(f"无法打开 {config.label} 登录页：{exc}") from exc


async def check_login_status(platform: str) -> dict:
    """Best-effort login status check using the persistent browser profile."""
    config = get_platform_config(platform)
    try:
        from playwright.async_api import async_playwright
    except Exception as exc:
        return {"status": "browser_missing", "note": "Playwright 未安装或不可用。", "detail": str(exc)}

    try:
        async with get_platform_lock(platform):
            async with async_playwright() as p:
                context = await launch_persistent_context(
                    p,
                    platform,
                    headless=False,
                    viewport={"width": 1280, "height": 900},
                )
                page = context.pages[0] if context.pages else await context.new_page()
                await page.goto(config.home_url, wait_until="domcontentloaded", timeout=45000)
                text = await page.locator("body").inner_text(timeout=10000)
                current_url = page.url
                await context.close()
    except Exception as exc:
        message = str(exc)
        if "Executable doesn't exist" in message or "browser" in message.lower():
            return {"status": "browser_missing", "note": "Playwright 浏览器未安装，请运行 python -m playwright install chromium。", "detail": message}
        return {"status": "check_failed", "note": "登录状态检测失败，可能需要手动打开平台确认。", "detail": message}

    clean_text = text.strip()
    if "_security_check" in current_url or "安全验证" in clean_text or "验证码" in clean_text:
        return {"status": "manual_required", "note": "平台触发安全验证，请打开登录窗口手动处理后重试。", "detail": current_url}
    if not clean_text:
        return {"status": "manual_required", "note": "平台页面为空白，可能被安全校验拦截，请打开登录窗口确认。", "detail": current_url}
    if any(flag in clean_text for flag in config.logged_out_texts):
        return {"status": "not_logged_in", "note": "检测到登录入口或验证码提示，请在平台账号页打开登录窗口处理。", "detail": ""}
    return {"status": "likely_logged_in", "note": "未检测到明显登录入口，浏览器会话可能已登录。", "detail": ""}

