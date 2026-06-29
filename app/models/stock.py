"""
종목 마스터 모델. 설계서 4.1 - stocks 대응.
시세 자체는 외부 API에서 실시간 조회하므로 DB에는 종목 메타데이터만 둔다.
"""
from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Stock(Base):
    __tablename__ = "stocks"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(10), unique=True, index=True)  # 예: 005930
    name: Mapped[str] = mapped_column(String(100), index=True)  # 예: 삼성전자
    market: Mapped[str] = mapped_column(String(10))  # KOSPI / KOSDAQ
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # TODO(구현 필요): 종목명 검색 시 자모 분리 검색(초성검색) 지원하려면
    # 별도 검색 인덱스(예: trigram, 혹은 검색엔진) 고려
