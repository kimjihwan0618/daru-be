"""add weather_favorites table

pgvector 전환 마이그레이션(6b4e42ce91e4)이 로컬 환경에 vector 익스텐션이 없어
아직 적용되지 못한 상태라, 이 마이그레이션은 그와 무관하게 503b754c8b0b 위에 별도
브랜치로 얹는다. pgvector 익스텐션 설치 후에는 `alembic merge heads`로 합칠 것.

Revision ID: 7f3a9c2e5b1d
Revises: 503b754c8b0b
Create Date: 2026-07-20 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '7f3a9c2e5b1d'
down_revision: Union[str, None] = '503b754c8b0b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'weather_favorites',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('label', sa.String(length=50), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('weather_favorites')
