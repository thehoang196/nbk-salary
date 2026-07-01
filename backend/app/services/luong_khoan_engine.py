"""
NBK Salary - Lương Khoán Calculation Engine

Calculates contracted salary (Lương Khoán) using the formula:
Lương_Khoán = đơn_giá_chức_vụ + đơn_giá_cấp_bậc + (số_nghiệp_vụ × 2,000,000) + (số_kiêm_nhiệm × 3,000,000)
"""

from typing import Dict, Optional
from sqlalchemy.orm import Session

from app.models.nhan_vien import NhanVien
from app.models.chuc_danh import DmChucVu, DmCapBacQL, NvNghiepVu, NvKiemNhiem
from app.config import settings

# Supplement amounts from settings (configurable by Admin)
NGHIEP_VU_SUPPLEMENT = settings.NGHIEP_VU_SUPPLEMENT
KIEM_NHIEM_SUPPLEMENT = settings.KIEM_NHIEM_SUPPLEMENT


def calculate_luong_khoan(nhan_vien_id: int, db: Session) -> int:
    """Calculate Lương Khoán for an employee.

    Formula: đơn_giá_chức_vụ + đơn_giá_cấp_bậc + (n × 2M) + (m × 3M)

    Returns the total Lương Khoán in VND (integer).
    Returns 0 if employee not found or has no position assignments.
    """
    nhan_vien = db.query(NhanVien).filter(NhanVien.id == nhan_vien_id).first()
    if not nhan_vien:
        return 0

    return calculate_luong_khoan_from_employee(nhan_vien, db)


def calculate_luong_khoan_from_employee(nhan_vien: NhanVien, db: Session) -> int:
    """Calculate Lương Khoán from an already-loaded NhanVien instance."""
    total = 0

    # Component 1: Chức vụ đơn giá
    if nhan_vien.chuc_vu_id:
        chuc_vu = db.query(DmChucVu).filter(DmChucVu.id == nhan_vien.chuc_vu_id).first()
        if chuc_vu:
            total += int(chuc_vu.don_gia_luong_khoan or 0)

    # Component 2: Cấp bậc quản lý đơn giá
    if nhan_vien.cap_bac_ql_id:
        cap_bac = db.query(DmCapBacQL).filter(DmCapBacQL.id == nhan_vien.cap_bac_ql_id).first()
        if cap_bac:
            total += int(cap_bac.don_gia_luong_khoan or 0)

    # Component 3: Số nghiệp vụ × 2M
    nghiep_vu_count = db.query(NvNghiepVu).filter(
        NvNghiepVu.nhan_vien_id == nhan_vien.id,
        NvNghiepVu.ngay_ket_thuc == None,  # Only active (no end date)
    ).count()
    total += nghiep_vu_count * NGHIEP_VU_SUPPLEMENT

    # Component 4: Số kiêm nhiệm × 3M
    kiem_nhiem_count = db.query(NvKiemNhiem).filter(
        NvKiemNhiem.nhan_vien_id == nhan_vien.id,
        NvKiemNhiem.ngay_ket_thuc == None,  # Only active (no end date)
    ).count()
    total += kiem_nhiem_count * KIEM_NHIEM_SUPPLEMENT

    return total


def get_luong_khoan_breakdown(nhan_vien_id: int, db: Session) -> Dict:
    """Get detailed breakdown of Lương Khoán components.

    Returns dict with:
    - chuc_vu_don_gia: int
    - cap_bac_don_gia: int
    - nghiep_vu_count: int
    - nghiep_vu_total: int (count × 2M)
    - kiem_nhiem_count: int
    - kiem_nhiem_total: int (count × 3M)
    - tong_luong_khoan: int
    """
    nhan_vien = db.query(NhanVien).filter(NhanVien.id == nhan_vien_id).first()
    if not nhan_vien:
        return {"error": "Nhân viên không tồn tại"}

    chuc_vu_don_gia = 0
    cap_bac_don_gia = 0

    if nhan_vien.chuc_vu_id:
        chuc_vu = db.query(DmChucVu).filter(DmChucVu.id == nhan_vien.chuc_vu_id).first()
        if chuc_vu:
            chuc_vu_don_gia = int(chuc_vu.don_gia_luong_khoan or 0)

    if nhan_vien.cap_bac_ql_id:
        cap_bac = db.query(DmCapBacQL).filter(DmCapBacQL.id == nhan_vien.cap_bac_ql_id).first()
        if cap_bac:
            cap_bac_don_gia = int(cap_bac.don_gia_luong_khoan or 0)

    nghiep_vu_count = db.query(NvNghiepVu).filter(
        NvNghiepVu.nhan_vien_id == nhan_vien.id,
        NvNghiepVu.ngay_ket_thuc == None,
    ).count()

    kiem_nhiem_count = db.query(NvKiemNhiem).filter(
        NvKiemNhiem.nhan_vien_id == nhan_vien.id,
        NvKiemNhiem.ngay_ket_thuc == None,
    ).count()

    nghiep_vu_total = nghiep_vu_count * NGHIEP_VU_SUPPLEMENT
    kiem_nhiem_total = kiem_nhiem_count * KIEM_NHIEM_SUPPLEMENT
    tong = chuc_vu_don_gia + cap_bac_don_gia + nghiep_vu_total + kiem_nhiem_total

    return {
        "nhan_vien_id": nhan_vien.id,
        "ho_ten": nhan_vien.ho_ten,
        "chuc_vu_don_gia": chuc_vu_don_gia,
        "cap_bac_don_gia": cap_bac_don_gia,
        "nghiep_vu_count": nghiep_vu_count,
        "nghiep_vu_total": nghiep_vu_total,
        "kiem_nhiem_count": kiem_nhiem_count,
        "kiem_nhiem_total": kiem_nhiem_total,
        "tong_luong_khoan": tong,
    }
