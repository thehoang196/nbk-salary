"""
NBK Salary API - Thời khóa biểu (TKB) Router

Endpoints for timetable import, retrieval, and template info.
Accepts pre-parsed JSON data (frontend handles file parsing).
"""

from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.danh_muc import DmKhoi, DmLop, DmMonHoc
from app.models.nhan_vien import NhanVien
from app.models.tkb import DlTkb, DlThayDoiNguoiDay, DlTietDayNgoai
from app.models.user import UserRole
from app.schemas.tkb import (
    TKBImportRequest, TKBImportResponse, TKBResponse,
    ThayDoiCreate, ThayDoiResponse,
    BCCResponse, PhatSinhCreate,
)
from app.services.bcc_service import BCCService
from app.utils.dependencies import get_current_user, require_role

router = APIRouter()

# Roles allowed to import TKB data
IMPORT_ROLES = [UserRole.admin, UserRole.accountant]


def _resolve_teacher(db: Session, giao_vien: str):
    """Resolve teacher by ma_nv or ho_ten. Returns NhanVien or None."""
    # Try matching by ma_nv first
    nv = db.query(NhanVien).filter(NhanVien.ma_nv == giao_vien).first()
    if nv:
        return nv
    # Fallback: match by ho_ten (exact, case-insensitive)
    nv = db.query(NhanVien).filter(NhanVien.ho_ten.ilike(giao_vien)).first()
    return nv


def _resolve_subject(db: Session, mon_hoc: str):
    """Resolve subject by ten or ma_mon. Returns DmMonHoc or None."""
    mh = db.query(DmMonHoc).filter(DmMonHoc.ma_mon == mon_hoc).first()
    if mh:
        return mh
    mh = db.query(DmMonHoc).filter(DmMonHoc.ten.ilike(mon_hoc)).first()
    return mh


def _resolve_grade(db: Session, khoi: str):
    """Resolve grade by ten. Returns DmKhoi or None."""
    return db.query(DmKhoi).filter(DmKhoi.ten.ilike(khoi)).first()


def _resolve_class(db: Session, lop: str):
    """Resolve class by ten. Returns DmLop or None."""
    return db.query(DmLop).filter(DmLop.ten.ilike(lop)).first()


@router.post("/import", response_model=TKBImportResponse, status_code=status.HTTP_201_CREATED)
def import_tkb(
    payload: TKBImportRequest,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role(IMPORT_ROLES)),
):
    """Import unified TKB data (all grades in one request).

    Accepts pre-parsed JSON rows. Validates each row against master data.
    Returns import counts and any validation errors per row.
    """
    thang = payload.thang
    nam = payload.nam

    # Check for existing data if replace_existing is False
    existing_count = (
        db.query(DlTkb)
        .filter(DlTkb.thang == thang, DlTkb.nam == nam)
        .count()
    )

    if existing_count > 0 and not payload.replace_existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Dữ liệu TKB tháng {thang}/{nam} đã tồn tại. "
                   f"Sử dụng replace_existing=true để ghi đè.",
        )

    # If replacing, delete existing records for this month
    if existing_count > 0 and payload.replace_existing:
        db.query(DlTkb).filter(DlTkb.thang == thang, DlTkb.nam == nam).delete()

    errors = []
    records_to_add = []

    for idx, row in enumerate(payload.rows, start=1):
        row_errors = []

        # Resolve teacher
        teacher = _resolve_teacher(db, row.giao_vien)
        if not teacher:
            row_errors.append({
                "row": idx,
                "field": "giao_vien",
                "error": f"Không tìm thấy giáo viên '{row.giao_vien}'",
            })

        # Resolve subject
        subject = _resolve_subject(db, row.mon_hoc)
        if not subject:
            row_errors.append({
                "row": idx,
                "field": "mon_hoc",
                "error": f"Không tìm thấy môn học '{row.mon_hoc}'",
            })

        # Resolve grade
        grade = _resolve_grade(db, row.khoi)
        if not grade:
            row_errors.append({
                "row": idx,
                "field": "khoi",
                "error": f"Không tìm thấy khối '{row.khoi}'",
            })

        # Resolve class
        lop = _resolve_class(db, row.lop)
        if not lop:
            row_errors.append({
                "row": idx,
                "field": "lop",
                "error": f"Không tìm thấy lớp '{row.lop}'",
            })

        if row_errors:
            errors.extend(row_errors)
            continue

        # All references resolved - create record
        record = DlTkb(
            thang=thang,
            nam=nam,
            nhan_vien_id=teacher.id,
            mon_hoc_id=subject.id,
            khoi_id=grade.id,
            lop_id=lop.id,
            so_tiet=row.so_tiet,
            loai_tiet=row.loai_tiet,
        )
        records_to_add.append(record)

    # Bulk insert valid records
    if records_to_add:
        db.add_all(records_to_add)
        db.commit()

    return TKBImportResponse(
        imported_count=len(records_to_add),
        total_rows=len(payload.rows),
        errors=errors,
    )


