"""
인증 비즈니스 로직.
app/routers/auth.py 에서 호출되는 함수들의 뼈대.
TODO 주석에 구현 방향을 적어두었다.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def handle_oauth_callback(provider: str, code: str, db: AsyncSession) -> tuple[User, bool]:
    """
    소셜 로그인 콜백 처리.
    Returns: (user, is_new_user)

    TODO(구현 필요):
    1. app/external/oauth_client.py 에서 provider별 토큰 교환 함수 호출
    2. 교환받은 access_token으로 provider의 사용자 정보 API 호출 (email, nickname, profile_image)
    3. User.provider == provider AND User.provider_id == 받아온 id 로 기존 유저 조회
    4. 없으면 신규 User 생성 (is_new_user=True), 있으면 last_login_at 갱신 (is_new_user=False)
    5. db.commit() 후 (user, is_new_user) 반환
    """
    raise NotImplementedError


async def issue_tokens(user: User) -> dict:
    """
    user에 대해 access_token + refresh_token 발급.

    TODO(구현 필요):
    - app.core.security.create_access_token / create_refresh_token 사용
    - refresh_token을 DB 또는 Redis에 저장해 추후 무효화(로그아웃) 가능하게 할지 결정
    """
    raise NotImplementedError
