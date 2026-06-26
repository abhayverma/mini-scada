"""add_permissions_rbac

Revision ID: 37ffc0f6f744
Revises: 1b9200420aa9
Create Date: 2026-06-26 16:39:16.832353

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '37ffc0f6f744'
down_revision: Union[str, None] = '1b9200420aa9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('permissions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), unique=True, nullable=False)
    )
    # Seed data
    op.execute("INSERT INTO permissions (name) VALUES ('operate_switches'), ('view_audit_logs'), ('view_telemetry')")
    
    # Add a role_permissions mapping
    op.create_table('role_permissions',
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('permission_id', sa.Integer(), sa.ForeignKey('permissions.id'))
    )


def downgrade() -> None:
    pass
