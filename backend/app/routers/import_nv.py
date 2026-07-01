"""
NBK Salary - Employee Import Router.

Provides a bulk import endpoint for employees via JSON body (parsed rows).
All-or-nothing: if any row fails validation, no records are inserted.
"""

from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.chuc_danh import DmChucVu, DmCapBacQL
from app.models.danh_muc import DmDonVi
from app.models.nhan_vien import NhanVien, NhomNV
from app.models.user import User, UserRole
from app.utils.dependencies import require_role

router = APIRouter()


# --- Schemas ---

class NhanVienImportRow(BaseModel):
    ma_nv: str
    ho_ten: str
    nhom_nv: str  # "GV" or "VP"
    don_vi: Optional[str] = None  # Department name for matching
    chuc_vu: Optional[str] = None  # Chức vụ ma for matching
    cap_bac_ql: Optional[str] = None  # Cấp bậc QL ma for matching
    ten_goi: Optional[str] = None
    email: Optional[str] = None
    sdt: Optional[str] = None


class NhanVienImportRequest(BaseModel):
    rows: List[NhanVienImportRow]


class NhanVienImportResponse(BaseModel):
    imported_count: int
    total_rows: int
    errors: List[Dict[str, Any]] = []


# --- Endpoint ---

@router.post(
    "/import",
    response_model=NhanVienImportResponse,
    status_code=status.HTTP_200_OK,
)
def import_nhan_vien(
    payload: NhanVienImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role([UserRole.admin, UserRole.accountant, UserRole.hr])
    ),
):
    """Bulk import employees from parsed rows (JSON body).

    All-or-nothing: if any row has validation errors, nothing is inserted.
    Returns per-row errors (up to 100).
    """
    errors: List[Dict[str, Any]] = []
    rows = payload.rows

    # --- Pre-fetch lookup tables ---
    don_vi_map: Dict[str, int] = {
        dv.ten.strip().lower(): dv.id
        for dv in db.query(DmDonVi).filter(DmDonVi.is_active == True).all()
    }
    chuc_vu_map: Dict[str, int] = {
        cv.ma.strip().lower(): cv.id
        for cv in db.query(DmChucVu).filter(DmChucVu.is_active == True).all()
    }
    cap_bac_map: Dict[str, int] = {
        cb.ma.strip().lower(): cb.id
        for cb in db.query(DmCapBacQL).filter(DmCapBacQL.is_active == True).all()
    }

    # --- Check for duplicates within the file ---
    seen_ma_nv: Dict[str, int] = {}  # ma_nv -> first row index
    for idx, row in enumerate(rows):
        ma_lower = row.ma_nv.strip().lower()
        if ma_lower in seen_ma_nv:
            errors.append({
                "row": idx + 1,
                "ma_nv": row.ma_nv,
                "error": f"Trùng mã NV trong file (trùng với dòng {seen_ma_nv[ma_lower] + 1})",
            })
        else:
            seen_ma_nv[ma_lower] = idx

    # --- Check for duplicates against DB ---
    existing_ma_nvs = {
        nv.ma_nv.strip().lower()
        for nv in db.query(NhanVien.ma_nv).all()
    }

    # --- Validate each row ---
    valid_employees: List[NhanVien] = []

    for idx, row in enumerate(rows):
        row_errors: List[str] = []
        ma_nv_stripped = row.ma_nv.strip()

        # Check empty ma_nv
        if not ma_nv_stripped:
            row_errors.append("Mã NV không được để trống")

        # Check duplicate against DB
        if ma_nv_stripped.lower() in existing_ma_nvs:
            row_errors.append(f"Mã NV '{ma_nv_stripped}' đã tồn tại trong hệ thống")

        # Validate nhom_nv
        nhom_nv_value = row.nhom_nv.strip().upper()
        if nhom_nv_value not in ("GV", "VP"):
            row_errors.append(f"Nhóm NV phải là 'GV' hoặc 'VP', nhận được: '{row.nhom_nv}'")

        # Match don_vi by name
        don_vi_id: Optional[int] = None
        if row.don_vi:
            don_vi_key = row.don_vi.strip().lower()
            don_vi_id = don_vi_map.get(don_vi_key)
            if don_vi_id is None:
                row_errors.append(f"Không tìm thấy đơn vị: '{row.don_vi}'")

        # Match chuc_vu by ma
        chuc_vu_id: Optional[int] = None
        if row.chuc_vu:
            chuc_vu_key = row.chuc_vu.strip().lower()
            chuc_vu_id = chuc_vu_map.get(chuc_vu_key)
            if chuc_vu_id is None:
                row_errors.append(f"Không tìm thấy chức vụ: '{row.chuc_vu}'")

        # Match cap_bac_ql by ma
        cap_bac_ql_id: Optional[int] = None
        if row.cap_bac_ql:
            cap_bac_key = row.cap_bac_ql.strip().lower()
            cap_bac_ql_id = cap_bac_map.get(cap_bac_key)
            if cap_bac_ql_id is None:
                row_errors.append(f"Không tìm thấy cấp bậc QL: '{row.cap_bac_ql}'")

        # If VP, set ten_goi = None
        ten_goi = row.ten_goi
        if nhom_nv_value == "VP":
            ten_goi = None

        # Collect errors for this row
        if row_errors:
            errors.append({
                "row": idx + 1,
                "ma_nv": row.ma_nv,
                "errors": row_errors,
            })
            # Cap errors at 100
            if len(errors) >= 100:
                break
        else:
            # Build NhanVien entity (only if no row-level errors)
            nv = NhanVien(
                ma_nv=ma_nv_stripped,
                ho_ten=row.ho_ten.strip(),
                nhom_nv=NhomNV(nhom_nv_value),
                don_vi_id=don_vi_id,
                chuc_vu_id=chuc_vu_id,
                cap_bac_ql_id=cap_bac_ql_id,
                ten_goi=ten_goi.strip() if ten_goi else None,
                email=row.email.strip() if row.email else None,
                sdt=row.sdt.strip() if row.sdt else None,
            )
            valid_employees.append(nv)

    # --- All-or-nothing insertion ---
    if errors:
        return NhanVienImportResponse(
            imported_count=0,
            total_rows=len(rows),
            errors=errors,
        )

    # Insert all valid employees
    for nv in valid_employees:
        db.add(nv)
    db.commit()

    return NhanVienImportResponse(
        imported_count=len(valid_employees),
        total_rows=len(rows),
        errors=[],
    )
