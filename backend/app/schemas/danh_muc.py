"""
NBK Salary - Catalog/Master Data Pydantic schemas (danh mục).

Provides Create, Update, and Response schemas for all 10 dm_* catalog entities.
"""

from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


# ===== DmDonVi =====
class DonViCreate(BaseModel):
    ten: str = Field(..., max_length=100)
    mo_ta: Optional[str] = Field(None, max_length=255)

class DonViUpdate(BaseModel):
    ten: Optional[str] = Field(None, max_length=100)
    mo_ta: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None

class DonViResponse(BaseModel):
    id: int
    ten: str
    mo_ta: Optional[str] = None
    is_active: bool
    model_config = {"from_attributes": True}


# ===== DmChucDanh =====
class ChucDanhCreate(BaseModel):
    ten: str = Field(..., max_length=100)
    mo_ta: Optional[str] = Field(None, max_length=255)

class ChucDanhUpdate(BaseModel):
    ten: Optional[str] = Field(None, max_length=100)
    mo_ta: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None

class ChucDanhResponse(BaseModel):
    id: int
    ten: str
    mo_ta: Optional[str] = None
    is_active: bool
    model_config = {"from_attributes": True}


# ===== DmKhoi =====
class KhoiCreate(BaseModel):
    ten: str = Field(..., max_length=20)
    thu_tu: int

class KhoiResponse(BaseModel):
    id: int
    ten: str
    thu_tu: int
    model_config = {"from_attributes": True}


# ===== DmLop =====
class LopCreate(BaseModel):
    ten: str = Field(..., max_length=50)
    khoi_id: int

class LopResponse(BaseModel):
    id: int
    ten: str
    khoi_id: int
    model_config = {"from_attributes": True}


# ===== DmMonHoc =====
class MonHocCreate(BaseModel):
    ten: str = Field(..., max_length=100)
    ma_mon: str = Field(..., max_length=20)

class MonHocUpdate(BaseModel):
    ten: Optional[str] = Field(None, max_length=100)
    ma_mon: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None

class MonHocResponse(BaseModel):
    id: int
    ten: str
    ma_mon: str
    is_active: bool
    model_config = {"from_attributes": True}


# ===== DmViTri =====
class ViTriCreate(BaseModel):
    ten: str = Field(..., max_length=100)
    mo_ta: Optional[str] = Field(None, max_length=255)

class ViTriResponse(BaseModel):
    id: int
    ten: str
    mo_ta: Optional[str] = None
    model_config = {"from_attributes": True}


# ===== DmHeSoLuong =====
class HeSoLuongCreate(BaseModel):
    bac: str = Field(..., max_length=50)
    he_so: float = Field(..., gt=0, le=99.99)
    ngay_hieu_luc: date

class HeSoLuongResponse(BaseModel):
    id: int
    bac: str
    he_so: float
    ngay_hieu_luc: date
    is_active: bool
    model_config = {"from_attributes": True}


# ===== DmKyHieuCong =====
class KyHieuCongCreate(BaseModel):
    ky_hieu: str = Field(..., max_length=10)
    ten: str = Field(..., max_length=100)
    gia_tri_ngay_cong: float = Field(..., ge=0, le=9.9)
    loai: str = Field(..., max_length=50)

class KyHieuCongResponse(BaseModel):
    id: int
    ky_hieu: str
    ten: str
    gia_tri_ngay_cong: float
    loai: str
    model_config = {"from_attributes": True}


# ===== DmNhiemVu =====
class NhiemVuCreate(BaseModel):
    ten: str = Field(..., max_length=100)
    don_gia: int = Field(..., ge=1, le=999999999)
    mo_ta: Optional[str] = Field(None, max_length=255)

class NhiemVuResponse(BaseModel):
    id: int
    ten: str
    don_gia: int
    mo_ta: Optional[str] = None
    model_config = {"from_attributes": True}


# ===== DmLoaiTietNgoai =====
class LoaiTietNgoaiCreate(BaseModel):
    ten: str = Field(..., max_length=100)

class LoaiTietNgoaiResponse(BaseModel):
    id: int
    ten: str
    is_active: bool
    model_config = {"from_attributes": True}


# ===== DmLoaiHoTro =====
class LoaiHoTroCreate(BaseModel):
    ten: str = Field(..., max_length=100)

class LoaiHoTroResponse(BaseModel):
    id: int
    ten: str
    is_active: bool
    model_config = {"from_attributes": True}


# ===== DmDonGiaDay =====
class DonGiaDayCreate(BaseModel):
    nhan_vien_id: int
    mon_hoc_id: int
    khoi_id: int
    don_gia: int = Field(..., ge=1, le=999999999)
    ngay_bat_dau: date
    ngay_ket_thuc: Optional[date] = None

class DonGiaDayUpdate(BaseModel):
    don_gia: Optional[int] = Field(None, ge=1, le=999999999)
    ngay_ket_thuc: Optional[date] = None
    is_active: Optional[bool] = None

class DonGiaDayResponse(BaseModel):
    id: int
    nhan_vien_id: int
    mon_hoc_id: int
    khoi_id: int
    don_gia: int
    ngay_bat_dau: date
    ngay_ket_thuc: Optional[date] = None
    is_active: bool
    model_config = {"from_attributes": True}
