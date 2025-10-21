"""profile picture attribute

Revision ID: 3a96e6673f83
Revises: 25c0a4a25aca
Create Date: 2025-10-10 22:58:29.226992

"""
from typing import Sequence, Union
from fastapi import File,UploadFile
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3a96e6673f83'
down_revision: Union[str, Sequence[str], None] = '25c0a4a25aca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('profile',sa.Column
    ('profile_picture',sa.String(),nullable=True))
    pass


def downgrade() -> None:
    op.drop_column('profile','profile_picture')
    pass
