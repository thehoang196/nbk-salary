"""
NBK Salary - MISA HR Models (Gia đình, Lịch sử lương, Quá trình công tác, Bằng cấp, Nghỉ phép).

Maps to MISA import/export forms for HR data management.
"""
from sqlalchemy import (
    Column, Integer, String, Boolean, Date, Numeric,
    ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship

from app.database import Base


class DlGiaDinh(Base):
    """Family members / dependents (Thông tin gia đình)."""
    __tablename__ = "dl_gia_dinh"

    id = Column(Integer, primary_key=True, index=True)
    nhan_vien_id = Column(Integer, ForeignKey("nhan_vien.id"), nullable=False)
    ho_ten_nguoi_than = Column(String(100), nullable=False)
    quan_he = Column(String(50), nullable=False)
    quan_he_chu_ho = Column(String(50), nullable=True)
    gioi_tinh = Column(String(10), nullable=True)
    ngay_sinh = Column(Date, nullable=True)
    quoc_tich = Column(String(50), nullable=True)
    so_cmnd = Column(String(20), nullable=True)
    sdt = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    nghe_nghiep = Column(String(100), nullable=True)
    mst_ca_nhan = Column(String(20), nullable=True)
    noi_lam_viec = Column(String(200), nullable=True)
    cung_so_ho_khau = Column(Boolean, nullable=True)
    da_mat = Column(Boolean, nullable=True)
    ngay_mat = Column(Date, nullable=True)
    ghi_chu = Column(String(255), nullable=True)
    la_nguoi_phu_thuoc = Column(Boolean, nullable=True)
    thoi_diem_tinh_gt = Column(Date, nullable=True)
    thoi_diem_ket_thuc_gt = Column(Date, nullable=True)
    dia_chi_thuong_tru = Column(String(300), nullable=True)
    cho_o_hien_nay = Column(String(300), nullable=True)

    nhan_vien = relationship("NhanVien", back_populates="gia_dinh_list")


class DlLichSuLuong(Base):
    """Salary history (Lịch sử lương)."""
    __tablename__ = "dl_lich_su_luong"

    id = Column(Integer, primary_key=True, index=True)
    nhan_vien_id = Column(Integer, ForeignKey("nhan_vien.id"), nullable=False)
    ngay_hieu_luc = Column(Date, nullable=False)
    loai_luong = Column(String(20), nullable=True)  # GROSS / NET
    don_vi_cong_tac = Column(String(100), nullable=True)
    vi_tri_cong_viec = Column(String(100), nullable=True)
    bac_luong = Column(String(50), nullable=True)
    luong_co_ban = Column(Numeric(12, 0), nullable=False)
    ty_le_huong_luong = Column(Numeric(5, 1), nullable=True)
    khoan_phu_cap = Column(String(100), nullable=True)
    gia_tri_phu_cap = Column(Numeric(12, 0), nullable=True)
    phu_cap_theo_cong = Column(Boolean, nullable=True)
    trang_thai_phu_cap = Column(String(50), nullable=True)
    khoan_khau_tru = Column(String(100), nullable=True)
    gia_tri_khau_tru = Column(Numeric(12, 0), nullable=True)
    khau_tru_theo_cong = Column(Boolean, nullable=True)
    trang_thai_khau_tru = Column(String(50), nullable=True)

    nhan_vien = relationship("NhanVien", back_populates="lich_su_luong_list")


class DlQuaTrinhCongTac(Base):
    """Work history (Quá trình công tác)."""
    __tablename__ = "dl_qua_trinh_cong_tac"

    id = Column(Integer, primary_key=True, index=True)
    nhan_vien_id = Column(Integer, ForeignKey("nhan_vien.id"), nullable=False)
    tu_ngay = Column(Date, nullable=False)
    loai_thu_tuc = Column(String(100), nullable=True)
    don_vi_cong_tac = Column(String(100), nullable=True)
    bac = Column(String(50), nullable=True)
    trang_thai_lao_dong = Column(String(50), nullable=True)
    tinh_chat_lao_dong = Column(String(50), nullable=True)
    quan_ly_truc_tiep = Column(String(100), nullable=True)
    vi_tri_cong_viec = Column(String(100), nullable=True)
    quan_ly_gian_tiep = Column(String(100), nullable=True)
    so_quyet_dinh = Column(String(50), nullable=True)
    ngay_quyet_dinh = Column(Date, nullable=True)
    ghi_chu = Column(String(255), nullable=True)

    nhan_vien = relationship("NhanVien", back_populates="qua_trinh_ct_list")


class DlBangCap(Base):
    """Qualifications/Degrees (Bằng cấp)."""
    __tablename__ = "dl_bang_cap"

    id = Column(Integer, primary_key=True, index=True)
    nhan_vien_id = Column(Integer, ForeignKey("nhan_vien.id"), nullable=False)
    noi_dao_tao = Column(String(200), nullable=False)
    tu_nam = Column(Integer, nullable=True)
    den_nam = Column(Integer, nullable=True)
    khoa = Column(String(100), nullable=True)
    chuyen_nganh = Column(String(100), nullable=True)
    trinh_do_dao_tao = Column(String(100), nullable=True)
    hinh_thuc = Column(String(50), nullable=True)
    xep_loai = Column(String(50), nullable=True)
    da_tot_nghiep = Column(Boolean, nullable=True)
    ngay_nhan_bang = Column(Date, nullable=True)
    ghi_chu = Column(String(255), nullable=True)

    nhan_vien = relationship("NhanVien", back_populates="bang_cap_list")


class DlNghiPhep(Base):
    """Leave balance summary (Bảng tổng hợp nghỉ phép)."""
    __tablename__ = "dl_nghi_phep"
    __table_args__ = (
        UniqueConstraint("nhan_vien_id", "nam", name="uq_nghi_phep_nv_nam"),
    )

    id = Column(Integer, primary_key=True, index=True)
    nhan_vien_id = Column(Integer, ForeignKey("nhan_vien.id"), nullable=False)
    nam = Column(Integer, nullable=False)
    so_np_nam_nay = Column(Numeric(4, 1), nullable=True)
    so_np_nam_truoc = Column(Numeric(4, 1), nullable=True)
    so_np_tham_nien = Column(Numeric(4, 1), nullable=True)
    so_np_thuong_khac = Column(Numeric(4, 1), nullable=True)
    so_np_da_huy = Column(Numeric(4, 1), nullable=True)
    so_np_da_su_dung = Column(Numeric(4, 1), nullable=True)

    nhan_vien = relationship("NhanVien", back_populates="nghi_phep_list")
