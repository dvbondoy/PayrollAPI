"""add gender column to employees

Revision ID: 6bb3b3ffdf37
Revises: 
Create Date: 2024-05-10 18:17:14.251406

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6bb3b3ffdf37'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # add column to employees table
    op.add_column('employees', sa.Column('gender', sa.String(10), nullable=True))
    pass


def downgrade() -> None:
    # remove column from employees table
    op.drop_column('employees', 'gender')
    pass
