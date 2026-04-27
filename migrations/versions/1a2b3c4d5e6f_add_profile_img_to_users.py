"""Add profile_img to users

Revision ID: 1a2b3c4d5e6f
Revises: 
Create Date: 2026-04-26 23:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1a2b3c4d5e6f'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('profile_img', sa.String(length=500), nullable=True), schema='auth')


def downgrade() -> None:
    op.drop_column('users', 'profile_img', schema='auth')
