"""
교통 라우터. 설계서 6.6 엔드포인트 명세 대응.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db, get_guest_session_id, get_optional_user
from app.models.user import User
from app.schemas.commute import (
    CommuteCheckRequest,
    CommuteCheckResponse,
    CommuteRouteCreateRequest,
    CommuteRouteResponse,
)
from app.schemas.common import ApiResponse

router = APIRouter(tags=["commute"])


@router.post("/commute/check", response_model=ApiResponse[CommuteCheckResponse])
async def check_commute(
    body: CommuteCheckRequest,
    current_user: User | None = Depends(get_optional_user),
    guest_session_id: str = Depends(get_guest_session_id),
    db: AsyncSession = Depends(get_db),
):
    """출발지·도착지 교통 확인. 인증: Optional.
    use_default=True면 로그인 사용자의 등록된 집/회사 경로를 사용.
    """
    # TODO(구현 필요): app/services/commute_service.py
    # 1. use_default=True && current_user 있으면 CommuteRoute(HOME/WORK) 조회해 좌표 사용
    # 2. 아니면 body의 주소를 geocoding (app/external/map_directions_client.py)
    # 3. 길찾기 API 호출 -> 소요시간/지연시간/추천 출발시간 계산
    # 4. CommuteQuery row 저장 (로그/통계용, user_id는 nullable)
    raise NotImplementedError


@router.get("/users/me/commute-routes", response_model=ApiResponse[list[CommuteRouteResponse]])
async def list_commute_routes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """등록된 집/회사 경로 목록. 인증: Required."""
    # TODO(구현 필요): CommuteRoute.user_id == current_user.id 조회
    raise NotImplementedError


@router.post("/users/me/commute-routes", response_model=ApiResponse[CommuteRouteResponse])
async def create_commute_route(
    body: CommuteRouteCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """집/회사 주소 등록. 인증: Required."""
    # TODO(구현 필요): label(HOME/WORK) 검증 + CommuteRoute insert
    raise NotImplementedError


@router.put("/users/me/commute-routes/{route_id}", response_model=ApiResponse[CommuteRouteResponse])
async def update_commute_route(
    route_id: int,
    body: CommuteRouteCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """등록 경로 수정. 인증: Required."""
    # TODO(구현 필요): route 소유자 확인(403) 후 업데이트
    raise NotImplementedError


@router.delete("/users/me/commute-routes/{route_id}", response_model=ApiResponse[None])
async def delete_commute_route(
    route_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """등록 경로 삭제. 인증: Required."""
    # TODO(구현 필요): route 소유자 확인(403) 후 삭제
    raise NotImplementedError
