"""
NBK Salary API - Tiết dạy ngoài (External Teaching Periods) Router

CRUD and bulk import for external teaching period entries.
Auto-computes thanh_tien = so_tiet × don_gia × he_so on create/update.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.danh_muc import DmLoaiTietNgoai
from app.models.nhan_vien import NhanVien
from app.models.tkb import DlTietDayNgoai
from app.models.user import UserRole
from app.schemas.tiet_ngoai import (
    TietNgoaiCreate,
    TietNgoaiImportRequest,
    TietNgoaiImportResponse,
    TietNgoaiResponse,
    TietNgoaiUpdate,
)
from app.utils.dependencies import get_current_user, require_role

router = APIRouter()

# Allowed roles for write operations
WRITE_ROLES = [UserRole.admin, UserRole.accountant]


def _compute_thanh_tien(so_tiet: float, don_gia: int, he_so: float) -> int:
    """Compute thanh_tien = int(so_tiet × don_gia × he_so)."""
    return int(so_tiet * don_gia * he_so)


def _validate_loai(loai: str, db: Session) -> None:
    """Validate that loai matches an active entry in dm_loai_tiet_ngoai."""
    exists = (
        db.query(DmLoaiTietNgoai)
        .filter(DmLoaiTietNgoai.ten == loai, DmLoaiTietNgoai.is_active == True)
        .first()
    )
    if not exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Loại tiết ngoài '{loai}' không hợp lệ hoặc không tồn tại trong danh mục",
        )


# =============================================================================
# Endpoints
# =============================================================================


@router.get("/{thang}/{nam}", response_model=List[TietNgoaiResponse])
def list_tiet_ngoai(
    thang: int,
    nam: int,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    """List all external periods for a given month/year (all teachers)."""
    records = (
        db.query(DlTietDayNgoai)
        .filter(DlTietDayNgoai.thang == thang, DlTietDayNgoai.nam == nam)
        .order_by(DlTietDayNgoai.nhan_vien_id, DlTietDayNgoai.loai)
        .all()
    )
    return [TietNgoaiResponse.model_validate(r) for r in records]


@router.post("", response_model=TietNgoaiResponse, status_code=status.HTTP_201_CREATED)
def create_tiet_ngoai(
    payload: TietNgoaiCreate,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role(WRITE_ROLES)),
):
    """Add a single external period entry.

    Validations:
    - nhan_vien_id must reference an existing employee
    - loai must match an active entry in dm_loai_tiet_ngoai
    Auto-computes thanh_tien = int(so_tiet × don_gia × he_so)
    """
    # Validate employee exists
    nhan_vien = db.query(NhanVien).filter(NhanVien.id == payload.nhan_vien_id).first()
    if not nhan_vien:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy nhân viên id={payload.nhan_vien_id}",
        )

    # Validate loai
    _validate_loai(payload.loai, db)

    # Compute thanh_tien
    thanh_tien = _compute_thanh_tien(payload.so_tiet, payload.don_gia, payload.he_so)

    record = DlTietDayNgoai(
        **payload.model_dump(),
        thanh_tien=thanh_tien,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return TietNgoaiResponse.model_validate(record)


@router.put("/{id}", response_model=TietNgoaiResponse)
def update_tiet_ngoai(
    id: int,
    payload: TietNgoaiUpdate,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role(WRITE_ROLES)),
):
    """Update an external period entry (recomputes thanh_tien)."""
    record = db.query(DlTietDayNgoai).filter(DlTietDayNgoai.id == id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy tiết dạy ngoài id={id}",
        )

    update_data = payload.model_dump(exclude_unset=True)

    # Validate loai if being updated
    if "loai" in update_data and update_data["loai"] is not None:
        _validate_loai(update_data["loai"], db)

    # Apply updates
    for field, value in update_data.items():
        setattr(record, field, value)

    # Recompute thanh_tien with current values
    record.thanh_tien = _compute_thanh_tien(
        float(record.so_tiet), int(record.don_gia), float(record.he_so)
    )

    db.commit()
    db.refresh(record)

    return TietNgoaiResponse.model_validate(record)


@router.delete("/{id}")
def delete_tiet_ngoai(
    id: int,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role(WRITE_ROLES)),
):
    """Delete an external period entry."""
    record = db.query(DlTietDayNgoai).filter(DlTietDayNgoai.id == id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy tiết dạy ngoài id={id}",
        )

    db.delete(record)
    db.commit()

    return {"detail": f"Đã xóa tiết dạy ngoài id={id}"}


@router.post("/import", response_model=TietNgoaiImportResponse)
def import_tiet_ngoai(
    payload: TietNgoaiImportRequest,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role(WRITE_ROLES)),
):
    """Bulk import external periods from parsed data.

    For each row:
    - Match ma_nv to NhanVien
    - Validate loai against dm_loai_tiet_ngoai
    - Compute thanh_tien
    Returns counts and errors for rows that could not be imported.
    """
    imported_count = 0
    errors = []

    for idx, row in enumerate(payload.rows):
        # Match ma_nv to employee
        nhan_vien = db.query(NhanVien).filter(NhanVien.ma_nv == row.ma_nv).first()
        if not nhan_vien:
            errors.append({
                "row": idx + 1,
                "ma_nv": row.ma_nv,
                "error": f"Không tìm thấy nhân viên với mã '{row.ma_nv}'",
            })
            continue

        # Validate loai
        loai_valid = (
            db.query(DmLoaiTietNgoai)
            .filter(DmLoaiTietNgoai.ten == row.loai, DmLoaiTietNgoai.is_active == True)
            .first()
        )
        if not loai_valid:
            errors.append({
                "row": idx + 1,
                "ma_nv": row.ma_nv,
                "error": f"Loại tiết ngoài '{row.loai}' không hợp lệ",
            })
            continue

        # Compute thanh_tien and create record
        thanh_tien = _compute_thanh_tien(row.so_tiet, row.don_gia, row.he_so)

        record = DlTietDayNgoai(
            thang=payload.thang,
            nam=payload.nam,
            nhan_vien_id=nhan_vien.id,
            loai=row.loai,
            so_tiet=row.so_tiet,
            don_gia=row.don_gia,
            he_so=row.he_so,
            thanh_tien=thanh_tien,
            ghi_chu=row.ghi_chu,
        )
        db.add(record)
        imported_count += 1

    # Commit all successful records
    if imported_count > 0:
        db.commit()

    return TietNgoaiImportResponse(
        imported_count=imported_count,
        total_rows=len(payload.rows),
        errors=errors,
    )
