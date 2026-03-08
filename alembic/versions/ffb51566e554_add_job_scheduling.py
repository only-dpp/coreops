"""add job scheduling

Revision ID: ffb51566e554
Revises: c0c5ffe4af26
Create Date: 2026-03-04 03:24:24.165524

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ffb51566e554'
down_revision: Union[str, Sequence[str], None] = 'c0c5ffe4af26'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

def upgrade():
    op.add_column("jobs", sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")))
    op.add_column("jobs", sa.Column("interval_seconds", sa.Integer(), nullable=False, server_default="60"))
    op.add_column("jobs", sa.Column("next_run_at", sa.DateTime(timezone=True), nullable=True))
    op.alter_column("jobs", "enabled", server_default=None)
    op.alter_column("jobs", "interval_seconds", server_default=None)

def downgrade():
    op.drop_column("jobs", "next_run_at")
    op.drop_column("jobs", "interval_seconds")
    op.drop_column("jobs", "enabled")