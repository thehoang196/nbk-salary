"""
NBK Salary - Chức danh Models (Position Titles & Related).

Defines models for:
- DmChucVu: Position titles (Chức vụ)
- DmCapBacQL: Management levels (Cấp bậc quản lý)
- DmNghiepVu: Professional duties (Nghiệp vụ) - each adds 2,000,000 VND to Lương Khoán
- DmKiemNhiem: Concurrent roles (Kiêm nhiệm) - each adds 3,000,000 VND to Lương Khoán
- NvNghiepVu: Junction table employee ↔ nghiệp vụ
- NvKiemNhiem: Junction table employee ↔ kiêm nhiệm
"""

from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, Numeric
from sqlalchemy.orm import relationship

from app.database import Base


class DmChucVu(Base):
    """Position titles (Chức vụ)."""
    __tablename__ = "dm_chuc_vu"

    id = Column(Integer, primary_key=True, index=True)
    ma = Column(String(20), unique=True, nullable=False)
    ten = Column(String(100), nullable=False)
    don_gia_luong_khoan = Column(Numeric(12, 0), default=0)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<DmChucVu(id={self.id}, ma='{self.ma}', ten='{self.ten}')>"


class DmCapBacQL(Base):
    """Management levels (Cấp bậc quản lý)."""
    __tablename__ = "dm_cap_bac_ql"

    id = Column(Integer, primary_key=True, index=True)
    ma = Column(String(20), unique=True, nullable=False)
    ten = Column(String(100), nullable=False)
    don_gia_luong_khoan = Column(Numeric(12, 0), default=0)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<DmCapBacQL(id={self.id}, ma='{self.ma}', ten='{self.ten}')>"


class DmNghiepVu(Base):
    """
    Professional duties (Nghiệp vụ).
    Each adds fixed 2,000,000 VND to Lương Khoán.
    """
    __tablename__ = "dm_nghiep_vu"

    id = Column(Integer, primary_key=True, index=True)
    ma = Column(String(20), unique=True, nullable=False)
    ten = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<DmNghiepVu(id={self.id}, ma='{self.ma}', ten='{self.ten}')>"


class DmKiemNhiem(Base):
    """
    Concurrent roles (Kiêm nhiệm).
    Each adds fixed 3,000,000 VND to Lương Khoán.
    """
    __tablename__ = "dm_kiem_nhiem"

    id = Column(Integer, primary_key=True, index=True)
    ma = Column(String(20), unique=True, nullable=False)
    ten = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<DmKiemNhiem(id={self.id}, ma='{self.ma}', ten='{self.ten}')>"


class NvNghiepVu(Base):
    """Junction table: employee ↔ nghiệp vụ (professional duties)."""
    __tablename__ = "nv_nghiep_vu"

    id = Column(Integer, primary_key=True, index=True)
    nhan_vien_id = Column(Integer, ForeignKey("nhan_vien.id"), nullable=False)
    nghiep_vu_id = Column(Integer, ForeignKey("dm_nghiep_vu.id"), nullable=False)
    mo_ta = Column(String(255), nullable=True)
    ngay_bat_dau = Column(Date, nullable=False)
    ngay_ket_thuc = Column(Date, nullable=True)

    # Relationships
    nhan_vien = relationship("NhanVien", back_populates="nghiep_vu_list")
    nghiep_vu = relationship("DmNghiepVu")

    def __repr__(self):
        return f"<NvNghiepVu(id={self.id}, nhan_vien_id={self.nhan_vien_id}, nghiep_vu_id={self.nghiep_vu_id})>"


class NvKiemNhiem(Base):
    """Junction table: employee ↔ kiêm nhiệm (concurrent roles)."""
    __tablename__ = "nv_kiem_nhiem"

    id = Column(Integer, primary_key=True, index=True)
    nhan_vien_id = Column(Integer, ForeignKey("nhan_vien.id"), nullable=False)
    kiem_nhiem_id = Column(Integer, ForeignKey("dm_kiem_nhiem.id"), nullable=False)
    mo_ta = Column(String(255), nullable=True)
    ngay_bat_dau = Column(Date, nullable=False)
    ngay_ket_thuc = Column(Date, nullable=True)

    # Relationships
    nhan_vien = relationship("NhanVien", back_populates="kiem_nhiem_list")
    kiem_nhiem = relationship("DmKiemNhiem")

    def __repr__(self):
        return f"<NvKiemNhiem(id={self.id}, nhan_vien_id={self.nhan_vien_id}, kiem_nhiem_id={self.kiem_nhiem_id})>"
