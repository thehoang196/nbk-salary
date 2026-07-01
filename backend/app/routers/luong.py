"""
NBK Salary API - Lương (Salary) Router

Endpoints for salary calculation, approval workflow, Lương Khoán query, and payslip retrieval.
"""
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.bang_luong import DlBangLuong, TrangThaiBangLuong
from app.models.nhan_vien import NhanVien, NhomNV, TrangThaiNV
from app.models.user import User, UserRole
from app.schemas.luong import (
    TinhLuongRequest, BangLuongResponse, BangLuongItem,
    PhieuLuongResponse, DuyetLuongRequest, LuongKhoanResponse,
)
from app.services.salary_engine import SalaryEngine
from app.services.luong_khoan_engine import get_luong_khoan_breakdown
from app.utils.dependencies import get_current_user, require_role

router = APIRouter()
WRITE_ROLES = [UserRole.admin, UserRole.accountant]


@router.post("/tinh-luong")
def tinh_luong_all(
    payload: TinhLuongRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(WRITE_ROLES)),
):
    """Calculate salary for all (or selected) employees for a month.
    Stores results in dl_bang_luong with status='draft'.
    """
    engine = SalaryEngine(db)

    # Get target employees
    query = db.query(NhanVien).filter(NhanVien.trang_thai == TrangThaiNV.dang_lam)
    if payload.nhan_vien_ids:
        query = query.filter(NhanVien.id.in_(payload.nhan_vien_ids))
    employees = query.all()

    results = []
    for nv in employees:
        manual = (payload.manual_inputs or {}).get(nv.id, {})
        payslip_data = engine.generate_payslip(nv.id, payload.thang, payload.nam, manual)

        if "error" in payslip_data:
            results.append({"nhan_vien_id": nv.id, "error": payslip_data["error"]})
            continue

        # Upsert dl_bang_luong
        existing = db.query(DlBangLuong).filter(
            DlBangLuong.nhan_vien_id == nv.id,
            DlBangLuong.thang == payload.thang,
            DlBangLuong.nam == payload.nam,
        ).first()

        if existing and existing.trang_thai == TrangThaiBangLuong.approved:
            results.append({"nhan_vien_id": nv.id, "error": "Đã duyệt, không thể tính lại"})
            continue

        if existing:
            existing.muc_i_json = payslip_data["muc_i"]
            existing.muc_ii_json = payslip_data["muc_ii"]
            existing.muc_iii_json = payslip_data["muc_iii"]
            existing.muc_iv_json = payslip_data["muc_iv"]
            existing.muc_v_json = payslip_data["muc_v"]
            existing.muc_vi_thuc_linh = payslip_data["muc_vi_thuc_linh"]
            existing.nguoi_tinh_id = current_user.id
            existing.ngay_tinh = datetime.now(timezone.utc)
            existing.trang_thai = TrangThaiBangLuong.draft
            existing.version += 1
        else:
            record = DlBangLuong(
                nhan_vien_id=nv.id,
                thang=payload.thang,
                nam=payload.nam,
                trang_thai=TrangThaiBangLuong.draft,
                muc_i_json=payslip_data["muc_i"],
                muc_ii_json=payslip_data["muc_ii"],
                muc_iii_json=payslip_data["muc_iii"],
                muc_iv_json=payslip_data["muc_iv"],
                muc_v_json=payslip_data["muc_v"],
                muc_vi_thuc_linh=payslip_data["muc_vi_thuc_linh"],
                nguoi_tinh_id=current_user.id,
                ngay_tinh=datetime.now(timezone.utc),
            )
            db.add(record)

        results.append({"nhan_vien_id": nv.id, "thuc_linh": payslip_data["muc_vi_thuc_linh"]})

    db.commit()
    return {"calculated": len([r for r in results if "error" not in r]), "total": len(employees), "results": results}


@router.post("/tinh-luong/{nv_id}")
def tinh_luong_single(
    nv_id: int,
    payload: TinhLuongRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(WRITE_ROLES)),
):
    """Calculate salary for a single employee."""
    payload.nhan_vien_ids = [nv_id]
    return tinh_luong_all(payload, db, current_user)


