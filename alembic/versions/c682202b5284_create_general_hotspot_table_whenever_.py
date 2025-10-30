"""Create general hotspot table, whenever inside,add each entry

Revision ID: c682202b5284
Revises: ba12cafb8ab5
Create Date: 2025-10-29 19:43:22.604537

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c682202b5284'
down_revision: Union[str, Sequence[str], None] = 'ba12cafb8ab5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table("General_hotspot",
                    sa.Column("id", sa.Integer, primary_key= True, nullable=False),
                    sa.Column("user_id", sa.Integer, nullable=False ),
                    sa.Column("user_name", sa.String, nullable=False),
                    sa.Column("hotspot_location", sa.String, nullable=False)
                    )
    pass


def downgrade() -> None:
    op.drop_table("General_hotspot")
    """Downgrade schema."""
    pass
