"""
일정 라우터. 설계서 6.8 엔드포인트 명세 대응.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db, get_optional_user
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.schedule import ScheduleCreateRequest, ScheduleItem

router = APIRouter(tags=["schedule"])


@router.get("/schedules/today", response_model=ApiResponse[list[ScheduleItem]])
async def get_today_schedules(
    current_user: User | None = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """오늘의 일정 - 시스템 공통 + 로그인 시 사용자 일정 병합. 인증: Optional."""
    # TODO(구현 필요):
    # 1. Schedule.user_id IS NULL AND schedule_date == today -> 공통 일정
    # 2. current_user 있으면 Schedule.user_id == current_user.id 추가 조회
    # 3. scheduled_time 기준 정렬해서 병합
    raise NotImplementedError


@router.post("/users/me/schedules", response_model=ApiResponse[ScheduleItem], status_code=201)
async def create_schedule(
    body: ScheduleCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """사용자 커스텀 일정 추가. 인증: Required."""
    # TODO(구현 필요): Schedule insert (user_id = current_user.id)
    raise NotImplementedError


@router.delete("/users/me/schedules/{schedule_id}", response_model=ApiResponse[None])
async def delete_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """사용자 일정 삭제. 인증: Required."""
    # TODO(구현 필요): 소유자 확인 후 삭제
    raise NotImplementedError
