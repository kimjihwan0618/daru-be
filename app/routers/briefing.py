"""
브리핑 라우터. 설계서 6.2 / 6.3 엔드포인트 명세 대응.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_guest_session_id, get_optional_user
from app.models.user import User
from app.schemas.briefing import (
    BriefingFeedbackRequest,
    ChangeEvidenceResponse,
    ShareBriefingResponse,
    TodayBriefingResponse,
    TopicBriefingResponse,
    TopicSummary,
)
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/briefings", tags=["briefing"])


@router.get("/today", response_model=ApiResponse[TodayBriefingResponse])
async def get_today_briefing(
    time_slot: str | None = Query(default=None, description="MORNING / EVENING"),
    current_user: User | None = Depends(get_optional_user),
    guest_session_id: str = Depends(get_guest_session_id),
    db: AsyncSession = Depends(get_db),
):
    """오늘의 브리핑. 인증: Optional.
    - 로그인: user_briefings 조회, 캐시 없으면 온디맨드 생성 fallback
    - 비로그인: daily_briefings(공통) 조회
    """
    # TODO(구현 필요): app/services/briefing_service.py 의 get_today_briefing() 호출
    # 1. time_slot 미지정 시 현재 시각 기준 MORNING/EVENING 판단
    # 2. current_user가 있으면 UserBriefing 조회 -> 없으면 rag_service로 즉시 1회 생성
    # 3. current_user가 없으면 DailyBriefing 조회
    # 4. weather는 app/external/weather_client.py 로 실시간 조회 (또는 캐시)
    raise NotImplementedError


@router.get("/today/changes/{change_id}/evidence", response_model=ApiResponse[ChangeEvidenceResponse])
async def get_change_evidence(
    change_id: int,
    current_user: User | None = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """"근거 보기" - 중요 변화 항목의 출처 근거. 인증: Optional."""
    # TODO(구현 필요): change_id -> issue_id 매핑 후 IssueCluster.articles 조회해 근거 조립
    raise NotImplementedError


@router.post("/today/share", response_model=ApiResponse[ShareBriefingResponse])
async def share_today_briefing(
    current_user: User | None = Depends(get_optional_user),
    guest_session_id: str = Depends(get_guest_session_id),
    db: AsyncSession = Depends(get_db),
):
    """브리핑 공유 링크 생성. 인증: Optional."""
    # TODO(구현 필요): app/services/share_service.py - SharedBriefing row 생성 + share_token 발급
    raise NotImplementedError


@router.get("/shared/{share_token}", response_model=ApiResponse[TodayBriefingResponse])
async def get_shared_briefing(share_token: str, db: AsyncSession = Depends(get_db)):
    """공유받은 브리핑 조회 (공유 당시 스냅샷). 인증: Public."""
    # TODO(구현 필요): SharedBriefing.share_token 으로 조회 후 원본 브리핑 데이터 반환
    raise NotImplementedError


@router.post("/today/feedback", response_model=ApiResponse[None])
async def submit_briefing_feedback(
    body: BriefingFeedbackRequest,
    current_user: User | None = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """브리핑 피드백(👍👎) 수집. 인증: Optional."""
    # TODO(구현 필요): 피드백 저장 테이블 별도 설계 필요 (설계서 ERD에 없음 - 추가 검토)
    raise NotImplementedError


@router.get("/topics", response_model=ApiResponse[list[TopicSummary]])
async def list_topics(db: AsyncSession = Depends(get_db)):
    """주제별 브리핑 목록 (AI/반도체/경제 등). 인증: Public."""
    # TODO(구현 필요): IssueCluster.category 별 group by + count
    raise NotImplementedError


@router.get("/topics/{topic_code}", response_model=ApiResponse[TopicBriefingResponse])
async def get_topic_briefing(topic_code: str, db: AsyncSession = Depends(get_db)):
    """특정 주제 브리핑 본문 + 관련 이슈 목록. 인증: Public."""
    # TODO(구현 필요): category=topic_code 인 IssueCluster 목록 + 주제 요약(LLM 생성본 또는 캐시) 조회
    raise NotImplementedError
