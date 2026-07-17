"""
증권 시세 조회 클라이언트 (한국투자증권 OpenAPI - 실전투자 기준).
문서: https://apiportal.koreainvestment.com

- 토큰(OAuth2 client credentials)은 발급 후 Redis에 캐싱해 재사용 (기본 24시간 유효).
- 시세 자체도 Redis에 1분 TTL로 캐싱해 API 호출 한도를 아낀다.
"""
from datetime import datetime, timedelta

import httpx

from app.core.config import settings
from app.core.redis import redis_client

KIS_BASE_URL = "https://openapi.koreainvestment.com:9443"
_TOKEN_CACHE_KEY = "kis:access_token"
_PRICE_CACHE_PREFIX = "kis:price:"
_HISTORY_CACHE_PREFIX = "kis:history:"

# prdy_vrss_sign(전일대비부호) -> UP/DOWN/FLAT
_CHANGE_DIRECTION = {
    "1": "UP",  # 상한
    "2": "UP",  # 상승
    "3": "FLAT",  # 보합
    "4": "DOWN",  # 하락
    "5": "DOWN",  # 하한
}


async def _get_access_token() -> str:
    cached = await redis_client.get(_TOKEN_CACHE_KEY)
    if cached:
        return cached

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{KIS_BASE_URL}/oauth2/tokenP",
            json={
                "grant_type": "client_credentials",
                "appkey": settings.STOCK_PRICE_API_KEY,
                "appsecret": settings.STOCK_PRICE_API_SECRET,
            },
            timeout=10.0,
        )
        resp.raise_for_status()
        body = resp.json()

    token = body["access_token"]
    expires_in = int(body.get("expires_in", 86400))
    await redis_client.set(_TOKEN_CACHE_KEY, token, ex=max(expires_in - 60, 60))
    return token


async def _auth_headers() -> dict:
    token = await _get_access_token()
    return {
        "authorization": f"Bearer {token}",
        "appkey": settings.STOCK_PRICE_API_KEY,
        "appsecret": settings.STOCK_PRICE_API_SECRET,
        "content-type": "application/json; charset=utf-8",
    }


async def get_current_price(stock_code: str) -> dict:
    """
    반환 예시: {"current_price": 71800, "change_rate": 1.27, "change_direction": "UP"}
    """
    cache_key = f"{_PRICE_CACHE_PREFIX}{stock_code}"
    cached = await redis_client.hgetall(cache_key)
    if cached:
        return {
            "current_price": float(cached["current_price"]),
            "change_rate": float(cached["change_rate"]),
            "change_direction": cached["change_direction"],
        }

    headers = await _auth_headers()
    headers["tr_id"] = "FHKST01010100"
    params = {"fid_cond_mrkt_div_code": "J", "fid_input_iscd": stock_code}

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{KIS_BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price",
            headers=headers,
            params=params,
            timeout=10.0,
        )
        resp.raise_for_status()
        output = resp.json()["output"]

    result = {
        "current_price": float(output["stck_prpr"]),
        "change_rate": float(output["prdy_ctrt"]),
        "change_direction": _CHANGE_DIRECTION.get(output.get("prdy_vrss_sign", "3"), "FLAT"),
    }

    await redis_client.hset(cache_key, mapping=result)
    await redis_client.expire(cache_key, 60)
    return result


async def get_price_history(stock_code: str, days: int = 7) -> list[float]:
    """일별 종가 리스트 반환 (오래된 날짜 -> 최근 날짜 순)."""
    cache_key = f"{_HISTORY_CACHE_PREFIX}{stock_code}:{days}"
    cached = await redis_client.get(cache_key)
    if cached:
        return [float(v) for v in cached.split(",")]

    headers = await _auth_headers()
    headers["tr_id"] = "FHKST03010100"

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days * 2)  # 주말/휴장일 감안해 여유있게 조회
    params = {
        "fid_cond_mrkt_div_code": "J",
        "fid_input_iscd": stock_code,
        "fid_input_date_1": start_date.strftime("%Y%m%d"),
        "fid_input_date_2": end_date.strftime("%Y%m%d"),
        "fid_period_div_code": "D",
        "fid_org_adj_prc": "1",
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{KIS_BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice",
            headers=headers,
            params=params,
            timeout=10.0,
        )
        resp.raise_for_status()
        rows = resp.json()["output2"]

    closes = [float(r["stck_clpr"]) for r in rows[:days]]
    closes.reverse()  # API가 최신순으로 내려주므로 오래된 순으로 뒤집음

    await redis_client.set(cache_key, ",".join(str(c) for c in closes), ex=60)
    return closes
