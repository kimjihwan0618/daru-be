"""
뉴스 중복 제거 / 클러스터링 로직. 설계서 7.1 참고.
Celery task(app/workers/tasks_news_dedup.py)에서 호출될 함수들.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.news import RawArticle


async def process_new_article(article: RawArticle, db: AsyncSession) -> int:
    """
    신규 기사를 임베딩 -> 기존 클러스터와 유사도 비교 -> 클러스터 할당 또는 신규 생성.
    Returns: 할당된(또는 신규 생성된) IssueCluster.id

    TODO(구현 필요) - 설계서 7.1 흐름:
    1. embedding = await rag_service.embed_text(article.title + article.content_snippet)
    2. NewsEmbedding row 저장
    3. rag_service.find_similar_issue_clusters(embedding, db, top_k=1) 로 가장 유사한 클러스터 탐색
    4. 유사도 >= settings.NEWS_CLUSTER_SIMILARITY_THRESHOLD 이면:
       - 해당 IssueCluster에 article 연결 (cluster_id 갱신)
       - centroid_embedding 재계산 (클러스터 내 임베딩 평균)
       - article_count += 1
    5. 아니면 신규 IssueCluster 생성 후 article 연결
    6. article_count가 3 이상이 된 클러스터는 요약 트리거 대상으로 표시 (반환값 또는 별도 큐)
    """
    raise NotImplementedError


async def recompute_centroid(cluster_id: int, db: AsyncSession) -> None:
    """
    클러스터 내 모든 기사 임베딩의 평균(centroid) 재계산.
    TODO(구현 필요): NewsEmbedding 들의 평균 벡터 계산 후 IssueCluster.centroid_embedding_id 갱신
    (평균 벡터를 NewsEmbedding 테이블에 새로 저장하거나, 별도 컬럼 운용 - 설계 시 결정 필요)
    """
    raise NotImplementedError
