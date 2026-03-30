"""前程无忧适配器"""
import httpx
import asyncio
import hashlib
import logging
from bs4 import BeautifulSoup
from app.crawler.anti_crawl import AntiCrawl
from app.crawler.rule_parser import RuleParser

logger = logging.getLogger("crawler.qianchen")

CITY_CODES = {
    "全国": "", "北京": "010000", "上海": "020000", "广州": "030200",
    "深圳": "040000", "杭州": "080200", "成都": "090200", "南京": "070200",
    "武汉": "180200", "西安": "200200", "苏州": "070300", "长沙": "190200",
    "天津": "050000", "重庆": "060000", "郑州": "170200",
}


class QianchenAdapter:
    """前程无忧爬虫适配器"""

    BASE_URL = "https://www.51job.com"
    SEARCH_URL = "https://search.51job.com/list"

    async def fetch(self, keyword: str, city: str, rule_config: dict, anti_crawl: AntiCrawl) -> list[dict]:
        """爬取前程无忧职位列表"""
        results = []
        city_code = CITY_CODES.get(city, "")
        max_pages = rule_config.get("list_page", {}).get("max_pages", 10)

        for page in range(1, min(max_pages + 1, 11)):
            try:
                url = f"{self.SEARCH_URL}/{city_code},000000,0000,00,9,99,{keyword},2,{page}.html"

                headers = anti_crawl.get_headers()
                headers["Referer"] = self.BASE_URL

                async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
                    resp = await client.get(url, headers=headers)

                    if resp.status_code != 200:
                        logger.warning(f"前程无忧请求失败: {resp.status_code}")
                        continue

                    soup = BeautifulSoup(resp.text, "html.parser")

                    list_config = rule_config.get("list_page", {})
                    item_selector = list_config.get("item_selector", ".j_joblist .e")
                    items = soup.select(item_selector)

                    if not items:
                        items = soup.select(".joblist-item") or soup.select(".el")

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
                logger.error(f"前程无忧第{page}页爬取异常: {e}")
                break

        return results

    def _parse_item(self, item, fields_config: dict) -> dict:
        if fields_config:
            return RuleParser.extract_fields(item, fields_config)

        title_el = item.select_one(".jname") or item.select_one(".t1 a")
        salary_el = item.select_one(".sal") or item.select_one(".t4")
        company_el = item.select_one(".cname") or item.select_one(".t2 a")
        city_el = item.select_one(".d") or item.select_one(".t3")

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
