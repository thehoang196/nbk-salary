"""
NBK Salary - Misa Attendance Import Service

Parses Misa Excel export files and maps VP attendance data to the internal format.
Matches employees by ma_nv or ho_ten.
"""
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session

from app.models.nhan_vien import NhanVien, NhomNV
from app.models.cham_cong import DlTongHopCong


class MisaImportService:
    """Service for importing VP attendance data from Misa Excel exports."""

    def __init__(self, db: Session):
        self.db = db

    def import_attendance(
        self, thang: int, nam: int, rows: List[Dict[str, Any]]
    ) -> Tuple[int, List[Dict[str, Any]]]:
        """Import attendance data from parsed Misa rows.

        Args:
            thang: Month (1-12)
            nam: Year
            rows: List of dicts with keys: ma_nv/ho_ten, ngay_cong, ngay_nghi, ngay_phep, lam_them

        Returns:
            Tuple of (imported_count, errors_list)
        """
        imported_count = 0
        errors = []

        for idx, row in enumerate(rows):
            # Match employee by ma_nv first, then ho_ten
            nhan_vien = None
            ma_nv = row.get("ma_nv")
            ho_ten = row.get("ho_ten")

            if ma_nv:
                nhan_vien = self.db.query(NhanVien).filter(
                    NhanVien.ma_nv == ma_nv
                ).first()

            if not nhan_vien and ho_ten:
                nhan_vien = self.db.query(NhanVien).filter(
                    NhanVien.ho_ten.ilike(ho_ten)
                ).first()

            if not nhan_vien:
                identifier = ma_nv or ho_ten or f"row {idx + 1}"
                errors.append({
                    "row": idx + 1,
                    "ma_nv": ma_nv or "",
                    "error": f"Không tìm thấy nhân viên: '{identifier}'"
                })
                continue

            # Only import for VP (Office Staff)
            if nhan_vien.nhom_nv != NhomNV.VP:
                errors.append({
                    "row": idx + 1,
                    "ma_nv": nhan_vien.ma_nv,
                    "error": f"Nhân viên '{nhan_vien.ma_nv}' không thuộc nhóm VP (văn phòng)"
                })
                continue

            # Upsert dl_tong_hop_cong for this employee/month
            existing = self.db.query(DlTongHopCong).filter(
                DlTongHopCong.nhan_vien_id == nhan_vien.id,
                DlTongHopCong.thang == thang,
                DlTongHopCong.nam == nam,
            ).first()

            ngay_cong = float(row.get("ngay_cong", 0))
            ngay_nghi = float(row.get("ngay_nghi", 0))
            ngay_phep = float(row.get("ngay_phep", 0))
            lam_them = float(row.get("lam_them", 0))

            if existing:
                # Update existing record
                existing.ngay_cong = ngay_cong
                existing.ngay_nghi = ngay_nghi
                existing.ngay_phep = ngay_phep
                existing.lam_them = lam_them
            else:
                # Create new record
                record = DlTongHopCong(
                    nhan_vien_id=nhan_vien.id,
                    thang=thang,
                    nam=nam,
                    ngay_cong=ngay_cong,
                    ngay_nghi=ngay_nghi,
                    ngay_phep=ngay_phep,
                    lam_them=lam_them,
                )
                self.db.add(record)

            imported_count += 1

        if imported_count > 0:
            self.db.commit()

        return imported_count, errors
