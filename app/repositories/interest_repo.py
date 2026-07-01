"""
관심 키워드/종목 DB 접근.
"""
from datetime import datetime

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user import GuestInterest, UserInterest


async def list_user_interests(user_id: int, db: AsyncSession) -> list[UserInterest]:
    result = await db.execute(select(UserInterest).where(UserInterest.user_id == user_id))
    return list(result.scalars().all())


async def get_user_interest(interest_id: int, db: AsyncSession) -> UserInterest | None:
    result = await db.execute(select(UserInterest).where(UserInterest.id == interest_id))
    return result.scalar_one_or_none()


async def create_user_interest(user_id: int, type_: str, value: str, db: AsyncSession) -> UserInterest:
    interest = UserInterest(user_id=user_id, type=type_, value=value)
    db.add(interest)
    await db.flush()
    return interest


async def delete_user_interest(interest_id: int, db: AsyncSession) -> None:
    await db.execute(delete(UserInterest).where(UserInterest.id == interest_id))


async def list_guest_interests(session_token: str, db: AsyncSession) -> list[GuestInterest]:
    result = await db.execute(
        select(GuestInterest).where(
            GuestInterest.session_token == session_token,
            GuestInterest.expires_at > datetime.utcnow(),
        )
    )
    return list(result.scalars().all())


async def get_guest_interest(interest_id: int, db: AsyncSession) -> GuestInterest | None:
    result = await db.execute(select(GuestInterest).where(GuestInterest.id == interest_id))
    return result.scalar_one_or_none()


async def create_guest_interest(
    session_token: str, type_: str, value: str, expires_at: datetime, db: AsyncSession
) -> GuestInterest:
    interest = GuestInterest(
        session_token=session_token,
        type=type_,
        value=value,
        expires_at=expires_at,
    )
    db.add(interest)
    await db.flush()
    return interest


async def delete_guest_interest(interest_id: int, db: AsyncSession) -> None:
    await db.execute(delete(GuestInterest).where(GuestInterest.id == interest_id))


async def migrate_guest_to_user(
    session_token: str, user_id: int, db: AsyncSession
) -> int:
    """게스트 관심사를 유저 관심사로 이전. 중복 제외 후 이전된 건수 반환."""
    guests = await list_guest_interests(session_token, db)
    existing = await list_user_interests(user_id, db)
    existing_keys = {(i.type, i.value) for i in existing}

    migrated = 0
    for g in guests:
        if (g.type, g.value) not in existing_keys:
            db.add(UserInterest(user_id=user_id, type=g.type, value=g.value))
            migrated += 1

    await db.execute(delete(GuestInterest).where(GuestInterest.session_token == session_token))
    return migrated
