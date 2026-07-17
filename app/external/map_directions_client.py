"""
지도/길찾기 API 클라이언트 (카카오 로컬 API + 카카오모빌리티 길찾기 API).
문서: https://developers.kakao.com/docs/latest/ko/local/dev-guide, https://developers.kakaomobility.com
"""
import httpx

from app.core.config import settings

KAKAO_LOCAL_ADDRESS_URL = "https://dapi.kakao.com/v2/local/search/address.json"
KAKAO_MOBILITY_DIRECTIONS_URL = "https://apis-navi.kakaomobility.com/v1/directions"


def _auth_headers() -> dict:
    return {"Authorization": f"KakaoAK {settings.MAP_DIRECTIONS_API_KEY}"}


async def geocode(address: str) -> tuple[float, float]:
    """주소 문자열 -> (lat, lng) 변환."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            KAKAO_LOCAL_ADDRESS_URL,
            headers=_auth_headers(),
            params={"query": address},
            timeout=10.0,
        )
        resp.raise_for_status()
        documents = resp.json()["documents"]

    if not documents:
        raise ValueError(f"주소를 찾을 수 없습니다: {address}")

    doc = documents[0]
    return float(doc["y"]), float(doc["x"])  # (lat, lng)


async def get_directions(
    origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float
) -> dict:
    """
    자동차 기준 소요시간/경로 조회.
    반환: {"estimated_minutes": 53, "delay_minutes": 0, "delay_reason": None, "route_polyline": None}

    카카오모빌리티 길찾기 API는 실시간 교통이 반영된 소요시간만 제공하고, "평소 대비 지연" 비교값이나
    사고/통제 사유는 별도로 주지 않는다. delay_minutes/delay_reason은 향후 별도 실시간 교통정보 API
    연동 전까지는 기본값(0, None)으로 둔다.
    """
    params = {
        "origin": f"{origin_lng},{origin_lat}",
        "destination": f"{dest_lng},{dest_lat}",
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            KAKAO_MOBILITY_DIRECTIONS_URL,
            headers=_auth_headers(),
            params=params,
            timeout=10.0,
        )
        resp.raise_for_status()
        route = resp.json()["routes"][0]

    duration_seconds = route["summary"]["duration"]

    return {
        "estimated_minutes": round(duration_seconds / 60),
        "delay_minutes": 0,
        "delay_reason": None,
        "route_polyline": None,
    }
