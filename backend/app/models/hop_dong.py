from sqlalchemy import Column, Integer, String, Date, DateTime, Numeric, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models.nhan_vien import LoaiHopDong


class DlHopDong(Base):
    """Contract/salary history (Hợp đồng lao động)."""
    __tablename__ = "dl_hop_dong"

    id = Column(Integer, primary_key=True, index=True)
    nhan_vien_id = Column(Integer, ForeignKey("nhan_vien.id"), nullable=False)
    loai = Column(SAEnum(LoaiHopDong), nullable=False)
    luong_khoan = Column(Numeric(12, 0), nullable=True)  # Contracted salary
    luong_dong_bh = Column(Numeric(12, 0), nullable=True)  # Insurance base salary
    he_so_luong_id = Column(Integer, ForeignKey("dm_he_so_luong.id"), nullable=True)
    thuong_hieu_qua = Column(Numeric(12, 0), nullable=True)  # Efficiency bonus rate
    ngay_bat_dau = Column(Date, nullable=False)
    ngay_ket_thuc = Column(Date, nullable=True)
    ghi_chu = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    nhan_vien = relationship("NhanVien", back_populates="hop_dong_list")
    he_so_luong = relationship("DmHeSoLuong")

    def __repr__(self):
        return f"<DlHopDong(id={self.id}, nhan_vien_id={self.nhan_vien_id}, loai='{self.loai}')>"
