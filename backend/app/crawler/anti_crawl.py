"""反爬策略模块"""
import random
from app.config import USER_AGENTS


class AntiCrawl:
    """反爬策略：UA轮换、随机延迟、代理池"""

    def __init__(self):
        self.user_agents = USER_AGENTS.copy()
        self.proxies: list[str] = []
        self._ua_index = 0

    def get_headers(self) -> dict:
        """获取随机请求头"""
        ua = random.choice(self.user_agents)
        return {
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
        }

    def get_proxy(self) -> str | None:
        """获取随机代理"""
        if not self.proxies:
            return None
        return random.choice(self.proxies)

    def get_delay(self, min_delay: float = 2.0, max_delay: float = 5.0) -> float:
        """获取随机延迟时间"""
        return random.uniform(min_delay, max_delay)

    def get_viewport(self) -> dict:
        """获取随机视口尺寸"""
        viewports = [
            {"width": 1920, "height": 1080},
            {"width": 1440, "height": 900},
            {"width": 1366, "height": 768},
            {"width": 1536, "height": 864},
            {"width": 1280, "height": 720},
        ]
        return random.choice(viewports)
