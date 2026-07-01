"""
일정 관련 스키마. 설계서 6.8 엔드포인트 명세 대응.
"""
from datetime import date, datetime

from pydantic import BaseModel


class ScheduleItem(BaseModel):
    id: int
    title: str
    scheduled_time: datetime
    category: str  # MARKET / ECONOMIC / COMMUTE / CUSTOM
    schedule_date: date


class ScheduleCreateRequest(BaseModel):
    title: str
    scheduled_time: datetime
    category: str = "CUSTOM"
