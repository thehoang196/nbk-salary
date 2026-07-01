"""
NBK Salary API - MISA HR Import Router

Provides bulk import endpoints compatible with MISA AMIS Excel templates:
- Thông tin gia đình (Family/Dependents)
- Lịch sử lương (Salary History)
- Quá trình công tác (Work History)
- Bằng cấp (Qualifications)
- Nghỉ phép (Leave Balance)
- Cơ cấu tổ chức (Organization Structure)
- Vị trí công việc (Job Positions)
"""
from typing import List, Dict, Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.nhan_vien import NhanVien
from app.models.misa_hr import (
    DlGiaDinh, DlLichSuLuong, DlQuaTrinhCongTac, DlBangCap, DlNghiPhep,
)
from app.models.danh_muc import DmDonVi, DmViTri
from app.models.user import User, UserRole
from app.schemas.misa_hr import (
    GiaDinhCreate, GiaDinhResponse, GiaDinhImportRequest,
    LichSuLuongCreate, LichSuLuongResponse, LichSuLuongImportRequest,
    QuaTrinhCTCreate, QuaTrinhCTResponse, QuaTrinhCTImportRequest,
    BangCapCreate, BangCapResponse, BangCapImportRequest,
    NghiPhepCreate, NghiPhepResponse, NghiPhepImportRequest,
    DonViMisaImportRequest, ViTriMisaImportRequest,
    MisaImportResponse,
)
from app.utils.dependencies import require_role

router = APIRouter()
WRITE_ROLES = [UserRole.admin, UserRole.accountant, UserRole.hr]


def _find_nv(db: Session, ma_nv: str):
    """Find employee by ma_nv (case-insensitive)."""
    return db.query(NhanVien).filter(
        NhanVien.ma_nv.ilike(ma_nv.strip())
    ).first()


# =============================================================================
# Gia đình Import
# =============================================================================

@router.post("/import/gia-dinh", response_model=MisaImportResponse)
def import_gia_dinh(
    payload: GiaDinhImportRequest,
    db: Session = Depends(get_db),
    _user: User = Depends(require_role(WRITE_ROLES)),
):
    """Import family/dependent data from MISA template."""
    errors = []
    imported = 0

    for idx, row in enumerate(payload.rows):
        nv = _find_nv(db, row.ma_nv)
        if not nv:
            errors.append({"row": idx + 1, "ma_nv": row.ma_nv,
                           "error": f"Không tìm thấy NV: '{row.ma_nv}'"})
            continue

        record = DlGiaDinh(
            nhan_vien_id=nv.id,
            **row.model_dump(exclude={"ma_nv"})
        )
        db.add(record)
        imported += 1

    if imported > 0:
        db.commit()

    return MisaImportResponse(
        imported_count=imported, total_rows=len(payload.rows), errors=errors
    )


@router.get("/{nv_id}/gia-dinh", response_model=List[GiaDinhResponse])
def list_gia_dinh(
    nv_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(require_role(WRITE_ROLES)),
):
    """List family members for an employee."""
    return db.query(DlGiaDinh).filter(DlGiaDinh.nhan_vien_id == nv_id).all()


# =============================================================================
# Lịch sử lương Import
# =============================================================================

@router.post("/import/lich-su-luong", response_model=MisaImportResponse)
def import_lich_su_luong(
    payload: LichSuLuongImportRequest,
    db: Session = Depends(get_db),
    _user: User = Depends(require_role(WRITE_ROLES)),
):
    """Import salary history from MISA template."""
    errors = []
    imported = 0

    for idx, row in enumerate(payload.rows):
        nv = _find_nv(db, row.ma_nv)
        if not nv:
            errors.append({"row": idx + 1, "ma_nv": row.ma_nv,
                           "error": f"Không tìm thấy NV: '{row.ma_nv}'"})
            continue

        record = DlLichSuLuong(
            nhan_vien_id=nv.id,
            **row.model_dump(exclude={"ma_nv"})
        )
        db.add(record)
        imported += 1

    if imported > 0:
        db.commit()

    return MisaImportResponse(
        imported_count=imported, total_rows=len(payload.rows), errors=errors
    )


@router.get("/{nv_id}/lich-su-luong", response_model=List[LichSuLuongResponse])
def list_lich_su_luong(
    nv_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(require_role(WRITE_ROLES)),
):
    """List salary history for an employee."""
    return db.query(DlLichSuLuong).filter(
        DlLichSuLuong.nhan_vien_id == nv_id
    ).order_by(DlLichSuLuong.ngay_hieu_luc.desc()).all()


# =============================================================================
# Quá trình công tác Import
# =============================================================================

@router.post("/import/qua-trinh-ct", response_model=MisaImportResponse)
def import_qua_trinh_ct(
    payload: QuaTrinhCTImportRequest,
    db: Session = Depends(get_db),
    _user: User = Depends(require_role(WRITE_ROLES)),
):
    """Import work history from MISA template."""
    errors = []
    imported = 0

    for idx, row in enumerate(payload.rows):
        nv = _find_nv(db, row.ma_nv)
        if not nv:
            errors.append({"row": idx + 1, "ma_nv": row.ma_nv,
                           "error": f"Không tìm thấy NV: '{row.ma_nv}'"})
            continue

        record = DlQuaTrinhCongTac(
            nhan_vien_id=nv.id,
            **row.model_dump(exclude={"ma_nv"})
        )
        db.add(record)
        imported += 1

    if imported > 0:
        db.commit()

    return MisaImportResponse(
        imported_count=imported, total_rows=len(payload.rows), errors=errors
    )


# =============================================================================
# Bằng cấp Import
# =============================================================================

