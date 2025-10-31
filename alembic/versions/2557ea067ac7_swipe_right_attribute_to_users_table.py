"""swipe_right attribute to users table

Revision ID: 2557ea067ac7
Revises: c682202b5284
Create Date: 2025-10-31 16:12:01.564095

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2557ea067ac7'
down_revision: Union[str, Sequence[str], None] = '46f75432cadd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('daily_swipe_count', sa.Integer, server_default='0',nullable=False))
    op.add_column('users',sa.Column('last_swipe_reset',sa.Date(), nullable=True))
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'last_swipe_reset')
    op.drop_column('users', 'daily_swipe_count')
    pass
