"""
NBK Salary - Timetable Models (Thời khóa biểu).

Defines tables for:
- DlTkb: Main timetable records (tiết dạy theo TKB)
- DlThayDoiNguoiDay: Teacher substitution changes
- DlBccTongTiet: BCC summary per teacher per month
- DlTietDayNgoai: External teaching periods
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, Date, DateTime, ForeignKey, Numeric,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.types import JSON

from app.database import Base


class DlTkb(Base):
    """Main timetable records - tiết dạy chính khóa theo TKB."""
    __tablename__ = "dl_tkb"

    id = Column(Integer, primary_key=True, index=True)
    thang = Column(Integer, nullable=False)
    nam = Column(Integer, nullable=False)
    nhan_vien_id = Column(Integer, ForeignKey("nhan_vien.id"), nullable=False)
    mon_hoc_id = Column(Integer, ForeignKey("dm_mon_hoc.id"), nullable=False)
    khoi_id = Column(Integer, ForeignKey("dm_khoi.id"), nullable=False)
    lop_id = Column(Integer, ForeignKey("dm_lop.id"), nullable=False)
    so_tiet = Column(Integer, nullable=False)
    loai_tiet = Column(String(50), nullable=False)  # chinh_khoa, tnst_vy, k9_luyen_thi, kh_ta, ielts

    # Relationships
    nhan_vien = relationship("NhanVien", foreign_keys=[nhan_vien_id])
    mon_hoc = relationship("DmMonHoc", foreign_keys=[mon_hoc_id])
    khoi = relationship("DmKhoi", foreign_keys=[khoi_id])
    lop = relationship("DmLop", foreign_keys=[lop_id])

    def __repr__(self):
        return f"<DlTkb(id={self.id}, nv={self.nhan_vien_id}, thang={self.thang}/{self.nam}, so_tiet={self.so_tiet})>"


class DlThayDoiNguoiDay(Base):
    """Teacher substitution changes - thay đổi người dạy."""
    __tablename__ = "dl_thay_doi_nguoi_day"

    id = Column(Integer, primary_key=True, index=True)
    ngay = Column(Date, nullable=False)
    tiet = Column(Integer, nullable=False)  # Period number 1-10
    lop_id = Column(Integer, ForeignKey("dm_lop.id"), nullable=False)
    mon_hoc_id = Column(Integer, ForeignKey("dm_mon_hoc.id"), nullable=False)
    gv_goc_id = Column(Integer, ForeignKey("nhan_vien.id"), nullable=False)  # Original teacher
    gv_thay_id = Column(Integer, ForeignKey("nhan_vien.id"), nullable=False)  # Substitute teacher
    ly_do = Column(String(200), nullable=True)
    thang = Column(Integer, nullable=False)
    nam = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    lop = relationship("DmLop", foreign_keys=[lop_id])
    mon_hoc = relationship("DmMonHoc", foreign_keys=[mon_hoc_id])
    gv_goc = relationship("NhanVien", foreign_keys=[gv_goc_id])
    gv_thay = relationship("NhanVien", foreign_keys=[gv_thay_id])

    def __repr__(self):
        return f"<DlThayDoiNguoiDay(id={self.id}, ngay={self.ngay}, tiet={self.tiet})>"


class DlBccTongTiet(Base):
    """BCC Summary per teacher per month - bảng chấm công tổng tiết."""
    __tablename__ = "dl_bcc_tong_tiet"

    id = Column(Integer, primary_key=True, index=True)
    thang = Column(Integer, nullable=False)
    nam = Column(Integer, nullable=False)
    nhan_vien_id = Column(Integer, ForeignKey("nhan_vien.id"), nullable=False)
    theo_tkb_json = Column(JSON, nullable=True)  # Scheduled periods breakdown
    thay_doi_json = Column(JSON, nullable=True)  # Changes breakdown
    phat_sinh_json = Column(JSON, nullable=True)  # Adjustments breakdown
    thuc_te_json = Column(JSON, nullable=True)  # Actual periods breakdown
    is_complete = Column(Boolean, default=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    nhan_vien = relationship("NhanVien", foreign_keys=[nhan_vien_id])

    def __repr__(self):
        return f"<DlBccTongTiet(id={self.id}, nv={self.nhan_vien_id}, thang={self.thang}/{self.nam})>"


class DlTietDayNgoai(Base):
    """External teaching periods - tiết dạy ngoài."""
    __tablename__ = "dl_tiet_day_ngoai"

    id = Column(Integer, primary_key=True, index=True)
    thang = Column(Integer, nullable=False)
    nam = Column(Integer, nullable=False)
    nhan_vien_id = Column(Integer, ForeignKey("nhan_vien.id"), nullable=False)
    loai = Column(String(100), nullable=False)  # Type: quản lý, chính khóa, ielts, etc.
    so_tiet = Column(Numeric(5, 1), nullable=False)
    don_gia = Column(Numeric(12, 0), nullable=False)
    he_so = Column(Numeric(3, 1), default=1.0)
    thanh_tien = Column(Numeric(12, 0), nullable=True)  # Computed: so_tiet × don_gia × he_so
    ghi_chu = Column(String(255), nullable=True)

    # Relationships
    nhan_vien = relationship("NhanVien", foreign_keys=[nhan_vien_id])

    def __repr__(self):
        return f"<DlTietDayNgoai(id={self.id}, nv={self.nhan_vien_id}, loai='{self.loai}')>"
