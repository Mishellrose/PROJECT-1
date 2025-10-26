"""location attribute in hotspot table

Revision ID: 470d59be276b
Revises: 9017967df282
Create Date: 2025-10-25 17:37:48.681639

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '470d59be276b'
down_revision: Union[str, Sequence[str], None] = '9017967df282'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('hotspot', sa.Column('location', sa.String, unique=True, nullable=False))
    pass


def downgrade() -> None:
    op.drop_column('hotspot', 'location')
    pass
