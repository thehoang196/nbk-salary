from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


# ===== DmChucVu =====
class ChucVuCreate(BaseModel):
    ma: str = Field(..., max_length=20)
    ten: str = Field(..., max_length=100)
    don_gia_luong_khoan: int = Field(0, ge=0, le=999999999)

class ChucVuUpdate(BaseModel):
    ma: Optional[str] = Field(None, max_length=20)
    ten: Optional[str] = Field(None, max_length=100)
    don_gia_luong_khoan: Optional[int] = Field(None, ge=0, le=999999999)
    is_active: Optional[bool] = None

class ChucVuResponse(BaseModel):
    id: int
    ma: str
    ten: str
    don_gia_luong_khoan: int
    is_active: bool
    model_config = {"from_attributes": True}


# ===== DmCapBacQL =====
class CapBacQLCreate(BaseModel):
    ma: str = Field(..., max_length=20)
    ten: str = Field(..., max_length=100)
    don_gia_luong_khoan: int = Field(0, ge=0, le=999999999)

class CapBacQLUpdate(BaseModel):
    ma: Optional[str] = Field(None, max_length=20)
    ten: Optional[str] = Field(None, max_length=100)
    don_gia_luong_khoan: Optional[int] = Field(None, ge=0, le=999999999)
    is_active: Optional[bool] = None

class CapBacQLResponse(BaseModel):
    id: int
    ma: str
    ten: str
    don_gia_luong_khoan: int
    is_active: bool
    model_config = {"from_attributes": True}


# ===== DmNghiepVu =====
class NghiepVuCreate(BaseModel):
    ma: str = Field(..., max_length=20)
    ten: str = Field(..., max_length=100)

class NghiepVuUpdate(BaseModel):
    ma: Optional[str] = Field(None, max_length=20)
    ten: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None

class NghiepVuResponse(BaseModel):
    id: int
    ma: str
    ten: str
    is_active: bool
    model_config = {"from_attributes": True}


# ===== DmKiemNhiem =====
class KiemNhiemCreate(BaseModel):
    ma: str = Field(..., max_length=20)
    ten: str = Field(..., max_length=100)

class KiemNhiemUpdate(BaseModel):
    ma: Optional[str] = Field(None, max_length=20)
    ten: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None

class KiemNhiemResponse(BaseModel):
    id: int
    ma: str
    ten: str
    is_active: bool
    model_config = {"from_attributes": True}


# ===== NvNghiepVu (assignment) =====
class NvNghiepVuCreate(BaseModel):
    nghiep_vu_id: int
    mo_ta: Optional[str] = Field(None, max_length=255)
    ngay_bat_dau: date
    ngay_ket_thuc: Optional[date] = None

class NvNghiepVuResponse(BaseModel):
    id: int
    nhan_vien_id: int
    nghiep_vu_id: int
    mo_ta: Optional[str] = None
    ngay_bat_dau: date
    ngay_ket_thuc: Optional[date] = None
    model_config = {"from_attributes": True}


# ===== NvKiemNhiem (assignment) =====
class NvKiemNhiemCreate(BaseModel):
    kiem_nhiem_id: int
    mo_ta: Optional[str] = Field(None, max_length=255)
    ngay_bat_dau: date
    ngay_ket_thuc: Optional[date] = None

class NvKiemNhiemResponse(BaseModel):
    id: int
    nhan_vien_id: int
    kiem_nhiem_id: int
    mo_ta: Optional[str] = None
    ngay_bat_dau: date
    ngay_ket_thuc: Optional[date] = None
    model_config = {"from_attributes": True}
