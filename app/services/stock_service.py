"""
종목 관련 비즈니스 로직.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import NotFoundException
from app.external import stock_price_client
from app.repositories import interest_repo, news_repo, stock_repo


async def search_stocks(query: str, db: AsyncSession) -> list[dict]:
    stocks = await stock_repo.search_by_name(query, db)
    return [{"code": s.code, "name": s.name, "market": s.market} for s in stocks]


async def get_stock_with_price(code: str, db: AsyncSession) -> dict:
    stock = await stock_repo.get_by_code(code, db)
    if not stock:
        raise NotFoundException(message="해당 종목을 찾을 수 없습니다.", code="STOCK_NOT_FOUND")

    price = await stock_price_client.get_current_price(code)
    history = await stock_price_client.get_price_history(code, days=7)
    issues = await news_repo.get_issues_by_stock_code(code, cursor_id=None, limit=5, db=db)

    return {
        "code": stock.code,
        "name": stock.name,
        "current_price": price["current_price"],
        "change_rate": price["change_rate"],
        "change_direction": price["change_direction"],
        "price_history_7d": history,
        "related_issues": [{"id": i.id, "title": i.title} for i in issues],
    }


async def get_top_stocks(market: str, db: AsyncSession) -> list[dict]:
    """설정값(config.DEFAULT_TOP_STOCKS)에 고정된 종목들의 현재 시세 조회. market은 현재 'domestic'만 지원."""
    items = []
    for code in settings.DEFAULT_TOP_STOCKS:
        stock = await stock_repo.get_by_code(code, db)
        if not stock:
            continue
        price = await stock_price_client.get_current_price(code)
        items.append(
            {
                "code": stock.code,
                "name": stock.name,
                "market": stock.market,
                "current_price": price["current_price"],
                "change_rate": price["change_rate"],
                "change_direction": price["change_direction"],
            }
        )
    return items


async def get_watchlist_market_impact(user_id: int, db: AsyncSession) -> list[dict]:
    interests = await interest_repo.list_user_interests(user_id, db)
    stock_codes = [i.value for i in interests if i.type == "STOCK"]

    items = []
    for code in stock_codes:
        stock = await stock_repo.get_by_code(code, db)
        if not stock:
            continue
        price = await stock_price_client.get_current_price(code)
        history = await stock_price_client.get_price_history(code, days=7)
        issues = await news_repo.get_issues_by_stock_code(code, cursor_id=None, limit=1, db=db)

        items.append(
            {
                "stock": {"code": stock.code, "name": stock.name, "market": stock.market},
                "related_issue_summary": issues[0].summary if issues else None,
                "current_price": price["current_price"],
                "change_rate": price["change_rate"],
                "change_direction": price["change_direction"],
                "sparkline_7d": history,
            }
        )
    return items
