"""make phone_number nullable for social auth users

Revision ID: 002
Revises: f876016b4480
Create Date: 2026-02-25 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "f876016b4480"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index("ix_users_phone_number", table_name="users")
    op.alter_column("users", "phone_number", existing_type=sa.String(50), nullable=True)
    op.execute(
        "CREATE UNIQUE INDEX ix_users_phone_number "
        "ON users (phone_number) WHERE phone_number IS NOT NULL"
    )


def downgrade() -> None:
    op.drop_index("ix_users_phone_number", table_name="users")
    op.alter_column("users", "phone_number", existing_type=sa.String(50), nullable=False)
    op.create_index("ix_users_phone_number", "users", ["phone_number"], unique=True)
