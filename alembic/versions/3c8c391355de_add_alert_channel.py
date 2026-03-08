"""add alert channel

Revision ID: 3c8c391355de
Revises: 1e165d1c28ef
Create Date: 2026-03-07 19:42:26.048895

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3c8c391355de'
down_revision: Union[str, Sequence[str], None] = '1e165d1c28ef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "jobs",
        sa.Column("alert_channel", sa.String(), nullable=True)
    )

    op.add_column(
        "jobs",
        sa.Column("alert_target", sa.String(), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
