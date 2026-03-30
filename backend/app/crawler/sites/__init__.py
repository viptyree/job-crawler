"""平台适配器注册"""
from typing import Optional


def get_site_adapter(site: str) -> Optional[object]:
    """根据平台标识获取适配器实例"""
    adapters = {
        "boss": _get_boss,
        "zhilian": _get_zhilian,
        "qianchen": _get_qianchen,
        "lagou": _get_lagou,
    }
    factory = adapters.get(site)
    return factory() if factory else None


def _get_boss():
    from app.crawler.sites.boss import BossAdapter
    return BossAdapter()

def _get_zhilian():
    from app.crawler.sites.zhilian import ZhilianAdapter
    return ZhilianAdapter()

def _get_qianchen():
    from app.crawler.sites.qianchen import QianchenAdapter
    return QianchenAdapter()

def _get_lagou():
    from app.crawler.sites.lagou import LagouAdapter
    return LagouAdapter()
