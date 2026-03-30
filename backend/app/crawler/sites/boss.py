"""BOSS直聘适配器"""
import httpx
import asyncio
import random
import hashlib
import logging
from datetime import datetime
from bs4 import BeautifulSoup
from app.crawler.anti_crawl import AntiCrawl
from app.crawler.rule_parser import RuleParser

logger = logging.getLogger("crawler.boss")

# BOSS直聘城市编码
CITY_CODES = {
    "全国": "100010000", "北京": "101010100", "上海": "101020100",
    "广州": "101280100", "深圳": "101280600", "杭州": "101210100",
    "成都": "101270100", "南京": "101190100", "武汉": "101200100",
    "西安": "101110100", "苏州": "101190400", "长沙": "101250100",
    "天津": "101030100", "重庆": "101040100", "郑州": "101180100",
    "合肥": "101220100", "济南": "101120100", "青岛": "101120200",
    "大连": "101070200", "厦门": "101230200", "沈阳": "101070100",
    "昆明": "101290100", "福州": "101230100", "哈尔滨": "101050100",
    "珠海": "101280700", "佛山": "101280800", "东莞": "101281600",
}


class BossAdapter:
    """BOSS直聘爬虫适配器"""

    BASE_URL = "https://www.zhipin.com"

    async def fetch(self, keyword: str, city: str, rule_config: dict, anti_crawl: AntiCrawl) -> list[dict]:
        """爬取 BOSS直聘 职位列表"""
        results = []
        city_code = CITY_CODES.get(city, CITY_CODES.get("全国", "100010000"))
        max_pages = rule_config.get("list_page", {}).get("max_pages", 10)

        for page in range(1, min(max_pages + 1, 11)):  # 最多10页
            try:
                url = f"{self.BASE_URL}/web/geek/job"
                params = {
                    "query": keyword,
                    "city": city_code,
                    "page": page,
                }

                headers = anti_crawl.get_headers()
                headers["Referer"] = self.BASE_URL

                async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
                    resp = await client.get(url, params=params, headers=headers)

                    if resp.status_code == 403:
                        logger.warning(f"BOSS直聘请求被拒绝(403)，可能触发反爬")
                        break
                    if resp.status_code != 200:
                        logger.warning(f"BOSS直聘请求失败: {resp.status_code}")
                        continue

                    soup = BeautifulSoup(resp.text, "html.parser")

                    # 尝试解析职位列表
                    list_config = rule_config.get("list_page", {})
                    item_selector = list_config.get("item_selector", ".job-card-wrapper")
                    items = soup.select(item_selector)

                    if not items:
                        # 尝试备用选择器
                        items = soup.select(".job-list-box .job-card-wrapper")

                    if not items:
                        logger.info(f"BOSS直聘第{page}页未找到职位卡片，结束翻页")
                        break

                    fields_config = list_config.get("fields", {})
                    for item in items:
                        try:
                            job_data = self._parse_item(item, fields_config)
                            if job_data.get("title"):
                                results.append(job_data)
                        except Exception as e:
                            logger.debug(f"解析职位卡片失败: {e}")

                # 翻页间隔
                delay = anti_crawl.get_delay()
                await asyncio.sleep(delay)

            except Exception as e:
                logger.error(f"BOSS直聘第{page}页爬取异常: {e}")
                break

        return results

    def _parse_item(self, item, fields_config: dict) -> dict:
        """解析单个职位卡片"""
        if fields_config:
            return RuleParser.extract_fields(item, fields_config)

        # 默认解析逻辑
        title_el = item.select_one(".job-name") or item.select_one(".job-title .job-name")
        salary_el = item.select_one(".salary") or item.select_one(".job-info .salary")
        company_el = item.select_one(".company-name") or item.select_one(".company-info .name")
        city_el = item.select_one(".job-area") or item.select_one(".job-info .job-area")

        # 提取链接中的 ID
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
            "url": f"{self.BASE_URL}{href}" if href.startswith("/") else href,
            "skills": [],
            "experience": "",
            "education": "",
        }
