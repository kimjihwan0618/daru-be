"""JSON 배열 컬럼을 postgres ARRAY 타입으로 대체 (sqlite 호환 흔적 제거)

Revision ID: 503b754c8b0b
Revises: 1dd57a123049
Create Date: 2026-07-04 08:14:43.115328

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '503b754c8b0b'
down_revision: Union[str, None] = '1dd57a123049'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 테이블이 비어 있어 데이터 캐스팅 없이 drop/add로 교체한다.
    op.drop_column('daily_briefings', 'top_issue_ids')
    op.add_column(
        'daily_briefings',
        sa.Column('top_issue_ids', sa.ARRAY(sa.Integer()), nullable=False, server_default='{}'),
    )

    op.drop_column('user_briefings', 'matched_issue_ids')
    op.add_column(
        'user_briefings',
        sa.Column('matched_issue_ids', sa.ARRAY(sa.Integer()), nullable=False, server_default='{}'),
    )

    op.drop_column('issue_clusters', 'related_stock_codes')
    op.add_column(
        'issue_clusters',
        sa.Column('related_stock_codes', sa.ARRAY(sa.String()), nullable=False, server_default='{}'),
    )


def downgrade() -> None:
    op.drop_column('issue_clusters', 'related_stock_codes')
    op.add_column(
        'issue_clusters',
        sa.Column('related_stock_codes', sa.JSON(), nullable=False, server_default='[]'),
    )

    op.drop_column('user_briefings', 'matched_issue_ids')
    op.add_column(
        'user_briefings',
        sa.Column('matched_issue_ids', sa.JSON(), nullable=False, server_default='[]'),
    )

    op.drop_column('daily_briefings', 'top_issue_ids')
    op.add_column(
        'daily_briefings',
        sa.Column('top_issue_ids', sa.JSON(), nullable=False, server_default='[]'),
    )
