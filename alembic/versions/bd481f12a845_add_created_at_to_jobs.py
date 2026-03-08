"""add created_at to jobs

Revision ID: bd481f12a845
Revises: 3c8c391355de
Create Date: 2026-03-07
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "bd481f12a845"
down_revision: Union[str, Sequence[str], None] = "3c8c391355de"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.execute("UPDATE jobs SET alert_channel = 'discord' WHERE alert_channel IS NULL")
    op.execute("UPDATE jobs SET consecutive_failures = 0 WHERE consecutive_failures IS NULL")

    op.alter_column(
        "jobs",
        "alert_channel",
        existing_type=sa.String(length=20),
        nullable=False,
    )

    op.alter_column(
        "jobs",
        "last_output",
        existing_type=sa.JSON(),
        type_=postgresql.JSONB(astext_type=sa.Text()),
        existing_nullable=True,
        postgresql_using="last_output::jsonb",
    )

def downgrade() -> None:
    op.alter_column(
        "jobs",
        "last_output",
        existing_type=postgresql.JSONB(astext_type=sa.Text()),
        type_=sa.JSON(),
        existing_nullable=True,
        postgresql_using="last_output::json",
    )

    op.alter_column(
        "jobs",
        "alert_channel",
        existing_type=sa.String(length=20),
        nullable=True,
    )