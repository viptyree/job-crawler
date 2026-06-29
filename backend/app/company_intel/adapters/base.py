"""Base adapter interfaces for company intelligence platforms."""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class CompanyIntelJobResult:
    platform: str
    company_name_raw: str
    job_title: str
    salary_raw: str
    city: str
    experience: str
    education: str
    source_url: str
    match_type: str = "mock"


class CompanyIntelAdapter(ABC):
    platform: str

    @abstractmethod
    async def search(self, company_name: str, aliases: list[str], city: str = "", keyword: str = "") -> list[CompanyIntelJobResult]:
        """Search company jobs on a platform."""

