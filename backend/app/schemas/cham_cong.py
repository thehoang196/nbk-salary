from datetime import date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class MisaImportRow(BaseModel):
    """Single row from Misa Excel export for VP attendance."""
    ma_nv: Optional[str] = None  # Employee code (for matching)
    ho_ten: Optional[str] = None  # Employee name (alternative matching)
    ngay_cong: float = Field(..., ge=0, le=31)
    ngay_nghi: float = Field(0, ge=0, le=31)
    ngay_phep: float = Field(0, ge=0, le=31)
    lam_them: float = Field(0, ge=0, le=31)


class MisaImportRequest(BaseModel):
    """Request body for Misa attendance import."""
    thang: int = Field(..., ge=1, le=12)
    nam: int = Field(..., ge=2020, le=2099)
    rows: List[MisaImportRow]


class MisaImportResponse(BaseModel):
    """Response after Misa import attempt."""
    imported_count: int
    total_rows: int
    errors: List[Dict[str, Any]] = []  # [{row: int, error: str, ma_nv: str}]


class ChamCongManualCreate(BaseModel):
    """Manual single attendance record entry."""
    nhan_vien_id: int
    ngay: date
    ky_hieu_cong_id: int
    ghi_chu: Optional[str] = Field(None, max_length=255)


class ChamCongResponse(BaseModel):
    id: int
    nhan_vien_id: int
    ngay: date
    ky_hieu_cong_id: int
    ghi_chu: Optional[str] = None
    model_config = {"from_attributes": True}


class TongHopCongResponse(BaseModel):
    """Monthly attendance summary per employee."""
    id: int
    nhan_vien_id: int
    thang: int
    nam: int
    ngay_cong: float
    ngay_nghi: float
    ngay_phep: float
    lam_them: float
    cong_chuan: int
    is_confirmed: bool
    model_config = {"from_attributes": True}


class ChamCongBatchEntry(BaseModel):
    """Single entry in a batch attendance update."""
    nhan_vien_id: int
    ngay: date
    ky_hieu_cong_id: int
    ghi_chu: Optional[str] = None


class ChamCongBatchRequest(BaseModel):
    """Batch attendance entry request."""
    entries: List[ChamCongBatchEntry]


class TongHopCongUpdate(BaseModel):
    """Update attendance summary fields (editable grid)."""
    ngay_cong: float = Field(..., ge=0, le=31)
    ngay_nghi: float = Field(0, ge=0, le=31)
    ngay_phep: float = Field(0, ge=0, le=31)
    lam_them: float = Field(0, ge=0, le=31)
    is_confirmed: Optional[bool] = None
