"""Pydantic 模式 - 职位"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class JobResponse(BaseModel):
    id: int
    source_site: str
    source_id: str
    title: str
    company_name: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    salary_raw: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    experience: Optional[str] = None
    education: Optional[str] = None
    job_type: Optional[str] = None
    skills: list[str] = []
    description: Optional[str] = None
    url: Optional[str] = None
    published_at: Optional[datetime] = None
    crawled_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class JobQuery(BaseModel):
    keyword: Optional[str] = None
    site: Optional[str] = None
    city: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    experience: Optional[str] = None
    education: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
