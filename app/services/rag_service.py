"""
RAG 핵심 로직. 설계서 7장 참고.
이 프로젝트의 학습 목표(RAG/임베딩 활용)가 집약되는 모듈.

흐름: Retrieval(유사 이슈 검색) -> Augmentation(프롬프트 조립) -> Generation(LLM 호출)
유사도 검색은 pgvector의 `<=>` 연산자로 DB에 위임한다 (app/models/news.py 참고).
"""
from sqlalchemy.ext.asyncio import AsyncSession


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

    TODO(구현 필요): is_active=True인 IssueCluster를 centroid_embedding(NewsEmbedding.embedding)
    기준 pgvector 코사인 거리 순으로 정렬해 top_k개 조회.
        SELECT ic.id FROM issue_clusters ic
        JOIN news_embeddings ne ON ne.id = ic.centroid_embedding_id
        WHERE ic.is_active = true
        ORDER BY ne.embedding <=> :query_embedding
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
