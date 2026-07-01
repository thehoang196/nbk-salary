"""
NBK Salary - Support Allowance Model (Hỗ trợ lương).

Defines the DlHoTroLuong table: one row per employee per month per allowance type.
Summed into payslip Section II item 4.
"""

from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class DlHoTroLuong(Base):
    __tablename__ = "dl_ho_tro_luong"

    id = Column(Integer, primary_key=True, index=True)
    nhan_vien_id = Column(Integer, ForeignKey("nhan_vien.id"), nullable=False)
    thang = Column(Integer, nullable=False)
    nam = Column(Integer, nullable=False)
    loai_ho_tro = Column(String(100), nullable=False)  # ăn trưa, gửi xe, ChatGPT, etc.
    so_tien = Column(Numeric(12, 0), nullable=False)  # Amount in VND (0–999,999,999)
    ghi_chu = Column(String(255), nullable=True)

    # Relationships
    nhan_vien = relationship("NhanVien", back_populates="ho_tro_luong_list")

    def __repr__(self):
        return (
            f"<DlHoTroLuong(id={self.id}, nhan_vien_id={self.nhan_vien_id}, "
            f"thang={self.thang}, nam={self.nam}, loai='{self.loai_ho_tro}', "
            f"so_tien={self.so_tien})>"
        )
