"""
사용자 프로필/설정 비즈니스 로직.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories import user_repo


async def get_profile(user: User) -> User:
    return user


async def update_profile(user: User, nickname: str | None, db: AsyncSession) -> User:
    if nickname is not None:
        user.nickname = nickname
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
