"""ORM 模型 - 公司信息表"""
from sqlalchemy import Column, Integer, String, Text
from app.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(300), unique=True, nullable=False, comment="公司名称")
    industry = Column(String(200), comment="行业")
    scale = Column(String(100), comment="公司规模")
    stage = Column(String(100), comment="融资阶段")
    description = Column(Text, comment="公司简介")
    logo_url = Column(String(500), comment="Logo URL")
