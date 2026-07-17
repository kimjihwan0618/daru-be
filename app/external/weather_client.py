"""
날씨 조회 클라이언트 (기상청 단기예보 - 초단기실황조회 API).
문서: https://www.data.go.kr/data/15084084/openapi.do
"""
import math
from datetime import datetime, timedelta

import httpx

from app.core.config import settings

KMA_NCST_URL = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"

# PTY(강수형태) 코드 -> 사용자에게 보여줄 condition 텍스트
_PTY_CONDITION = {
    "0": "맑음",
    "1": "비",
    "2": "비/눈",
    "3": "눈",
    "4": "소나기",
    "5": "빗방울",
    "6": "빗방울눈날림",
    "7": "눈날림",
}


def _latlng_to_grid(latitude: float, longitude: float) -> tuple[int, int]:
    """위경도 -> 기상청 격자좌표(nx, ny) 변환 (Lambert Conformal Conic 투영)."""
    RE = 6371.00877  # 지구 반경(km)
    GRID = 5.0  # 격자 간격(km)
    SLAT1, SLAT2 = 30.0, 60.0  # 표준위도
    OLON, OLAT = 126.0, 38.0  # 기준점 경도/위도
    XO, YO = 43, 136  # 기준점 X, Y 좌표

    DEGRAD = math.pi / 180.0
    re = RE / GRID
    slat1, slat2 = SLAT1 * DEGRAD, SLAT2 * DEGRAD
    olon, olat = OLON * DEGRAD, OLAT * DEGRAD

    sn = math.tan(math.pi * 0.25 + slat2 * 0.5) / math.tan(math.pi * 0.25 + slat1 * 0.5)
    sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(sn)
    sf = math.tan(math.pi * 0.25 + slat1 * 0.5)
    sf = math.pow(sf, sn) * math.cos(slat1) / sn
    ro = math.tan(math.pi * 0.25 + olat * 0.5)
    ro = re * sf / math.pow(ro, sn)

    ra = math.tan(math.pi * 0.25 + latitude * DEGRAD * 0.5)
    ra = re * sf / math.pow(ra, sn)
    theta = longitude * DEGRAD - olon
    if theta > math.pi:
        theta -= 2.0 * math.pi
    if theta < -math.pi:
        theta += 2.0 * math.pi
    theta *= sn

    nx = int(ra * math.sin(theta) + XO + 0.5)
    ny = int(ro - ra * math.cos(theta) + YO + 0.5)
    return nx, ny


def _latest_base_datetime() -> tuple[str, str]:
    """
    초단기실황은 매시 40분에 생성되어 10분 뒤(50분)부터 조회 가능.
    현재 시각 기준 가장 최근에 확실히 존재하는 base_date/base_time을 계산.
    """
    now = datetime.now()
    if now.minute < 45:
        now -= timedelta(hours=1)
    return now.strftime("%Y%m%d"), now.strftime("%H00")


async def get_current_weather(latitude: float, longitude: float) -> dict:
    """
    위경도 기준 현재 기온/강수 상태 조회.
    반환: {"temp_c": 21.3, "condition": "맑음"}
    """
    nx, ny = _latlng_to_grid(latitude, longitude)
    base_date, base_time = _latest_base_datetime()

    params = {
        "serviceKey": settings.WEATHER_API_KEY,
        "pageNo": 1,
        "numOfRows": 10,
        "dataType": "JSON",
        "base_date": base_date,
        "base_time": base_time,
        "nx": nx,
        "ny": ny,
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(KMA_NCST_URL, params=params, timeout=10.0)
        resp.raise_for_status()
        items = resp.json()["response"]["body"]["items"]["item"]

    values = {item["category"]: item["obsrValue"] for item in items}
    temp_c = float(values.get("T1H", 0))
    condition = _PTY_CONDITION.get(values.get("PTY", "0"), "맑음")

    return {"temp_c": temp_c, "condition": condition}
