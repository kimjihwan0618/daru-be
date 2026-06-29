"""
날씨 조회 클라이언트 (기상청 API 등).

TODO(구현 필요):
- 좌표 또는 지역코드로 현재 기온/날씨 상태 조회
- 기상청 API는 격자 좌표(nx, ny) 변환이 필요한 경우가 많음 - 위경도 -> 격자 변환 함수 필요
"""


async def get_current_weather(latitude: float, longitude: float) -> dict:
    """
    TODO(구현 필요):
    반환 예시: {"temp_c": 21, "condition": "맑음"}
    """
    raise NotImplementedError
