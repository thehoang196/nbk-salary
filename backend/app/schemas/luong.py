from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class TinhLuongRequest(BaseModel):
    thang: int = Field(..., ge=1, le=12)
    nam: int = Field(..., ge=2020, le=2099)
    nhan_vien_ids: Optional[List[int]] = None  # None = all employees
    manual_inputs: Optional[Dict[int, Dict[str, Any]]] = None  # nv_id → manual input values


class BangLuongItem(BaseModel):
    id: int
    nhan_vien_id: int
    ho_ten: str
    ma_nv: str
    nhom_nv: str
    thang: int
    nam: int
    trang_thai: str
    muc_vi_thuc_linh: Optional[int] = None
    ngay_tinh: Optional[datetime] = None
    model_config = {"from_attributes": True}


class BangLuongResponse(BaseModel):
    thang: int
    nam: int
    items: List[BangLuongItem]
    total_count: int
    total_thuc_linh: int


class PhieuLuongResponse(BaseModel):
    nhan_vien_id: int
    thang: int
    nam: int
    trang_thai: str
    muc_i: Dict[str, Any]
    muc_ii: Dict[str, Any]
    muc_iii: Dict[str, Any]
    muc_iv: Dict[str, Any]
    muc_v: Dict[str, Any]
    muc_vi_thuc_linh: int
    ngay_tinh: Optional[datetime] = None
    nguoi_tinh: Optional[str] = None
    ngay_duyet: Optional[datetime] = None
    nguoi_duyet: Optional[str] = None
    version: int = 1


class DuyetLuongRequest(BaseModel):
    trang_thai_moi: str = Field(..., description="reviewed or approved")
    version: int  # For optimistic locking


class LuongKhoanResponse(BaseModel):
    nhan_vien_id: int
    ho_ten: str
    chuc_vu_don_gia: int
    cap_bac_don_gia: int
    nghiep_vu_count: int
    nghiep_vu_total: int
    kiem_nhiem_count: int
    kiem_nhiem_total: int
    tong_luong_khoan: int
