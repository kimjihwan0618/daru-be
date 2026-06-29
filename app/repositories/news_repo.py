"""
News/Issue 관련 DB 접근 캡슐화.
cursor 기반 페이지네이션 구현 시 이 파일에 헬퍼를 모아둔다.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.news import IssueCluster


async def get_issue_by_id(issue_id: int, db: AsyncSession) -> IssueCluster | None:
    result = await db.execute(select(IssueCluster).where(IssueCluster.id == issue_id))
    return result.scalar_one_or_none()


async def list_active_issues(
    category: str | None,
    cursor_id: int | None,
    limit: int,
    db: AsyncSession,
) -> list[IssueCluster]:
    """
    TODO(구현 필요):
    1. is_active=True 필터
    2. category 있으면 IssueCluster.category == category 추가 필터
    3. cursor_id 있으면 IssueCluster.id < cursor_id (id 내림차순 페이징 가정)
    4. order_by(IssueCluster.id.desc()).limit(limit)
    5. cursor 인코딩/디코딩은 base64(json) 권장 - 설계서 5.6 예시(eyJpZCI6MTIzfQ)가 그 형태
    """
    raise NotImplementedError


# TODO(구현 필요): search_issues(키워드 검색), get_issues_by_stock_code 등 추가
