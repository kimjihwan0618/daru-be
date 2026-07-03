"""
인증 라우터. 설계서 6.1 엔드포인트 명세 대응.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.core.exceptions import InvalidRequestException, UnauthorizedException
from app.core.security import create_access_token, decode_token
from app.models.user import User
from app.repositories import user_repo
from app.schemas.auth import (
    AccessTokenResponse,
    LoginRequest,
    LoginUrlResponse,
    OAuthCallbackRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    UserSummary,
)
from app.schemas.common import ApiResponse
from app.services import auth_service
from app.external.oauth_client import SUPPORTED_PROVIDERS, build_authorize_url

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/{provider}/login-url", response_model=ApiResponse[LoginUrlResponse])
async def get_login_url(provider: str):
    """소셜 로그인 진입 URL 발급. 인증: Public."""
    if provider not in SUPPORTED_PROVIDERS:
        raise InvalidRequestException(f"지원하지 않는 provider입니다: {provider}")

    url = build_authorize_url(provider)
    return ApiResponse(success=True, data=LoginUrlResponse(login_url=url))


@router.post("/{provider}/callback", response_model=ApiResponse[TokenResponse])
async def oauth_callback(
    provider: str,
    body: OAuthCallbackRequest,
    db: AsyncSession = Depends(get_db),
):
    """소셜 로그인 콜백 처리 → 회원가입/로그인 + JWT 발급. 인증: Public."""
    if provider not in SUPPORTED_PROVIDERS:
        raise InvalidRequestException(f"지원하지 않는 provider입니다: {provider}")

    user, is_new_user = await auth_service.handle_oauth_callback(provider, body.code, db)
    tokens = auth_service.issue_tokens(user)

    return ApiResponse(
        success=True,
        data=TokenResponse(
            **tokens,
            is_new_user=is_new_user,
            user=UserSummary(
                id=user.id,
                nickname=user.nickname,
                profile_image_url=user.profile_image_url,
            ),
        ),
    )


@router.post("/register", response_model=ApiResponse[TokenResponse])
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """이메일/비밀번호 회원가입 → 로그인 + JWT 발급. 인증: Public."""
    user, is_new_user = await auth_service.register_local_user(body.email, body.password, body.nickname, db)
    tokens = auth_service.issue_tokens(user)

    return ApiResponse(
        success=True,
        data=TokenResponse(
            **tokens,
            is_new_user=is_new_user,
            user=UserSummary(
                id=user.id,
                nickname=user.nickname,
                profile_image_url=user.profile_image_url,
            ),
        ),
    )


@router.post("/login", response_model=ApiResponse[TokenResponse])
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    """이메일/비밀번호 로그인. 인증: Public."""
    user = await auth_service.login_local_user(body.email, body.password, db)
    tokens = auth_service.issue_tokens(user)

    return ApiResponse(
        success=True,
        data=TokenResponse(
            **tokens,
            is_new_user=False,
            user=UserSummary(
                id=user.id,
                nickname=user.nickname,
                profile_image_url=user.profile_image_url,
            ),
        ),
    )


@router.post("/refresh", response_model=ApiResponse[AccessTokenResponse])
async def refresh_access_token(
    body: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """refresh_token으로 access_token 재발급. 인증: Public."""
    payload = decode_token(body.refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise UnauthorizedException(message="유효하지 않은 refresh token입니다.", code="INVALID_REFRESH_TOKEN")

    user_id = payload.get("sub")
    user = await user_repo.get_by_id(int(user_id), db)
    if user is None:
        raise UnauthorizedException(message="존재하지 않는 사용자입니다.", code="INVALID_REFRESH_TOKEN")

    from app.core.config import settings
    new_access_token = create_access_token(user.id)

    return ApiResponse(
        success=True,
        data=AccessTokenResponse(
            access_token=new_access_token,
            expires_in=settings.JWT_ACCESS_EXPIRE_MINUTES * 60,
        ),
    )


@router.post("/logout", response_model=ApiResponse[None])
async def logout(current_user: User = Depends(get_current_user)):
    """
    로그아웃. 인증: Required.
    현재는 클라이언트 측 토큰 폐기 방식으로 동작.
    refresh_token 서버 측 무효화는 Redis 도입 후 구현 예정.
    """
    return ApiResponse(success=True, data=None)


@router.delete("/withdraw", response_model=ApiResponse[None])
async def withdraw(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """회원 탈퇴. 인증: Required."""
    await auth_service.withdraw_user(current_user.id, db)
    return ApiResponse(success=True, data=None)
