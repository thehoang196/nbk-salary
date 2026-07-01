"""
NBK Salary - Salary/Payslip Model (Bảng lương).

Stores complete payslip data with 6 sections in JSON columns.
Supports workflow: draft → reviewed → approved.
"""

from sqlalchemy import (
    Column, Integer, String, DateTime, Numeric, ForeignKey,
    Enum as SAEnum, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.types import JSON
import enum

from app.database import Base


class TrangThaiBangLuong(str, enum.Enum):
    draft = "draft"
    reviewed = "reviewed"
    approved = "approved"


class DlBangLuong(Base):
    """Salary record / Payslip (Bảng lương / Phiếu lương)."""
    __tablename__ = "dl_bang_luong"
    __table_args__ = (
        UniqueConstraint(
            "nhan_vien_id", "thang", "nam",
            name="uq_bang_luong_nv_thang_nam"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    nhan_vien_id = Column(Integer, ForeignKey("nhan_vien.id"), nullable=False)
    thang = Column(Integer, nullable=False)
    nam = Column(Integer, nullable=False)
    trang_thai = Column(SAEnum(TrangThaiBangLuong), default=TrangThaiBangLuong.draft)
    
    # 6 Payslip sections stored as JSON
    muc_i_json = Column(JSON, nullable=True)    # Section I: Employee Info
    muc_ii_json = Column(JSON, nullable=True)   # Section II: Total Income (9 items)
    muc_iii_json = Column(JSON, nullable=True)  # Section III: Bonuses Already Received
    muc_iv_json = Column(JSON, nullable=True)   # Section IV: Deductions (5 items)
    muc_v_json = Column(JSON, nullable=True)    # Section V: Tax Settlement
    muc_vi_thuc_linh = Column(Numeric(14, 0), nullable=True)  # Section VI: Net Pay
    
    # Workflow tracking
    nguoi_tinh_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    nguoi_duyet_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    ngay_tinh = Column(DateTime(timezone=True), nullable=True)
    ngay_duyet = Column(DateTime(timezone=True), nullable=True)
    
    # Optimistic locking
    version = Column(Integer, default=1)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    nhan_vien = relationship("NhanVien")
    nguoi_tinh = relationship("User", foreign_keys=[nguoi_tinh_id])
    nguoi_duyet = relationship("User", foreign_keys=[nguoi_duyet_id])

    def __repr__(self):
        return f"<DlBangLuong(id={self.id}, nv={self.nhan_vien_id}, {self.thang}/{self.nam}, {self.trang_thai})>"
