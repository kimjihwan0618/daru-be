"""
종목 관련 비즈니스 로직.
"""
from sqlalchemy.ext.asyncio import AsyncSession


async def search_stocks(query: str, db: AsyncSession) -> list[dict]:
    """
    TODO(구현 필요): app/repositories/stock_repo.py 에서 Stock.name LIKE 검색
    """
    raise NotImplementedError


async def get_stock_with_price(code: str, db: AsyncSession) -> dict:
    """
    TODO(구현 필요):
    1. Stock 조회 (없으면 NotFoundException)
    2. app/external/stock_price_client.py 로 실시간 시세 조회 (캐시 우선 - Redis TTL 1분 권장)
    3. 관련 IssueCluster 조회 (related_stock_codes 에 code 포함)
    """
    raise NotImplementedError
