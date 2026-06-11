"""add memories and user_preferences tables

Revision ID: d01066597cc0
Revises: 46ef651ce216
Create Date: 2026-06-06 16:00:00.000000

"""
from typing import Sequence, Union

import pgvector
from alembic import op
import sqlalchemy as sa


revision: str = 'd01066597cc0'
down_revision: Union[str, Sequence[str], None] = '46ef651ce216'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    is_sqlite = conn.dialect.name == 'sqlite'

    op.create_table(
        'memories',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), nullable=False, index=True),
        sa.Column('session_id', sa.String(length=36), sa.ForeignKey('sessions.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('memory_type', sa.String(length=30), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding', sa.Text() if is_sqlite else pgvector.sqlalchemy.vector.VECTOR(dim=384), nullable=True),
        sa.Column('importance', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('source', sa.String(length=50), nullable=False, server_default='extraction'),
        sa.Column('access_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_accessed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('meta_json', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    op.create_table(
        'user_preferences',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), unique=True, nullable=False, index=True),
        sa.Column('preferences', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )


def downgrade() -> None:
    op.drop_table('user_preferences')
    op.drop_table('memories')
