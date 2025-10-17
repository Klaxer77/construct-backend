"""init2

Revision ID: e30a08093767
Revises: 5c6afe51ee7a
Create Date: 2025-10-17 12:14:16.938770

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e30a08093767'
down_revision: Union[str, Sequence[str], None] = '5c6afe51ee7a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    list_of_works_status_enum = sa.Enum(
        'PASSED', 'AWAITING_VERIFICATION', 'VERIFICATION_REJECTED',
        name='list_of_works_status_enum'
    )
    list_of_works_status_enum.create(op.get_bind(), checkfirst=True)

    op.add_column('list_of_works', sa.Column('status', list_of_works_status_enum, nullable=False, server_default='AWAITING_VERIFICATION'))


def downgrade() -> None:
    op.drop_column('list_of_works', 'status')

    list_of_works_status_enum = sa.Enum(
        'PASSED', 'AWAITING_VERIFICATION', 'VERIFICATION_REJECTED',
        name='list_of_works_status_enum'
    )
    list_of_works_status_enum.drop(op.get_bind(), checkfirst=True)