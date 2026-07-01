"""
NBK Salary - Catalog/Master Data Models (danh mục).

Defines 10 SQLAlchemy models for all dm_* catalog tables:
departments, positions, grades, classes, subjects, job positions,
salary grades, attendance symbols, tasks/duties, and teaching unit prices.
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, Date, Numeric,
    ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship

from app.database import Base


class DmDonVi(Base):
    """Departments (Đơn vị)."""
    __tablename__ = "dm_don_vi"

    id = Column(Integer, primary_key=True, index=True)
    ten = Column(String(100), unique=True, nullable=False)
    mo_ta = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    # MISA Cơ cấu tổ chức fields
    ma_don_vi = Column(String(20), nullable=True)
    thuoc_don_vi = Column(String(20), nullable=True)
    dia_chi = Column(String(300), nullable=True)
    cap_to_chuc = Column(String(50), nullable=True)
    truong_don_vi = Column(String(100), nullable=True)
    chuc_nang_nhiem_vu = Column(String(500), nullable=True)
    hach_toan = Column(String(50), nullable=True)
    thu_tu_sap_xep = Column(Integer, nullable=True)
    ma_so_dkkd = Column(String(30), nullable=True)
    ngay_cap_dkkd = Column(Date, nullable=True)
    noi_cap_dkkd = Column(String(200), nullable=True)

    def __repr__(self):
        return f"<DmDonVi(id={self.id}, ten='{self.ten}')>"


class DmChucDanh(Base):
    """Positions (Chức danh)."""
    __tablename__ = "dm_chuc_danh"

    id = Column(Integer, primary_key=True, index=True)
    ten = Column(String(100), unique=True, nullable=False)
    mo_ta = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<DmChucDanh(id={self.id}, ten='{self.ten}')>"


class DmKhoi(Base):
    """Grades/Blocks (Khối 6, 7, 8, 9)."""
    __tablename__ = "dm_khoi"

    id = Column(Integer, primary_key=True, index=True)
    ten = Column(String(20), unique=True, nullable=False)
    thu_tu = Column(Integer, nullable=False)

    # Relationships
    lop_list = relationship("DmLop", back_populates="khoi")
    don_gia_day_list = relationship("DmDonGiaDay", back_populates="khoi")

    def __repr__(self):
        return f"<DmKhoi(id={self.id}, ten='{self.ten}')>"


class DmLop(Base):
    """Classes (Lớp)."""
    __tablename__ = "dm_lop"

    id = Column(Integer, primary_key=True, index=True)
    ten = Column(String(50), unique=True, nullable=False)
    khoi_id = Column(Integer, ForeignKey("dm_khoi.id"), nullable=False)

    # Relationships
    khoi = relationship("DmKhoi", back_populates="lop_list")

    def __repr__(self):
        return f"<DmLop(id={self.id}, ten='{self.ten}', khoi_id={self.khoi_id})>"


class DmMonHoc(Base):
    """Subjects (Môn học)."""
    __tablename__ = "dm_mon_hoc"

    id = Column(Integer, primary_key=True, index=True)
    ten = Column(String(100), unique=True, nullable=False)
    ma_mon = Column(String(20), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)

    # Relationships
    don_gia_day_list = relationship("DmDonGiaDay", back_populates="mon_hoc")

    def __repr__(self):
        return f"<DmMonHoc(id={self.id}, ten='{self.ten}', ma_mon='{self.ma_mon}')>"


class DmViTri(Base):
    """Job positions (Vị trí)."""
    __tablename__ = "dm_vi_tri"

    id = Column(Integer, primary_key=True, index=True)
    ten = Column(String(100), unique=True, nullable=False)
    mo_ta = Column(String(255), nullable=True)
    # MISA Vị trí công việc fields
    ma_vi_tri = Column(String(20), nullable=True)
    don_vi_cong_tac = Column(String(100), nullable=True)
    nhom_vi_tri = Column(String(100), nullable=True)
    chuc_danh = Column(String(100), nullable=True)
    trang_thai = Column(String(50), nullable=True)

    def __repr__(self):
        return f"<DmViTri(id={self.id}, ten='{self.ten}')>"


class DmHeSoLuong(Base):
    """Salary grades (Hệ số lương)."""
    __tablename__ = "dm_he_so_luong"

    id = Column(Integer, primary_key=True, index=True)
    bac = Column(String(50), nullable=False)
    he_so = Column(Numeric(5, 2), nullable=False)
    ngay_hieu_luc = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<DmHeSoLuong(id={self.id}, bac='{self.bac}', he_so={self.he_so})>"


class DmKyHieuCong(Base):
    """Attendance symbols (Ký hiệu công)."""
    __tablename__ = "dm_ky_hieu_cong"

    id = Column(Integer, primary_key=True, index=True)
    ky_hieu = Column(String(10), unique=True, nullable=False)
    ten = Column(String(100), nullable=False)
    gia_tri_ngay_cong = Column(Numeric(3, 1), nullable=False)
    loai = Column(String(50), nullable=False)  # e.g. "present", "leave", "overtime"

    # Relationships
    cham_cong_list = relationship("DlChamCong", back_populates="ky_hieu_cong")

    def __repr__(self):
        return f"<DmKyHieuCong(id={self.id}, ky_hieu='{self.ky_hieu}', loai='{self.loai}')>"


class DmNhiemVu(Base):
    """Tasks/duties with unit prices (Nhiệm vụ)."""
    __tablename__ = "dm_nhiem_vu"

    id = Column(Integer, primary_key=True, index=True)
    ten = Column(String(100), nullable=False)
    don_gia = Column(Numeric(12, 0), nullable=False)
    mo_ta = Column(String(255), nullable=True)

    def __repr__(self):
        return f"<DmNhiemVu(id={self.id}, ten='{self.ten}', don_gia={self.don_gia})>"


class DmDonGiaDay(Base):
    """Teaching unit prices - Teacher×Subject×Grade (Đơn giá dạy)."""
    __tablename__ = "dm_don_gia_day"
    # Note: Ideally a partial unique constraint on (nhan_vien_id, mon_hoc_id, khoi_id)
    # WHERE is_active=True should be enforced at the database level via a partial index.
    # SQLAlchemy's UniqueConstraint does not support WHERE clauses natively;
    # use Alembic migration or raw SQL to add the partial unique index.
    __table_args__ = (
        UniqueConstraint(
            "nhan_vien_id", "mon_hoc_id", "khoi_id",
            name="uq_don_gia_day_nv_mon_khoi"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    nhan_vien_id = Column(Integer, ForeignKey("nhan_vien.id"), nullable=False)
    mon_hoc_id = Column(Integer, ForeignKey("dm_mon_hoc.id"), nullable=False)
    khoi_id = Column(Integer, ForeignKey("dm_khoi.id"), nullable=False)
    don_gia = Column(Numeric(12, 0), nullable=False)
    ngay_bat_dau = Column(Date, nullable=False)
    ngay_ket_thuc = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    mon_hoc = relationship("DmMonHoc", back_populates="don_gia_day_list")
    khoi = relationship("DmKhoi", back_populates="don_gia_day_list")

    def __repr__(self):
        return (
            f"<DmDonGiaDay(id={self.id}, nhan_vien_id={self.nhan_vien_id}, "
            f"mon_hoc_id={self.mon_hoc_id}, khoi_id={self.khoi_id})>"
        )


class DmLoaiTietNgoai(Base):
    """External period types (Loại tiết ngoài) - e.g. Vĩnh Yên, Bồi dưỡng, IELTS, Luyện thi, Âm nhạc."""
    __tablename__ = "dm_loai_tiet_ngoai"

    id = Column(Integer, primary_key=True, index=True)
    ten = Column(String(100), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<DmLoaiTietNgoai(id={self.id}, ten='{self.ten}')>"


class DmLoaiHoTro(Base):
    """Support allowance types (Loại hỗ trợ) - e.g. ăn trưa, gửi xe, ChatGPT."""
    __tablename__ = "dm_loai_ho_tro"

    id = Column(Integer, primary_key=True, index=True)
    ten = Column(String(100), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<DmLoaiHoTro(id={self.id}, ten='{self.ten}')>"
