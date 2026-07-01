"""
교통 비즈니스 로직.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.commute import CommuteRoute
from app.repositories import commute_repo


async def list_routes(user_id: int, db: AsyncSession) -> list[CommuteRoute]:
    return await commute_repo.list_routes(user_id, db)


async def create_route(
    user_id: int,
    label: str,
    address: str,
    lat: float,
    lng: float,
    db: AsyncSession,
) -> CommuteRoute:
    route = await commute_repo.create_route(user_id, label, address, lat, lng, db)
    await db.commit()
    await db.refresh(route)
    return route


async def update_route(
    route_id: int,
    user_id: int,
    label: str,
    address: str,
    lat: float,
    lng: float,
    db: AsyncSession,
) -> CommuteRoute:
    route = await commute_repo.get_route(route_id, db)
    if not route:
        raise NotFoundException("경로를 찾을 수 없습니다.")
    if route.user_id != user_id:
        raise ForbiddenException()
    route = await commute_repo.update_route(route, label, address, lat, lng, db)
    await db.commit()
    await db.refresh(route)
    return route


async def delete_route(route_id: int, user_id: int, db: AsyncSession) -> None:
    route = await commute_repo.get_route(route_id, db)
    if not route:
        raise NotFoundException("경로를 찾을 수 없습니다.")
    if route.user_id != user_id:
        raise ForbiddenException()
    await commute_repo.delete_route(route_id, db)
    await db.commit()


async def check_commute(
    user_id: int | None,
    use_default: bool,
    origin_address: str | None,
    destination_address: str | None,
    db: AsyncSession,
) -> dict:
    """
    TODO(구현 필요):
    1. use_default=True && user_id 있으면 CommuteRoute(HOME/WORK) 조회해 좌표 사용
    2. 아니면 origin/destination 주소 geocoding (map_directions_client)
    3. 길찾기 API 호출 -> estimated_minutes, delay_minutes 계산
    4. commute_repo.save_query() 로 로그 저장
    """
    raise NotImplementedError
