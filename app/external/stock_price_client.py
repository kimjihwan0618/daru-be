"""
증권 시세 조회 클라이언트.
설계서에서는 한국투자증권 OpenAPI 등을 예시로 들었으나, 실제 사용할 API는 직접 확인 필요.

TODO(구현 필요):
- 종목코드로 현재가/등락률/7일 가격 히스토리 조회
- 토큰 발급(OAuth2 client credentials 방식인 API가 많음) 후 캐싱 - 토큰 만료시간 주의
- Redis로 1분 TTL 캐싱 권장 (실시간성과 API 호출 한도의 균형)
"""


async def get_current_price(stock_code: str) -> dict:
    """
    TODO(구현 필요): 실제 증권 API 연동.
    반환 예시: {"current_price": 71800, "change_rate": 1.27, "change_direction": "UP"}
    """
    raise NotImplementedError


async def get_price_history(stock_code: str, days: int = 7) -> list[float]:
    """
    TODO(구현 필요): 일별 종가 리스트 반환
    """
    raise NotImplementedError
