"""
NBK Salary API - Chấm công (Attendance) Router

Manages daily attendance records and monthly summaries for VP employees.
Supports Misa Excel import and manual entry.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.cham_cong import DlChamCong, DlTongHopCong
from app.models.danh_muc import DmKyHieuCong
from app.models.nhan_vien import NhanVien
from app.models.user import UserRole
from app.schemas.cham_cong import (
    ChamCongManualCreate,
    ChamCongResponse,
    MisaImportRequest,
    MisaImportResponse,
    TongHopCongResponse,
    TongHopCongUpdate,
)
from app.services.misa_import_service import MisaImportService
from app.utils.dependencies import get_current_user, require_role

router = APIRouter()

# Allowed roles for write operations
WRITE_ROLES = [UserRole.admin, UserRole.accountant]


# =============================================================================
# Misa Import Endpoint
# =============================================================================


@router.post("/import-misa", response_model=MisaImportResponse)
def import_misa(
    payload: MisaImportRequest,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role(WRITE_ROLES)),
):
    """Import VP attendance data from Misa Excel export.

    Accepts parsed rows and uses MisaImportService to process.
    Returns counts and any row-level errors.
    """
    service = MisaImportService(db)
    rows_data = [row.model_dump() for row in payload.rows]
    imported_count, errors = service.import_attendance(
        thang=payload.thang,
        nam=payload.nam,
        rows=rows_data,
    )

    return MisaImportResponse(
        imported_count=imported_count,
        total_rows=len(payload.rows),
        errors=errors,
    )


# =============================================================================
# Attendance Summary (Tổng hợp công)
# =============================================================================


@router.get("/tong-hop/{thang}/{nam}", response_model=List[TongHopCongResponse])
def get_tong_hop_cong(
    thang: int,
    nam: int,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    """Get monthly attendance summary for all employees.

    Returns list of TongHopCongResponse, including is_confirmed flag
    to identify incomplete records.
    """
    if thang < 1 or thang > 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tháng phải từ 1 đến 12",
        )

    records = (
        db.query(DlTongHopCong)
        .filter(DlTongHopCong.thang == thang, DlTongHopCong.nam == nam)
        .order_by(DlTongHopCong.nhan_vien_id)
        .all()
    )

    return [TongHopCongResponse.model_validate(r) for r in records]


# =============================================================================
# Daily Attendance Records (Chấm công hàng ngày)
# =============================================================================


@router.get("/{thang}/{nam}", response_model=List[ChamCongResponse])
def list_cham_cong(
    thang: int,
    nam: int,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    """List all daily attendance records for a given month/year.

    Filters dl_cham_cong where ngay falls within the specified month.
    """
    if thang < 1 or thang > 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tháng phải từ 1 đến 12",
        )

    from sqlalchemy import extract

    records = (
        db.query(DlChamCong)
        .filter(
            extract("month", DlChamCong.ngay) == thang,
            extract("year", DlChamCong.ngay) == nam,
        )
        .order_by(DlChamCong.nhan_vien_id, DlChamCong.ngay)
        .all()
    )

    return [ChamCongResponse.model_validate(r) for r in records]


@router.post("", response_model=ChamCongResponse, status_code=status.HTTP_201_CREATED)
def create_cham_cong(
    payload: ChamCongManualCreate,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role(WRITE_ROLES)),
):
    """Create a manual single attendance entry.

    Validations:
    - nhan_vien_id must reference an existing employee
    - ky_hieu_cong_id must reference dm_ky_hieu_cong
    - Unique constraint on (nhan_vien_id, ngay) - upsert behavior
    """
    # Validate employee exists
    nhan_vien = db.query(NhanVien).filter(NhanVien.id == payload.nhan_vien_id).first()
    if not nhan_vien:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy nhân viên id={payload.nhan_vien_id}",
        )

    # Validate ky_hieu_cong exists
    ky_hieu = db.query(DmKyHieuCong).filter(DmKyHieuCong.id == payload.ky_hieu_cong_id).first()
    if not ky_hieu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy ký hiệu công id={payload.ky_hieu_cong_id}",
        )

    # Check unique constraint - upsert behavior
    existing = (
        db.query(DlChamCong)
        .filter(
            DlChamCong.nhan_vien_id == payload.nhan_vien_id,
            DlChamCong.ngay == payload.ngay,
        )
        .first()
    )

    if existing:
        # Upsert: update existing record
        existing.ky_hieu_cong_id = payload.ky_hieu_cong_id
        existing.ghi_chu = payload.ghi_chu
        db.commit()
        db.refresh(existing)
        return ChamCongResponse.model_validate(existing)

    # Create new record
    record = DlChamCong(
        nhan_vien_id=payload.nhan_vien_id,
        ngay=payload.ngay,
        ky_hieu_cong_id=payload.ky_hieu_cong_id,
        ghi_chu=payload.ghi_chu,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return ChamCongResponse.model_validate(record)


@router.put("/{id}", response_model=ChamCongResponse)
def update_cham_cong(
    id: int,
    payload: ChamCongManualCreate,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role(WRITE_ROLES)),
):
    """Update an existing attendance record by ID.

    Validations:
    - Record must exist (404 if not)
    - ky_hieu_cong_id must reference dm_ky_hieu_cong
    - nhan_vien_id must reference an existing employee
    - Unique constraint on (nhan_vien_id, ngay) enforced
    """
    record = db.query(DlChamCong).filter(DlChamCong.id == id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy bản ghi chấm công id={id}",
        )

    # Validate employee exists
    nhan_vien = db.query(NhanVien).filter(NhanVien.id == payload.nhan_vien_id).first()
    if not nhan_vien:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy nhân viên id={payload.nhan_vien_id}",
        )

    # Validate ky_hieu_cong exists
    ky_hieu = db.query(DmKyHieuCong).filter(DmKyHieuCong.id == payload.ky_hieu_cong_id).first()
    if not ky_hieu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy ký hiệu công id={payload.ky_hieu_cong_id}",
        )

    # Check unique constraint if nhan_vien_id or ngay changed
    if payload.nhan_vien_id != record.nhan_vien_id or payload.ngay != record.ngay:
        conflict = (
            db.query(DlChamCong)
            .filter(
                DlChamCong.nhan_vien_id == payload.nhan_vien_id,
                DlChamCong.ngay == payload.ngay,
                DlChamCong.id != id,
            )
            .first()
        )
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Đã tồn tại bản ghi chấm công cho nhân viên id={payload.nhan_vien_id} ngày {payload.ngay}",
            )

    # Apply updates
    record.nhan_vien_id = payload.nhan_vien_id
    record.ngay = payload.ngay
    record.ky_hieu_cong_id = payload.ky_hieu_cong_id
    record.ghi_chu = payload.ghi_chu

    db.commit()
    db.refresh(record)

    return ChamCongResponse.model_validate(record)



# =============================================================================
# Update Attendance Summary (Tổng hợp công - editable grid)
# =============================================================================


@router.put("/tong-hop/{id}", response_model=TongHopCongResponse)
def update_tong_hop_cong(
    id: int,
    payload: TongHopCongUpdate,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role(WRITE_ROLES)),
):
    """Update an attendance summary record (for manual edit in grid).

    Allows editing ngay_cong, ngay_nghi, ngay_phep, lam_them.
    Validates record exists.
    """
    record = db.query(DlTongHopCong).filter(DlTongHopCong.id == id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy bản ghi tổng hợp công id={id}",
        )

    record.ngay_cong = payload.ngay_cong
    record.ngay_nghi = payload.ngay_nghi
    record.ngay_phep = payload.ngay_phep
    record.lam_them = payload.lam_them

    if payload.is_confirmed is not None:
        record.is_confirmed = payload.is_confirmed

    db.commit()
    db.refresh(record)

    return TongHopCongResponse.model_validate(record)
