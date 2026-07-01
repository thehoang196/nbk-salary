"""
NBK Salary - Attendance Summary Auto-Calculation Service

Recalculates dl_tong_hop_cong (monthly attendance summary) from individual
dl_cham_cong daily records for an employee in a given month.
"""

from sqlalchemy.orm import Session
from sqlalchemy import extract

from app.models.cham_cong import DlChamCong, DlTongHopCong
from app.models.danh_muc import DmKyHieuCong


class AttendanceService:
    DEFAULT_STANDARD_DAYS = 26

    def __init__(self, db: Session):
        self.db = db

    def recalculate_summary(self, nhan_vien_id: int, thang: int, nam: int) -> DlTongHopCong:
        """Recalculate monthly attendance summary from daily records.

        Sums gia_tri_ngay_cong from dm_ky_hieu_cong for each attendance type:
        - loai "present" → ngay_cong
        - loai "leave" → ngay_nghi
        - loai "overtime" → lam_them
        - loai with gia_tri > 0 that is "holiday" → also counts as ngay_cong

        Phép (paid leave) tracked separately if loai == "leave" and ky_hieu == "P"
        """
        # Get all daily records for this employee/month
        records = (
            self.db.query(DlChamCong, DmKyHieuCong)
            .join(DmKyHieuCong, DlChamCong.ky_hieu_cong_id == DmKyHieuCong.id)
            .filter(
                DlChamCong.nhan_vien_id == nhan_vien_id,
                extract('month', DlChamCong.ngay) == thang,
                extract('year', DlChamCong.ngay) == nam,
            )
            .all()
        )

        ngay_cong = 0.0
        ngay_nghi = 0.0
        ngay_phep = 0.0
        lam_them = 0.0

        for cham_cong, ky_hieu in records:
            gia_tri = float(ky_hieu.gia_tri_ngay_cong)
            loai = ky_hieu.loai.lower()

            if loai == "present" or loai == "holiday":
                ngay_cong += gia_tri
            elif loai == "leave":
                ngay_nghi += 1
                if ky_hieu.ky_hieu == "P":  # Paid leave
                    ngay_phep += 1
            elif loai == "overtime":
                lam_them += gia_tri

        # Upsert dl_tong_hop_cong
        existing = self.db.query(DlTongHopCong).filter(
            DlTongHopCong.nhan_vien_id == nhan_vien_id,
            DlTongHopCong.thang == thang,
            DlTongHopCong.nam == nam,
        ).first()

        if existing:
            existing.ngay_cong = ngay_cong
            existing.ngay_nghi = ngay_nghi
            existing.ngay_phep = ngay_phep
            existing.lam_them = lam_them
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            summary = DlTongHopCong(
                nhan_vien_id=nhan_vien_id,
                thang=thang,
                nam=nam,
                ngay_cong=ngay_cong,
                ngay_nghi=ngay_nghi,
                ngay_phep=ngay_phep,
                lam_them=lam_them,
                cong_chuan=self.DEFAULT_STANDARD_DAYS,
                is_confirmed=False,
            )
            self.db.add(summary)
            self.db.commit()
            self.db.refresh(summary)
            return summary
