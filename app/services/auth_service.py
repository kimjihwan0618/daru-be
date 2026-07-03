"""
인증 비즈니스 로직.
"""
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password
from app.external import oauth_client
from app.models.user import User
from app.repositories import user_repo


async def register_local_user(
    email: str, password: str, nickname: str, db: AsyncSession
) -> tuple[User, bool]:
    """
    이메일/비밀번호 회원가입.
    Returns: (user, is_new_user) - OAuth 콜백과 동일한 반환 형태로 라우터에서 재사용.
    """
    existing = await user_repo.get_by_email(email, db)
    if existing is not None:
        raise ConflictException(message="이미 가입된 이메일입니다.")

    user = await user_repo.create_local_user(
        email=email,
        password_hash=hash_password(password),
        nickname=nickname,
        db=db,
    )
    try:
        await db.commit()
    except IntegrityError:
        # 동시 요청으로 같은 이메일이 먼저 커밋된 경우 (check-then-insert race)
        await db.rollback()
        raise ConflictException(message="이미 가입된 이메일입니다.")
    await db.refresh(user)
    return user, True


async def login_local_user(email: str, password: str, db: AsyncSession) -> User:
    """이메일/비밀번호 로그인."""
    user = await user_repo.get_by_email(email, db)
    if user is None or user.password_hash is None or not verify_password(password, user.password_hash):
        raise UnauthorizedException(message="이메일 또는 비밀번호가 올바르지 않습니다.", code="INVALID_CREDENTIALS")

    await user_repo.update_last_login(user, db)
    await db.commit()
    await db.refresh(user)
    return user


async def handle_oauth_callback(
    provider: str, code: str, db: AsyncSession
) -> tuple[User, bool]:
    """
    소셜 로그인 콜백 처리.
    Returns: (user, is_new_user)
    """
    access_token = await oauth_client.exchange_code_for_token(provider, code)
    info = await oauth_client.fetch_user_info(provider, access_token)

    user = await user_repo.get_by_provider(provider, info["provider_id"], db)

    if user is None:
        user = await user_repo.create_user(
            provider=provider,
            provider_id=info["provider_id"],
            nickname=info["nickname"],
            email=info.get("email"),
            profile_image_url=info.get("profile_image_url"),
            db=db,
        )
        is_new_user = True
        try:
            await db.commit()
        except IntegrityError:
            # 동시 콜백 요청으로 같은 소셜 계정이 먼저 커밋된 경우 (check-then-insert race)
            # 신규 가입이 아니라 로그인으로 취급하고 기존 유저를 재조회한다.
            await db.rollback()
            user = await user_repo.get_by_provider(provider, info["provider_id"], db)
            if user is None:
                raise
            await user_repo.update_last_login(user, db)
            await db.commit()
            is_new_user = False
    else:
        await user_repo.update_last_login(user, db)
        is_new_user = False
        await db.commit()

    await db.refresh(user)
    return user, is_new_user


async def withdraw_user(user_id: int, db: AsyncSession) -> None:
    """회원 탈퇴. FK cascade로 연관 데이터(user_interests 등)도 함께 삭제된다."""
    await user_repo.delete_user(user_id, db)
    await db.commit()


def issue_tokens(user: User) -> dict:
    """access_token + refresh_token 발급."""
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "expires_in": settings.JWT_ACCESS_EXPIRE_MINUTES * 60,
    }
