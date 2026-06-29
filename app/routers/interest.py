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

router = APIRouter(prefix="/interests", tags=["interest"])


@router.get("", response_model=ApiResponse[list[InterestItem]])
async def list_interests(
    current_user: User | None = Depends(get_optional_user),
    guest_session_id: str = Depends(get_guest_session_id),
    db: AsyncSession = Depends(get_db),
):
    """현재 선택된 관심 키워드/종목 목록. 인증: Optional."""
    # TODO(구현 필요):
    # - current_user 있으면 UserInterest.user_id == current_user.id 조회
    # - 없으면 GuestInterest.session_token == guest_session_id (expires_at > now) 조회
    raise NotImplementedError


@router.post("", response_model=ApiResponse[InterestItem], status_code=201)
async def create_interest(
    body: InterestCreateRequest,
    current_user: User | None = Depends(get_optional_user),
    guest_session_id: str = Depends(get_guest_session_id),
    db: AsyncSession = Depends(get_db),
):
    """관심 키워드/종목 추가. 인증: Optional.
    응답 헤더에 X-Guest-Session-Id 포함 (get_guest_session_id Depends가 자동 처리).
    """
    # TODO(구현 필요):
    # 1. 중복 등록 체크 -> ConflictException(409)
    # 2. current_user 있으면 UserInterest insert, 없으면 GuestInterest insert (TTL 적용)
    # 3. 비동기로 interest_embeddings 생성 트리거 (app/services/rag_service.py)
    #    - 지금 단계는 동기 호출도 가능, 추후 Celery task로 분리 권장
    raise NotImplementedError


@router.delete("/{interest_id}", response_model=ApiResponse[None])
async def delete_interest(
    interest_id: int,
    current_user: User | None = Depends(get_optional_user),
    guest_session_id: str = Depends(get_guest_session_id),
    db: AsyncSession = Depends(get_db),
):
    """관심 항목 삭제. 인증: Optional."""
    # TODO(구현 필요): 소유자 확인 (user_id 또는 session_token 일치) -> 불일치 시 403 ForbiddenException
    raise NotImplementedError


@router.post("/migrate", response_model=ApiResponse[InterestMigrateResponse])
async def migrate_guest_interests(
    body: InterestMigrateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """비로그인 임시 관심사를 로그인 계정으로 이전. 인증: Required."""
    # TODO(구현 필요):
    # 1. GuestInterest.session_token == body.guest_session_id 전체 조회
    # 2. 각 row를 UserInterest로 변환 insert (중복 제외)
    # 3. 이전 완료된 GuestInterest는 삭제 (또는 만료 처리)
    raise NotImplementedError
