"""Initial schema creation

Revision ID: 1b9200420aa9
Revises: 
Create Date: 2026-06-26 14:45:44.780877

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1b9200420aa9'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create Users Table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False)
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # 2. Create Audit Logs Table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('action', sa.String(length=255), nullable=False),
        sa.Column('details', sa.Text(), nullable=True)
    )
    op.create_index(op.f('ix_audit_logs_id'), 'audit_logs', ['id'], unique=False)

    # 3. Create Alarms Table
    op.create_table(
        'alarms',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.Column('severity', sa.String(length=50), nullable=False),
        sa.Column('message', sa.Text(), nullable=False)
    )
    op.create_index(op.f('ix_alarms_id'), 'alarms', ['id'], unique=False)

    # 4. Create Telemetry Table
    op.create_table(
        'telemetry',
        sa.Column('time', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False, primary_key=True),
        sa.Column('measurement_id', sa.String(length=50), nullable=False),
        sa.Column('voltage_v', sa.Float(), nullable=True),
        sa.Column('current_a', sa.Float(), nullable=True),
        sa.Column('active_power_kw', sa.Float(), nullable=True),
        sa.Column('reactive_power_kvar', sa.Float(), nullable=True),
        sa.Column('power_factor', sa.Float(), nullable=True),
        sa.Column('frequency_hz', sa.Float(), nullable=True),
        sa.Column('energized', sa.Boolean(), nullable=True),
        sa.Column('fault_current', sa.Boolean(), nullable=True)
    )
    
    # Turn Telemetry into a TimescaleDB hypertable
    op.execute("SELECT create_hypertable('telemetry', 'time', if_not_exists => TRUE);")


def downgrade() -> None:
    op.drop_table('telemetry')
    op.drop_index(op.f('ix_alarms_id'), table_name='alarms')
    op.drop_table('alarms')
    op.drop_index(op.f('ix_audit_logs_id'), table_name='audit_logs')
    op.drop_table('audit_logs')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###
