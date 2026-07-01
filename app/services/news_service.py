"""
뉴스/이슈 비즈니스 로직.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.news import IssueCluster
from app.repositories import news_repo


async def list_issues(
    category: str | None,
    cursor: str | None,
    limit: int,
    db: AsyncSession,
) -> tuple[list[IssueCluster], str | None]:
    """
    TODO(구현 필요): news_repo.list_active_issues() cursor 페이지네이션 호출
    """
    raise NotImplementedError


async def get_issue_detail(issue_id: int, db: AsyncSession) -> IssueCluster:
    """
    TODO(구현 필요): news_repo.get_with_articles() 호출 후 NotFoundException 처리
    """
    raise NotImplementedError


async def search_issues(
    q: str,
    cursor: str | None,
    limit: int,
    db: AsyncSession,
) -> tuple[list[IssueCluster], str | None]:
    """
    TODO(구현 필요): news_repo.search() title/summary LIKE 검색
    """
    raise NotImplementedError
