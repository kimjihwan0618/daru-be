"""pgvector 익스텐션 및 임베딩 컬럼 Vector(1536) 전환

DB 서버에 vector 익스텐션이 설치되어 있어야 적용 가능하다
(예: `apt install postgresql-16-pgvector` 후 서버 재시작).
설치 전에는 `alembic upgrade head`가 CREATE EXTENSION 단계에서 실패한다.

Revision ID: 6b4e42ce91e4
Revises: 503b754c8b0b
Create Date: 2026-07-04 08:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = '6b4e42ce91e4'
down_revision: Union[str, None] = '503b754c8b0b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    # 테이블이 비어 있어 데이터 캐스팅 없이 drop/add로 교체한다.
    op.drop_column('news_embeddings', 'embedding')
    op.add_column('news_embeddings', sa.Column('embedding', Vector(1536), nullable=False))

    op.drop_column('interest_embeddings', 'embedding')
    op.add_column('interest_embeddings', sa.Column('embedding', Vector(1536), nullable=False))

    op.create_index(
        'ix_news_embeddings_embedding_hnsw',
        'news_embeddings',
        ['embedding'],
        unique=False,
        postgresql_using='hnsw',
        postgresql_with={'m': 16, 'ef_construction': 64},
        postgresql_ops={'embedding': 'vector_cosine_ops'},
    )


def downgrade() -> None:
    op.drop_index('ix_news_embeddings_embedding_hnsw', table_name='news_embeddings')

    op.drop_column('interest_embeddings', 'embedding')
    op.add_column('interest_embeddings', sa.Column('embedding', sa.JSON(), nullable=False))

    op.drop_column('news_embeddings', 'embedding')
    op.add_column('news_embeddings', sa.Column('embedding', sa.JSON(), nullable=False))
