"""
교통 관련 비즈니스 로직.
"""
from sqlalchemy.ext.asyncio import AsyncSession


async def check_commute(
    origin_address: str | None,
    destination_address: str | None,
    use_default: bool,
    user_id: int | None,
    db: AsyncSession,
) -> dict:
    """
    TODO(구현 필요):
    1. use_default=True && user_id 있으면 CommuteRoute(HOME/WORK) 조회해 좌표 사용
       (둘 다 없으면 InvalidRequestException - 주소도 없고 기본 경로도 없는 경우)
    2. 주소 기반이면 app/external/map_directions_client.py 로 geocoding
    3. 길찾기 API 호출 (예: 카카오모빌리티 길찾기, 네이버 Directions API)
    4. 평소 소요시간 대비 지연시간 계산 (평소 소요시간을 어디서 가져올지 결정 필요 -
       과거 CommuteQuery 평균을 쓸지, 외부 API의 "정상 소요시간" 필드를 쓸지)
    5. CommuteQuery row 저장
    """
    raise NotImplementedError
