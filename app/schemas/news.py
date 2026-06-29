"""
뉴스/이슈 관련 스키마. 설계서 6.4 엔드포인트 명세 대응.
"""
from datetime import datetime

from pydantic import BaseModel


class IssueSummary(BaseModel):
    id: int
    category: str | None = None
    article_count: int
    title: str
    thumbnail_url: str | None = None
    source_logos: list[str] = []
    extra_source_count: int = 0


class IssueListResponse(BaseModel):
    total_raw_articles: int
    total_issues: int
    issues: list[IssueSummary]
    next_cursor: str | None = None


class RelatedStock(BaseModel):
    code: str
    name: str


class ArticleBrief(BaseModel):
    title: str
    source: str
    url: str
    published_at: datetime


class IssueDetailResponse(BaseModel):
    id: int
    title: str
    summary: str | None = None
    category: str | None = None
    related_stocks: list[RelatedStock] = []
    articles: list[ArticleBrief] = []