@router.post("/import/bang-cap", response_model=MisaImportResponse)
def import_bang_cap(
    payload: BangCapImportRequest,
    db: Session = Depends(get_db),
    _user: User = Depends(require_role(WRITE_ROLES)),
):
    """Import qualifications from MISA template."""
    errors = []
    imported = 0

    for idx, row in enumerate(payload.rows):
        nv = _find_nv(db, row.ma_nv)
        if not nv:
            errors.append({"row": idx + 1, "ma_nv": row.ma_nv,
                           "error": f"Không tìm thấy NV: '{row.ma_nv}'"})
            continue

        record = DlBangCap(
            nhan_vien_id=nv.id,
            **row.model_dump(exclude={"ma_nv"})
        )
        db.add(record)
        imported += 1

    if imported > 0:
        db.commit()

    return MisaImportResponse(
        imported_count=imported, total_rows=len(payload.rows), errors=errors
    )


# =============================================================================
# Nghỉ phép Import
# =============================================================================

@router.post("/import/nghi-phep", response_model=MisaImportResponse)
def import_nghi_phep(
    payload: NghiPhepImportRequest,
    db: Session = Depends(get_db),
    _user: User = Depends(require_role(WRITE_ROLES)),
):
    """Import leave balance from MISA template."""
    errors = []
    imported = 0

    for idx, row in enumerate(payload.rows):
        nv = _find_nv(db, row.ma_nv)
        if not nv:
            errors.append({"row": idx + 1, "ma_nv": row.ma_nv,
                           "error": f"Không tìm thấy NV: '{row.ma_nv}'"})
            continue

        # Upsert by nhan_vien_id + nam
        existing = db.query(DlNghiPhep).filter(
            DlNghiPhep.nhan_vien_id == nv.id,
            DlNghiPhep.nam == payload.nam,
        ).first()

        data = row.model_dump(exclude={"ma_nv"})
        if existing:
            for k, v in data.items():
                if v is not None:
                    setattr(existing, k, v)
        else:
            record = DlNghiPhep(nhan_vien_id=nv.id, nam=payload.nam, **data)
            db.add(record)

        imported += 1

    if imported > 0:
        db.commit()

    return MisaImportResponse(
        imported_count=imported, total_rows=len(payload.rows), errors=errors
    )


# =============================================================================
# Cơ cấu tổ chức Import
# =============================================================================

@router.post("/import/co-cau-to-chuc", response_model=MisaImportResponse)
def import_co_cau_to_chuc(
    payload: DonViMisaImportRequest,
    db: Session = Depends(get_db),
    _user: User = Depends(require_role(WRITE_ROLES)),
):
    """Import organization structure from MISA template."""
    errors = []
    imported = 0

    for idx, row in enumerate(payload.rows):
        # Upsert by ma_don_vi
        existing = db.query(DmDonVi).filter(
            DmDonVi.ten.ilike(row.ten.strip())
        ).first()

        if existing:
            existing.ma_don_vi = row.ma_don_vi
            existing.thuoc_don_vi = row.thuoc_don_vi
            existing.dia_chi = row.dia_chi
            existing.cap_to_chuc = row.cap_to_chuc
            existing.truong_don_vi = row.truong_don_vi
            existing.chuc_nang_nhiem_vu = row.chuc_nang_nhiem_vu
            existing.hach_toan = row.hach_toan
            existing.thu_tu_sap_xep = row.thu_tu_sap_xep
            if row.trang_thai and "ngừng" in row.trang_thai.lower():
                existing.is_active = False
        else:
            is_active = True
            if row.trang_thai and "ngừng" in row.trang_thai.lower():
                is_active = False
            record = DmDonVi(
                ten=row.ten.strip(),
                ma_don_vi=row.ma_don_vi,
                thuoc_don_vi=row.thuoc_don_vi,
                dia_chi=row.dia_chi,
                cap_to_chuc=row.cap_to_chuc,
                truong_don_vi=row.truong_don_vi,
                chuc_nang_nhiem_vu=row.chuc_nang_nhiem_vu,
                hach_toan=row.hach_toan,
                thu_tu_sap_xep=row.thu_tu_sap_xep,
                is_active=is_active,
            )
            db.add(record)

        imported += 1

    if imported > 0:
        db.commit()

    return MisaImportResponse(
        imported_count=imported, total_rows=len(payload.rows), errors=errors
    )


# =============================================================================
# Vị trí công việc Import
# =============================================================================

@router.post("/import/vi-tri-cong-viec", response_model=MisaImportResponse)
def import_vi_tri_cong_viec(
    payload: ViTriMisaImportRequest,
    db: Session = Depends(get_db),
    _user: User = Depends(require_role(WRITE_ROLES)),
):
    """Import job positions from MISA template."""
    errors = []
    imported = 0

    for idx, row in enumerate(payload.rows):
        existing = db.query(DmViTri).filter(
            DmViTri.ten.ilike(row.ten.strip())
        ).first()

        if existing:
            existing.ma_vi_tri = row.ma_vi_tri
            existing.don_vi_cong_tac = row.don_vi_cong_tac
            existing.nhom_vi_tri = row.nhom_vi_tri
            existing.chuc_danh = row.chuc_danh
            existing.trang_thai = row.trang_thai
        else:
            record = DmViTri(
                ten=row.ten.strip(),
                ma_vi_tri=row.ma_vi_tri,
                don_vi_cong_tac=row.don_vi_cong_tac,
                nhom_vi_tri=row.nhom_vi_tri,
                chuc_danh=row.chuc_danh,
                trang_thai=row.trang_thai,
            )
            db.add(record)

        imported += 1

    if imported > 0:
        db.commit()

    return MisaImportResponse(
        imported_count=imported, total_rows=len(payload.rows), errors=errors
    )
