"""
일정 DB 접근.
"""
from datetime import date, datetime

from sqlalchemy import delete, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.schedule import Schedule


async def list_today(user_id: int | None, today: date, db: AsyncSession) -> list[Schedule]:
    """공통 일정 + 로그인 사용자 일정 병합 조회."""
    conditions = [Schedule.user_id.is_(None)]
    if user_id:
        conditions.append(Schedule.user_id == user_id)

    result = await db.execute(
        select(Schedule)
        .where(Schedule.schedule_date == today, or_(*conditions))
        .order_by(Schedule.scheduled_time)
    )
    return list(result.scalars().all())


async def get(schedule_id: int, db: AsyncSession) -> Schedule | None:
    result = await db.execute(select(Schedule).where(Schedule.id == schedule_id))
    return result.scalar_one_or_none()


async def create(
    user_id: int,
    title: str,
    scheduled_time: datetime,
    category: str,
    schedule_date: date,
    db: AsyncSession,
) -> Schedule:
    schedule = Schedule(
        user_id=user_id,
        title=title,
        scheduled_time=scheduled_time,
        category=category,
        schedule_date=schedule_date,
    )
    db.add(schedule)
    await db.flush()
    return schedule


async def delete_schedule(schedule_id: int, db: AsyncSession) -> None:
    await db.execute(delete(Schedule).where(Schedule.id == schedule_id))
