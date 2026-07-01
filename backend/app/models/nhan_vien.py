"""
NBK Salary - Employee Model (Nhân viên).

Defines the NhanVien (Employee) table and related enums:
NhomNV (employee group), LoaiHopDong (contract type), TrangThaiNV (status).
"""

from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey, Numeric, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base


class NhomNV(str, enum.Enum):
    GV = "GV"  # Giáo viên (Teacher)
    VP = "VP"  # Văn phòng (Office Staff)


class LoaiHopDong(str, enum.Enum):
    xac_dinh = "xac_dinh"           # Definite-term
    khong_xac_dinh = "khong_xac_dinh"  # Indefinite-term
    thu_viec = "thu_viec"           # Probationary


class TrangThaiNV(str, enum.Enum):
    dang_lam = "dang_lam"    # Active
    nghi_viec = "nghi_viec"  # Resigned
    tam_ngung = "tam_ngung"  # Suspended


class NhanVien(Base):
    __tablename__ = "nhan_vien"

    id = Column(Integer, primary_key=True, index=True)
    ma_nv = Column(String(20), unique=True, nullable=False, index=True)
    cccd = Column(String(12), unique=True, nullable=True, index=True)  # Căn cước công dân 12 số
    ho_ten = Column(String(100), nullable=False)
    nhom_nv = Column(SAEnum(NhomNV), nullable=False)  # GV or VP
    don_vi_id = Column(Integer, ForeignKey("dm_don_vi.id"), nullable=True)
    chuc_vu_id = Column(Integer, ForeignKey("dm_chuc_vu.id"), nullable=True)
    cap_bac_ql_id = Column(Integer, ForeignKey("dm_cap_bac_ql.id"), nullable=True)
    ten_goi = Column(String(50), nullable=True)  # Display nickname, only for GV group
    loai_hop_dong = Column(SAEnum(LoaiHopDong), nullable=True)
    trang_thai = Column(SAEnum(TrangThaiNV), default=TrangThaiNV.dang_lam)
    ngay_sinh = Column(Date, nullable=True)
    email = Column(String(100), nullable=True)
    sdt = Column(String(20), nullable=True)
    ngay_vao_lam = Column(Date, nullable=True)
    so_nguoi_phu_thuoc = Column(Integer, default=0)  # For tax calculation

    # --- MISA HR fields (Nhập khẩu hồ sơ) ---
    gioi_tinh = Column(String(10), nullable=True)
    noi_sinh = Column(String(200), nullable=True)
    nguyen_quan = Column(String(200), nullable=True)
    tinh_trang_hon_nhan = Column(String(50), nullable=True)
    mst_ca_nhan = Column(String(20), nullable=True)
    dan_toc = Column(String(50), nullable=True)
    ton_giao = Column(String(50), nullable=True)
    quoc_tich = Column(String(50), nullable=True)
    loai_giay_to = Column(String(50), nullable=True)
    so_cmnd_cccd = Column(String(20), nullable=True)
    ngay_cap_cmnd = Column(Date, nullable=True)
    noi_cap_cmnd = Column(String(200), nullable=True)
    ngay_het_han_cmnd = Column(Date, nullable=True)
    so_ho_chieu = Column(String(20), nullable=True)
    ngay_cap_ho_chieu = Column(Date, nullable=True)
    noi_cap_ho_chieu = Column(String(200), nullable=True)
    ngay_het_han_ho_chieu = Column(Date, nullable=True)
    trinh_do_van_hoa = Column(String(50), nullable=True)
    trinh_do_dao_tao = Column(String(100), nullable=True)
    noi_dao_tao = Column(String(200), nullable=True)
    khoa = Column(String(100), nullable=True)
    chuyen_nganh = Column(String(100), nullable=True)
    nam_tot_nghiep = Column(Integer, nullable=True)
    xep_loai = Column(String(50), nullable=True)
    dt_co_quan = Column(String(20), nullable=True)
    dt_nha_rieng = Column(String(20), nullable=True)
    email_co_quan = Column(String(100), nullable=True)
    so_so_ho_khau = Column(String(50), nullable=True)
    ma_so_ho_gia_dinh = Column(String(50), nullable=True)
    luong_co_ban = Column(Numeric(12, 0), nullable=True)
    bac_luong = Column(String(50), nullable=True)
    tinh_chat_lao_dong = Column(String(50), nullable=True)
    ly_do_nghi = Column(String(200), nullable=True)
    ngay_nghi_viec = Column(Date, nullable=True)
    noi_lam_viec = Column(String(200), nullable=True)
    so_so_ql_lao_dong = Column(String(50), nullable=True)
    ngay_hoc_viec = Column(Date, nullable=True)
    ngay_thu_viec = Column(Date, nullable=True)
    ngay_chinh_thuc = Column(Date, nullable=True)
    quan_ly_truc_tiep = Column(String(100), nullable=True)
    quan_ly_gian_tiep = Column(String(100), nullable=True)
    luong_dong_bh = Column(Numeric(12, 0), nullable=True)
    tk_ngan_hang = Column(String(30), nullable=True)
    ngan_hang = Column(String(100), nullable=True)
    tham_gia_cong_doan = Column(Boolean, nullable=True)
    tham_gia_bao_hiem = Column(Boolean, nullable=True)
    ngay_tham_gia_bh = Column(Date, nullable=True)
    ty_le_dong_bh = Column(Numeric(5, 2), nullable=True)
    ty_le_dong_bhxh = Column(Numeric(5, 2), nullable=True)
    ty_le_dong_bhyt = Column(Numeric(5, 2), nullable=True)
    ty_le_dong_bhtn = Column(Numeric(5, 2), nullable=True)
    so_so_bhxh = Column(String(30), nullable=True)
    ma_so_bhxh = Column(String(30), nullable=True)
    noi_dang_ky_kcb = Column(String(200), nullable=True)
    dia_chi_hktt = Column(String(300), nullable=True)
    dia_chi_hien_nay = Column(String(300), nullable=True)
    thue_suat = Column(Numeric(5, 2), nullable=True)
    giam_tru_ban_than = Column(Boolean, nullable=True)
    ma_cham_cong = Column(String(20), nullable=True)
    so_ngay_phep = Column(Numeric(4, 1), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    don_vi = relationship("DmDonVi")
    chuc_vu = relationship("DmChucVu")
    cap_bac_ql = relationship("DmCapBacQL")
    nghiep_vu_list = relationship("NvNghiepVu", back_populates="nhan_vien")
    kiem_nhiem_list = relationship("NvKiemNhiem", back_populates="nhan_vien")
    hop_dong_list = relationship("DlHopDong", back_populates="nhan_vien")
    don_gia_day_list = relationship("DmDonGiaDay")
    cham_cong_list = relationship("DlChamCong", back_populates="nhan_vien")
    tong_hop_cong_list = relationship("DlTongHopCong", back_populates="nhan_vien")
    ho_tro_luong_list = relationship("DlHoTroLuong", back_populates="nhan_vien")
    gia_dinh_list = relationship("DlGiaDinh", back_populates="nhan_vien")
    lich_su_luong_list = relationship("DlLichSuLuong", back_populates="nhan_vien")
    qua_trinh_ct_list = relationship("DlQuaTrinhCongTac", back_populates="nhan_vien")
    bang_cap_list = relationship("DlBangCap", back_populates="nhan_vien")
    nghi_phep_list = relationship("DlNghiPhep", back_populates="nhan_vien")

    def __repr__(self):
        return f"<NhanVien(id={self.id}, ma_nv='{self.ma_nv}', ho_ten='{self.ho_ten}')>"
