"""Initial migration

Revision ID: 175a4807d4f0
Revises: 
Create Date: 2024-05-22 04:52:30.679511

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = '175a4807d4f0'
down_revision = None
branch_labels = None
depends_on = None

def table_exists(table_name):
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)
    return table_name in inspector.get_table_names()

def upgrade():
    op.create_table(
        'api_users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(), nullable=False, unique=True),
        sa.Column('password', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
    )
    op.create_table(
        'api_memories',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_message', sa.String(), nullable=False),
        sa.Column('llm_response', sa.String(), nullable=False),
        sa.Column('conversations_summary', sa.String(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('owner_id', sa.Integer(), sa.ForeignKey('api_users.id', ondelete='CASCADE'), nullable=False),
    )
    op.create_table(
        'api_votes',
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('api_users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('post_id', sa.Integer(), sa.ForeignKey('api_memories.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('memory_id', sa.Integer(), sa.ForeignKey('api_memories.id'), nullable=True),
    )

def downgrade():
    op.drop_table('api_votes', if_exists=True)
    op.drop_table('api_memories', if_exists=True)
    op.drop_table('api_users', if_exists=True)
