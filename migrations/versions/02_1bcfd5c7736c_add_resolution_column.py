"""add resolution column

Revision ID: 1bcfd5c7736c
Revises: 9018b4fb75f3
Create Date: 2024-09-02 22:38:31.264043

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1bcfd5c7736c"
down_revision: Union[str, None] = "9018b4fb75f3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "chat_messages", sa.Column("is_resolution", sa.Boolean(), nullable=False)
    )


def downgrade() -> None:
    op.drop_column("chat_messages", "is_resolution")
