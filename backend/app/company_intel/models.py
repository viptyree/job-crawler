"""ORM models for company intelligence."""
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class IntelCompany(Base):
    __tablename__ = "company_intel_companies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(300), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    aliases = relationship("IntelCompanyAlias", back_populates="company", cascade="all, delete-orphan")


class IntelCompanyAlias(Base):
    __tablename__ = "company_intel_aliases"
    __table_args__ = (UniqueConstraint("company_id", "alias", name="uq_company_intel_alias"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("company_intel_companies.id"), nullable=False)
    alias = Column(String(300), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    company = relationship("IntelCompany", back_populates="aliases")


class IntelQuery(Base):
    __tablename__ = "company_intel_queries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("company_intel_companies.id"), nullable=False)
    company_name = Column(String(300), nullable=False)
    platforms = Column(Text, default="[]")
    city = Column(String(100), default="")
    keyword = Column(String(200), default="")
    status = Column(String(50), default="pending")
    total_count = Column(Integer, default=0)
    error_message = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.now)
    finished_at = Column(DateTime)


class IntelJob(Base):
    __tablename__ = "company_intel_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    query_id = Column(Integer, ForeignKey("company_intel_queries.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("company_intel_companies.id"), nullable=False)
    platform = Column(String(50), nullable=False)
    company_name_raw = Column(String(300), nullable=False)
    job_title = Column(String(300), nullable=False)
    salary_raw = Column(String(100), default="")
    city = Column(String(100), default="")
    experience = Column(String(100), default="")
    education = Column(String(100), default="")
    source_url = Column(String(1000), default="")
    match_type = Column(String(50), default="mock")
    published_at = Column(DateTime, default=datetime.now)
    created_at = Column(DateTime, default=datetime.now)


class IntelPlatformAccount(Base):
    __tablename__ = "company_intel_platform_accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    platform = Column(String(50), unique=True, nullable=False)
    status = Column(String(50), default="not_configured")
    note = Column(Text, default="")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class IntelScore(Base):
    __tablename__ = "company_intel_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    query_id = Column(Integer, ForeignKey("company_intel_queries.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("company_intel_companies.id"), nullable=False)
    score = Column(Integer, nullable=False)
    level = Column(String(50), nullable=False)
    reason_text = Column(Text, default="")
    detail_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.now)

