"""Recreate initial tables

Revision ID: 40cdfcb5d376
Revises: cc73f37941da
Create Date: 2024-05-22 18:42:51.766164

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '40cdfcb5d376'
down_revision: Union[str, None] = 'cc73f37941da'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
