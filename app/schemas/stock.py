"""
종목 관련 스키마. 설계서 6.5 엔드포인트 명세 대응.
"""
from pydantic import BaseModel


class StockSearchResult(BaseModel):
    code: str
    name: str
    market: str


class RelatedIssueBrief(BaseModel):
    id: int
    title: str


class StockDetailResponse(BaseModel):
    code: str
    name: str
    current_price: float
    change_rate: float
    change_direction: str  # UP / DOWN / FLAT
    price_history_7d: list[float] = []
    related_issues: list[RelatedIssueBrief] = []


class WatchlistImpactItem(BaseModel):
    stock: StockSearchResult
    related_issue_summary: str | None = None
    current_price: float
    change_rate: float
    change_direction: str
    sparkline_7d: list[float] = []
