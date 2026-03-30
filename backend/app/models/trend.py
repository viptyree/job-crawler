"""ORM 模型 - 行业趋势聚合表"""
from sqlalchemy import Column, Integer, String, Float, Date, Text
from app.database import Base


class Trend(Base):
    __tablename__ = "trends"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stat_date = Column(Date, nullable=False, comment="统计日期")
    stat_type = Column(String(50), nullable=False, comment="统计类型: salary/skill/city/company")
    dimension = Column(String(200), nullable=False, comment="维度值")
    site = Column(String(50), comment="来源平台（null=全平台）")
    value = Column(Float, comment="统计值")
    extra = Column(Text, comment="附加数据 JSON")
