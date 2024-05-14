"""add attendance table

Revision ID: b85f298a257b
Revises: 6bb3b3ffdf37
Create Date: 2024-05-12 18:20:45.253733

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b85f298a257b'
down_revision: Union[str, None] = '6bb3b3ffdf37'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'attendance',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('employee_id', sa.Integer, sa.ForeignKey('employees.id')),
        sa.Column('date', sa.String(100)),
        sa.Column('time_in', sa.String(100)),
        sa.Column('time_out', sa.String(100))
    )
    # op.create_foreign_key('attendance_employee_id_fkey', 'attendance', 'employees', ['employee_id'], ['id'])
    pass


def downgrade() -> None:
    op.drop_table('attendance')
    pass
