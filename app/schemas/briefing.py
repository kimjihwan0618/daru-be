"""
브리핑 관련 스키마. 설계서 6.2 / 6.3 엔드포인트 명세 대응.
"""
from datetime import datetime

from pydantic import BaseModel


class WeatherInfo(BaseModel):
    temp_c: float
    condition: str


class KeyChange(BaseModel):
    id: int
    icon: str
    text: str
    issue_id: int | None = None


class TodayBriefingResponse(BaseModel):
    briefing_date: str
    time_slot: str
    greeting: str
    headline: str
    subtext: str | None = None
    weather: WeatherInfo | None = None
    summary_text: str
    is_personalized: bool
    key_changes: list[KeyChange]
    updated_at: datetime


class EvidenceArticle(BaseModel):
    title: str
    source: str
    url: str
    published_at: datetime


class ChangeEvidenceResponse(BaseModel):
    change_id: int
    explanation: str
    source_articles: list[EvidenceArticle]


class ShareBriefingResponse(BaseModel):
    share_url: str
    expires_at: datetime


class BriefingFeedbackRequest(BaseModel):
    is_helpful: bool


class TopicSummary(BaseModel):
    code: str
    label: str
    article_count_today: int


class TopicIssue(BaseModel):
    id: int
    title: str
    article_count: int
    thumbnail_url: str | None = None
    source_logos: list[str] = []
    updated_at: datetime


class TopicBriefingResponse(BaseModel):
    topic_code: str
    label: str
    summary_text: str
    issues: list[TopicIssue]
