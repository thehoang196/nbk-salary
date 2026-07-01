"""refactor position structure

Revision ID: 002
Revises: 001
Create Date: 2024-01-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. dm_chuc_vu
    op.create_table(
        "dm_chuc_vu",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("ma", sa.String(20), unique=True, nullable=False),
        sa.Column("ten", sa.String(100), nullable=False),
        sa.Column("don_gia_luong_khoan", sa.Numeric(12, 0), server_default=sa.text("0")),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
    )

    # 2. dm_cap_bac_ql
    op.create_table(
        "dm_cap_bac_ql",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("ma", sa.String(20), unique=True, nullable=False),
        sa.Column("ten", sa.String(100), nullable=False),
        sa.Column("don_gia_luong_khoan", sa.Numeric(12, 0), server_default=sa.text("0")),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
    )

    # 3. dm_nghiep_vu
    op.create_table(
        "dm_nghiep_vu",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("ma", sa.String(20), unique=True, nullable=False),
        sa.Column("ten", sa.String(100), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
    )

    # 4. dm_kiem_nhiem
    op.create_table(
        "dm_kiem_nhiem",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("ma", sa.String(20), unique=True, nullable=False),
        sa.Column("ten", sa.String(100), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
    )

    # 5. nv_nghiep_vu (junction: employee <-> nghiệp vụ)
    op.create_table(
        "nv_nghiep_vu",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("nhan_vien_id", sa.Integer(), sa.ForeignKey("nhan_vien.id"), nullable=False),
        sa.Column("nghiep_vu_id", sa.Integer(), sa.ForeignKey("dm_nghiep_vu.id"), nullable=False),
        sa.Column("mo_ta", sa.String(255), nullable=True),
        sa.Column("ngay_bat_dau", sa.Date(), nullable=False),
        sa.Column("ngay_ket_thuc", sa.Date(), nullable=True),
    )

    # 6. nv_kiem_nhiem (junction: employee <-> kiêm nhiệm)
    op.create_table(
        "nv_kiem_nhiem",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("nhan_vien_id", sa.Integer(), sa.ForeignKey("nhan_vien.id"), nullable=False),
        sa.Column("kiem_nhiem_id", sa.Integer(), sa.ForeignKey("dm_kiem_nhiem.id"), nullable=False),
        sa.Column("mo_ta", sa.String(255), nullable=True),
        sa.Column("ngay_bat_dau", sa.Date(), nullable=False),
        sa.Column("ngay_ket_thuc", sa.Date(), nullable=True),
    )

    # 7. dm_loai_tiet_ngoai
    op.create_table(
        "dm_loai_tiet_ngoai",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("ten", sa.String(100), unique=True, nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
    )

    # 8. dm_loai_ho_tro
    op.create_table(
        "dm_loai_ho_tro",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("ten", sa.String(100), unique=True, nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
    )

    # 9. dl_ho_tro_luong
    op.create_table(
        "dl_ho_tro_luong",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("nhan_vien_id", sa.Integer(), sa.ForeignKey("nhan_vien.id"), nullable=False),
        sa.Column("thang", sa.Integer(), nullable=False),
        sa.Column("nam", sa.Integer(), nullable=False),
        sa.Column("loai_ho_tro", sa.String(100), nullable=False),
        sa.Column("so_tien", sa.Numeric(12, 0), nullable=False),
        sa.Column("ghi_chu", sa.String(255), nullable=True),
    )

    # 10. Alter nhan_vien: add new columns, drop chuc_danh_id
    op.add_column("nhan_vien", sa.Column("chuc_vu_id", sa.Integer(), nullable=True))
    op.add_column("nhan_vien", sa.Column("cap_bac_ql_id", sa.Integer(), nullable=True))
    op.add_column("nhan_vien", sa.Column("ten_goi", sa.String(50), nullable=True))

    op.create_foreign_key(
        "fk_nhan_vien_chuc_vu_id",
        "nhan_vien",
        "dm_chuc_vu",
        ["chuc_vu_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_nhan_vien_cap_bac_ql_id",
        "nhan_vien",
        "dm_cap_bac_ql",
        ["cap_bac_ql_id"],
        ["id"],
    )

    # Drop the old chuc_danh_id column (may not exist in all environments)
    try:
        op.drop_constraint("nhan_vien_chuc_danh_id_fkey", "nhan_vien", type_="foreignkey")
    except Exception:
        pass
    try:
        op.drop_column("nhan_vien", "chuc_danh_id")
    except Exception:
        pass


def downgrade() -> None:
    # Reverse alter nhan_vien: re-add chuc_danh_id, drop new columns
    op.add_column(
        "nhan_vien",
        sa.Column("chuc_danh_id", sa.Integer(), nullable=True),
    )
    try:
        op.create_foreign_key(
            "nhan_vien_chuc_danh_id_fkey",
            "nhan_vien",
            "dm_chuc_danh",
            ["chuc_danh_id"],
            ["id"],
        )
    except Exception:
        pass

    op.drop_constraint("fk_nhan_vien_cap_bac_ql_id", "nhan_vien", type_="foreignkey")
    op.drop_constraint("fk_nhan_vien_chuc_vu_id", "nhan_vien", type_="foreignkey")

    op.drop_column("nhan_vien", "ten_goi")
    op.drop_column("nhan_vien", "cap_bac_ql_id")
    op.drop_column("nhan_vien", "chuc_vu_id")

    # Drop new tables in reverse order
    op.drop_table("dl_ho_tro_luong")
    op.drop_table("dm_loai_ho_tro")
    op.drop_table("dm_loai_tiet_ngoai")
    op.drop_table("nv_kiem_nhiem")
    op.drop_table("nv_nghiep_vu")
    op.drop_table("dm_kiem_nhiem")
    op.drop_table("dm_nghiep_vu")
    op.drop_table("dm_cap_bac_ql")
    op.drop_table("dm_chuc_vu")
