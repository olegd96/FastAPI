"""Create rate in bookings

Revision ID: e1aa3a26f9ef
Revises: 90adf8ac3bdc
Create Date: 2024-04-06 22:17:45.162868

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e1aa3a26f9ef'
down_revision: Union[str, None] = '90adf8ac3bdc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bookings', sa.Column('rate', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('bookings', 'rate')
    # ### end Alembic commands ###
