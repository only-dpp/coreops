"""add job scheduling

Revision ID: 17674761bb90
Revises: ffb51566e554
Create Date: 2026-03-04 03:28:09.747685

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '17674761bb90'
down_revision: Union[str, Sequence[str], None] = 'ffb51566e554'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
