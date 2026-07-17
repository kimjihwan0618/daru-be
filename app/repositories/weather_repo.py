"""
날씨 즐겨찾기 DB 접근.
"""
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.weather import WeatherFavorite


async def list_favorites(user_id: int, db: AsyncSession) -> list[WeatherFavorite]:
    result = await db.execute(
        select(WeatherFavorite).where(WeatherFavorite.user_id == user_id).order_by(WeatherFavorite.id)
    )
    return list(result.scalars().all())


async def get_favorite(favorite_id: int, db: AsyncSession) -> WeatherFavorite | None:
    result = await db.execute(select(WeatherFavorite).where(WeatherFavorite.id == favorite_id))
    return result.scalar_one_or_none()


async def create_favorite(
    user_id: int, label: str, lat: float, lng: float, db: AsyncSession
) -> WeatherFavorite:
    favorite = WeatherFavorite(user_id=user_id, label=label, latitude=lat, longitude=lng)
    db.add(favorite)
    await db.flush()
    return favorite


async def delete_favorite(favorite_id: int, db: AsyncSession) -> None:
    await db.execute(delete(WeatherFavorite).where(WeatherFavorite.id == favorite_id))
