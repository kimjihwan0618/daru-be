"""
뉴스/이슈 관련 모델. 설계서 4.1, 4.2 - raw_articles / issue_clusters / news_embeddings 대응.

임베딩 컬럼은 pgvector의 Vector(1536) 타입을 사용한다. 유사도 검색은
`embedding <=> :query` 연산자로 DB에 위임한다 (app/services/rag_service.py 참고).
`CREATE EXTENSION IF NOT EXISTS vector;`가 선행되어야 하며, HNSW 인덱스는
Alembic migration에서 `CREATE INDEX ... USING hnsw (embedding vector_cosine_ops)`로 추가한다.
"""
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import ARRAY, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class IssueCluster(Base):
    """중복 제거된 핵심 이슈. 설계서 4.1 - issue_clusters 대응."""

    __tablename__ = "issue_clusters"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)  # 반도체/금리/AI 등
    article_count: Mapped[int] = mapped_column(Integer, default=0)

    # 클러스터 대표 벡터를 가리키는 참조 (NewsEmbedding.id). pgvector 전환 후에도 유지.
    centroid_embedding_id: Mapped[int | None] = mapped_column(
        ForeignKey("news_embeddings.id"), nullable=True
    )

    # 관련 종목 코드 목록.
    related_stock_codes: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    is_active: Mapped[bool] = mapped_column(default=True)  # 당일 브리핑 노출 여부

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    articles: Mapped[list["RawArticle"]] = relationship(back_populates="cluster")

    # TODO(구현 필요): category 별 인덱스, is_active + created_at 복합 인덱스(당일 이슈 조회용)


class RawArticle(Base):
    """수집된 원본 기사. 설계서 4.1 - raw_articles 대응."""

    __tablename__ = "raw_articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(50))  # 언론사명
    title: Mapped[str] = mapped_column(String(300))
    url: Mapped[str] = mapped_column(String(500), unique=True)
    published_at: Mapped[datetime] = mapped_column(DateTime)
    content_snippet: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)

    cluster_id: Mapped[int | None] = mapped_column(ForeignKey("issue_clusters.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    cluster: Mapped["IssueCluster | None"] = relationship(back_populates="articles")

    # TODO(구현 필요): url unique 제약을 활용한 수집 단계 중복 insert 방지(ON CONFLICT DO NOTHING)


class NewsEmbedding(Base):
    """기사 본문 임베딩. 설계서 4.2 - news_embeddings 대응."""

    __tablename__ = "news_embeddings"

    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("raw_articles.id", ondelete="CASCADE"))
    embedding: Mapped[list[float]] = mapped_column(Vector(1536))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # TODO(구현 필요): article_id unique 제약 (기사 1건당 임베딩 1개)


class InterestEmbedding(Base):
    """사용자/게스트 관심 키워드의 임베딩. RAG retrieval용. 설계서 4.2 - interest_embeddings 대응."""

    __tablename__ = "interest_embeddings"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_type: Mapped[str] = mapped_column(String(10))  # USER / GUEST
    owner_ref_id: Mapped[str] = mapped_column(String(64))  # user_id(str) 또는 guest session_token
    keyword: Mapped[str] = mapped_column(String(100))
    embedding: Mapped[list[float]] = mapped_column(Vector(1536))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # TODO(구현 필요): (owner_type, owner_ref_id, keyword) unique 제약
