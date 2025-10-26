"""temporary table create

Revision ID: e72f781e1c6d
Revises: 470d59be276b
Create Date: 2025-10-25 19:00:30.550289

"""
from typing import Sequence, Union
from sqlalchemy import Column
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e72f781e1c6d'
down_revision: Union[str, Sequence[str], None] = '470d59be276b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table("temptable",
        sa.Column("user_id",sa.Integer),
        sa.Column("hotspot_location",sa.String),
        sa.ForeignKeyConstraint(['user_id'],['users.id'],ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['hotspot_location'],['hotspot.location'],ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'hotspot_location')
    )
    pass

#sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ondelete='CASCADE'),
   # sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
def downgrade() -> None:
    op.drop_table
    pass
