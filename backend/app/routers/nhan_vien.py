"""
NBK Salary API - Nhân viên (Employee) Router

CRUD for employees with position assignments, nghiep_vu/kiem_nhiem junction management,
and contract history endpoints.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.chuc_danh import (
    DmCapBacQL,
    DmChucVu,
    DmKiemNhiem,
    DmNghiepVu,
    NvKiemNhiem,
    NvNghiepVu,
)
from app.models.danh_muc import DmHeSoLuong
from app.models.hop_dong import DlHopDong
from app.models.nhan_vien import NhanVien, NhomNV, TrangThaiNV
from app.models.user import UserRole
from app.schemas.chuc_danh import (
    NvKiemNhiemCreate,
    NvKiemNhiemResponse,
    NvNghiepVuCreate,
    NvNghiepVuResponse,
)
from app.schemas.nhan_vien import (
    HopDongCreate,
    HopDongResponse,
    NhanVienCreate,
    NhanVienResponse,
    NhanVienUpdate,
)
from app.utils.dependencies import get_current_user, require_role

router = APIRouter()

# Supplement amounts from settings (configurable by Admin)
from app.config import settings
NGHIEP_VU_SUPPLEMENT = settings.NGHIEP_VU_SUPPLEMENT
KIEM_NHIEM_SUPPLEMENT = settings.KIEM_NHIEM_SUPPLEMENT

# Allowed roles for write operations
WRITE_ROLES = [UserRole.admin, UserRole.accountant, UserRole.hr]


def _compute_luong_khoan(nhan_vien: NhanVien, db: Session) -> int:
    """Compute lương khoán for an employee.

    Formula: chuc_vu.don_gia_luong_khoan + cap_bac_ql.don_gia_luong_khoan
             + (count nghiep_vu × 2M) + (count kiem_nhiem × 3M)
    """
    total = 0

    # Chức vụ component
    if nhan_vien.chuc_vu_id and nhan_vien.chuc_vu:
        total += int(nhan_vien.chuc_vu.don_gia_luong_khoan or 0)

    # Cấp bậc quản lý component
    if nhan_vien.cap_bac_ql_id and nhan_vien.cap_bac_ql:
        total += int(nhan_vien.cap_bac_ql.don_gia_luong_khoan or 0)

    # Nghiệp vụ component (count × 2M)
    nghiep_vu_count = (
        db.query(NvNghiepVu)
        .filter(NvNghiepVu.nhan_vien_id == nhan_vien.id)
        .count()
    )
    total += nghiep_vu_count * NGHIEP_VU_SUPPLEMENT

    # Kiêm nhiệm component (count × 3M)
    kiem_nhiem_count = (
        db.query(NvKiemNhiem)
        .filter(NvKiemNhiem.nhan_vien_id == nhan_vien.id)
        .count()
    )
    total += kiem_nhiem_count * KIEM_NHIEM_SUPPLEMENT

    return total


def _to_response(nv: NhanVien, db: Session) -> NhanVienResponse:
    """Convert NhanVien ORM instance to response with computed luong_khoan."""
    resp = NhanVienResponse.model_validate(nv)
    resp.luong_khoan = _compute_luong_khoan(nv, db)
    return resp


# =============================================================================
# Employee CRUD Endpoints (Task 7.2)
# =============================================================================


@router.get("", response_model=List[NhanVienResponse])
def list_nhan_vien(
    nhom_nv: Optional[NhomNV] = Query(None, description="Filter by nhóm NV (GV/VP)"),
    trang_thai: Optional[TrangThaiNV] = Query(None, description="Filter by trạng thái"),
    don_vi_id: Optional[int] = Query(None, description="Filter by đơn vị ID"),
    search: Optional[str] = Query(None, description="Search by mã NV or họ tên"),
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    """List all employees with optional filters."""
    query = db.query(NhanVien)

    if nhom_nv is not None:
        query = query.filter(NhanVien.nhom_nv == nhom_nv)
    if trang_thai is not None:
        query = query.filter(NhanVien.trang_thai == trang_thai)
    if don_vi_id is not None:
        query = query.filter(NhanVien.don_vi_id == don_vi_id)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (NhanVien.ma_nv.ilike(search_pattern))
            | (NhanVien.ho_ten.ilike(search_pattern))
        )

    employees = query.order_by(NhanVien.ho_ten).all()
    return [_to_response(nv, db) for nv in employees]


@router.post("", response_model=NhanVienResponse, status_code=status.HTTP_201_CREATED)
def create_nhan_vien(
    payload: NhanVienCreate,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role(WRITE_ROLES)),
):
    """Create a new employee.

    Validations:
    - nhom_nv is required (GV/VP)
    - If nhom_nv == VP, force ten_goi = None
    - chuc_vu_id must reference dm_chuc_vu if provided
    - cap_bac_ql_id must reference dm_cap_bac_ql if provided
    - ma_nv must be unique (409 on duplicate)
    """
    # Check unique ma_nv
    existing = db.query(NhanVien).filter(NhanVien.ma_nv == payload.ma_nv).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Mã nhân viên '{payload.ma_nv}' đã tồn tại",
        )

    # Validate chuc_vu_id reference
    if payload.chuc_vu_id is not None:
        chuc_vu = db.query(DmChucVu).filter(DmChucVu.id == payload.chuc_vu_id).first()
        if not chuc_vu:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Chức vụ id={payload.chuc_vu_id} không tồn tại",
            )

    # Validate cap_bac_ql_id reference
    if payload.cap_bac_ql_id is not None:
        cap_bac = db.query(DmCapBacQL).filter(DmCapBacQL.id == payload.cap_bac_ql_id).first()
        if not cap_bac:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cấp bậc quản lý id={payload.cap_bac_ql_id} không tồn tại",
            )

    # Build data, force ten_goi = None for VP
    data = payload.model_dump()
    if payload.nhom_nv == NhomNV.VP:
        data["ten_goi"] = None

    nhan_vien = NhanVien(**data)
    db.add(nhan_vien)
    db.commit()
    db.refresh(nhan_vien)

    return _to_response(nhan_vien, db)


@router.get("/{nv_id}", response_model=NhanVienResponse)
def get_nhan_vien(
    nv_id: int,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    """Get employee detail with computed lương khoán."""
    nhan_vien = db.query(NhanVien).filter(NhanVien.id == nv_id).first()
    if not nhan_vien:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy nhân viên id={nv_id}",
        )

    return _to_response(nhan_vien, db)


@router.put("/{nv_id}", response_model=NhanVienResponse)
def update_nhan_vien(
    nv_id: int,
    payload: NhanVienUpdate,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role(WRITE_ROLES)),
):
    """Update an existing employee.

    If nhom_nv is VP, prevent setting ten_goi (force to None).
    """
    nhan_vien = db.query(NhanVien).filter(NhanVien.id == nv_id).first()
    if not nhan_vien:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy nhân viên id={nv_id}",
        )

    update_data = payload.model_dump(exclude_unset=True)

    # Validate chuc_vu_id if being updated
    if "chuc_vu_id" in update_data and update_data["chuc_vu_id"] is not None:
        chuc_vu = db.query(DmChucVu).filter(DmChucVu.id == update_data["chuc_vu_id"]).first()
        if not chuc_vu:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Chức vụ id={update_data['chuc_vu_id']} không tồn tại",
            )

    # Validate cap_bac_ql_id if being updated
    if "cap_bac_ql_id" in update_data and update_data["cap_bac_ql_id"] is not None:
        cap_bac = db.query(DmCapBacQL).filter(DmCapBacQL.id == update_data["cap_bac_ql_id"]).first()
        if not cap_bac:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cấp bậc quản lý id={update_data['cap_bac_ql_id']} không tồn tại",
            )

    # If employee is VP group, force ten_goi to None
    if nhan_vien.nhom_nv == NhomNV.VP:
        update_data["ten_goi"] = None

    for field, value in update_data.items():
        setattr(nhan_vien, field, value)

    db.commit()
    db.refresh(nhan_vien)

    return _to_response(nhan_vien, db)


@router.delete("/{nv_id}")
def delete_nhan_vien(
    nv_id: int,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role(WRITE_ROLES)),
):
    """Soft-delete employee by setting trang_thai = nghi_viec."""
    nhan_vien = db.query(NhanVien).filter(NhanVien.id == nv_id).first()
    if not nhan_vien:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy nhân viên id={nv_id}",
        )

    nhan_vien.trang_thai = TrangThaiNV.nghi_viec
    db.commit()
    db.refresh(nhan_vien)

    return _to_response(nhan_vien, db)



# =============================================================================
# Assignment Endpoints (Task 7.3)
# =============================================================================


# --- Nghiệp vụ assignments ---

@router.get("/{nv_id}/nghiep-vu", response_model=List[NvNghiepVuResponse])
def list_nghiep_vu_assignments(
    nv_id: int,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role(WRITE_ROLES)),
):
    """List all nghiệp vụ assignments for an employee."""
    employee = db.query(NhanVien).filter(NhanVien.id == nv_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy nhân viên với id={nv_id}",
        )

    assignments = (
        db.query(NvNghiepVu)
        .filter(NvNghiepVu.nhan_vien_id == nv_id)
        .order_by(NvNghiepVu.ngay_bat_dau.desc())
        .all()
    )
    return [NvNghiepVuResponse.model_validate(a) for a in assignments]


@router.post(
    "/{nv_id}/nghiep-vu",
    response_model=NvNghiepVuResponse,
    status_code=status.HTTP_201_CREATED,
)
def assign_nghiep_vu(
    nv_id: int,
    payload: NvNghiepVuCreate,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role(WRITE_ROLES)),
):
    """Assign a nghiệp vụ to an employee."""
    # Validate employee exists
    employee = db.query(NhanVien).filter(NhanVien.id == nv_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy nhân viên với id={nv_id}",
        )

    # Validate nghiep_vu exists
    nghiep_vu = db.query(DmNghiepVu).filter(DmNghiepVu.id == payload.nghiep_vu_id).first()
    if not nghiep_vu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy nghiệp vụ với id={payload.nghiep_vu_id}",
        )

    assignment = NvNghiepVu(nhan_vien_id=nv_id, **payload.model_dump())
    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return NvNghiepVuResponse.model_validate(assignment)


@router.delete("/{nv_id}/nghiep-vu/{assignment_id}")
def remove_nghiep_vu(
    nv_id: int,
    assignment_id: int,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role(WRITE_ROLES)),
):
    """Remove a nghiệp vụ assignment from an employee."""
    assignment = (
        db.query(NvNghiepVu)
        .filter(NvNghiepVu.id == assignment_id, NvNghiepVu.nhan_vien_id == nv_id)
        .first()
    )
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy phân công nghiệp vụ id={assignment_id} cho nhân viên id={nv_id}",
        )

    db.delete(assignment)
    db.commit()

    return {"detail": "Đã xóa phân công nghiệp vụ"}


# --- Kiêm nhiệm assignments ---

@router.get("/{nv_id}/kiem-nhiem", response_model=List[NvKiemNhiemResponse])
def list_kiem_nhiem_assignments(
    nv_id: int,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role(WRITE_ROLES)),
):
    """List all kiêm nhiệm assignments for an employee."""
    employee = db.query(NhanVien).filter(NhanVien.id == nv_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy nhân viên với id={nv_id}",
        )

    assignments = (
        db.query(NvKiemNhiem)
        .filter(NvKiemNhiem.nhan_vien_id == nv_id)
        .order_by(NvKiemNhiem.ngay_bat_dau.desc())
        .all()
    )
    return [NvKiemNhiemResponse.model_validate(a) for a in assignments]


@router.post(
    "/{nv_id}/kiem-nhiem",
    response_model=NvKiemNhiemResponse,
    status_code=status.HTTP_201_CREATED,
)
def assign_kiem_nhiem(
    nv_id: int,
    payload: NvKiemNhiemCreate,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role(WRITE_ROLES)),
):
    """Assign a kiêm nhiệm to an employee."""
    # Validate employee exists
    employee = db.query(NhanVien).filter(NhanVien.id == nv_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy nhân viên với id={nv_id}",
        )

    # Validate kiem_nhiem exists
    kiem_nhiem = db.query(DmKiemNhiem).filter(DmKiemNhiem.id == payload.kiem_nhiem_id).first()
    if not kiem_nhiem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy kiêm nhiệm với id={payload.kiem_nhiem_id}",
        )

    assignment = NvKiemNhiem(nhan_vien_id=nv_id, **payload.model_dump())
    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return NvKiemNhiemResponse.model_validate(assignment)


@router.delete("/{nv_id}/kiem-nhiem/{assignment_id}")
def remove_kiem_nhiem(
    nv_id: int,
    assignment_id: int,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role(WRITE_ROLES)),
):
    """Remove a kiêm nhiệm assignment from an employee."""
    assignment = (
        db.query(NvKiemNhiem)
        .filter(NvKiemNhiem.id == assignment_id, NvKiemNhiem.nhan_vien_id == nv_id)
        .first()
    )
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy phân công kiêm nhiệm id={assignment_id} cho nhân viên id={nv_id}",
        )

    db.delete(assignment)
    db.commit()

    return {"detail": "Đã xóa phân công kiêm nhiệm"}



# =============================================================================
# Contract History Endpoints (Task 7.4)
# =============================================================================


@router.get("/{nv_id}/hop-dong", response_model=List[HopDongResponse])
def list_contracts(
    nv_id: int,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role(WRITE_ROLES)),
):
    """List all contracts for an employee, ordered by ngay_bat_dau descending."""
    # Validate employee exists
    employee = db.query(NhanVien).filter(NhanVien.id == nv_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy nhân viên với id={nv_id}",
        )

    contracts = (
        db.query(DlHopDong)
        .filter(DlHopDong.nhan_vien_id == nv_id)
        .order_by(DlHopDong.ngay_bat_dau.desc())
        .all()
    )
    return [HopDongResponse.model_validate(c) for c in contracts]


@router.post(
    "/{nv_id}/hop-dong",
    response_model=HopDongResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_contract(
    nv_id: int,
    payload: HopDongCreate,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role(WRITE_ROLES)),
):
    """Create a new contract for an employee.

    Validations:
    - Employee must exist (404 if not)
    - ngay_bat_dau <= ngay_ket_thuc (if ngay_ket_thuc provided)
    - he_so_luong_id must reference dm_he_so_luong (if provided)
    """
    # Validate employee exists
    employee = db.query(NhanVien).filter(NhanVien.id == nv_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy nhân viên với id={nv_id}",
        )

    # Validate date range
    if payload.ngay_ket_thuc is not None and payload.ngay_bat_dau > payload.ngay_ket_thuc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Ngày bắt đầu phải nhỏ hơn hoặc bằng ngày kết thúc",
        )

    # Validate he_so_luong_id reference
    if payload.he_so_luong_id is not None:
        he_so = db.query(DmHeSoLuong).filter(DmHeSoLuong.id == payload.he_so_luong_id).first()
        if not he_so:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Không tìm thấy hệ số lương với id={payload.he_so_luong_id}",
            )

    contract = DlHopDong(nhan_vien_id=nv_id, **payload.model_dump())
    db.add(contract)
    db.commit()
    db.refresh(contract)

    return HopDongResponse.model_validate(contract)


@router.put("/{nv_id}/hop-dong/{hd_id}", response_model=HopDongResponse)
def update_contract(
    nv_id: int,
    hd_id: int,
    payload: HopDongCreate,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role(WRITE_ROLES)),
):
    """Update a contract.

    Validations:
    - Contract must belong to the specified employee
    - ngay_bat_dau <= ngay_ket_thuc (if ngay_ket_thuc provided)
    - he_so_luong_id must reference dm_he_so_luong (if provided)
    """
    # Validate contract exists and belongs to this employee
    contract = (
        db.query(DlHopDong)
        .filter(DlHopDong.id == hd_id, DlHopDong.nhan_vien_id == nv_id)
        .first()
    )
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy hợp đồng id={hd_id} cho nhân viên id={nv_id}",
        )

    # Validate date range
    if payload.ngay_ket_thuc is not None and payload.ngay_bat_dau > payload.ngay_ket_thuc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Ngày bắt đầu phải nhỏ hơn hoặc bằng ngày kết thúc",
        )

    # Validate he_so_luong_id reference
    if payload.he_so_luong_id is not None:
        he_so = db.query(DmHeSoLuong).filter(DmHeSoLuong.id == payload.he_so_luong_id).first()
        if not he_so:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Không tìm thấy hệ số lương với id={payload.he_so_luong_id}",
            )

    # Apply updates
    update_data = payload.model_dump()
    for field, value in update_data.items():
        setattr(contract, field, value)

    db.commit()
    db.refresh(contract)

    return HopDongResponse.model_validate(contract)