@router.get("/luong-khoan/{nv_id}", response_model=LuongKhoanResponse)
def get_luong_khoan(
    nv_id: int,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    """Get Lương Khoán breakdown for an employee."""
    breakdown = get_luong_khoan_breakdown(nv_id, db)
    if "error" in breakdown:
        raise HTTPException(status_code=404, detail=breakdown["error"])
    return breakdown


@router.put("/duyet/{id}")
def duyet_luong(
    id: int,
    payload: DuyetLuongRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(WRITE_ROLES)),
):
    """Approve/review salary record with version conflict detection.
    Workflow: draft → reviewed → approved
    """
    record = db.query(DlBangLuong).filter(DlBangLuong.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Không tìm thấy bảng lương")

    # Optimistic locking - version conflict detection (Req 13.2, 13.3)
    if record.version != payload.version:
        # Return current saved values so the frontend can display them
        nguoi_duyet_name = None
        if record.nguoi_duyet_id:
            approver = db.query(User).filter(User.id == record.nguoi_duyet_id).first()
            nguoi_duyet_name = approver.full_name if approver else None

        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=409,
            content={
                "detail": "Xung đột phiên bản. Dữ liệu đã được cập nhật bởi người khác.",
                "current": {
                    "trang_thai": record.trang_thai.value,
                    "version": record.version,
                    "nguoi_duyet": nguoi_duyet_name,
                    "ngay_duyet": record.ngay_duyet.isoformat() if record.ngay_duyet else None,
                },
            },
        )

    # Validate state transition
    valid_transitions = {
        "draft": "reviewed",
        "reviewed": "approved",
    }
    current = record.trang_thai.value
    if valid_transitions.get(current) != payload.trang_thai_moi:
        raise HTTPException(
            status_code=400,
            detail=f"Không thể chuyển từ '{current}' sang '{payload.trang_thai_moi}'",
        )

    record.trang_thai = TrangThaiBangLuong(payload.trang_thai_moi)
    record.nguoi_duyet_id = current_user.id
    record.ngay_duyet = datetime.now(timezone.utc)
    record.version += 1

    db.commit()
    db.refresh(record)
    return {"detail": f"Đã chuyển sang '{payload.trang_thai_moi}'", "version": record.version}


@router.get("/bang-luong/{thang}/{nam}", response_model=BangLuongResponse)
def get_bang_luong(
    thang: int, nam: int,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    """Get salary table for a month."""
    records = db.query(DlBangLuong).filter(
        DlBangLuong.thang == thang, DlBangLuong.nam == nam
    ).all()

    items = []
    total_thuc_linh = 0
    for r in records:
        nv = db.query(NhanVien).filter(NhanVien.id == r.nhan_vien_id).first()
        item = BangLuongItem(
            id=r.id, nhan_vien_id=r.nhan_vien_id,
            ho_ten=nv.ho_ten if nv else "", ma_nv=nv.ma_nv if nv else "",
            nhom_nv=nv.nhom_nv.value if nv else "",
            thang=r.thang, nam=r.nam,
            trang_thai=r.trang_thai.value,
            muc_vi_thuc_linh=int(r.muc_vi_thuc_linh) if r.muc_vi_thuc_linh else 0,
            ngay_tinh=r.ngay_tinh,
        )
        items.append(item)
        total_thuc_linh += int(r.muc_vi_thuc_linh or 0)

    return BangLuongResponse(thang=thang, nam=nam, items=items, total_count=len(items), total_thuc_linh=total_thuc_linh)


@router.get("/phieu-luong/{nv_id}/{thang}/{nam}", response_model=PhieuLuongResponse)
def get_phieu_luong(
    nv_id: int, thang: int, nam: int,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    """Get individual payslip."""
    record = db.query(DlBangLuong).filter(
        DlBangLuong.nhan_vien_id == nv_id,
        DlBangLuong.thang == thang, DlBangLuong.nam == nam,
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Chưa có phiếu lương")

    return PhieuLuongResponse(
        nhan_vien_id=record.nhan_vien_id, thang=thang, nam=nam,
        trang_thai=record.trang_thai.value,
        muc_i=record.muc_i_json or {},
        muc_ii=record.muc_ii_json or {},
        muc_iii=record.muc_iii_json or {},
        muc_iv=record.muc_iv_json or {},
        muc_v=record.muc_v_json or {},
        muc_vi_thuc_linh=int(record.muc_vi_thuc_linh or 0),
        ngay_tinh=record.ngay_tinh,
        ngay_duyet=record.ngay_duyet,
        version=record.version,
    )
