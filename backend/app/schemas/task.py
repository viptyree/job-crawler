"""Pydantic 模式 - 任务"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TaskCreate(BaseModel):
    rule_id: int = Field(..., description="规则ID")


class TaskResponse(BaseModel):
    id: int
    rule_id: int
    status: str = "pending"
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    total_count: int = 0
    success_count: int = 0
    error_count: int = 0
    log_text: Optional[str] = ""
    error_msg: Optional[str] = ""
    rule_name: Optional[str] = None
    rule_site: Optional[str] = None

    class Config:
        from_attributes = True
