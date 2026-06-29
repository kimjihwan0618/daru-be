"""
지도/길찾기 API 클라이언트 (카카오모빌리티 또는 네이버 Directions API 등).

TODO(구현 필요):
- geocode(address): 주소 -> 좌표(lat, lng) 변환
- get_directions(origin, destination): 소요시간/지연시간/경로(polyline) 조회
"""


async def geocode(address: str) -> tuple[float, float]:
    """
    TODO(구현 필요): 주소 문자열 -> (lat, lng) 변환
    카카오 로컬 API(주소 검색) 또는 네이버 지도 API 활용
    """
    raise NotImplementedError


async def get_directions(
    origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float
) -> dict:
    """
    TODO(구현 필요):
    반환 예시: {
        "estimated_minutes": 53,
        "delay_minutes": 12,
        "delay_reason": "분당수서로 사고로 평소보다 12분 더 걸려요",
        "route_polyline": "encoded_polyline_string..."
    }
    - "delay_reason"은 API가 직접 안 줄 가능성이 높음 -> 실시간 교통정보 API에서
      별도로 사고/통제 정보를 받아 텍스트로 가공하는 로직 필요
    """
    raise NotImplementedError
