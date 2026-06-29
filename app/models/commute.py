"""
교통 관련 모델. 설계서 4.1 - commute_routes / commute_queries 대응.
"""
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CommuteRoute(Base):
    """로그인 사용자가 등록한 집/회사 경로. 설계서 6.6 /users/me/commute-routes 대응."""

    __tablename__ = "commute_routes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    label: Mapped[str] = mapped_column(String(20))  # HOME / WORK
    address: Mapped[str] = mapped_column(String(255))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    is_default: Mapped[bool] = mapped_column(default=True)

    # TODO(구현 필요): (user_id, label) unique 제약 - 집/회사 각 1개로 제한할지 여부는 기획 확인


class CommuteQuery(Base):
    """일회성 교통조회 로그 (비로그인 포함). 설계서 6.6 POST /commute/check 대응."""

    __tablename__ = "commute_queries"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    origin_address: Mapped[str] = mapped_column(String(255))
    destination_address: Mapped[str] = mapped_column(String(255))
    origin_lat: Mapped[float] = mapped_column(Float)
    origin_lng: Mapped[float] = mapped_column(Float)
    dest_lat: Mapped[float] = mapped_column(Float)
    dest_lng: Mapped[float] = mapped_column(Float)

    estimated_minutes: Mapped[int] = mapped_column(Integer)
    delay_minutes: Mapped[int] = mapped_column(Integer, default=0)

    queried_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # TODO(구현 필요): 외부 지도 API 응답 캐싱(같은 출발/도착 좌표 + 짧은 시간 내 재요청 시 캐시 활용)
