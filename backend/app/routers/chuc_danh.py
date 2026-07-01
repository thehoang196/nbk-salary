"""
NBK Salary API - Chức danh Router (Position Titles & Related)

Dedicated CRUD endpoints for 4 position-related catalog entities:
- Chức Vụ (Position Titles)
- Cấp Bậc QL (Management Levels)
- Nghiệp Vụ (Professional Duties)
- Kiêm Nhiệm (Concurrent Roles)
"""

from typing import Any, List, Optional, Type

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.chuc_danh import DmCapBacQL, DmChucVu, DmKiemNhiem, DmNghiepVu, NvKiemNhiem, NvNghiepVu
from app.models.nhan_vien import NhanVien
from app.models.user import UserRole
from app.schemas.chuc_danh import (
    CapBacQLCreate,
    CapBacQLResponse,
    CapBacQLUpdate,
    ChucVuCreate,
    ChucVuResponse,
    ChucVuUpdate,
    KiemNhiemCreate,
    KiemNhiemResponse,
    KiemNhiemUpdate,
    NghiepVuCreate,
    NghiepVuResponse,
    NghiepVuUpdate,
)
from app.utils.dependencies import require_role

router = APIRouter()


# =============================================================================
# Helper functions to reduce repetition
# =============================================================================

def _list_items(
    db: Session,
    model: Any,
    response_schema: Type[BaseModel],
    is_active: Optional[bool] = None,
) -> list:
    """List all items with optional is_active filter."""
    query = db.query(model)
    if is_active is not None:
        query = query.filter(model.is_active == is_active)
    items = query.all()
    return [response_schema.model_validate(item) for item in items]


def _create_item(
    db: Session,
    model: Any,
    create_schema: Type[BaseModel],
    response_schema: Type[BaseModel],
    payload: BaseModel,
) -> BaseModel:
    """Create a new item with unique 'ma' validation."""
    # Validate unique ma
    existing = db.query(model).filter(model.ma == payload.ma).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Đã tồn tại bản ghi với mã '{payload.ma}'",
        )

    item = model(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return response_schema.model_validate(item)


def _update_item(
    db: Session,
    model: Any,
    response_schema: Type[BaseModel],
    item_id: int,
    payload: BaseModel,
) -> BaseModel:
    """Update an existing item by ID. Validates unique ma if changed."""
    item = db.query(model).filter(model.id == item_id).first()
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy bản ghi với id={item_id}",
        )

    update_data = payload.model_dump(exclude_unset=True)

    # If updating ma, check for uniqueness
    if "ma" in update_data and update_data["ma"] is not None:
        existing = db.query(model).filter(
            model.ma == update_data["ma"],
            model.id != item_id,
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Đã tồn tại bản ghi với mã '{update_data['ma']}'",
            )

    for field, value in update_data.items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return response_schema.model_validate(item)


def _delete_item(
    db: Session,
    model: Any,
    response_schema: Type[BaseModel],
    item_id: int,
    ref_checks: List[tuple],
) -> BaseModel:
    """Soft-delete an item (set is_active=False) after checking referential integrity."""
    item = db.query(model).filter(model.id == item_id).first()
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy bản ghi với id={item_id}",
        )

    # Check referential integrity
    for ref_model, ref_field in ref_checks:
        ref_count = db.query(ref_model).filter(getattr(ref_model, ref_field) == item_id).count()
        if ref_count > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Không thể xóa: bản ghi đang được sử dụng bởi {ref_model.__tablename__}",
            )

    item.is_active = False
    db.commit()
    db.refresh(item)
    return response_schema.model_validate(item)


# =============================================================================
# Chức Vụ (Position Titles)
# =============================================================================

@router.get("/chuc-vu", response_model=List[ChucVuResponse])
def list_chuc_vu(
    is_active: Optional[bool] = Query(None, description="Lọc theo trạng thái hoạt động"),
    db: Session = Depends(get_db),
):
    """Danh sách tất cả Chức vụ."""
    return _list_items(db, DmChucVu, ChucVuResponse, is_active)


@router.post("/chuc-vu", response_model=ChucVuResponse, status_code=status.HTTP_201_CREATED)
def create_chuc_vu(
    payload: ChucVuCreate,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role([UserRole.admin, UserRole.accountant])),
):
    """Tạo mới Chức vụ. Yêu cầu quyền admin hoặc accountant."""
    return _create_item(db, DmChucVu, ChucVuCreate, ChucVuResponse, payload)


@router.put("/chuc-vu/{id}", response_model=ChucVuResponse)
def update_chuc_vu(
    id: int,
    payload: ChucVuUpdate,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role([UserRole.admin, UserRole.accountant])),
):
    """Cập nhật Chức vụ. Yêu cầu quyền admin hoặc accountant."""
    return _update_item(db, DmChucVu, ChucVuResponse, id, payload)


@router.delete("/chuc-vu/{id}", response_model=ChucVuResponse)
def delete_chuc_vu(
    id: int,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role([UserRole.admin, UserRole.accountant])),
):
    """Xóa mềm Chức vụ (is_active=False). Kiểm tra ràng buộc NhanVien.chuc_vu_id."""
    return _delete_item(db, DmChucVu, ChucVuResponse, id, [(NhanVien, "chuc_vu_id")])


# =============================================================================
# Cấp Bậc QL (Management Levels)
# =============================================================================

