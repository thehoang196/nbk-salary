"""
NBK Salary API - Đơn giá dạy (Teaching Unit Price) Router

Specialized CRUD for dm_don_gia_day with history tracking.
Business rules:
- Unique active price per Teacher×Subject×Grade combination
- Updates deactivate the old record and create a new one (preserving history)
- Soft-delete sets is_active=False and ngay_ket_thuc=today
"""

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.danh_muc import DmDonGiaDay
from app.models.user import UserRole
from app.schemas.danh_muc import DonGiaDayCreate, DonGiaDayResponse, DonGiaDayUpdate
from app.utils.dependencies import require_role

router = APIRouter()


@router.get("/", response_model=List[DonGiaDayResponse])
def list_don_gia_day(
    nhan_vien_id: Optional[int] = Query(None, description="Filter by teacher ID"),
    mon_hoc_id: Optional[int] = Query(None, description="Filter by subject ID"),
    khoi_id: Optional[int] = Query(None, description="Filter by grade ID"),
    db: Session = Depends(get_db),
):
    """List all active teaching unit prices with optional filters."""
    query = db.query(DmDonGiaDay).filter(DmDonGiaDay.is_active == True)

    if nhan_vien_id is not None:
        query = query.filter(DmDonGiaDay.nhan_vien_id == nhan_vien_id)
    if mon_hoc_id is not None:
        query = query.filter(DmDonGiaDay.mon_hoc_id == mon_hoc_id)
    if khoi_id is not None:
        query = query.filter(DmDonGiaDay.khoi_id == khoi_id)

    return query.all()


@router.get("/history/{nhan_vien_id}", response_model=List[DonGiaDayResponse])
def get_history(
    nhan_vien_id: int,
    db: Session = Depends(get_db),
):
    """Get price history for a teacher (all records including inactive)."""
    records = (
        db.query(DmDonGiaDay)
        .filter(DmDonGiaDay.nhan_vien_id == nhan_vien_id)
        .order_by(DmDonGiaDay.ngay_bat_dau.desc())
        .all()
    )
    return records


@router.get("/{id}", response_model=DonGiaDayResponse)
def get_don_gia_day(
    id: int,
    db: Session = Depends(get_db),
):
    """Get a single price record by ID."""
    item = db.query(DmDonGiaDay).filter(DmDonGiaDay.id == id).first()
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy đơn giá dạy với id={id}",
        )
    return item


@router.post("/", response_model=DonGiaDayResponse, status_code=status.HTTP_201_CREATED)
def create_don_gia_day(
    payload: DonGiaDayCreate,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role([UserRole.admin, UserRole.accountant])),
):
    """Create a new teaching unit price.

    Validates that no other active price exists for the same
    (nhan_vien_id, mon_hoc_id, khoi_id) combination.
    Returns 409 Conflict if a duplicate active record exists.
    """
    existing = (
        db.query(DmDonGiaDay)
        .filter(
            DmDonGiaDay.nhan_vien_id == payload.nhan_vien_id,
            DmDonGiaDay.mon_hoc_id == payload.mon_hoc_id,
            DmDonGiaDay.khoi_id == payload.khoi_id,
            DmDonGiaDay.is_active == True,
        )
        .first()
    )

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Đã tồn tại đơn giá đang hoạt động cho "
                f"nhân viên={payload.nhan_vien_id}, "
                f"môn học={payload.mon_hoc_id}, "
                f"khối={payload.khoi_id}"
            ),
        )

    item = DmDonGiaDay(**payload.model_dump(), is_active=True)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{id}", response_model=DonGiaDayResponse)
def update_don_gia_day(
    id: int,
    payload: DonGiaDayUpdate,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role([UserRole.admin, UserRole.accountant])),
):
    """Update a teaching unit price with history tracking.

    Deactivates the current record (is_active=False, ngay_ket_thuc=today)
    and creates a new active record with the updated don_gia.
    This preserves the price history.
    """
    current = db.query(DmDonGiaDay).filter(DmDonGiaDay.id == id).first()
    if current is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy đơn giá dạy với id={id}",
        )

    if not current.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể cập nhật bản ghi đã bị vô hiệu hóa",
        )

    today = date.today()

    # Deactivate the current record
    current.is_active = False
    current.ngay_ket_thuc = today

    # Determine the new don_gia value
    new_don_gia = payload.don_gia if payload.don_gia is not None else current.don_gia

    # Create a new active record
    new_record = DmDonGiaDay(
        nhan_vien_id=current.nhan_vien_id,
        mon_hoc_id=current.mon_hoc_id,
        khoi_id=current.khoi_id,
        don_gia=new_don_gia,
        ngay_bat_dau=today,
        ngay_ket_thuc=payload.ngay_ket_thuc,
        is_active=True,
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record


@router.delete("/{id}", response_model=DonGiaDayResponse)
def delete_don_gia_day(
    id: int,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role([UserRole.admin, UserRole.accountant])),
):
    """Soft-delete a teaching unit price (set is_active=False, ngay_ket_thuc=today)."""
    item = db.query(DmDonGiaDay).filter(DmDonGiaDay.id == id).first()
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy đơn giá dạy với id={id}",
        )

    if not item.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bản ghi đã bị vô hiệu hóa trước đó",
        )

    item.is_active = False
    item.ngay_ket_thuc = date.today()
    db.commit()
    db.refresh(item)
    return item
