"""
브리핑 모델. 설계서 4.1 - daily_briefings / user_briefings / shared_briefings 대응.
"""
from datetime import date, datetime

from sqlalchemy import JSON, Date, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DailyBriefing(Base):
    """공통 브리핑. 비로그인 포함 전체 사용자가 공유. 설계서 4.1 / 6.2 대응."""

    __tablename__ = "daily_briefings"

    id: Mapped[int] = mapped_column(primary_key=True)
    briefing_date: Mapped[date] = mapped_column(Date, index=True)
    time_slot: Mapped[str] = mapped_column(String(10))  # MORNING / EVENING
    summary_text: Mapped[str] = mapped_column(Text)

    # issue_clusters.id 목록. SQLite는 array 미지원 -> JSON 직렬화.
    top_issue_ids: Mapped[list[int]] = mapped_column(JSON, default=list)

    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # TODO(구현 필요): (briefing_date, time_slot) unique 제약


class UserBriefing(Base):
    """로그인 사용자 개인화 브리핑 캐시. 설계서 4.1 / 7.3 RAG 결과물 저장 위치."""

    __tablename__ = "user_briefings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    briefing_date: Mapped[date] = mapped_column(Date, index=True)
    time_slot: Mapped[str] = mapped_column(String(10))
    personalized_text: Mapped[str] = mapped_column(Text)
    matched_issue_ids: Mapped[list[int]] = mapped_column(JSON, default=list)
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # TODO(구현 필요): (user_id, briefing_date, time_slot) unique 제약
    # TODO(구현 필요): 캐시 미스 시 온디맨드 생성하는 fallback 로직 - services/briefing_service.py


class SharedBriefing(Base):
    """브리핑 공유 링크. 설계서 4.1 / 6.2 POST /briefings/today/share 대응."""

    __tablename__ = "shared_briefings"

    id: Mapped[int] = mapped_column(primary_key=True)
    briefing_type: Mapped[str] = mapped_column(String(10))  # DAILY / USER
    briefing_ref_id: Mapped[int] = mapped_column()
    share_token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # TODO(구현 필요): 공유 시점 스냅샷(JSON) 컬럼 추가 검토
    # - 원본 브리핑이 나중에 갱신/삭제돼도 공유 링크는 당시 내용을 그대로 보여줘야 하므로
