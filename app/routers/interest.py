"""
관심 키워드/종목 라우터. 설계서 6.7 엔드포인트 명세 대응.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db, get_guest_session_id, get_optional_user
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.interest import (
    InterestCreateRequest,
    InterestItem,
    InterestMigrateRequest,
    InterestMigrateResponse,
)
from app.services import interest_service

router = APIRouter(prefix="/interests", tags=["interest"])


@router.get("", response_model=ApiResponse[list[InterestItem]])
async def list_interests(
    current_user: User | None = Depends(get_optional_user),
    guest_session_id: str = Depends(get_guest_session_id),
    db: AsyncSession = Depends(get_db),
):
    """현재 선택된 관심 키워드/종목 목록. 인증: Optional."""
    user_id = current_user.id if current_user else None
    items = await interest_service.list_interests(user_id, guest_session_id, db)
    return ApiResponse(
        success=True,
        data=[InterestItem(id=i.id, type=i.type, value=i.value) for i in items],
    )


@router.post("", response_model=ApiResponse[InterestItem], status_code=201)
async def create_interest(
    body: InterestCreateRequest,
    current_user: User | None = Depends(get_optional_user),
    guest_session_id: str = Depends(get_guest_session_id),
    db: AsyncSession = Depends(get_db),
):
    """관심 키워드/종목 추가. 인증: Optional."""
    user_id = current_user.id if current_user else None
    interest = await interest_service.create_interest(
        body.type, body.value, user_id, guest_session_id, db
    )
    return ApiResponse(
        success=True,
        data=InterestItem(id=interest.id, type=interest.type, value=interest.value),
    )


@router.delete("/{interest_id}", response_model=ApiResponse[None])
async def delete_interest(
    interest_id: int,
    current_user: User | None = Depends(get_optional_user),
    guest_session_id: str = Depends(get_guest_session_id),
    db: AsyncSession = Depends(get_db),
):
    """관심 항목 삭제. 인증: Optional."""
    user_id = current_user.id if current_user else None
    await interest_service.delete_interest(interest_id, user_id, guest_session_id, db)
    return ApiResponse(success=True, data=None)


@router.post("/migrate", response_model=ApiResponse[InterestMigrateResponse])
async def migrate_guest_interests(
    body: InterestMigrateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """비로그인 임시 관심사를 로그인 계정으로 이전. 인증: Required."""
    migrated = await interest_service.migrate_guest_interests(
        body.guest_session_id, current_user.id, db
    )
    return ApiResponse(
        success=True,
        data=InterestMigrateResponse(migrated_count=migrated),
    )
