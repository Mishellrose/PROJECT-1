"""added name column in user table

Revision ID: 25c0a4a25aca
Revises: 
Create Date: 2025-10-10 22:21:33.690999

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '25c0a4a25aca'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users',
                  sa.Column('name',sa.String(),nullable=False)                
                  )
    pass


def downgrade() -> None:
    op.drop_column('users','name')
    pass
