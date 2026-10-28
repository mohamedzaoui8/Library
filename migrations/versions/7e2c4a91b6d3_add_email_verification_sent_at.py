"""add email verification sent timestamp

Revision ID: 7e2c4a91b6d3
Revises: 40cd133a7d7e
Create Date: 2026-10-27 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7e2c4a91b6d3"
down_revision: Union[str, Sequence[str], None] = "40cd133a7d7e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("email_verification_sent_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "email_verification_sent_at")
