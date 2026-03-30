"""Models 包"""
from app.models.crawler_rule import CrawlerRule
from app.models.task import Task
from app.models.job import Job
from app.models.company import Company
from app.models.trend import Trend

__all__ = ["CrawlerRule", "Task", "Job", "Company", "Trend"]