@router.get("/cap-bac-ql", response_model=List[CapBacQLResponse])
def list_cap_bac_ql(
    is_active: Optional[bool] = Query(None, description="Lọc theo trạng thái hoạt động"),
    db: Session = Depends(get_db),
):
    """Danh sách tất cả Cấp bậc quản lý."""
    return _list_items(db, DmCapBacQL, CapBacQLResponse, is_active)


@router.post("/cap-bac-ql", response_model=CapBacQLResponse, status_code=status.HTTP_201_CREATED)
def create_cap_bac_ql(
    payload: CapBacQLCreate,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role([UserRole.admin, UserRole.accountant])),
):
    """Tạo mới Cấp bậc quản lý. Yêu cầu quyền admin hoặc accountant."""
    return _create_item(db, DmCapBacQL, CapBacQLCreate, CapBacQLResponse, payload)


@router.put("/cap-bac-ql/{id}", response_model=CapBacQLResponse)
def update_cap_bac_ql(
    id: int,
    payload: CapBacQLUpdate,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role([UserRole.admin, UserRole.accountant])),
):
    """Cập nhật Cấp bậc quản lý. Yêu cầu quyền admin hoặc accountant."""
    return _update_item(db, DmCapBacQL, CapBacQLResponse, id, payload)


@router.delete("/cap-bac-ql/{id}", response_model=CapBacQLResponse)
def delete_cap_bac_ql(
    id: int,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role([UserRole.admin, UserRole.accountant])),
):
    """Xóa mềm Cấp bậc QL (is_active=False). Kiểm tra ràng buộc NhanVien.cap_bac_ql_id."""
    return _delete_item(db, DmCapBacQL, CapBacQLResponse, id, [(NhanVien, "cap_bac_ql_id")])


# =============================================================================
# Nghiệp Vụ (Professional Duties)
# =============================================================================

@router.get("/nghiep-vu", response_model=List[NghiepVuResponse])
def list_nghiep_vu(
    is_active: Optional[bool] = Query(None, description="Lọc theo trạng thái hoạt động"),
    db: Session = Depends(get_db),
):
    """Danh sách tất cả Nghiệp vụ."""
    return _list_items(db, DmNghiepVu, NghiepVuResponse, is_active)


@router.post("/nghiep-vu", response_model=NghiepVuResponse, status_code=status.HTTP_201_CREATED)
def create_nghiep_vu(
    payload: NghiepVuCreate,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role([UserRole.admin, UserRole.accountant])),
):
    """Tạo mới Nghiệp vụ. Yêu cầu quyền admin hoặc accountant."""
    return _create_item(db, DmNghiepVu, NghiepVuCreate, NghiepVuResponse, payload)


@router.put("/nghiep-vu/{id}", response_model=NghiepVuResponse)
def update_nghiep_vu(
    id: int,
    payload: NghiepVuUpdate,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role([UserRole.admin, UserRole.accountant])),
):
    """Cập nhật Nghiệp vụ. Yêu cầu quyền admin hoặc accountant."""
    return _update_item(db, DmNghiepVu, NghiepVuResponse, id, payload)


@router.delete("/nghiep-vu/{id}", response_model=NghiepVuResponse)
def delete_nghiep_vu(
    id: int,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role([UserRole.admin, UserRole.accountant])),
):
    """Xóa mềm Nghiệp vụ (is_active=False). Kiểm tra ràng buộc NvNghiepVu."""
    return _delete_item(db, DmNghiepVu, NghiepVuResponse, id, [(NvNghiepVu, "nghiep_vu_id")])


# =============================================================================
# Kiêm Nhiệm (Concurrent Roles)
# =============================================================================

@router.get("/kiem-nhiem", response_model=List[KiemNhiemResponse])
def list_kiem_nhiem(
    is_active: Optional[bool] = Query(None, description="Lọc theo trạng thái hoạt động"),
    db: Session = Depends(get_db),
):
    """Danh sách tất cả Kiêm nhiệm."""
    return _list_items(db, DmKiemNhiem, KiemNhiemResponse, is_active)


@router.post("/kiem-nhiem", response_model=KiemNhiemResponse, status_code=status.HTTP_201_CREATED)
def create_kiem_nhiem(
    payload: KiemNhiemCreate,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role([UserRole.admin, UserRole.accountant])),
):
    """Tạo mới Kiêm nhiệm. Yêu cầu quyền admin hoặc accountant."""
    return _create_item(db, DmKiemNhiem, KiemNhiemCreate, KiemNhiemResponse, payload)


@router.put("/kiem-nhiem/{id}", response_model=KiemNhiemResponse)
def update_kiem_nhiem(
    id: int,
    payload: KiemNhiemUpdate,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role([UserRole.admin, UserRole.accountant])),
):
    """Cập nhật Kiêm nhiệm. Yêu cầu quyền admin hoặc accountant."""
    return _update_item(db, DmKiemNhiem, KiemNhiemResponse, id, payload)


@router.delete("/kiem-nhiem/{id}", response_model=KiemNhiemResponse)
def delete_kiem_nhiem(
    id: int,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role([UserRole.admin, UserRole.accountant])),
):
    """Xóa mềm Kiêm nhiệm (is_active=False). Kiểm tra ràng buộc NvKiemNhiem."""
    return _delete_item(db, DmKiemNhiem, KiemNhiemResponse, id, [(NvKiemNhiem, "kiem_nhiem_id")])
