"""Platform adapter registry."""
from app.company_intel.adapters.base import CompanyIntelAdapter
from app.company_intel.adapters.boss_adapter import BossAdapter
from app.company_intel.adapters.job51_adapter import Job51Adapter
from app.company_intel.adapters.lagou_adapter import LagouAdapter
from app.company_intel.adapters.playwright_adapter import PlaywrightCompanyIntelAdapter
from app.company_intel.adapters.zhilian_adapter import ZhilianAdapter


PLATFORM_LABELS = {
    "boss": "BOSS直聘",
    "zhilian": "智联招聘",
    "job51": "前程无忧",
    "lagou": "拉勾网",
}


def get_adapters(platforms: list[str] | None = None) -> list[CompanyIntelAdapter]:
    registry = {
        "boss": BossAdapter(),
        "zhilian": ZhilianAdapter(),
        "job51": Job51Adapter(),
        "lagou": LagouAdapter(),
    }
    selected = platforms or list(registry.keys())
    return [registry[name] for name in selected if name in registry]


def get_real_adapters(platforms: list[str] | None = None) -> list[CompanyIntelAdapter]:
    selected = platforms or list(PLATFORM_LABELS.keys())
    return [PlaywrightCompanyIntelAdapter(name) for name in selected if name in PLATFORM_LABELS]


def list_platforms() -> list[dict]:
    return [{"value": key, "label": label} for key, label in PLATFORM_LABELS.items()]
