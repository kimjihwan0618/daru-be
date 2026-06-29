"""
뉴스/이슈 라우터. 설계서 6.4 엔드포인트 명세 대응.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.schemas.common import ApiResponse
from app.schemas.news import IssueDetailResponse, IssueListResponse

router = APIRouter(prefix="/news", tags=["news"])


@router.get("/issues", response_model=ApiResponse[IssueListResponse])
async def list_issues(
    category: str | None = Query(default=None),
    cursor: str | None = Query(default=None),
    limit: int = Query(default=10, le=50),
    db: AsyncSession = Depends(get_db),
):
    """중복 제거된 이슈 목록. 인증: Public."""
    # TODO(구현 필요): app/repositories/news_repo.py 의 cursor 기반 페이지네이션 쿼리
    # IssueCluster.is_active=True, category 필터, created_at 기준 cursor 페이징
    raise NotImplementedError


@router.get("/issues/{issue_id}", response_model=ApiResponse[IssueDetailResponse])
async def get_issue_detail(issue_id: int, db: AsyncSession = Depends(get_db)):
    """이슈 상세 - 요약 + 원문 기사 목록. 인증: Public."""
    # TODO(구현 필요): IssueCluster + 연결된 RawArticle 목록 + related_stock_codes -> Stock 조인
    raise NotImplementedError


@router.get("/search", response_model=ApiResponse[IssueListResponse])
async def search_news(
    q: str = Query(..., min_length=1),
    cursor: str | None = Query(default=None),
    limit: int = Query(default=10, le=50),
    db: AsyncSession = Depends(get_db),
):
    """키워드로 뉴스/이슈 검색. 인증: Public."""
    # TODO(구현 필요): 1차 버전은 title/summary LIKE 검색, 추후 임베딩 기반 검색으로 고도화 가능
    raise NotImplementedError
