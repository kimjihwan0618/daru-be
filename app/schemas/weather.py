"""
날씨 관련 스키마.
"""
from pydantic import BaseModel

from app.schemas.briefing import WeatherInfo
from app.schemas.commute import LocationPoint


class WeatherResponse(BaseModel):
    location: LocationPoint
    weather: WeatherInfo


class WeatherFavoriteCreateRequest(BaseModel):
    label: str
    latitude: float
    longitude: float


class WeatherFavoriteResponse(BaseModel):
    id: int
    label: str
    latitude: float
    longitude: float


class FavoriteWeatherItem(BaseModel):
    favorite: WeatherFavoriteResponse
    weather: WeatherInfo
