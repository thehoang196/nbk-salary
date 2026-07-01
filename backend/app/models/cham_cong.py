"""
NBK Salary - Attendance Models (Chấm công).

Defines:
- DlChamCong: Daily attendance records per employee.
- DlTongHopCong: Monthly attendance summary per employee.
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, Date, Numeric,
    ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship

from app.database import Base


class DlChamCong(Base):
    """Daily attendance records (Dữ liệu chấm công hàng ngày)."""
    __tablename__ = "dl_cham_cong"
    __table_args__ = (
        UniqueConstraint(
            "nhan_vien_id", "ngay",
            name="uq_cham_cong_nv_ngay"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    nhan_vien_id = Column(Integer, ForeignKey("nhan_vien.id"), nullable=False)
    ngay = Column(Date, nullable=False)
    ky_hieu_cong_id = Column(Integer, ForeignKey("dm_ky_hieu_cong.id"), nullable=False)
    ghi_chu = Column(String(255), nullable=True)

    # Relationships
    nhan_vien = relationship("NhanVien", back_populates="cham_cong_list")
    ky_hieu_cong = relationship("DmKyHieuCong", back_populates="cham_cong_list")

    def __repr__(self):
        return (
            f"<DlChamCong(id={self.id}, nhan_vien_id={self.nhan_vien_id}, "
            f"ngay={self.ngay}, ky_hieu_cong_id={self.ky_hieu_cong_id})>"
        )


class DlTongHopCong(Base):
    """Monthly attendance summary (Tổng hợp công tháng)."""
    __tablename__ = "dl_tong_hop_cong"
    __table_args__ = (
        UniqueConstraint(
            "nhan_vien_id", "thang", "nam",
            name="uq_tong_hop_cong_nv_thang_nam"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    nhan_vien_id = Column(Integer, ForeignKey("nhan_vien.id"), nullable=False)
    thang = Column(Integer, nullable=False)
    nam = Column(Integer, nullable=False)
    ngay_cong = Column(Numeric(4, 1), nullable=False)
    ngay_nghi = Column(Numeric(4, 1), nullable=False)
    ngay_phep = Column(Numeric(4, 1), nullable=False)
    lam_them = Column(Numeric(4, 1), nullable=False)
    cong_chuan = Column(Integer, default=26)
    is_confirmed = Column(Boolean, default=False)

    # Relationships
    nhan_vien = relationship("NhanVien", back_populates="tong_hop_cong_list")

    def __repr__(self):
        return (
            f"<DlTongHopCong(id={self.id}, nhan_vien_id={self.nhan_vien_id}, "
            f"thang={self.thang}, nam={self.nam})>"
        )
