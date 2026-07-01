"""
NBK Salary API - Catalog (Danh mục) Router

Generic CRUD router handling all 9 danh mục types via a {loai} path parameter.
Maps each loai slug to the corresponding SQLAlchemy model and Pydantic schemas.
"""

from typing import Any, Dict, Optional, Tuple, Type

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.cham_cong import DlChamCong
from app.models.danh_muc import (
    DmDonGiaDay,
    DmDonVi,
    DmHeSoLuong,
    DmKhoi,
    DmKyHieuCong,
    DmLoaiHoTro,
    DmLoaiTietNgoai,
    DmLop,
    DmMonHoc,
    DmNhiemVu,
    DmViTri,
)
from app.models.hop_dong import DlHopDong
from app.models.nhan_vien import NhanVien
from app.models.tkb import DlTkb, DlThayDoiNguoiDay
from app.models.user import UserRole
from app.schemas.danh_muc import (
    DonViCreate,
    DonViResponse,
    DonViUpdate,
    HeSoLuongCreate,
    HeSoLuongResponse,
    KhoiCreate,
    KhoiResponse,
    KyHieuCongCreate,
    KyHieuCongResponse,
    LoaiHoTroCreate,
    LoaiHoTroResponse,
    LoaiTietNgoaiCreate,
    LoaiTietNgoaiResponse,
    LopCreate,
    LopResponse,
    MonHocCreate,
    MonHocResponse,
    MonHocUpdate,
    NhiemVuCreate,
    NhiemVuResponse,
    ViTriCreate,
    ViTriResponse,
)
from app.utils.dependencies import require_role

router = APIRouter()

# Mapping: loai slug → (Model, CreateSchema, UpdateSchema | None, ResponseSchema)
LOAI_MAP: Dict[str, Tuple[Any, Type[BaseModel], Optional[Type[BaseModel]], Type[BaseModel]]] = {
    "don-vi": (DmDonVi, DonViCreate, DonViUpdate, DonViResponse),
    "khoi": (DmKhoi, KhoiCreate, None, KhoiResponse),
    "lop": (DmLop, LopCreate, None, LopResponse),
    "mon-hoc": (DmMonHoc, MonHocCreate, MonHocUpdate, MonHocResponse),
    "vi-tri": (DmViTri, ViTriCreate, None, ViTriResponse),
    "he-so-luong": (DmHeSoLuong, HeSoLuongCreate, None, HeSoLuongResponse),
    "ky-hieu-cong": (DmKyHieuCong, KyHieuCongCreate, None, KyHieuCongResponse),
    "nhiem-vu": (DmNhiemVu, NhiemVuCreate, None, NhiemVuResponse),
    "loai-tiet-ngoai": (DmLoaiTietNgoai, LoaiTietNgoaiCreate, None, LoaiTietNgoaiResponse),
    "loai-ho-tro": (DmLoaiHoTro, LoaiHoTroCreate, None, LoaiHoTroResponse),
}

# Referential integrity map: loai → list of (Model, foreign_key_field) to check before deletion
REFERENCE_CHECK_MAP: Dict[str, list] = {
    "don-vi": [(NhanVien, "don_vi_id")],
    "khoi": [(DmLop, "khoi_id"), (DmDonGiaDay, "khoi_id"), (DlTkb, "khoi_id")],
    "lop": [(DlTkb, "lop_id"), (DlThayDoiNguoiDay, "lop_id")],
    "mon-hoc": [(DmDonGiaDay, "mon_hoc_id"), (DlTkb, "mon_hoc_id")],
    "ky-hieu-cong": [(DlChamCong, "ky_hieu_cong_id")],
    "he-so-luong": [(DlHopDong, "he_so_luong_id")],
    "loai-tiet-ngoai": [],
    "loai-ho-tro": [],
}


