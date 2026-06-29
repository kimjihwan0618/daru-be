"""
RAG 핵심 로직. 설계서 7장 참고.
이 프로젝트의 학습 목표(RAG/임베딩 활용)가 집약되는 모듈.

흐름: Retrieval(유사 이슈 검색) -> Augmentation(프롬프트 조립) -> Generation(LLM 호출)
"""
from sqlalchemy.ext.asyncio import AsyncSession


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    코사인 유사도 계산.

    NOTE: 현재 SQLite 단계에서는 DB가 벡터 연산을 못 하므로
    애플리케이션 레벨(이 함수)에서 직접 계산해야 한다.
    PostgreSQL+pgvector 전환 후에는 SQL의 `<=>` 연산자로 대체 가능
    (app/models/news.py 모듈 docstring의 전환 가이드 참고).

    TODO(구현 필요): numpy 사용 권장
        import numpy as np
        a, b = np.array(vec_a), np.array(vec_b)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
    """
    raise NotImplementedError


async def embed_text(text: str) -> list[float]:
    """
    OpenAI Embedding API 호출.
    TODO(구현 필요): app/external/openai_client.py 의 클라이언트 사용
        response = client.embeddings.create(model=settings.OPENAI_EMBEDDING_MODEL, input=text)
        return response.data[0].embedding
    """
    raise NotImplementedError


async def find_similar_issue_clusters(
    query_embedding: list[float],
    db: AsyncSession,
    top_k: int = 3,
) -> list[int]:
    """
    쿼리 임베딩과 가장 유사한 IssueCluster id 목록 반환.

    TODO(구현 필요) - SQLite 단계:
    1. is_active=True인 IssueCluster 전체의 centroid_embedding(NewsEmbedding) 로드
    2. 각각에 대해 cosine_similarity() 계산 (전체 스캔 - 데이터 적을 때만 허용)
    3. 유사도 내림차순 top_k개의 IssueCluster.id 반환

    TODO(구현 필요) - PostgreSQL+pgvector 전환 후:
    SQL로 대체:
        SELECT id FROM issue_clusters
        ORDER BY centroid_embedding <=> :query_embedding
        LIMIT :top_k
    """
    raise NotImplementedError


async def generate_personalized_briefing(
    user_id: int,
    base_briefing_text: str,
    interest_keywords: list[str],
    db: AsyncSession,
) -> dict:
    """
    개인화 브리핑 생성 (RAG 본체). 설계서 7.3 참고.

    TODO(구현 필요):
    1. Retrieval: interest_keywords 각각을 embed_text() -> find_similar_issue_clusters()
       로 관련 이슈 클러스터 수집 (중복 제거)
    2. Augmentation: 시스템 프롬프트 + base_briefing_text + interest_keywords
       + retrieval된 이슈 요약들을 조합한 user 프롬프트 작성 (설계서 7.3의 프롬프트 예시 참고)
    3. Generation: app/external/openai_client.py 로 chat completion 호출
       (response_format json_object 권장 - "오늘 나에게 중요한 변화 3가지" + 헤드라인 구조로 받기)
    4. 결과를 dict로 반환 (호출부에서 UserBriefing에 저장)
    """
    raise NotImplementedError


async def summarize_issue_cluster(article_titles: list[str]) -> dict:
    """
    이슈 클러스터 요약 (설계서 7.2).
    TODO(구현 필요): LLM에 기사 제목 목록을 보내 headline/summary/category/related_stocks 추출
    (JSON mode 사용 권장)
    """
    raise NotImplementedError
