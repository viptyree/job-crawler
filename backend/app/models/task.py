"""ORM 模型 - 任务执行记录表"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from app.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_id = Column(Integer, ForeignKey("crawler_rules.id"), nullable=False, comment="关联规则ID")
    status = Column(String(20), default="pending", comment="状态: pending/running/success/failed/stopped")
    started_at = Column(DateTime, comment="开始时间")
    finished_at = Column(DateTime, comment="结束时间")
    total_count = Column(Integer, default=0, comment="总爬取条数")
    success_count = Column(Integer, default=0, comment="成功条数")
    error_count = Column(Integer, default=0, comment="失败条数")
    log_text = Column(Text, default="", comment="执行日志")
    error_msg = Column(Text, default="", comment="错误信息")
