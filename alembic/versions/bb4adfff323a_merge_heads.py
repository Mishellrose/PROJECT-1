"""merge heads

Revision ID: bb4adfff323a
Revises: 2557ea067ac7, c682202b5284
Create Date: 2025-11-01 11:38:19.330336

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bb4adfff323a'
down_revision: Union[str, Sequence[str], None] = ('2557ea067ac7', 'c682202b5284')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