@router.get("/template")
def get_template_info():
    """Return info about the expected TKB import format (column names and descriptions)."""
    return {
        "description": "Định dạng file TKB thống nhất (tất cả khối trong 1 file)",
        "columns": [
            {
                "name": "giao_vien",
                "description": "Mã nhân viên hoặc họ tên giáo viên",
                "required": True,
            },
            {
                "name": "mon_hoc",
                "description": "Mã môn hoặc tên môn học",
                "required": True,
            },
            {
                "name": "khoi",
                "description": "Tên khối (Khối 6, Khối 7, Khối 8, Khối 9)",
                "required": True,
            },
            {
                "name": "lop",
                "description": "Tên lớp (6A1, 7B2, ...)",
                "required": True,
            },
            {
                "name": "so_tiet",
                "description": "Số tiết dạy (số nguyên >= 0)",
                "required": True,
            },
            {
                "name": "loai_tiet",
                "description": "Loại tiết: chinh_khoa, tnst_vy, k9_luyen_thi, kh_ta, ielts",
                "required": True,
            },
        ],
        "loai_tiet_options": [
            "chinh_khoa",
            "tnst_vy",
            "k9_luyen_thi",
            "kh_ta",
            "ielts",
        ],
        "notes": [
            "Cột giao_vien có thể dùng mã nhân viên (ma_nv) hoặc họ tên đầy đủ",
            "Cột mon_hoc có thể dùng mã môn (ma_mon) hoặc tên môn học",
            "Dữ liệu import theo từng tháng/năm",
            "Nếu dữ liệu đã tồn tại, dùng replace_existing=true để ghi đè",
        ],
    }


@router.get("/{thang}/{nam}", response_model=List[TKBResponse])
def get_tkb_by_month(
    thang: int,
    nam: int,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    """Get all TKB records for a specific month/year."""
    if thang < 1 or thang > 12:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Tháng phải từ 1 đến 12",
        )
    if nam < 2020 or nam > 2099:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Năm phải từ 2020 đến 2099",
        )

    records = (
        db.query(DlTkb)
        .filter(DlTkb.thang == thang, DlTkb.nam == nam)
        .order_by(DlTkb.nhan_vien_id, DlTkb.khoi_id, DlTkb.lop_id)
        .all()
    )

    return [TKBResponse.model_validate(r) for r in records]



# ─── Change Log (Thay đổi người dạy) Endpoints ───────────────────────────────

CHANGE_LOG_ROLES = [UserRole.admin, UserRole.accountant]


def _validate_thay_doi(db: Session, data: ThayDoiCreate) -> List[Dict[str, Any]]:
    """Validate a single ThayDoiCreate record. Returns list of error dicts."""
    errors: List[Dict[str, Any]] = []

    # Validate gv_goc_id exists
    if not db.query(NhanVien).filter(NhanVien.id == data.gv_goc_id).first():
        errors.append({"field": "gv_goc_id", "error": f"Không tìm thấy giáo viên gốc id={data.gv_goc_id}"})

    # Validate gv_thay_id exists
    if not db.query(NhanVien).filter(NhanVien.id == data.gv_thay_id).first():
        errors.append({"field": "gv_thay_id", "error": f"Không tìm thấy giáo viên thay id={data.gv_thay_id}"})

    # Validate lop_id exists
    if not db.query(DmLop).filter(DmLop.id == data.lop_id).first():
        errors.append({"field": "lop_id", "error": f"Không tìm thấy lớp id={data.lop_id}"})

    # Validate mon_hoc_id exists
    if not db.query(DmMonHoc).filter(DmMonHoc.id == data.mon_hoc_id).first():
        errors.append({"field": "mon_hoc_id", "error": f"Không tìm thấy môn học id={data.mon_hoc_id}"})

    # Validate tiet range (also validated by schema, but double-check)
    if data.tiet < 1 or data.tiet > 10:
        errors.append({"field": "tiet", "error": "Tiết phải từ 1 đến 10"})

    return errors


