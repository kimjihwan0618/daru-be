"""
일정 라우터. 설계서 6.8 엔드포인트 명세 대응.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db, get_optional_user
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.schedule import ScheduleCreateRequest, ScheduleItem
from app.services import schedule_service

router = APIRouter(tags=["schedule"])


@router.get("/schedules/today", response_model=ApiResponse[list[ScheduleItem]])
async def get_today_schedules(
    current_user: User | None = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """오늘의 일정 - 시스템 공통 + 로그인 시 사용자 일정 병합. 인증: Optional."""
    user_id = current_user.id if current_user else None
    schedules = await schedule_service.get_today_schedules(user_id, db)
    return ApiResponse(
        success=True,
        data=[
            ScheduleItem(
                id=s.id,
                title=s.title,
                scheduled_time=s.scheduled_time,
                category=s.category,
                schedule_date=s.schedule_date,
            )
            for s in schedules
        ],
    )


@router.post("/users/me/schedules", response_model=ApiResponse[ScheduleItem], status_code=201)
async def create_schedule(
    body: ScheduleCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """사용자 커스텀 일정 추가. 인증: Required."""
    schedule = await schedule_service.create_schedule(
        user_id=current_user.id,
        title=body.title,
        scheduled_time=body.scheduled_time,
        category=body.category,
        db=db,
    )
    return ApiResponse(
        success=True,
        data=ScheduleItem(
            id=schedule.id,
            title=schedule.title,
            scheduled_time=schedule.scheduled_time,
            category=schedule.category,
            schedule_date=schedule.schedule_date,
        ),
    )


@router.delete("/users/me/schedules/{schedule_id}", response_model=ApiResponse[None])
async def delete_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """사용자 일정 삭제. 인증: Required."""
    await schedule_service.delete_schedule(schedule_id, current_user.id, db)
    return ApiResponse(success=True, data=None)
