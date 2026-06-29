"""
사용자/설정 라우터. 설계서 6.9 엔드포인트 명세 대응.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.user import (
    UserPreferencesResponse,
    UserPreferencesUpdateRequest,
    UserProfileResponse,
    UserProfileUpdateRequest,
)

router = APIRouter(prefix="/users/me", tags=["user"])


@router.get("", response_model=ApiResponse[UserProfileResponse])
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """내 프로필 조회. 인증: Required."""
    # TODO(구현 필요): current_user -> UserProfileResponse 매핑
    raise NotImplementedError


@router.patch("", response_model=ApiResponse[UserProfileResponse])
async def update_my_profile(
    body: UserProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """프로필 수정(닉네임 등). 인증: Required."""
    # TODO(구현 필요): 전달된 필드만 업데이트
    raise NotImplementedError


@router.get("/preferences", response_model=ApiResponse[UserPreferencesResponse])
async def get_my_preferences(current_user: User = Depends(get_current_user)):
    """브리핑 알림 시간/푸시 설정 조회. 인증: Required."""
    # TODO(구현 필요): 설계서 ERD에 preferences 테이블이 없음 - 별도 테이블/컬럼 추가 설계 필요
    # (users 테이블에 컬럼 추가 또는 user_preferences 테이블 신설 검토)
    raise NotImplementedError


@router.put("/preferences", response_model=ApiResponse[UserPreferencesResponse])
async def update_my_preferences(
    body: UserPreferencesUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """브리핑 알림 시간/푸시 설정 변경. 인증: Required."""
    # TODO(구현 필요): 위 get_my_preferences와 동일하게 저장 위치 설계 필요
    raise NotImplementedError
