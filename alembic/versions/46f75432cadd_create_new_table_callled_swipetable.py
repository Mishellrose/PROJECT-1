"""create new table callled SwipeTable

Revision ID: 46f75432cadd
Revises: 470d59be276b
Create Date: 2025-10-29 18:11:30.876801

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '46f75432cadd'
down_revision: Union[str, Sequence[str], None] = '470d59be276b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table("SwipeTable",
                    sa.Column("id", sa.Integer(),primary_key=True, nullable=False),
                    sa.Column("user_id", sa.Integer(), nullable=False),
                    sa.Column("user_name", sa.String(), nullable=False),
                    sa.Column("swiped_on_id", sa.Integer(), nullable=False),
                    sa.Column("swiped_on_id_name", sa.String(), nullable=False),
                    sa.Column("direction", sa.String(), nullable=False)
                    )
    pass


def downgrade() -> None:
    op.drop_table
    pass
