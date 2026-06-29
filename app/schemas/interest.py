"""
관심 키워드/종목 관련 스키마. 설계서 6.7 엔드포인트 명세 대응.
"""
from pydantic import BaseModel


class InterestItem(BaseModel):
    id: int
    type: str  # KEYWORD / STOCK
    value: str


class InterestCreateRequest(BaseModel):
    type: str  # KEYWORD / STOCK
    value: str


class InterestMigrateRequest(BaseModel):
    guest_session_id: str


class InterestMigrateResponse(BaseModel):
    migrated_count: int
