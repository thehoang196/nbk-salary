from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class HoTroLuongCreate(BaseModel):
    nhan_vien_id: int
    thang: int = Field(..., ge=1, le=12)
    nam: int = Field(..., ge=2020, le=2099)
    loai_ho_tro: str = Field(..., max_length=100, description="Type from dm_loai_ho_tro")
    so_tien: int = Field(..., ge=0, le=999999999)
    ghi_chu: Optional[str] = Field(None, max_length=255)


class HoTroLuongUpdate(BaseModel):
    loai_ho_tro: Optional[str] = Field(None, max_length=100)
    so_tien: Optional[int] = Field(None, ge=0, le=999999999)
    ghi_chu: Optional[str] = Field(None, max_length=255)


class HoTroLuongResponse(BaseModel):
    id: int
    nhan_vien_id: int
    thang: int
    nam: int
    loai_ho_tro: str
    so_tien: int
    ghi_chu: Optional[str] = None
    model_config = {"from_attributes": True}


class HoTroLuongBatchEntry(BaseModel):
    """Single entry in a batch allowance creation."""
    nhan_vien_id: int
    so_tien: int = Field(..., ge=0, le=999999999)
    ghi_chu: Optional[str] = None


class HoTroLuongBatchCreate(BaseModel):
    """Batch create: one allowance type for multiple employees in a month."""
    thang: int = Field(..., ge=1, le=12)
    nam: int = Field(..., ge=2020, le=2099)
    loai_ho_tro: str = Field(..., max_length=100)
    entries: List[HoTroLuongBatchEntry]


class HoTroLuongImportRow(BaseModel):
    """Row for bulk import from Excel/CSV."""
    ma_nv: str
    loai_ho_tro: str
    so_tien: int = Field(..., ge=0)
    ghi_chu: Optional[str] = None


class HoTroLuongImportRequest(BaseModel):
    thang: int = Field(..., ge=1, le=12)
    nam: int = Field(..., ge=2020, le=2099)
    rows: List[HoTroLuongImportRow]


class HoTroLuongImportResponse(BaseModel):
    imported_count: int
    total_rows: int
    errors: List[Dict[str, Any]] = []
