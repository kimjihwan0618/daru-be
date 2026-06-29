"""
사용자/설정 관련 스키마. 설계서 6.9 엔드포인트 명세 대응.
"""
from datetime import datetime

from pydantic import BaseModel


class UserProfileResponse(BaseModel):
    id: int
    email: str | None = None
    nickname: str
    provider: str
    profile_image_url: str | None = None
    created_at: datetime


class UserProfileUpdateRequest(BaseModel):
    nickname: str | None = None
    profile_image_url: str | None = None


class UserPreferencesResponse(BaseModel):
    morning_briefing_time: str
    push_enabled: bool


class UserPreferencesUpdateRequest(BaseModel):
    morning_briefing_time: str | None = None
    push_enabled: bool | None = None
