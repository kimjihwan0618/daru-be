"""
사용자 및 관심사 모델.
설계서 4.1 - users / user_interests / guest_interests 대응.
"""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("provider", "provider_id", name="uq_users_provider_provider_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    nickname: Mapped[str] = mapped_column(String(50))
    provider: Mapped[str] = mapped_column(String(20))  # kakao / naver / google / local
    provider_id: Mapped[str] = mapped_column(String(255))
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)  # provider="local" 회원가입 유저만 사용
    profile_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    interests: Mapped[list["UserInterest"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class UserInterest(Base):
    """로그인 사용자의 영구 관심 키워드/종목. 설계서 6.7 /interests 대응."""

    __tablename__ = "user_interests"
    __table_args__ = (UniqueConstraint("user_id", "type", "value", name="uq_user_interests_user_id_type_value"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    type: Mapped[str] = mapped_column(String(20))  # KEYWORD / STOCK
    value: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="interests")


class GuestInterest(Base):
    """비로그인 임시 관심 키워드/종목. TTL 후 만료. 설계서 5.3 게스트 식별 참고."""

    __tablename__ = "guest_interests"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_token: Mapped[str] = mapped_column(String(64), index=True)
    type: Mapped[str] = mapped_column(String(20))
    value: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime)

    # TODO(구현 필요): workers/tasks 에서 expires_at 지난 row 주기적 삭제
