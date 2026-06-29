"""
Briefing 관련 DB 접근 캡슐화.
"""
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.briefing import DailyBriefing, UserBriefing


async def get_daily_briefing(briefing_date: date, time_slot: str, db: AsyncSession) -> DailyBriefing | None:
    result = await db.execute(
        select(DailyBriefing).where(
            DailyBriefing.briefing_date == briefing_date,
            DailyBriefing.time_slot == time_slot,
        )
    )
    return result.scalar_one_or_none()


async def get_user_briefing(
    user_id: int, briefing_date: date, time_slot: str, db: AsyncSession
) -> UserBriefing | None:
    result = await db.execute(
        select(UserBriefing).where(
            UserBriefing.user_id == user_id,
            UserBriefing.briefing_date == briefing_date,
            UserBriefing.time_slot == time_slot,
        )
    )
    return result.scalar_one_or_none()


# TODO(구현 필요): save_user_briefing(upsert), save_daily_briefing 등 쓰기 함수 추가
