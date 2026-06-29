"""
브리핑 생성 task. 설계서 2.1 데이터 흐름 4~5단계.
"""
from app.workers.taskiq_app import broker


@broker.task(schedule=[
    {"cron": "0 6 * * *"},   # 매일 오전 6시 (MORNING)
    {"cron": "0 17 * * *"},  # 매일 오후 5시 (EVENING)
])
async def generate_daily_briefing():
    """
    TODO(구현 필요):
    1. 오늘 활성(is_active=True) 상위 IssueCluster들 조회 (article_count 기준 정렬)
    2. app/services/rag_service 활용해 LLM으로 공통 3분 브리핑 텍스트 생성
    3. DailyBriefing row 저장 (briefing_date=today, time_slot=현재 시각 기준)
    """
    raise NotImplementedError


@broker.task(schedule=[
    {"cron": "5 6 * * *"},   # 매일 오전 6시 5분 (MORNING)
    {"cron": "5 17 * * *"},  # 매일 오후 5시 5분 (EVENING)
])
async def generate_user_briefings():
    """
    TODO(구현 필요):
    1. 최근 활성 사용자(예: 최근 7일 내 로그인) 목록 조회
    2. 각 사용자의 UserInterest 조회
    3. rag_service.generate_personalized_briefing() 호출
    4. UserBriefing upsert
    """
    raise NotImplementedError
