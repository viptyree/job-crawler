"""拉勾网适配器"""
import httpx
import asyncio
import hashlib
import logging
from bs4 import BeautifulSoup
from app.crawler.anti_crawl import AntiCrawl
from app.crawler.rule_parser import RuleParser

logger = logging.getLogger("crawler.lagou")

CITY_CODES = {
    "全国": "全国", "北京": "北京", "上海": "上海", "广州": "广州",
    "深圳": "深圳", "杭州": "杭州", "成都": "成都", "南京": "南京",
    "武汉": "武汉", "西安": "西安", "苏州": "苏州", "长沙": "长沙",
    "天津": "天津", "重庆": "重庆", "郑州": "郑州",
}


class LagouAdapter:
    """拉勾网爬虫适配器"""

    BASE_URL = "https://www.lagou.com"

    async def fetch(self, keyword: str, city: str, rule_config: dict, anti_crawl: AntiCrawl) -> list[dict]:
        """爬取拉勾网职位列表"""
        results = []
        city_name = CITY_CODES.get(city, city or "全国")
        max_pages = rule_config.get("list_page", {}).get("max_pages", 10)

        for page in range(1, min(max_pages + 1, 11)):
            try:
                url = f"{self.BASE_URL}/wn/zhaopin"
                params = {
                    "kd": keyword,
                    "city": city_name,
                    "pn": page,
                }

                headers = anti_crawl.get_headers()
                headers["Referer"] = f"{self.BASE_URL}/jobs/list_{keyword}"
                headers["X-Requested-With"] = "XMLHttpRequest"

                async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
                    resp = await client.get(url, params=params, headers=headers)

                    if resp.status_code != 200:
                        logger.warning(f"拉勾网请求失败: {resp.status_code}")
                        continue

                    soup = BeautifulSoup(resp.text, "html.parser")

                    list_config = rule_config.get("list_page", {})
                    item_selector = list_config.get("item_selector", ".item__10RTO")
                    items = soup.select(item_selector)

                    if not items:
                        items = soup.select(".con_list_item") or soup.select(".position-list li")

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
                logger.error(f"拉勾网第{page}页爬取异常: {e}")
                break

        return results

    def _parse_item(self, item, fields_config: dict) -> dict:
        if fields_config:
            return RuleParser.extract_fields(item, fields_config)

        title_el = item.select_one(".p_top h3") or item.select_one(".position_link h3")
        salary_el = item.select_one(".money") or item.select_one(".p_bot .li_b_l span")
        company_el = item.select_one(".company_name") or item.select_one(".company a")
        city_el = item.select_one(".add") or item.select_one(".p_top .add em")

        link = item.select_one("a")
        href = link.get("href", "") if link else ""
        source_id = href.split("/")[-1].replace(".html", "") if href else hashlib.md5(
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
