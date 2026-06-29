"""
뉴스 중복제거/클러스터링 + 이슈 요약 task. 설계서 2.1 데이터 흐름 2~3단계.
"""
from app.workers.taskiq_app import broker


@broker.task(schedule=[{"cron": "*/10 * * * *"}])
async def dedup_and_cluster():
    """
    TODO(구현 필요):
    1. cluster_id가 아직 없는 RawArticle 조회
    2. 각각에 app/services/news_dedup_service.process_new_article() 호출
    3. article_count가 3 이상이 된 클러스터는 summarize_clusters로 전달
    """
    raise NotImplementedError


@broker.task()
async def summarize_clusters():
    """
    TODO(구현 필요):
    1. summary가 아직 없거나 article_count가 최근 갱신된 IssueCluster 조회
    2. app/services/rag_service.summarize_issue_cluster() 호출해 LLM 요약 생성
    3. IssueCluster.summary, category, related_stock_codes 갱신
    """
    raise NotImplementedError
