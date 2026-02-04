"""add_birth_charts_unique_constraint

Revision ID: 086bfce243f6
Revises: 7576219f0ea0
Create Date: 2026-02-04 14:23:31.936123

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '086bfce243f6'
down_revision: Union[str, Sequence[str], None] = '7576219f0ea0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add unique constraint on user_id in birth_charts."""
    # One birth chart per user
    op.create_unique_constraint(
        "uq_birth_charts_user_id",
        "birth_charts",
        ["user_id"]
    )


def downgrade() -> None:
    """Remove unique constraint."""
    op.drop_constraint("uq_birth_charts_user_id", "birth_charts", type_="unique")
