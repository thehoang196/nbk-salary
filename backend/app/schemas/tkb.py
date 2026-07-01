from datetime import date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class TKBImportRow(BaseModel):
    """Single row from unified TKB Excel import."""
    giao_vien: str = Field(..., description="Teacher code or name")
    mon_hoc: str = Field(..., description="Subject code or name")
    khoi: str = Field(..., description="Grade name (Khối 6, 7, 8, 9)")
    lop: str = Field(..., description="Class name")
    so_tiet: int = Field(..., ge=0)
    loai_tiet: str = Field(..., description="chinh_khoa, tnst_vy, k9_luyen_thi, kh_ta, ielts")


class TKBImportRequest(BaseModel):
    """Request for TKB import (after file parsing)."""
    thang: int = Field(..., ge=1, le=12)
    nam: int = Field(..., ge=2020, le=2099)
    rows: List[TKBImportRow]
    replace_existing: bool = False  # If true, replace existing TKB for this month


class TKBImportResponse(BaseModel):
    """Response after TKB import attempt."""
    imported_count: int
    total_rows: int
    errors: List[Dict[str, Any]] = []  # [{row: int, field: str, error: str}]
    summary: Optional[Dict[str, Any]] = None  # Period totals per teacher


class TKBResponse(BaseModel):
    id: int
    thang: int
    nam: int
    nhan_vien_id: int
    mon_hoc_id: int
    khoi_id: int
    lop_id: int
    so_tiet: int
    loai_tiet: str
    model_config = {"from_attributes": True}


class ThayDoiCreate(BaseModel):
    """Create a teacher substitution change record."""
    ngay: date
    tiet: int = Field(..., ge=1, le=10)
    lop_id: int
    mon_hoc_id: int
    gv_goc_id: int
    gv_thay_id: int
    ly_do: Optional[str] = Field(None, max_length=200)
    thang: int = Field(..., ge=1, le=12)
    nam: int = Field(..., ge=2020, le=2099)


class ThayDoiResponse(BaseModel):
    id: int
    ngay: date
    tiet: int
    lop_id: int
    mon_hoc_id: int
    gv_goc_id: int
    gv_thay_id: int
    ly_do: Optional[str] = None
    thang: int
    nam: int
    model_config = {"from_attributes": True}


class PhatSinhCreate(BaseModel):
    """Manual BCC adjustment entry."""
    nhan_vien_id: int
    thang: int = Field(..., ge=1, le=12)
    nam: int = Field(..., ge=2020, le=2099)
    loai: str = Field(..., description="Category: tiet_chinh, tnst_vy, k9_lt, kh_ta, ielts")
    so_tiet: float = Field(..., ge=-50.0, le=50.0)
    ly_do: str = Field(..., max_length=200)


class BCCTeacherRow(BaseModel):
    """One teacher's row in the BCC summary."""
    nhan_vien_id: int
    ho_ten: str
    theo_tkb: Dict[str, float]  # {k6: n, k7: n, k8: n, k9: n, gd_loi_song: n, tong_tiet_chinh: n, kh_ta: n, ielts: n}
    thay_doi: Dict[str, float]  # {nghi_k6_8: n, nghi_k9: n, nghi_kh_ta: n, nghi_ielts: n, thay_k6_8: n, thay_k9: n, thay_kh_ta: n, thay_ielts: n}
    phat_sinh: Dict[str, float]  # {tiet_chinh: n, tnst_vy: n, k9_lt: n, kh_ta: n, ielts: n}
    thuc_te: Dict[str, float]  # {tiet_chinh_hs1: n, tnst_vy: n, k9_lt: n, kh_ta: n, ielts: n, tong: n}
    is_complete: bool


class BCCResponse(BaseModel):
    """Full BCC summary for a month."""
    thang: int
    nam: int
    rows: List[BCCTeacherRow]
    total_teachers: int
    incomplete_count: int
