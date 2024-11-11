"""Add RepeatType enum to reminder properlys

Revision ID: b30cb31b20b1
Revises: 25ab781aab0f
Create Date: 2024-10-01 14:58:55.119161

"""

from typing import Optional, Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b30cb31b20b1"
down_revision: Optional[str] = "25ab781aab0f"
branch_labels: Optional[Sequence[str]] = None
depends_on: Optional[Sequence[str]] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, "users", ["user_id"])
    op.execute("ALTER TYPE repeattype ADD VALUE 'MONTH'")

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "users", type_="unique")
    # ### end Alembic commands ###
