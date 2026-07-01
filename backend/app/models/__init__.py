"""
NBK Salary - SQLAlchemy ORM Models
"""
from app.database import Base

from app.models.user import User, UserRole
from app.models.danh_muc import (
    DmDonVi, DmChucDanh, DmKhoi, DmLop, DmMonHoc, DmViTri,
    DmHeSoLuong, DmKyHieuCong, DmNhiemVu, DmDonGiaDay,
    DmLoaiTietNgoai, DmLoaiHoTro
)
from app.models.chuc_danh import (
    DmChucVu, DmCapBacQL, DmNghiepVu, DmKiemNhiem,
    NvNghiepVu, NvKiemNhiem
)
from app.models.nhan_vien import NhanVien, NhomNV, LoaiHopDong, TrangThaiNV
from app.models.hop_dong import DlHopDong
from app.models.tkb import DlTkb, DlThayDoiNguoiDay, DlBccTongTiet, DlTietDayNgoai
from app.models.cham_cong import DlChamCong, DlTongHopCong
from app.models.bang_luong import DlBangLuong, TrangThaiBangLuong
from app.models.ho_tro_luong import DlHoTroLuong
from app.models.misa_hr import (
    DlGiaDinh, DlLichSuLuong, DlQuaTrinhCongTac, DlBangCap, DlNghiPhep
)
