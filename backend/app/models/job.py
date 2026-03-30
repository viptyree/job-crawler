"""ORM 模型 - 职位信息表"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, UniqueConstraint
from app.database import Base


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (
        UniqueConstraint("source_site", "source_id", name="uq_source"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_site = Column(String(50), nullable=False, comment="来源平台")
    source_id = Column(String(200), nullable=False, comment="平台原始ID")
    title = Column(String(500), nullable=False, comment="职位名称")
    company_name = Column(String(300), comment="公司名称")
    city = Column(String(100), comment="城市")
    district = Column(String(100), comment="区域")
    salary_raw = Column(String(100), comment="原始薪资字符串")
    salary_min = Column(Integer, comment="最低月薪(元)")
    salary_max = Column(Integer, comment="最高月薪(元)")
    experience = Column(String(100), comment="经验要求")
    education = Column(String(100), comment="学历要求")
    job_type = Column(String(100), comment="职位类型")
    skills = Column(Text, default="[]", comment="技能标签 JSON数组")
    description = Column(Text, comment="职位描述")
    url = Column(String(1000), comment="原始链接")
    published_at = Column(DateTime, comment="发布时间")
    crawled_at = Column(DateTime, default=datetime.now, comment="爬取时间")
