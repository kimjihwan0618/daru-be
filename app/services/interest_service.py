"""
관심 키워드/종목 비즈니스 로직.
"""
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ConflictException, ForbiddenException, NotFoundException
from app.models.user import GuestInterest, UserInterest
from app.repositories import interest_repo


async def list_interests(
    user_id: int | None,
    guest_session_id: str,
    db: AsyncSession,
) -> list[UserInterest | GuestInterest]:
    if user_id:
        return await interest_repo.list_user_interests(user_id, db)
    return await interest_repo.list_guest_interests(guest_session_id, db)


async def create_interest(
    type_: str,
    value: str,
    user_id: int | None,
    guest_session_id: str,
    db: AsyncSession,
) -> UserInterest | GuestInterest:
    if user_id:
        existing = await interest_repo.list_user_interests(user_id, db)
        if any(i.type == type_ and i.value == value for i in existing):
            raise ConflictException("이미 등록된 관심 항목입니다.")
        interest = await interest_repo.create_user_interest(user_id, type_, value, db)
    else:
        existing = await interest_repo.list_guest_interests(guest_session_id, db)
        if any(i.type == type_ and i.value == value for i in existing):
            raise ConflictException("이미 등록된 관심 항목입니다.")
        expires_at = datetime.utcnow() + timedelta(hours=settings.GUEST_SESSION_TTL_HOURS)
        interest = await interest_repo.create_guest_interest(
            guest_session_id, type_, value, expires_at, db
        )

    await db.commit()
    await db.refresh(interest)
    return interest


async def delete_interest(
    interest_id: int,
    user_id: int | None,
    guest_session_id: str,
    db: AsyncSession,
) -> None:
    if user_id:
        interest = await interest_repo.get_user_interest(interest_id, db)
        if not interest:
            raise NotFoundException("관심 항목을 찾을 수 없습니다.")
        if interest.user_id != user_id:
            raise ForbiddenException()
        await interest_repo.delete_user_interest(interest_id, db)
    else:
        interest = await interest_repo.get_guest_interest(interest_id, db)
        if not interest:
            raise NotFoundException("관심 항목을 찾을 수 없습니다.")
        if interest.session_token != guest_session_id:
            raise ForbiddenException()
        await interest_repo.delete_guest_interest(interest_id, db)

    await db.commit()


async def migrate_guest_interests(
    guest_session_id: str,
    user_id: int,
    db: AsyncSession,
) -> int:
    migrated = await interest_repo.migrate_guest_to_user(guest_session_id, user_id, db)
    await db.commit()
    return migrated
