"""Recreate initial tables

Revision ID: cc73f37941da
Revises: 175a4807d4f0
Create Date: 2024-05-22 18:42:38.480164

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cc73f37941da'
down_revision: Union[str, None] = '175a4807d4f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
