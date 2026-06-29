"""
User 관련 DB 접근 캡슐화.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user import GuestInterest, User, UserInterest


async def get_by_provider(provider: str, provider_id: str, db: AsyncSession) -> User | None:
    result = await db.execute(
        select(User).where(User.provider == provider, User.provider_id == provider_id)
    )
    return result.scalar_one_or_none()


async def get_by_id(user_id: int, db: AsyncSession) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def list_user_interests(user_id: int, db: AsyncSession) -> list[UserInterest]:
    result = await db.execute(select(UserInterest).where(UserInterest.user_id == user_id))
    return list(result.scalars().all())


async def list_guest_interests(session_token: str, db: AsyncSession) -> list[GuestInterest]:
    """
    TODO(구현 필요): expires_at > now() 조건 추가 (만료된 항목 제외)
    """
    result = await db.execute(
        select(GuestInterest).where(GuestInterest.session_token == session_token)
    )
    return list(result.scalars().all())


# TODO(구현 필요): create_user, update_last_login, create_user_interest,
# create_guest_interest, delete_interest 등 나머지 CRUD 함수 추가
