"""ORM 模型 - 爬虫规则配置表"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from app.database import Base


class CrawlerRule(Base):
    __tablename__ = "crawler_rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, comment="规则名称")
    site = Column(String(50), nullable=False, comment="平台标识: boss/zhilian/qianchen/lagou")
    keywords = Column(Text, default="[]", comment="搜索关键词 JSON数组")
    cities = Column(Text, default="[]", comment="目标城市 JSON数组")
    rule_config = Column(Text, default="{}", comment="完整爬取规则 JSON")
    schedule = Column(String(100), default="", comment="Cron 表达式")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
