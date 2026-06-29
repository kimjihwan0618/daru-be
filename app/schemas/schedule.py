"""
일정 관련 스키마. 설계서 6.8 엔드포인트 명세 대응.
"""
from datetime import datetime

from pydantic import BaseModel


class ScheduleItem(BaseModel):
    id: int
    time: str
    title: str
    category: str  # MARKET / ECONOMIC / COMMUTE / CUSTOM


class ScheduleCreateRequest(BaseModel):
    title: str
    scheduled_time: datetime
    category: str = "CUSTOM"
