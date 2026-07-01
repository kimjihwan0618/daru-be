"""
일정 비즈니스 로직.
"""
from datetime import date, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.schedule import Schedule
from app.repositories import schedule_repo


async def get_today_schedules(user_id: int | None, db: AsyncSession) -> list[Schedule]:
    return await schedule_repo.list_today(user_id, date.today(), db)


async def create_schedule(
    user_id: int,
    title: str,
    scheduled_time: datetime,
    category: str,
    db: AsyncSession,
) -> Schedule:
    schedule = await schedule_repo.create(
        user_id=user_id,
        title=title,
        scheduled_time=scheduled_time,
        category=category,
        schedule_date=scheduled_time.date(),
        db=db,
    )
    await db.commit()
    await db.refresh(schedule)
    return schedule


async def delete_schedule(schedule_id: int, user_id: int, db: AsyncSession) -> None:
    schedule = await schedule_repo.get(schedule_id, db)
    if not schedule:
        raise NotFoundException("일정을 찾을 수 없습니다.")
    if schedule.user_id != user_id:
        raise ForbiddenException()
    await schedule_repo.delete_schedule(schedule_id, db)
    await db.commit()
