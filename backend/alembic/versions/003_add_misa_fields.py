"""add MISA-compatible fields for employee profile, family, attendance

Revision ID: 003
Revises: 002
Create Date: 2026-07-01

Adds columns to nhan_vien for MISA HR import compatibility,
creates dl_gia_dinh (family/dependents) and dl_lich_su_luong tables.
"""
from alembic import op
import sqlalchemy as sa

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # =========================================================================
    # 1. Extend nhan_vien with MISA "Nhập khẩu hồ sơ" fields
    # =========================================================================
    cols = [
        ("gioi_tinh", sa.String(10)),
        ("noi_sinh", sa.String(200)),
        ("nguyen_quan", sa.String(200)),
        ("tinh_trang_hon_nhan", sa.String(50)),
        ("mst_ca_nhan", sa.String(20)),
        ("dan_toc", sa.String(50)),
        ("ton_giao", sa.String(50)),
        ("quoc_tich", sa.String(50)),
        ("loai_giay_to", sa.String(50)),
        ("so_cmnd_cccd", sa.String(20)),
        ("ngay_cap_cmnd", sa.Date()),
        ("noi_cap_cmnd", sa.String(200)),
        ("ngay_het_han_cmnd", sa.Date()),
        ("so_ho_chieu", sa.String(20)),
        ("ngay_cap_ho_chieu", sa.Date()),
        ("noi_cap_ho_chieu", sa.String(200)),
        ("ngay_het_han_ho_chieu", sa.Date()),
        ("trinh_do_van_hoa", sa.String(50)),
        ("trinh_do_dao_tao", sa.String(100)),
        ("noi_dao_tao", sa.String(200)),
        ("khoa", sa.String(100)),
        ("chuyen_nganh", sa.String(100)),
        ("nam_tot_nghiep", sa.Integer()),
        ("xep_loai", sa.String(50)),
        ("dt_co_quan", sa.String(20)),
        ("dt_nha_rieng", sa.String(20)),
        ("email_co_quan", sa.String(100)),
        ("so_so_ho_khau", sa.String(50)),
        ("ma_so_ho_gia_dinh", sa.String(50)),
        ("luong_co_ban", sa.Numeric(12, 0)),
        ("bac_luong", sa.String(50)),
        ("tinh_chat_lao_dong", sa.String(50)),
        ("ly_do_nghi", sa.String(200)),
        ("ngay_nghi_viec", sa.Date()),
        ("noi_lam_viec", sa.String(200)),
        ("so_so_ql_lao_dong", sa.String(50)),
        ("ngay_hoc_viec", sa.Date()),
        ("ngay_thu_viec", sa.Date()),
        ("ngay_chinh_thuc", sa.Date()),
        ("quan_ly_truc_tiep", sa.String(100)),
        ("quan_ly_gian_tiep", sa.String(100)),
        ("luong_dong_bh", sa.Numeric(12, 0)),
        ("tk_ngan_hang", sa.String(30)),
        ("ngan_hang", sa.String(100)),
        ("tham_gia_cong_doan", sa.Boolean()),
        ("tham_gia_bao_hiem", sa.Boolean()),
        ("ngay_tham_gia_bh", sa.Date()),
        ("ty_le_dong_bh", sa.Numeric(5, 2)),
        ("ty_le_dong_bhxh", sa.Numeric(5, 2)),
        ("ty_le_dong_bhyt", sa.Numeric(5, 2)),
        ("ty_le_dong_bhtn", sa.Numeric(5, 2)),
        ("so_so_bhxh", sa.String(30)),
        ("ma_so_bhxh", sa.String(30)),
        ("noi_dang_ky_kcb", sa.String(200)),
        ("dia_chi_hktt", sa.String(300)),
        ("dia_chi_hien_nay", sa.String(300)),
        ("thue_suat", sa.Numeric(5, 2)),
        ("giam_tru_ban_than", sa.Boolean()),
        ("ma_cham_cong", sa.String(20)),
        ("so_ngay_phep", sa.Numeric(4, 1)),
    ]
    for col_name, col_type in cols:
        op.add_column("nhan_vien", sa.Column(col_name, col_type, nullable=True))

    # =========================================================================
    # 2. dl_gia_dinh - Family members / dependents (MISA Thông tin gia đình)
    # =========================================================================
    op.create_table(
        "dl_gia_dinh",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("nhan_vien_id", sa.Integer(), sa.ForeignKey("nhan_vien.id"), nullable=False),
        sa.Column("ho_ten_nguoi_than", sa.String(100), nullable=False),
        sa.Column("quan_he", sa.String(50), nullable=False),
        sa.Column("quan_he_chu_ho", sa.String(50), nullable=True),
        sa.Column("gioi_tinh", sa.String(10), nullable=True),
        sa.Column("ngay_sinh", sa.Date(), nullable=True),
        sa.Column("quoc_tich", sa.String(50), nullable=True),
        sa.Column("so_cmnd", sa.String(20), nullable=True),
        sa.Column("sdt", sa.String(20), nullable=True),
        sa.Column("email", sa.String(100), nullable=True),
        sa.Column("nghe_nghiep", sa.String(100), nullable=True),
        sa.Column("mst_ca_nhan", sa.String(20), nullable=True),
        sa.Column("noi_lam_viec", sa.String(200), nullable=True),
        sa.Column("cung_so_ho_khau", sa.Boolean(), nullable=True),
        sa.Column("da_mat", sa.Boolean(), nullable=True),
        sa.Column("ngay_mat", sa.Date(), nullable=True),
        sa.Column("ghi_chu", sa.String(255), nullable=True),
        sa.Column("la_nguoi_phu_thuoc", sa.Boolean(), nullable=True),
        sa.Column("thoi_diem_tinh_gt", sa.Date(), nullable=True),
        sa.Column("thoi_diem_ket_thuc_gt", sa.Date(), nullable=True),
        sa.Column("dia_chi_thuong_tru", sa.String(300), nullable=True),
        sa.Column("cho_o_hien_nay", sa.String(300), nullable=True),
    )

    # =========================================================================
    # 3. dl_lich_su_luong - Salary history (MISA Lịch sử lương)
    # =========================================================================
    op.create_table(
        "dl_lich_su_luong",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("nhan_vien_id", sa.Integer(), sa.ForeignKey("nhan_vien.id"), nullable=False),
        sa.Column("ngay_hieu_luc", sa.Date(), nullable=False),
        sa.Column("loai_luong", sa.String(20), nullable=True),  # GROSS / NET
        sa.Column("don_vi_cong_tac", sa.String(100), nullable=True),
        sa.Column("vi_tri_cong_viec", sa.String(100), nullable=True),
        sa.Column("bac_luong", sa.String(50), nullable=True),
        sa.Column("luong_co_ban", sa.Numeric(12, 0), nullable=False),
        sa.Column("ty_le_huong_luong", sa.Numeric(5, 1), nullable=True),
        sa.Column("khoan_phu_cap", sa.String(100), nullable=True),
        sa.Column("gia_tri_phu_cap", sa.Numeric(12, 0), nullable=True),
        sa.Column("phu_cap_theo_cong", sa.Boolean(), nullable=True),
        sa.Column("trang_thai_phu_cap", sa.String(50), nullable=True),
        sa.Column("khoan_khau_tru", sa.String(100), nullable=True),
        sa.Column("gia_tri_khau_tru", sa.Numeric(12, 0), nullable=True),
        sa.Column("khau_tru_theo_cong", sa.Boolean(), nullable=True),
        sa.Column("trang_thai_khau_tru", sa.String(50), nullable=True),
    )

    # =========================================================================
    # 4. dl_qua_trinh_cong_tac - Work history (MISA Quá trình công tác)
    # =========================================================================
    op.create_table(
        "dl_qua_trinh_cong_tac",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("nhan_vien_id", sa.Integer(), sa.ForeignKey("nhan_vien.id"), nullable=False),
        sa.Column("tu_ngay", sa.Date(), nullable=False),
        sa.Column("loai_thu_tuc", sa.String(100), nullable=True),
        sa.Column("don_vi_cong_tac", sa.String(100), nullable=True),
        sa.Column("bac", sa.String(50), nullable=True),
        sa.Column("trang_thai_lao_dong", sa.String(50), nullable=True),
        sa.Column("tinh_chat_lao_dong", sa.String(50), nullable=True),
        sa.Column("quan_ly_truc_tiep", sa.String(100), nullable=True),
        sa.Column("vi_tri_cong_viec", sa.String(100), nullable=True),
        sa.Column("quan_ly_gian_tiep", sa.String(100), nullable=True),
        sa.Column("so_quyet_dinh", sa.String(50), nullable=True),
        sa.Column("ngay_quyet_dinh", sa.Date(), nullable=True),
        sa.Column("ghi_chu", sa.String(255), nullable=True),
    )

    # =========================================================================
    # 5. dl_bang_cap - Qualifications (MISA Bằng cấp)
    # =========================================================================
    op.create_table(
        "dl_bang_cap",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("nhan_vien_id", sa.Integer(), sa.ForeignKey("nhan_vien.id"), nullable=False),
        sa.Column("noi_dao_tao", sa.String(200), nullable=False),
        sa.Column("tu_nam", sa.Integer(), nullable=True),
        sa.Column("den_nam", sa.Integer(), nullable=True),
        sa.Column("khoa", sa.String(100), nullable=True),
        sa.Column("chuyen_nganh", sa.String(100), nullable=True),
        sa.Column("trinh_do_dao_tao", sa.String(100), nullable=True),
        sa.Column("hinh_thuc", sa.String(50), nullable=True),
        sa.Column("xep_loai", sa.String(50), nullable=True),
        sa.Column("da_tot_nghiep", sa.Boolean(), nullable=True),
        sa.Column("ngay_nhan_bang", sa.Date(), nullable=True),
        sa.Column("ghi_chu", sa.String(255), nullable=True),
    )

    # =========================================================================
    # 6. Extend dm_don_vi with MISA "Cơ cấu tổ chức" fields
    # =========================================================================
    dv_cols = [
        ("ma_don_vi", sa.String(20)),
        ("thuoc_don_vi", sa.String(20)),
        ("dia_chi", sa.String(300)),
        ("cap_to_chuc", sa.String(50)),
        ("truong_don_vi", sa.String(100)),
        ("chuc_nang_nhiem_vu", sa.String(500)),
        ("hach_toan", sa.String(50)),
        ("thu_tu_sap_xep", sa.Integer()),
        ("ma_so_dkkd", sa.String(30)),
        ("ngay_cap_dkkd", sa.Date()),
        ("noi_cap_dkkd", sa.String(200)),
    ]
    for col_name, col_type in dv_cols:
        op.add_column("dm_don_vi", sa.Column(col_name, col_type, nullable=True))

    # =========================================================================
    # 7. Extend dm_vi_tri with MISA "Vị trí công việc" fields
    # =========================================================================
    vt_cols = [
        ("ma_vi_tri", sa.String(20)),
        ("don_vi_cong_tac", sa.String(100)),
        ("nhom_vi_tri", sa.String(100)),
        ("chuc_danh", sa.String(100)),
        ("trang_thai", sa.String(50)),
    ]
    for col_name, col_type in vt_cols:
        op.add_column("dm_vi_tri", sa.Column(col_name, col_type, nullable=True))

    # =========================================================================
    # 8. dl_nghi_phep - Leave balance (MISA Bảng tổng hợp nghỉ phép)
    # =========================================================================
    op.create_table(
        "dl_nghi_phep",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("nhan_vien_id", sa.Integer(), sa.ForeignKey("nhan_vien.id"), nullable=False),
        sa.Column("nam", sa.Integer(), nullable=False),
        sa.Column("so_np_nam_nay", sa.Numeric(4, 1), nullable=True),
        sa.Column("so_np_nam_truoc", sa.Numeric(4, 1), nullable=True),
        sa.Column("so_np_tham_nien", sa.Numeric(4, 1), nullable=True),
        sa.Column("so_np_thuong_khac", sa.Numeric(4, 1), nullable=True),
        sa.Column("so_np_da_huy", sa.Numeric(4, 1), nullable=True),
        sa.Column("so_np_da_su_dung", sa.Numeric(4, 1), nullable=True),
        sa.UniqueConstraint("nhan_vien_id", "nam", name="uq_nghi_phep_nv_nam"),
    )


