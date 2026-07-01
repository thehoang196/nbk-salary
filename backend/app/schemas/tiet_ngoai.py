from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class TietNgoaiCreate(BaseModel):
    nhan_vien_id: int
    thang: int = Field(..., ge=1, le=12)
    nam: int = Field(..., ge=2020, le=2099)
    loai: str = Field(..., max_length=100, description="Type from dm_loai_tiet_ngoai")
    so_tiet: float = Field(..., gt=0, le=999.9)
    don_gia: int = Field(..., ge=0, le=999999999)
    he_so: float = Field(1.0, ge=0.1, le=9.9)
    ghi_chu: Optional[str] = Field(None, max_length=255)


class TietNgoaiUpdate(BaseModel):
    loai: Optional[str] = Field(None, max_length=100)
    so_tiet: Optional[float] = Field(None, gt=0, le=999.9)
    don_gia: Optional[int] = Field(None, ge=0, le=999999999)
    he_so: Optional[float] = Field(None, ge=0.1, le=9.9)
    ghi_chu: Optional[str] = Field(None, max_length=255)


class TietNgoaiResponse(BaseModel):
    id: int
    nhan_vien_id: int
    thang: int
    nam: int
    loai: str
    so_tiet: float
    don_gia: int
    he_so: float
    thanh_tien: Optional[int] = None  # Computed: so_tiet × don_gia × he_so
    ghi_chu: Optional[str] = None
    model_config = {"from_attributes": True}


class TietNgoaiImportRow(BaseModel):
    """Row for bulk import from Excel/CSV."""
    ma_nv: str  # Employee code for matching
    loai: str
    so_tiet: float = Field(..., gt=0)
    don_gia: int = Field(..., ge=0)
    he_so: float = Field(1.0, ge=0.1)
    ghi_chu: Optional[str] = None


class TietNgoaiImportRequest(BaseModel):
    thang: int = Field(..., ge=1, le=12)
    nam: int = Field(..., ge=2020, le=2099)
    rows: List[TietNgoaiImportRow]


class TietNgoaiImportResponse(BaseModel):
    imported_count: int
    total_rows: int
    errors: List[Dict[str, Any]] = []
