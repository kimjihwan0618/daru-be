"""
인증 비즈니스 로직.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token
from app.external import oauth_client
from app.models.user import User
from app.repositories import user_repo


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
    else:
        await user_repo.update_last_login(user, db)
        is_new_user = False

    await db.commit()
    await db.refresh(user)
    return user, is_new_user


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
