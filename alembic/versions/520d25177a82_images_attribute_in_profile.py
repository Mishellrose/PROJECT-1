"""images attribute in profile

Revision ID: 520d25177a82
Revises: 3a96e6673f83
Create Date: 2025-10-12 12:50:52.920550

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '520d25177a82'
down_revision: Union[str, Sequence[str], None] = '3a96e6673f83'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('profile',
                  sa.Column('images',sa.String(),nullable=True))
    pass


def downgrade() -> None:
    op.drop_column('profile','images')
    
    pass
