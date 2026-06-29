"""
뉴스 수집 task. 설계서 2.1 데이터 흐름 1단계.
"""
from taskiq import TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource

from app.workers.taskiq_app import broker


@broker.task(schedule=[{"cron": "*/10 * * * *"}])
async def collect_news():
    """
    TODO(구현 필요):
    1. app/external/naver_news_client.py 로 주제별(반도체/금리/AI 등) 뉴스 검색
    2. 중복 url 제외하고 RawArticle insert
    3. 신규 저장된 article들을 dedup_and_cluster task에 전달(또는 다음 주기에 일괄 처리)
    """
    raise NotImplementedError


@broker.task(schedule=[{"cron": "0 * * * *"}])
async def cleanup_expired_guest_interests():
    """
    TODO(구현 필요): GuestInterest.expires_at < now() 인 row 삭제
    """
    raise NotImplementedError
