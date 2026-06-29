"""
인증 라우터. 설계서 6.1 엔드포인트 명세 대응.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.auth import (
    AccessTokenResponse,
    LoginUrlResponse,
    OAuthCallbackRequest,
    RefreshTokenRequest,
    TokenResponse,
)
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/auth", tags=["auth"])

SUPPORTED_PROVIDERS = {"kakao", "naver", "google"}


@router.get("/{provider}/login-url", response_model=ApiResponse[LoginUrlResponse])
async def get_login_url(provider: str):
    """소셜 로그인 진입 URL 발급. 인증: Public."""
    # TODO(구현 필요):
    # 1. provider in SUPPORTED_PROVIDERS 검증 (아니면 InvalidRequestException)
    # 2. provider 별 OAuth authorize URL 조립 (app/external/oauth_client.py 에서 구현)
    #    - kakao: https://kauth.kakao.com/oauth/authorize?client_id=...&redirect_uri=...&response_type=code
    #    - naver/google 유사
    # 3. CSRF 방지용 state 파라미터 생성 + 임시 저장(Redis 등) 고려
    raise NotImplementedError


@router.post("/{provider}/callback", response_model=ApiResponse[TokenResponse])
async def oauth_callback(
    provider: str,
    body: OAuthCallbackRequest,
    db: AsyncSession = Depends(get_db),
):
    """소셜 로그인 콜백 처리 → 회원가입/로그인 + JWT 발급. 인증: Public."""
    # TODO(구현 필요): app/services/auth_service.py 의 handle_oauth_callback() 호출
    # 1. provider에 code 전달해 access_token 교환 (app/external/oauth_client.py)
    # 2. provider로부터 사용자 식별 정보(email, nickname, profile_image) 조회
    # 3. (provider, provider_id) 기준 기존 유저 조회, 없으면 신규 생성
    # 4. last_login_at 갱신
    # 5. create_access_token / create_refresh_token 발급 (app/core/security.py)
    raise NotImplementedError


@router.post("/refresh", response_model=ApiResponse[AccessTokenResponse])
async def refresh_access_token(body: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """refresh_token으로 access_token 재발급. 인증: Public (refresh_token이 인증 수단)."""
    # TODO(구현 필요):
    # 1. decode_token(body.refresh_token) - type이 "refresh"인지 확인
    # 2. 무효(만료/위조/로그아웃으로 블랙리스트 처리됨)면 401 INVALID_REFRESH_TOKEN
    # 3. 유효하면 새 access_token 발급
    raise NotImplementedError


@router.post("/logout", response_model=ApiResponse[None])
async def logout(current_user: User = Depends(get_current_user)):
    """로그아웃 - refresh_token 무효화. 인증: Required."""
    # TODO(구현 필요): refresh_token 블랙리스트/화이트리스트 관리 방식 결정 후 구현
    # (DB에 활성 refresh_token 목록을 두거나, Redis에 jti 블랙리스트)
    raise NotImplementedError


@router.delete("/withdraw", response_model=ApiResponse[None])
async def withdraw(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """회원 탈퇴. 인증: Required."""
    # TODO(구현 필요): user 삭제 시 관련 데이터(user_interests, user_briefings,
    # commute_routes, schedules 등) cascade 삭제 확인 - 모델에 ondelete="CASCADE" 설정되어 있음
    raise NotImplementedError
