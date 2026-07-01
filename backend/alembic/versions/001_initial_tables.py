"""initial tables

Revision ID: 001
Revises: None
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


# revision identifiers, used by Alembic.
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("username", sa.String(50), unique=True, nullable=False, index=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(100), nullable=True),
        sa.Column(
            "role",
            sa.Enum("admin", "accountant", "hr", "teacher", name="userrole"),
            nullable=False,
            server_default="teacher",
        ),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("failed_login_count", sa.Integer(), server_default=sa.text("0")),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # 2. dm_don_vi
    op.create_table(
        "dm_don_vi",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("ten", sa.String(100), unique=True, nullable=False),
        sa.Column("mo_ta", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
    )

    # 3. dm_chuc_danh
    op.create_table(
        "dm_chuc_danh",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("ten", sa.String(100), unique=True, nullable=False),
        sa.Column("mo_ta", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
    )

    # 4. dm_khoi
    op.create_table(
        "dm_khoi",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("ten", sa.String(20), unique=True, nullable=False),
        sa.Column("thu_tu", sa.Integer(), nullable=False),
    )

    # 5. dm_mon_hoc
    op.create_table(
        "dm_mon_hoc",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("ten", sa.String(100), unique=True, nullable=False),
        sa.Column("ma_mon", sa.String(20), unique=True, nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
    )

    # 6. dm_vi_tri
    op.create_table(
        "dm_vi_tri",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("ten", sa.String(100), unique=True, nullable=False),
        sa.Column("mo_ta", sa.String(255), nullable=True),
    )

    # 7. dm_he_so_luong
    op.create_table(
        "dm_he_so_luong",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("bac", sa.String(50), nullable=False),
        sa.Column("he_so", sa.Numeric(5, 2), nullable=False),
        sa.Column("ngay_hieu_luc", sa.Date(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
    )

    # 8. dm_ky_hieu_cong
    op.create_table(
        "dm_ky_hieu_cong",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("ky_hieu", sa.String(10), unique=True, nullable=False),
        sa.Column("ten", sa.String(100), nullable=False),
        sa.Column("gia_tri_ngay_cong", sa.Numeric(3, 1), nullable=False),
        sa.Column("loai", sa.String(50), nullable=False),
    )

    # 9. dm_nhiem_vu
    op.create_table(
        "dm_nhiem_vu",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("ten", sa.String(100), nullable=False),
        sa.Column("don_gia", sa.Numeric(12, 0), nullable=False),
        sa.Column("mo_ta", sa.String(255), nullable=True),
    )

    # 10. dm_lop (FK to dm_khoi)
    op.create_table(
        "dm_lop",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("ten", sa.String(50), unique=True, nullable=False),
        sa.Column("khoi_id", sa.Integer(), sa.ForeignKey("dm_khoi.id"), nullable=False),
    )

    # 11. nhan_vien (FK to dm_don_vi, dm_chuc_danh)
    op.create_table(
        "nhan_vien",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("ma_nv", sa.String(20), unique=True, nullable=False, index=True),
        sa.Column("ho_ten", sa.String(100), nullable=False),
        sa.Column(
            "nhom_nv",
            sa.Enum("GV", "VP", name="nhomnv"),
            nullable=False,
        ),
        sa.Column("don_vi_id", sa.Integer(), sa.ForeignKey("dm_don_vi.id"), nullable=True),
        sa.Column("chuc_danh_id", sa.Integer(), sa.ForeignKey("dm_chuc_danh.id"), nullable=True),
        sa.Column(
            "loai_hop_dong",
            sa.Enum("xac_dinh", "khong_xac_dinh", "thu_viec", name="loaihopdong"),
            nullable=True,
        ),
        sa.Column(
            "trang_thai",
            sa.Enum("dang_lam", "nghi_viec", "tam_ngung", name="trangthainv"),
            server_default="dang_lam",
        ),
        sa.Column("ngay_sinh", sa.Date(), nullable=True),
        sa.Column("email", sa.String(100), nullable=True),
        sa.Column("sdt", sa.String(20), nullable=True),
        sa.Column("ngay_vao_lam", sa.Date(), nullable=True),
        sa.Column("so_nguoi_phu_thuoc", sa.Integer(), server_default=sa.text("0")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # 12. dm_don_gia_day (FK to nhan_vien, dm_mon_hoc, dm_khoi)
    op.create_table(
        "dm_don_gia_day",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("nhan_vien_id", sa.Integer(), sa.ForeignKey("nhan_vien.id"), nullable=False),
        sa.Column("mon_hoc_id", sa.Integer(), sa.ForeignKey("dm_mon_hoc.id"), nullable=False),
        sa.Column("khoi_id", sa.Integer(), sa.ForeignKey("dm_khoi.id"), nullable=False),
        sa.Column("don_gia", sa.Numeric(12, 0), nullable=False),
        sa.Column("ngay_bat_dau", sa.Date(), nullable=False),
        sa.Column("ngay_ket_thuc", sa.Date(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
        sa.UniqueConstraint(
            "nhan_vien_id", "mon_hoc_id", "khoi_id",
            name="uq_don_gia_day_nv_mon_khoi",
        ),
    )

    # 13. dl_hop_dong (FK to nhan_vien, dm_he_so_luong)
    op.create_table(
        "dl_hop_dong",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("nhan_vien_id", sa.Integer(), sa.ForeignKey("nhan_vien.id"), nullable=False),
        sa.Column(
            "loai",
            sa.Enum("xac_dinh", "khong_xac_dinh", "thu_viec", name="loaihopdong"),
            nullable=False,
        ),
        sa.Column("luong_khoan", sa.Numeric(12, 0), nullable=True),
        sa.Column("luong_dong_bh", sa.Numeric(12, 0), nullable=True),
        sa.Column("he_so_luong_id", sa.Integer(), sa.ForeignKey("dm_he_so_luong.id"), nullable=True),
        sa.Column("thuong_hieu_qua", sa.Numeric(12, 0), nullable=True),
        sa.Column("ngay_bat_dau", sa.Date(), nullable=False),
        sa.Column("ngay_ket_thuc", sa.Date(), nullable=True),
        sa.Column("ghi_chu", sa.String(500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # 14. dl_tkb (FK to nhan_vien, dm_mon_hoc, dm_khoi, dm_lop)
    op.create_table(
        "dl_tkb",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("thang", sa.Integer(), nullable=False),
        sa.Column("nam", sa.Integer(), nullable=False),
        sa.Column("nhan_vien_id", sa.Integer(), sa.ForeignKey("nhan_vien.id"), nullable=False),
        sa.Column("mon_hoc_id", sa.Integer(), sa.ForeignKey("dm_mon_hoc.id"), nullable=False),
        sa.Column("khoi_id", sa.Integer(), sa.ForeignKey("dm_khoi.id"), nullable=False),
        sa.Column("lop_id", sa.Integer(), sa.ForeignKey("dm_lop.id"), nullable=False),
        sa.Column("so_tiet", sa.Integer(), nullable=False),
        sa.Column("loai_tiet", sa.String(50), nullable=False),
    )

    # 15. dl_thay_doi_nguoi_day (FK to dm_lop, dm_mon_hoc, nhan_vien×2)
    op.create_table(
        "dl_thay_doi_nguoi_day",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("ngay", sa.Date(), nullable=False),
        sa.Column("tiet", sa.Integer(), nullable=False),
        sa.Column("lop_id", sa.Integer(), sa.ForeignKey("dm_lop.id"), nullable=False),
        sa.Column("mon_hoc_id", sa.Integer(), sa.ForeignKey("dm_mon_hoc.id"), nullable=False),
        sa.Column("gv_goc_id", sa.Integer(), sa.ForeignKey("nhan_vien.id"), nullable=False),
        sa.Column("gv_thay_id", sa.Integer(), sa.ForeignKey("nhan_vien.id"), nullable=False),
        sa.Column("ly_do", sa.String(200), nullable=True),
        sa.Column("thang", sa.Integer(), nullable=False),
        sa.Column("nam", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # 16. dl_bcc_tong_tiet (FK to nhan_vien)
    op.create_table(
        "dl_bcc_tong_tiet",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("thang", sa.Integer(), nullable=False),
        sa.Column("nam", sa.Integer(), nullable=False),
        sa.Column("nhan_vien_id", sa.Integer(), sa.ForeignKey("nhan_vien.id"), nullable=False),
        sa.Column("theo_tkb_json", JSON(), nullable=True),
        sa.Column("thay_doi_json", JSON(), nullable=True),
        sa.Column("phat_sinh_json", JSON(), nullable=True),
        sa.Column("thuc_te_json", JSON(), nullable=True),
        sa.Column("is_complete", sa.Boolean(), server_default=sa.text("false")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # 17. dl_tiet_day_ngoai (FK to nhan_vien)
    op.create_table(
        "dl_tiet_day_ngoai",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("thang", sa.Integer(), nullable=False),
        sa.Column("nam", sa.Integer(), nullable=False),
        sa.Column("nhan_vien_id", sa.Integer(), sa.ForeignKey("nhan_vien.id"), nullable=False),
        sa.Column("loai", sa.String(100), nullable=False),
        sa.Column("so_tiet", sa.Numeric(5, 1), nullable=False),
        sa.Column("don_gia", sa.Numeric(12, 0), nullable=False),
        sa.Column("he_so", sa.Numeric(3, 1), server_default=sa.text("1.0")),
        sa.Column("thanh_tien", sa.Numeric(12, 0), nullable=True),
        sa.Column("ghi_chu", sa.String(255), nullable=True),
    )

    # 18. dl_cham_cong (FK to nhan_vien, dm_ky_hieu_cong)
    op.create_table(
        "dl_cham_cong",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("nhan_vien_id", sa.Integer(), sa.ForeignKey("nhan_vien.id"), nullable=False),
        sa.Column("ngay", sa.Date(), nullable=False),
        sa.Column("ky_hieu_cong_id", sa.Integer(), sa.ForeignKey("dm_ky_hieu_cong.id"), nullable=False),
        sa.Column("ghi_chu", sa.String(255), nullable=True),
        sa.UniqueConstraint(
            "nhan_vien_id", "ngay",
            name="uq_cham_cong_nv_ngay",
        ),
    )

    # 19. dl_tong_hop_cong (FK to nhan_vien)
    op.create_table(
        "dl_tong_hop_cong",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("nhan_vien_id", sa.Integer(), sa.ForeignKey("nhan_vien.id"), nullable=False),
        sa.Column("thang", sa.Integer(), nullable=False),
        sa.Column("nam", sa.Integer(), nullable=False),
        sa.Column("ngay_cong", sa.Numeric(4, 1), nullable=False),
        sa.Column("ngay_nghi", sa.Numeric(4, 1), nullable=False),
        sa.Column("ngay_phep", sa.Numeric(4, 1), nullable=False),
        sa.Column("lam_them", sa.Numeric(4, 1), nullable=False),
        sa.Column("cong_chuan", sa.Integer(), server_default=sa.text("26")),
        sa.Column("is_confirmed", sa.Boolean(), server_default=sa.text("false")),
        sa.UniqueConstraint(
            "nhan_vien_id", "thang", "nam",
            name="uq_tong_hop_cong_nv_thang_nam",
        ),
    )

    # 20. dl_bang_luong (FK to nhan_vien, users×2)
    op.create_table(
        "dl_bang_luong",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("nhan_vien_id", sa.Integer(), sa.ForeignKey("nhan_vien.id"), nullable=False),
        sa.Column("thang", sa.Integer(), nullable=False),
        sa.Column("nam", sa.Integer(), nullable=False),
        sa.Column(
            "trang_thai",
            sa.Enum("draft", "reviewed", "approved", name="trangthaibangluong"),
            server_default="draft",
        ),
        sa.Column("muc_i_json", JSON(), nullable=True),
        sa.Column("muc_ii_json", JSON(), nullable=True),
        sa.Column("muc_iii_json", JSON(), nullable=True),
        sa.Column("muc_iv_json", JSON(), nullable=True),
        sa.Column("muc_v_json", JSON(), nullable=True),
        sa.Column("muc_vi_thuc_linh", sa.Numeric(14, 0), nullable=True),
        sa.Column("nguoi_tinh_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("nguoi_duyet_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("ngay_tinh", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ngay_duyet", sa.DateTime(timezone=True), nullable=True),
        sa.Column("version", sa.Integer(), server_default=sa.text("1")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint(
            "nhan_vien_id", "thang", "nam",
            name="uq_bang_luong_nv_thang_nam",
        ),
    )


def downgrade() -> None:
    # Drop tables in reverse order (respecting FK dependencies)
    op.drop_table("dl_bang_luong")
    op.drop_table("dl_tong_hop_cong")
    op.drop_table("dl_cham_cong")
    op.drop_table("dl_tiet_day_ngoai")
    op.drop_table("dl_bcc_tong_tiet")
    op.drop_table("dl_thay_doi_nguoi_day")
    op.drop_table("dl_tkb")
    op.drop_table("dl_hop_dong")
    op.drop_table("dm_don_gia_day")
    op.drop_table("nhan_vien")
    op.drop_table("dm_lop")
    op.drop_table("dm_nhiem_vu")
    op.drop_table("dm_ky_hieu_cong")
    op.drop_table("dm_he_so_luong")
    op.drop_table("dm_vi_tri")
    op.drop_table("dm_mon_hoc")
    op.drop_table("dm_khoi")
    op.drop_table("dm_chuc_danh")
    op.drop_table("dm_don_vi")
    op.drop_table("users")

    # Drop enum types
    op.execute("DROP TYPE IF EXISTS trangthaibangluong")
    op.execute("DROP TYPE IF EXISTS loaihopdong")
    op.execute("DROP TYPE IF EXISTS trangthainv")
    op.execute("DROP TYPE IF EXISTS nhomnv")
    op.execute("DROP TYPE IF EXISTS userrole")
