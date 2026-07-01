from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.nhan_vien import NhomNV, LoaiHopDong, TrangThaiNV


class NhanVienCreate(BaseModel):
    ma_nv: str = Field(..., max_length=20)
    cccd: Optional[str] = Field(None, min_length=12, max_length=12, pattern=r"^\d{12}$")
    ho_ten: str = Field(..., max_length=100)
    nhom_nv: NhomNV  # GV or VP (required)
    don_vi_id: Optional[int] = None
    chuc_vu_id: Optional[int] = None
    cap_bac_ql_id: Optional[int] = None
    ten_goi: Optional[str] = Field(None, max_length=50)  # GV only
    loai_hop_dong: Optional[LoaiHopDong] = None
    trang_thai: TrangThaiNV = TrangThaiNV.dang_lam
    ngay_sinh: Optional[date] = None
    email: Optional[str] = Field(None, max_length=100)
    sdt: Optional[str] = Field(None, max_length=20)
    ngay_vao_lam: Optional[date] = None
    so_nguoi_phu_thuoc: int = 0


class NhanVienUpdate(BaseModel):
    ho_ten: Optional[str] = Field(None, max_length=100)
    cccd: Optional[str] = Field(None, min_length=12, max_length=12, pattern=r"^\d{12}$")
    don_vi_id: Optional[int] = None
    chuc_vu_id: Optional[int] = None
    cap_bac_ql_id: Optional[int] = None
    ten_goi: Optional[str] = Field(None, max_length=50)
    loai_hop_dong: Optional[LoaiHopDong] = None
    trang_thai: Optional[TrangThaiNV] = None
    ngay_sinh: Optional[date] = None
    email: Optional[str] = Field(None, max_length=100)
    sdt: Optional[str] = Field(None, max_length=20)
    ngay_vao_lam: Optional[date] = None
    so_nguoi_phu_thuoc: Optional[int] = None


class NhanVienResponse(BaseModel):
    id: int
    ma_nv: str
    cccd: Optional[str] = None
    ho_ten: str
    nhom_nv: NhomNV
    don_vi_id: Optional[int] = None
    chuc_vu_id: Optional[int] = None
    cap_bac_ql_id: Optional[int] = None
    ten_goi: Optional[str] = None
    loai_hop_dong: Optional[LoaiHopDong] = None
    trang_thai: TrangThaiNV
    ngay_sinh: Optional[date] = None
    email: Optional[str] = None
    sdt: Optional[str] = None
    ngay_vao_lam: Optional[date] = None
    so_nguoi_phu_thuoc: int = 0
    luong_khoan: Optional[int] = None  # Computed field (not from DB directly)
    created_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class HopDongCreate(BaseModel):
    loai: LoaiHopDong
    luong_dong_bh: Optional[int] = Field(None, ge=0, le=999999999)
    he_so_luong_id: Optional[int] = None
    thuong_hieu_qua: Optional[int] = Field(None, ge=0)
    ngay_bat_dau: date
    ngay_ket_thuc: Optional[date] = None
    ghi_chu: Optional[str] = Field(None, max_length=500)


class HopDongResponse(BaseModel):
    id: int
    nhan_vien_id: int
    loai: LoaiHopDong
    luong_dong_bh: Optional[int] = None
    he_so_luong_id: Optional[int] = None
    thuong_hieu_qua: Optional[int] = None
    ngay_bat_dau: date
    ngay_ket_thuc: Optional[date] = None
    ghi_chu: Optional[str] = None
    created_at: Optional[datetime] = None
    model_config = {"from_attributes": True}
