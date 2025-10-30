"""create new table match table

Revision ID: ba12cafb8ab5
Revises: 46f75432cadd
Create Date: 2025-10-29 19:22:09.219393

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ba12cafb8ab5'
down_revision: Union[str, Sequence[str], None] = '46f75432cadd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table("MatchTable",
                    sa.Column("id", sa.Integer, primary_key=True, nullable=False),
                    sa.Column("user_id", sa.Integer, nullable=False),
                    sa.Column("user_name", sa.String, nullable=False),
                    sa.Column("matched_user_id", sa.Integer, nullable=False),
                    sa.Column("matched_user_name", sa.String, nullable=False)
    )

    pass


def downgrade() -> None:
    op.drop_table("MatchTable")
    pass
