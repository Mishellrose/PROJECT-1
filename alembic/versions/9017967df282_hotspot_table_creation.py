"""Hotspot table creation

Revision ID: 9017967df282
Revises: 520d25177a82
Create Date: 2025-10-24 13:49:42.571206

"""
from typing import Sequence, Union
from sqlalchemy import Column  
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9017967df282'
down_revision: Union[str, Sequence[str], None] = '520d25177a82'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table("hotspot",
                    Column("id",sa.Integer,primary_key=True,nullable=False),
                    Column("name",sa.String,nullable=False),
                    Column("description",sa.String,nullable=True),
                    Column("image",sa.String,nullable=True)
    )
    pass


def downgrade() -> None:
    op.drop_table
    pass
