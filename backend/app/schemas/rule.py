"""Pydantic 模式 - 爬虫规则"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RuleConfigBase(BaseModel):
    """规则配置基础模式"""
    name: str = Field(..., description="规则名称", examples=["BOSS直聘-Python岗"])
    site: str = Field(..., description="平台标识", examples=["boss"])
    keywords: list[str] = Field(default=[], description="搜索关键词")
    cities: list[str] = Field(default=[], description="目标城市")
    rule_config: dict = Field(default={}, description="完整爬取规则 JSON")
    schedule: str = Field(default="", description="Cron 表达式")
    is_active: bool = Field(default=True, description="是否启用")


class RuleCreate(RuleConfigBase):
    pass


class RuleUpdate(BaseModel):
    name: Optional[str] = None
    site: Optional[str] = None
    keywords: Optional[list[str]] = None
    cities: Optional[list[str]] = None
    rule_config: Optional[dict] = None
    schedule: Optional[str] = None
    is_active: Optional[bool] = None


class RuleResponse(RuleConfigBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