def _get_config(loai: str):
    """Resolve loai path param to (Model, CreateSchema, UpdateSchema, ResponseSchema).

    Raises 404 if loai is not recognized.
    """
    config = LOAI_MAP.get(loai)
    if config is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Loại danh mục '{loai}' không tồn tại",
        )
    return config


@router.get("/{loai}")
def list_items(
    loai: str,
    is_active: Optional[bool] = Query(None, description="Filter by is_active status"),
    db: Session = Depends(get_db),
):
    """List all items of a given catalog type.

    Optionally filter by is_active if the model supports it.
    """
    model, _, _, response_schema = _get_config(loai)

    query = db.query(model)

    # Apply is_active filter only if the model has the column and filter is provided
    if is_active is not None and hasattr(model, "is_active"):
        query = query.filter(model.is_active == is_active)

    items = query.all()
    return [response_schema.model_validate(item) for item in items]


@router.post("/{loai}", status_code=status.HTTP_201_CREATED)
def create_item(
    loai: str,
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    _current_user=Depends(require_role([UserRole.admin, UserRole.accountant])),
):
    """Create a new catalog item. Requires admin or accountant role."""
    model, create_schema, _, response_schema = _get_config(loai)

    # Validate payload against the create schema
    validated = create_schema(**payload)

    # Check for duplicate unique fields
    if hasattr(model, 'ten'):
        existing = db.query(model).filter(model.ten == validated.ten).first() if hasattr(validated, 'ten') else None
        if existing:
            raise HTTPException(status_code=409, detail=f"Đã tồn tại bản ghi với tên '{validated.ten}'")

    if hasattr(validated, 'ky_hieu'):
        existing = db.query(model).filter(model.ky_hieu == validated.ky_hieu).first()
        if existing:
            raise HTTPException(status_code=409, detail=f"Đã tồn tại ký hiệu công '{validated.ky_hieu}'")

    if hasattr(validated, 'ma_mon'):
        existing = db.query(model).filter(model.ma_mon == validated.ma_mon).first()
        if existing:
            raise HTTPException(status_code=409, detail=f"Đã tồn tại mã môn '{validated.ma_mon}'")

    # Create ORM instance
    item = model(**validated.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)

    return response_schema.model_validate(item)


@router.put("/{loai}/{id}")
def update_item(
    loai: str,
    id: int,
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    _current_user=Depends(require_role([UserRole.admin, UserRole.accountant])),
):
    """Update an existing catalog item. Requires admin or accountant role."""
    model, _, update_schema, response_schema = _get_config(loai)

    item = db.query(model).filter(model.id == id).first()
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy bản ghi với id={id}",
        )

    if update_schema is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Loại '{loai}' không hỗ trợ cập nhật",
        )

    # Validate and apply partial update
    validated = update_schema(**payload)
    update_data = validated.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)

    return response_schema.model_validate(item)


@router.delete("/{loai}/{id}")
def delete_item(
    loai: str,
    id: int,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role([UserRole.admin])),
):
    """Delete (soft-delete) a catalog item. Requires admin role.

    If the model has an is_active column, sets it to False (soft-delete).
    Otherwise, performs a hard delete.
    """
    model, _, _, response_schema = _get_config(loai)

    item = db.query(model).filter(model.id == id).first()
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy bản ghi với id={id}",
        )

    # Check referential integrity before deletion
    ref_checks = REFERENCE_CHECK_MAP.get(loai, [])
    for ref_model, ref_field in ref_checks:
        ref_count = db.query(ref_model).filter(getattr(ref_model, ref_field) == id).count()
        if ref_count > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Không thể xóa: bản ghi đang được sử dụng bởi {ref_model.__tablename__}",
            )

    # Soft-delete if model has is_active field, otherwise hard delete
    if hasattr(model, "is_active"):
        item.is_active = False
        db.commit()
        db.refresh(item)
        return response_schema.model_validate(item)
    else:
        db.delete(item)
        db.commit()
        return {"detail": "Đã xóa thành công"}
