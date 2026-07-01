"""
뉴스/이슈 라우터. 설계서 6.4 엔드포인트 명세 대응.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.schemas.common import ApiResponse
from app.schemas.news import IssueDetailResponse, IssueListResponse
from app.services import news_service

router = APIRouter(prefix="/news", tags=["news"])


@router.get("/issues", response_model=ApiResponse[IssueListResponse])
async def list_issues(
    category: str | None = Query(default=None),
    cursor: str | None = Query(default=None),
    limit: int = Query(default=10, le=50),
    db: AsyncSession = Depends(get_db),
):
    """중복 제거된 이슈 목록. 인증: Public."""
    # TODO(구현 필요): news_service.list_issues() 구현 후 주석 해제
    raise NotImplementedError


@router.get("/issues/{issue_id}", response_model=ApiResponse[IssueDetailResponse])
async def get_issue_detail(issue_id: int, db: AsyncSession = Depends(get_db)):
    """이슈 상세 - 요약 + 원문 기사 목록. 인증: Public."""
    # TODO(구현 필요): news_service.get_issue_detail() 구현 후 주석 해제
    raise NotImplementedError


@router.get("/search", response_model=ApiResponse[IssueListResponse])
async def search_news(
    q: str = Query(..., min_length=1),
    cursor: str | None = Query(default=None),
    limit: int = Query(default=10, le=50),
    db: AsyncSession = Depends(get_db),
):
    """키워드로 뉴스/이슈 검색. 인증: Public."""
    # TODO(구현 필요): news_service.search_issues() 구현 후 주석 해제
    raise NotImplementedError
