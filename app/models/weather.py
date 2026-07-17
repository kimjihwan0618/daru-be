"""
날씨 관련 모델.
"""
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class WeatherFavorite(Base):
    """로그인 사용자가 등록한 즐겨찾기 날씨 지역 (최대 3개, 서비스 레이어에서 제한)."""

    __tablename__ = "weather_favorites"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    label: Mapped[str] = mapped_column(String(50))  # 예: "집", "회사", "부산 본가"
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