@router.post("/thay-doi", status_code=status.HTTP_201_CREATED)
def create_thay_doi(
    payload: ThayDoiCreate,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role(CHANGE_LOG_ROLES)),
):
    """Create a single teacher substitution change record.

    Returns 201 on success, or 200 with warning flag if gv_goc is not
    in the current TKB for that month.
    """
    # Validate references
    errors = _validate_thay_doi(db, payload)
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=errors,
        )

    # Duplicate detection: same gv_goc_id + ngay + tiet + lop_id
    duplicate = (
        db.query(DlThayDoiNguoiDay)
        .filter(
            DlThayDoiNguoiDay.gv_goc_id == payload.gv_goc_id,
            DlThayDoiNguoiDay.ngay == payload.ngay,
            DlThayDoiNguoiDay.tiet == payload.tiet,
            DlThayDoiNguoiDay.lop_id == payload.lop_id,
        )
        .first()
    )
    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Đã tồn tại bản ghi thay đổi cho GV gốc id={payload.gv_goc_id}, "
                   f"ngày {payload.ngay}, tiết {payload.tiet}, lớp id={payload.lop_id}.",
        )

    # Check if gv_goc is in the current TKB for that month (warn if not)
    tkb_exists = (
        db.query(DlTkb)
        .filter(
            DlTkb.nhan_vien_id == payload.gv_goc_id,
            DlTkb.thang == payload.thang,
            DlTkb.nam == payload.nam,
        )
        .first()
    )

    # Insert the record
    record = DlThayDoiNguoiDay(
        ngay=payload.ngay,
        tiet=payload.tiet,
        lop_id=payload.lop_id,
        mon_hoc_id=payload.mon_hoc_id,
        gv_goc_id=payload.gv_goc_id,
        gv_thay_id=payload.gv_thay_id,
        ly_do=payload.ly_do,
        thang=payload.thang,
        nam=payload.nam,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    response_data = ThayDoiResponse.model_validate(record).model_dump(mode="json")

    # If gv_goc not found in TKB, return 200 with warning flag
    if not tkb_exists:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "warning": True,
                "message": f"GV gốc id={payload.gv_goc_id} không có trong TKB tháng {payload.thang}/{payload.nam}.",
                "data": response_data,
            },
        )

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=response_data,
    )


@router.get("/thay-doi/{thang}/{nam}", response_model=List[ThayDoiResponse])
def get_thay_doi_by_month(
    thang: int,
    nam: int,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    """List all teacher substitution changes for a specific month/year."""
    if thang < 1 or thang > 12:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Tháng phải từ 1 đến 12",
        )
    if nam < 2020 or nam > 2099:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Năm phải từ 2020 đến 2099",
        )

    records = (
        db.query(DlThayDoiNguoiDay)
        .filter(DlThayDoiNguoiDay.thang == thang, DlThayDoiNguoiDay.nam == nam)
        .order_by(DlThayDoiNguoiDay.ngay, DlThayDoiNguoiDay.tiet)
        .all()
    )

    return [ThayDoiResponse.model_validate(r) for r in records]


@router.put("/thay-doi/{id}", response_model=ThayDoiResponse)
def update_thay_doi(
    id: int,
    payload: ThayDoiCreate,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role(CHANGE_LOG_ROLES)),
):
    """Update an existing teacher substitution change record."""
    record = db.query(DlThayDoiNguoiDay).filter(DlThayDoiNguoiDay.id == id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy bản ghi thay đổi id={id}.",
        )

    # Validate references
    errors = _validate_thay_doi(db, payload)
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=errors,
        )

    # Duplicate detection (excluding current record)
    duplicate = (
        db.query(DlThayDoiNguoiDay)
        .filter(
            DlThayDoiNguoiDay.id != id,
            DlThayDoiNguoiDay.gv_goc_id == payload.gv_goc_id,
            DlThayDoiNguoiDay.ngay == payload.ngay,
            DlThayDoiNguoiDay.tiet == payload.tiet,
            DlThayDoiNguoiDay.lop_id == payload.lop_id,
        )
        .first()
    )
    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Đã tồn tại bản ghi thay đổi cho GV gốc id={payload.gv_goc_id}, "
                   f"ngày {payload.ngay}, tiết {payload.tiet}, lớp id={payload.lop_id}.",
        )

    # Update fields
    record.ngay = payload.ngay
    record.tiet = payload.tiet
    record.lop_id = payload.lop_id
    record.mon_hoc_id = payload.mon_hoc_id
    record.gv_goc_id = payload.gv_goc_id
    record.gv_thay_id = payload.gv_thay_id
    record.ly_do = payload.ly_do
    record.thang = payload.thang
    record.nam = payload.nam

    db.commit()
    db.refresh(record)

    return ThayDoiResponse.model_validate(record)


@router.delete("/thay-doi/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_thay_doi(
    id: int,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role(CHANGE_LOG_ROLES)),
):
    """Delete a teacher substitution change record."""
    record = db.query(DlThayDoiNguoiDay).filter(DlThayDoiNguoiDay.id == id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy bản ghi thay đổi id={id}.",
        )

    db.delete(record)
    db.commit()


