"""
교통 비즈니스 로직.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ForbiddenException, NotFoundException
from app.external import map_directions_client
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
    1. use_default=True && 로그인 사용자면 CommuteRoute(HOME/WORK) 좌표 사용
    2. origin/destination 주소가 있으면 geocoding
    3. 둘 다 없으면(비로그인 기본값) 설정값(config)의 기본 경로 사용
    4. 길찾기 API 호출 -> estimated_minutes, delay_minutes 계산
    5. commute_repo.save_query() 로 로그 저장
    """
    if use_default and user_id:
        routes = await commute_repo.list_routes(user_id, db)
        home = next((r for r in routes if r.label == "HOME"), None)
        work = next((r for r in routes if r.label == "WORK"), None)
        if not home or not work:
            raise NotFoundException("등록된 집/회사 경로가 없습니다.")
        origin_label, origin_lat, origin_lng = home.address, home.latitude, home.longitude
        dest_label, dest_lat, dest_lng = work.address, work.latitude, work.longitude
    elif origin_address and destination_address:
        origin_label = origin_address
        dest_label = destination_address
        origin_lat, origin_lng = await map_directions_client.geocode(origin_address)
        dest_lat, dest_lng = await map_directions_client.geocode(destination_address)
    else:
        origin_label = settings.DEFAULT_COMMUTE_ORIGIN_LABEL
        origin_lat, origin_lng = settings.DEFAULT_COMMUTE_ORIGIN_LAT, settings.DEFAULT_COMMUTE_ORIGIN_LNG
        dest_label = settings.DEFAULT_COMMUTE_DESTINATION_LABEL
        dest_lat, dest_lng = settings.DEFAULT_COMMUTE_DESTINATION_LAT, settings.DEFAULT_COMMUTE_DESTINATION_LNG

    directions = await map_directions_client.get_directions(origin_lat, origin_lng, dest_lat, dest_lng)

    await commute_repo.save_query(
        user_id=user_id,
        origin_address=origin_label,
        destination_address=dest_label,
        origin_lat=origin_lat,
        origin_lng=origin_lng,
        dest_lat=dest_lat,
        dest_lng=dest_lng,
        estimated_minutes=directions["estimated_minutes"],
        delay_minutes=directions["delay_minutes"],
        db=db,
    )
    await db.commit()

    return {
        "origin": {"label": origin_label, "lat": origin_lat, "lng": origin_lng},
        "destination": {"label": dest_label, "lat": dest_lat, "lng": dest_lng},
        "estimated_minutes": directions["estimated_minutes"],
        "delay_minutes": directions["delay_minutes"],
        "delay_reason": directions["delay_reason"],
        "recommended_departure_time": None,
        "route_polyline": directions["route_polyline"],
    }
