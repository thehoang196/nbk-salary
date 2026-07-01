"""
NBK Salary API - Hỗ trợ lương (Support Allowance) Router

Manage monthly support allowances per employee (ăn trưa, gửi xe, ChatGPT, etc.).
Supports single create, batch create, bulk import, update, and delete.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.danh_muc import DmLoaiHoTro
from app.models.ho_tro_luong import DlHoTroLuong
from app.models.nhan_vien import NhanVien
from app.models.user import UserRole
from app.schemas.ho_tro_luong import (
    HoTroLuongBatchCreate,
    HoTroLuongCreate,
    HoTroLuongImportRequest,
    HoTroLuongImportResponse,
    HoTroLuongResponse,
    HoTroLuongUpdate,
)
from app.utils.dependencies import get_current_user, require_role

router = APIRouter()

# Allowed roles for write operations
WRITE_ROLES = [UserRole.admin, UserRole.accountant]


def _validate_loai_ho_tro(loai_ho_tro: str, db: Session) -> None:
    """Validate that loai_ho_tro exists in dm_loai_ho_tro table by ten."""
    exists = db.query(DmLoaiHoTro).filter(DmLoaiHoTro.ten == loai_ho_tro).first()
    if not exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Loại hỗ trợ '{loai_ho_tro}' không tồn tại trong danh mục",
        )


def _validate_nhan_vien(nhan_vien_id: int, db: Session) -> None:
    """Validate that employee exists."""
    nv = db.query(NhanVien).filter(NhanVien.id == nhan_vien_id).first()
    if not nv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy nhân viên id={nhan_vien_id}",
        )


# =============================================================================
# Endpoints
# =============================================================================


@router.get("/{thang}/{nam}", response_model=List[HoTroLuongResponse])
def list_ho_tro_luong(
    thang: int,
    nam: int,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    """List all support allowances for a given month/year."""
    records = (
        db.query(DlHoTroLuong)
        .filter(DlHoTroLuong.thang == thang, DlHoTroLuong.nam == nam)
        .order_by(DlHoTroLuong.nhan_vien_id)
        .all()
    )
    return [HoTroLuongResponse.model_validate(r) for r in records]


@router.post("", response_model=HoTroLuongResponse, status_code=status.HTTP_201_CREATED)
def create_ho_tro_luong(
    payload: HoTroLuongCreate,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role(WRITE_ROLES)),
):
    """Add a single support allowance entry.

    Validates:
    - nhan_vien_id exists
    - loai_ho_tro is recognized in dm_loai_ho_tro
    """
    _validate_nhan_vien(payload.nhan_vien_id, db)
    _validate_loai_ho_tro(payload.loai_ho_tro, db)

    record = DlHoTroLuong(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)

    return HoTroLuongResponse.model_validate(record)


@router.post("/batch", response_model=List[HoTroLuongResponse], status_code=status.HTTP_201_CREATED)
def batch_create_ho_tro_luong(
    payload: HoTroLuongBatchCreate,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role(WRITE_ROLES)),
):
    """Batch create: one allowance type for multiple employees in one month.

    Validates all employee IDs and loai_ho_tro before creating.
    """
    _validate_loai_ho_tro(payload.loai_ho_tro, db)

    # Validate all employee IDs upfront
    for entry in payload.entries:
        nv = db.query(NhanVien).filter(NhanVien.id == entry.nhan_vien_id).first()
        if not nv:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Không tìm thấy nhân viên id={entry.nhan_vien_id}",
            )

    # Create all records
    records = []
    for entry in payload.entries:
        record = DlHoTroLuong(
            nhan_vien_id=entry.nhan_vien_id,
            thang=payload.thang,
            nam=payload.nam,
            loai_ho_tro=payload.loai_ho_tro,
            so_tien=entry.so_tien,
            ghi_chu=entry.ghi_chu,
        )
        db.add(record)
        records.append(record)

    db.commit()
    for r in records:
        db.refresh(r)

    return [HoTroLuongResponse.model_validate(r) for r in records]


@router.post("/import", response_model=HoTroLuongImportResponse)
def import_ho_tro_luong(
    payload: HoTroLuongImportRequest,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role(WRITE_ROLES)),
):
    """Bulk import support allowances from Excel/CSV data.

    Matches ma_nv to NhanVien, validates loai_ho_tro.
    Returns count of imported rows and any errors.
    """
    imported_count = 0
    errors = []

    for idx, row in enumerate(payload.rows):
        # Match ma_nv to employee
        nv = db.query(NhanVien).filter(NhanVien.ma_nv == row.ma_nv).first()
        if not nv:
            errors.append({
                "row": idx + 1,
                "ma_nv": row.ma_nv,
                "error": f"Không tìm thấy nhân viên với mã '{row.ma_nv}'",
            })
            continue

        # Validate loai_ho_tro
        loai = db.query(DmLoaiHoTro).filter(DmLoaiHoTro.ten == row.loai_ho_tro).first()
        if not loai:
            errors.append({
                "row": idx + 1,
                "ma_nv": row.ma_nv,
                "error": f"Loại hỗ trợ '{row.loai_ho_tro}' không tồn tại trong danh mục",
            })
            continue

        # Create record
        record = DlHoTroLuong(
            nhan_vien_id=nv.id,
            thang=payload.thang,
            nam=payload.nam,
            loai_ho_tro=row.loai_ho_tro,
            so_tien=row.so_tien,
            ghi_chu=row.ghi_chu,
        )
        db.add(record)
        imported_count += 1

    db.commit()

    return HoTroLuongImportResponse(
        imported_count=imported_count,
        total_rows=len(payload.rows),
        errors=errors,
    )


@router.put("/{id}", response_model=HoTroLuongResponse)
def update_ho_tro_luong(
    id: int,
    payload: HoTroLuongUpdate,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role(WRITE_ROLES)),
):
    """Update an existing support allowance entry."""
    record = db.query(DlHoTroLuong).filter(DlHoTroLuong.id == id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy hỗ trợ lương id={id}",
        )

    update_data = payload.model_dump(exclude_unset=True)

    # Validate loai_ho_tro if being updated
    if "loai_ho_tro" in update_data and update_data["loai_ho_tro"] is not None:
        _validate_loai_ho_tro(update_data["loai_ho_tro"], db)

    for field, value in update_data.items():
        setattr(record, field, value)

    db.commit()
    db.refresh(record)

    return HoTroLuongResponse.model_validate(record)


@router.delete("/{id}")
def delete_ho_tro_luong(
    id: int,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role(WRITE_ROLES)),
):
    """Delete a support allowance entry."""
    record = db.query(DlHoTroLuong).filter(DlHoTroLuong.id == id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy hỗ trợ lương id={id}",
        )

    db.delete(record)
    db.commit()

    return {"detail": f"Đã xóa hỗ trợ lương id={id}"}