@router.post("/thay-doi/import", status_code=status.HTTP_201_CREATED)
def import_thay_doi(
    payload: List[ThayDoiCreate],
    db: Session = Depends(get_db),
    _current_user=Depends(require_role(CHANGE_LOG_ROLES)),
):
    """Bulk import teacher substitution changes.

    Accepts a list of ThayDoiCreate (max 500 rows).
    If any row fails validation, rejects the ENTIRE batch and returns all row errors.
    """
    if len(payload) > 500:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Tối đa 500 dòng mỗi lần import. Nhận được {len(payload)} dòng.",
        )

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Danh sách import rỗng.",
        )

    # Validate all rows first
    all_errors: List[Dict[str, Any]] = []
    for idx, row in enumerate(payload, start=1):
        row_errors = _validate_thay_doi(db, row)
        for err in row_errors:
            all_errors.append({"row": idx, **err})

        # Also check for duplicates within the batch
        duplicate = (
            db.query(DlThayDoiNguoiDay)
            .filter(
                DlThayDoiNguoiDay.gv_goc_id == row.gv_goc_id,
                DlThayDoiNguoiDay.ngay == row.ngay,
                DlThayDoiNguoiDay.tiet == row.tiet,
                DlThayDoiNguoiDay.lop_id == row.lop_id,
            )
            .first()
        )
        if duplicate:
            all_errors.append({
                "row": idx,
                "field": "duplicate",
                "error": f"Đã tồn tại bản ghi: GV gốc id={row.gv_goc_id}, "
                         f"ngày {row.ngay}, tiết {row.tiet}, lớp id={row.lop_id}.",
            })

    # If any errors, reject entire batch
    if all_errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Import thất bại. Vui lòng sửa các lỗi sau và thử lại.",
                "errors": all_errors,
                "total_rows": len(payload),
            },
        )

    # All valid — insert records
    records = []
    for row in payload:
        record = DlThayDoiNguoiDay(
            ngay=row.ngay,
            tiet=row.tiet,
            lop_id=row.lop_id,
            mon_hoc_id=row.mon_hoc_id,
            gv_goc_id=row.gv_goc_id,
            gv_thay_id=row.gv_thay_id,
            ly_do=row.ly_do,
            thang=row.thang,
            nam=row.nam,
        )
        records.append(record)

    db.add_all(records)
    db.commit()

    # Refresh all records to get IDs
    for r in records:
        db.refresh(r)

    return {
        "imported_count": len(records),
        "total_rows": len(payload),
        "data": [ThayDoiResponse.model_validate(r).model_dump(mode="json") for r in records],
    }


# ─── BCC Summary & Phát Sinh Endpoints ────────────────────────────────────────

BCC_ROLES = [UserRole.admin, UserRole.accountant]


@router.get("/bcc/{thang}/{nam}", response_model=BCCResponse)
def get_bcc_summary(
    thang: int,
    nam: int,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    """Generate and return BCC summary for a given month/year.

    Recalculates from current source data each time (TKB, thay đổi, phát sinh).
    """
    if thang < 1 or thang > 12:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Tháng phải từ 1 đến 12",
        )
    if nam < 2020 or nam > 2099:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Năm phải từ 2020 đến 2099",
        )

    service = BCCService(db)
    rows = service.calculate_bcc(thang, nam)
    incomplete = sum(1 for r in rows if not r["is_complete"])

    return BCCResponse(
        thang=thang,
        nam=nam,
        rows=rows,
        total_teachers=len(rows),
        incomplete_count=incomplete,
    )


@router.post("/phat-sinh", status_code=status.HTTP_201_CREATED)
def create_phat_sinh(
    payload: PhatSinhCreate,
    db: Session = Depends(get_db),
    _current_user=Depends(require_role(BCC_ROLES)),
):
    """Create a manual BCC adjustment entry (phát sinh).

    Inserts as a dl_tiet_day_ngoai record which feeds into BCC calculation.
    Requires accountant or admin role.
    """
    # Validate nhan_vien_id exists
    teacher = db.query(NhanVien).filter(NhanVien.id == payload.nhan_vien_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Không tìm thấy nhân viên id={payload.nhan_vien_id}",
        )

    record = DlTietDayNgoai(
        nhan_vien_id=payload.nhan_vien_id,
        thang=payload.thang,
        nam=payload.nam,
        loai=payload.loai,
        so_tiet=payload.so_tiet,
        don_gia=0,
        he_so=1.0,
        thanh_tien=0,
        ghi_chu=payload.ly_do,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {"detail": "Đã thêm phát sinh", "id": record.id}
