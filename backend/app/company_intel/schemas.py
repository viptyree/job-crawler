"""Pydantic schemas for company intelligence."""
from datetime import datetime
from pydantic import BaseModel, Field


class AliasGenerateRequest(BaseModel):
    company_name: str = Field(min_length=1)


class AliasGenerateResponse(BaseModel):
    aliases: list[str]


class CompanySearchRequest(BaseModel):
    company_name: str = Field(min_length=1)
    platforms: list[str] = Field(default_factory=lambda: ["boss", "zhilian", "job51", "lagou"])
    city: str = ""
    keyword: str = ""
    search_mode: str = "mock"


class CompanySearchResponse(BaseModel):
    query_id: int
    company_id: int
    status: str
    total_count: int


class QueryResponse(BaseModel):
    id: int
    company_id: int
    company_name: str
    platforms: list[str]
    city: str
    keyword: str
    status: str
    total_count: int
    error_message: str
    created_at: datetime | None
    finished_at: datetime | None


class JobResponse(BaseModel):
    id: int
    query_id: int
    company_id: int
    platform: str
    company_name_raw: str
    job_title: str
    salary_raw: str
    city: str
    experience: str
    education: str
    source_url: str
    match_type: str
    created_at: datetime | None


class ScoreResponse(BaseModel):
    id: int
    query_id: int
    company_id: int
    score: int
    level: str
    reason_text: str
    detail: dict
    created_at: datetime | None
