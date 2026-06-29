"""
브리핑 조합/캐싱 조회 로직.
설계서 7.3 개인화 브리핑 생성의 서빙(온라인) 단계를 담당.
실제 생성(LLM 호출)은 rag_service에 위임하고, 여기서는 캐시 조회 + fallback 트리거만 담당.
"""
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


def determine_time_slot(now_hour: int) -> str:
    """현재 시각 기준 MORNING/EVENING 판단.
    TODO(구현 필요): 정확한 경계 시각은 기획 확인 (예: 12시 이전 MORNING, 이후 EVENING)
    """
    return "MORNING" if now_hour < 12 else "EVENING"


async def get_today_briefing_for_user(user: User | None, time_slot: str, db: AsyncSession) -> dict:
    """
    오늘의 브리핑 조회. 로그인 여부에 따라 분기.

    TODO(구현 필요):
    1. user가 None이면:
       - DailyBriefing.briefing_date == today, time_slot == time_slot 조회
       - 없으면 아직 배치가 안 돌았다는 뜻 -> 503 또는 가장 최근 브리핑 fallback 정책 결정
    2. user가 있으면:
       - UserBriefing 캐시 조회
       - 캐시 없으면 (신규 가입/관심사 변경 직후) rag_service.generate_personalized_briefing()
         즉시 1회 호출 -> UserBriefing에 저장 후 반환 (설계서 8장 fallback 로직)
    3. 날씨(app/external/weather_client.py), 교통(commute) 등 브리핑 카드 내 다른 섹션과 조합
    """
    raise NotImplementedError


async def get_change_evidence(change_id: int, db: AsyncSession) -> dict:
    """
    "근거 보기" 클릭 시 출처 근거 조립.
    TODO(구현 필요): change_id로부터 연결된 issue_id 추적 후 IssueCluster.articles 조회
    """
    raise NotImplementedError
