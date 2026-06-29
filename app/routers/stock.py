"""
종목 라우터. 설계서 6.5 엔드포인트 명세 대응.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.news import IssueListResponse
from app.schemas.stock import StockDetailResponse, StockSearchResult, WatchlistImpactItem

router = APIRouter(tags=["stock"])


@router.get("/stocks/search", response_model=ApiResponse[list[StockSearchResult]])
async def search_stocks(q: str = Query(..., min_length=1), db: AsyncSession = Depends(get_db)):
    """종목명/코드 검색(자동완성). 인증: Public."""
    # TODO(구현 필요): Stock.name LIKE 검색 (자모 분리 검색은 추후 고도화)
    raise NotImplementedError


@router.get("/stocks/{code}", response_model=ApiResponse[StockDetailResponse])
async def get_stock_detail(code: str, db: AsyncSession = Depends(get_db)):
    """종목 현재가/등락률 + 관련 뉴스 이슈. 인증: Public."""
    # TODO(구현 필요):
    # 1. Stock 조회 (없으면 404 NOT_FOUND)
    # 2. app/external/stock_price_client.py 로 실시간 시세 조회
    # 3. IssueCluster.related_stock_codes 에 code가 포함된 이슈 목록 조회
    raise NotImplementedError


@router.get("/stocks/{code}/news", response_model=ApiResponse[IssueListResponse])
async def get_stock_news(
    code: str,
    cursor: str | None = Query(default=None),
    limit: int = Query(default=10, le=50),
    db: AsyncSession = Depends(get_db),
):
    """특정 종목 관련 뉴스만 필터링. 인증: Public."""
    # TODO(구현 필요): IssueCluster.related_stock_codes 필터 + cursor 페이지네이션
    raise NotImplementedError


@router.get("/users/me/watchlist/market-impact", response_model=ApiResponse[list[WatchlistImpactItem]])
async def get_watchlist_market_impact(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """로그인 사용자의 관심 종목 "오늘의 영향" 카드. 인증: Required."""
    # TODO(구현 필요):
    # 1. UserInterest(type=STOCK) 조회
    # 2. 각 종목의 실시간 시세 + 관련 이슈 요약 조립
    raise NotImplementedError
