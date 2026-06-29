"""Generate practical company search aliases."""

LEGAL_SUFFIXES = [
    "有限责任公司",
    "股份有限公司",
    "集团有限公司",
    "有限公司",
    "股份公司",
    "集团",
]

WEAK_SUFFIXES = [
    "信息技术",
    "网络科技",
    "智能科技",
    "科技",
    "技术",
    "信息",
    "网络",
]

REGION_PREFIXES = [
    "广州", "深圳", "上海", "北京", "杭州", "成都", "武汉", "南京", "苏州", "重庆",
    "天津", "西安", "长沙", "郑州", "佛山", "东莞", "厦门", "青岛", "宁波",
]


def _strip_suffix(value: str, suffixes: list[str]) -> str:
    for suffix in suffixes:
        if value.endswith(suffix) and len(value) > len(suffix):
            return value[: -len(suffix)]
    return value


def generate_aliases(company_name: str) -> list[str]:
    name = (company_name or "").strip()
    if not name:
        return []

    aliases: list[str] = []

    def add(value: str) -> None:
        value = value.strip()
        if value and value not in aliases:
            aliases.append(value)

    add(name)
    without_legal = _strip_suffix(name, LEGAL_SUFFIXES)
    add(without_legal)

    without_region = without_legal
    for prefix in REGION_PREFIXES:
        if without_region.startswith(prefix) and len(without_region) > len(prefix):
            without_region = without_region[len(prefix):]
            break
    add(without_region)

    add(_strip_suffix(without_region, WEAK_SUFFIXES))
    add(_strip_suffix(without_legal, WEAK_SUFFIXES))

    return aliases

