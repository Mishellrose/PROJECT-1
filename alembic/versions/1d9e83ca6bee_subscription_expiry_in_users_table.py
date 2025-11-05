"""subscription_expiry in users table

Revision ID: 1d9e83ca6bee
Revises: bb4adfff323a
Create Date: 2025-11-03 15:45:31.625235

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1d9e83ca6bee'
down_revision: Union[str, Sequence[str], None] = 'bb4adfff323a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users',
                  sa.Column('subscription_expiry',sa.DateTime,nullable=True))
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users','subscription_expiry')
    pass
