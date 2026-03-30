"""智联招聘适配器"""
import httpx
import asyncio
import hashlib
import logging
from bs4 import BeautifulSoup
from app.crawler.anti_crawl import AntiCrawl
from app.crawler.rule_parser import RuleParser

logger = logging.getLogger("crawler.zhilian")

CITY_CODES = {
    "全国": "", "北京": "530", "上海": "538", "广州": "763",
    "深圳": "765", "杭州": "653", "成都": "801", "南京": "635",
    "武汉": "736", "西安": "854", "苏州": "639", "长沙": "749",
    "天津": "531", "重庆": "551", "郑州": "719", "合肥": "664",
    "济南": "702", "青岛": "703", "大连": "600", "厦门": "682",
}


class ZhilianAdapter:
    """智联招聘爬虫适配器"""

    BASE_URL = "https://www.zhaopin.com"
    SEARCH_URL = "https://sou.zhaopin.com"

    async def fetch(self, keyword: str, city: str, rule_config: dict, anti_crawl: AntiCrawl) -> list[dict]:
        """爬取智联招聘职位列表"""
        results = []
        city_code = CITY_CODES.get(city, "")
        max_pages = rule_config.get("list_page", {}).get("max_pages", 10)

        for page in range(1, min(max_pages + 1, 11)):
            try:
                params = {
                    "jl": city_code,
                    "kw": keyword,
                    "p": page,
                }

                headers = anti_crawl.get_headers()
                headers["Referer"] = self.SEARCH_URL

                async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
                    resp = await client.get(self.SEARCH_URL, params=params, headers=headers)

                    if resp.status_code != 200:
                        logger.warning(f"智联招聘请求失败: {resp.status_code}")
                        continue

                    soup = BeautifulSoup(resp.text, "html.parser")

                    list_config = rule_config.get("list_page", {})
                    item_selector = list_config.get("item_selector", ".joblist-box__item")
                    items = soup.select(item_selector)

                    if not items:
                        items = soup.select(".positionlist .joblist-box__item")

                    if not items:
                        break

                    fields_config = list_config.get("fields", {})
                    for item in items:
                        try:
                            job_data = self._parse_item(item, fields_config)
                            if job_data.get("title"):
                                results.append(job_data)
                        except Exception as e:
                            logger.debug(f"解析失败: {e}")

                delay = anti_crawl.get_delay()
                await asyncio.sleep(delay)

            except Exception as e:
                logger.error(f"智联招聘第{page}页爬取异常: {e}")
                break

        return results

    def _parse_item(self, item, fields_config: dict) -> dict:
        if fields_config:
            return RuleParser.extract_fields(item, fields_config)

        title_el = item.select_one(".iteminfo__line1__jobname") or item.select_one(".jobinfo .jobname")
        salary_el = item.select_one(".iteminfo__line1__jobname__salary") or item.select_one(".jobinfo .salary")
        company_el = item.select_one(".iteminfo__line1__companyname") or item.select_one(".company_name")
        city_el = item.select_one(".iteminfo__line2__jobdesc span") or item.select_one(".workplace")

        link = item.select_one("a")
        href = link.get("href", "") if link else ""
        source_id = href.split("/")[-1].replace(".htm", "") if href else hashlib.md5(
            (title_el.get_text(strip=True) if title_el else "").encode()
        ).hexdigest()[:16]

        return {
            "source_id": source_id,
            "title": title_el.get_text(strip=True) if title_el else "",
            "salary_raw": salary_el.get_text(strip=True) if salary_el else "",
            "company_name": company_el.get_text(strip=True) if company_el else "",
            "city": city_el.get_text(strip=True) if city_el else "",
            "url": href if href.startswith("http") else f"{self.BASE_URL}{href}",
            "skills": [],
            "experience": "",
            "education": "",
        }
