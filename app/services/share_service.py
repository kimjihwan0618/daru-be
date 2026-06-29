"""
브리핑 공유 관련 비즈니스 로직.
"""
from sqlalchemy.ext.asyncio import AsyncSession


async def create_share_link(
    briefing_type: str,
    briefing_ref_id: int,
    created_by_user_id: int | None,
    db: AsyncSession,
) -> dict:
    """
    TODO(구현 필요):
    1. uuid로 share_token 생성
    2. SharedBriefing row 저장 (briefing_type: DAILY/USER)
    3. share_url 조립 (프론트엔드 도메인 + /s/{share_token})
    4. 만료 정책 결정 (설계서 예시는 7일 - expires_at 컬럼이 모델에 없으므로 추가 검토 필요)
    """
    raise NotImplementedError


async def get_shared_briefing(share_token: str, db: AsyncSession) -> dict:
    """
    TODO(구현 필요): SharedBriefing.share_token 조회 후 원본 브리핑 데이터 조립해 반환
    """
    raise NotImplementedError
