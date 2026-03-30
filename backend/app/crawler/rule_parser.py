"""JSON 规则解析器"""
import re
from typing import Any


class RuleParser:
    """解析 JSON 规则配置，用于从页面提取数据"""

    @staticmethod
    def build_url(url_template: str, params: dict) -> str:
        """构造URL"""
        url = url_template
        for key, value in params.items():
            url = url.replace(f"{{{key}}}", str(value))
        return url

    @staticmethod
    def extract_field(element, field_config) -> str:
        """根据配置从元素中提取字段值"""
        if isinstance(field_config, str):
            # 简单的CSS选择器
            target = element.select_one(field_config)
            return target.get_text(strip=True) if target else ""
        elif isinstance(field_config, dict):
            selector = field_config.get("selector", "")
            attr = field_config.get("attr", "")
            target = element.select_one(selector) if selector else element
            if target:
                if attr:
                    return target.get(attr, "")
                return target.get_text(strip=True)
        return ""

    @staticmethod
    def extract_fields(element, fields_config: dict) -> dict:
        """从元素中提取所有字段"""
        result = {}
        for field_name, config in fields_config.items():
            result[field_name] = RuleParser.extract_field(element, config)
        return result
