"""add cccd column to nhan_vien

Revision ID: 004
Revises: 003
Create Date: 2026-07-01

Adds cccd (Căn cước công dân) column to nhan_vien table.
"""
from alembic import op
import sqlalchemy as sa

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "nhan_vien",
        sa.Column("cccd", sa.String(12), nullable=True, unique=True),
    )
    op.create_index("ix_nhan_vien_cccd", "nhan_vien", ["cccd"])


def downgrade() -> None:
    op.drop_index("ix_nhan_vien_cccd", table_name="nhan_vien")
    op.drop_column("nhan_vien", "cccd")
