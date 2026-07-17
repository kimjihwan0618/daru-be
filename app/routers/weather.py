"""
날씨 라우터.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.weather import (
    FavoriteWeatherItem,
    WeatherFavoriteCreateRequest,
    WeatherFavoriteResponse,
    WeatherResponse,
)
from app.services import weather_service

router = APIRouter(tags=["weather"])


@router.get("/weather", response_model=ApiResponse[WeatherResponse])
async def get_current_weather(
    lat: float | None = Query(default=None),
    lng: float | None = Query(default=None),
):
    """현재 날씨 조회. 인증: Public. lat/lng 미지정 시 기본 지역(설정값) 사용."""
    result = await weather_service.get_weather(lat, lng)
    return ApiResponse(success=True, data=result)


@router.get("/users/me/weather-favorites", response_model=ApiResponse[list[WeatherFavoriteResponse]])
async def list_weather_favorites(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """즐겨찾기 날씨 지역 목록. 인증: Required."""
    favorites = await weather_service.list_favorites(current_user.id, db)
    return ApiResponse(
        success=True,
        data=[
            WeatherFavoriteResponse(id=f.id, label=f.label, latitude=f.latitude, longitude=f.longitude)
            for f in favorites
        ],
    )


@router.get(
    "/users/me/weather-favorites/weather", response_model=ApiResponse[list[FavoriteWeatherItem]]
)
async def get_weather_favorites_weather(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """즐겨찾기 지역들의 현재 날씨. 인증: Required. 즐겨찾기가 없으면 빈 배열 반환."""
    items = await weather_service.get_favorites_weather(current_user.id, db)
    return ApiResponse(success=True, data=[FavoriteWeatherItem(**item) for item in items])


@router.post(
    "/users/me/weather-favorites", response_model=ApiResponse[WeatherFavoriteResponse], status_code=201
)
async def create_weather_favorite(
    body: WeatherFavoriteCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """즐겨찾기 날씨 지역 추가 (최대 3개). 인증: Required."""
    favorite = await weather_service.add_favorite(
        current_user.id, body.label, body.latitude, body.longitude, db
    )
    return ApiResponse(
        success=True,
        data=WeatherFavoriteResponse(
            id=favorite.id, label=favorite.label, latitude=favorite.latitude, longitude=favorite.longitude
        ),
    )


@router.delete("/users/me/weather-favorites/{favorite_id}", response_model=ApiResponse[None])
async def delete_weather_favorite(
    favorite_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """즐겨찾기 날씨 지역 삭제. 인증: Required."""
    await weather_service.remove_favorite(favorite_id, current_user.id, db)
    return ApiResponse(success=True, data=None)
