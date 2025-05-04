"""add_s3_export_path

Revision ID: 1a8fdc23eb6f
Revises: 9023b46c8d4c
Create Date: 2025-04-22 20:01:13.247491

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1a8fdc23eb6f'
down_revision: Union[str, None] = '9023b46c8d4c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add s3_export_path column to generation_metadata table
    with op.batch_alter_table('generation_metadata', schema=None) as batch_op:
        batch_op.add_column(sa.Column('s3_export_path', sa.Text(), nullable=True))

    # Add s3_export_path column to export_metadata table
    with op.batch_alter_table('export_metadata', schema=None) as batch_op:
        batch_op.add_column(sa.Column('s3_export_path', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove s3_export_path column from generation_metadata table
    with op.batch_alter_table('generation_metadata', schema=None) as batch_op:
        batch_op.drop_column('s3_export_path')

    # Remove s3_export_path column from export_metadata table
    with op.batch_alter_table('export_metadata', schema=None) as batch_op:
        batch_op.drop_column('s3_export_path')