def downgrade() -> None:
    op.drop_table("dl_nghi_phep")
    op.drop_table("dl_bang_cap")
    op.drop_table("dl_qua_trinh_cong_tac")
    op.drop_table("dl_lich_su_luong")
    op.drop_table("dl_gia_dinh")

    # Drop dm_vi_tri extra columns
    for col_name in ["ma_vi_tri", "don_vi_cong_tac", "nhom_vi_tri", "chuc_danh", "trang_thai"]:
        op.drop_column("dm_vi_tri", col_name)

    # Drop dm_don_vi extra columns
    for col_name in ["ma_don_vi", "thuoc_don_vi", "dia_chi", "cap_to_chuc",
                     "truong_don_vi", "chuc_nang_nhiem_vu", "hach_toan",
                     "thu_tu_sap_xep", "ma_so_dkkd", "ngay_cap_dkkd", "noi_cap_dkkd"]:
        op.drop_column("dm_don_vi", col_name)

    # Drop nhan_vien extra columns
    nv_cols = [
        "gioi_tinh", "noi_sinh", "nguyen_quan", "tinh_trang_hon_nhan",
        "mst_ca_nhan", "dan_toc", "ton_giao", "quoc_tich",
        "loai_giay_to", "so_cmnd_cccd", "ngay_cap_cmnd", "noi_cap_cmnd",
        "ngay_het_han_cmnd", "so_ho_chieu", "ngay_cap_ho_chieu",
        "noi_cap_ho_chieu", "ngay_het_han_ho_chieu",
        "trinh_do_van_hoa", "trinh_do_dao_tao", "noi_dao_tao",
        "khoa", "chuyen_nganh", "nam_tot_nghiep", "xep_loai",
        "dt_co_quan", "dt_nha_rieng", "email_co_quan",
        "so_so_ho_khau", "ma_so_ho_gia_dinh",
        "luong_co_ban", "bac_luong", "tinh_chat_lao_dong",
        "ly_do_nghi", "ngay_nghi_viec", "noi_lam_viec",
        "so_so_ql_lao_dong", "ngay_hoc_viec", "ngay_thu_viec", "ngay_chinh_thuc",
        "quan_ly_truc_tiep", "quan_ly_gian_tiep",
        "luong_dong_bh", "tk_ngan_hang", "ngan_hang",
        "tham_gia_cong_doan", "tham_gia_bao_hiem",
        "ngay_tham_gia_bh", "ty_le_dong_bh",
        "ty_le_dong_bhxh", "ty_le_dong_bhyt", "ty_le_dong_bhtn",
        "so_so_bhxh", "ma_so_bhxh", "noi_dang_ky_kcb",
        "dia_chi_hktt", "dia_chi_hien_nay",
        "thue_suat", "giam_tru_ban_than",
        "ma_cham_cong", "so_ngay_phep",
    ]
    for col_name in nv_cols:
        op.drop_column("nhan_vien", col_name)
