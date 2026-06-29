"""
일정 모델. 설계서 4.1 / 6.8 - schedules 대응.
user_id가 null이면 시스템 공통 일정(증시개장, 경제지표 발표 등).
"""
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Schedule(Base):
    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    title: Mapped[str] = mapped_column(String(100))
    scheduled_time: Mapped[datetime] = mapped_column(DateTime)
    category: Mapped[str] = mapped_column(String(20))  # MARKET / ECONOMIC / COMMUTE / CUSTOM
    schedule_date: Mapped[date] = mapped_column(Date, index=True)

    # TODO(구현 필요): "예상 퇴근" 같이 commute_routes 기반으로 동적 계산되는 항목은
    # DB row가 아니라 응답 조립 시점에 합성할지, 매일 배치로 row 생성할지 정책 결정 필요
