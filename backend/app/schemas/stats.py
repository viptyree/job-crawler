"""Pydantic 模式 - 统计分析"""
from pydantic import BaseModel
from typing import Optional


class DashboardStats(BaseModel):
    total_jobs: int = 0
    today_new: int = 0
    total_companies: int = 0
    active_rules: int = 0
    running_tasks: int = 0
    site_distribution: dict = {}
    recent_trend: list = []


class SalaryTrendItem(BaseModel):
    date: str
    avg_salary: float
    min_salary: float
    max_salary: float
    count: int


class SkillHeatItem(BaseModel):
    skill: str
    count: int
    avg_salary: Optional[float] = None


class CityDistItem(BaseModel):
    city: str
    count: int
    avg_salary: Optional[float] = None
