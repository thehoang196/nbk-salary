"""
NBK Salary - BCC Summary Calculation Service

Calculates the BCC tổng tiết report with 4 column groups:
1. Theo TKB (scheduled periods from timetable)
2. Thay đổi (changes from substitution records)
3. Phát sinh (adjustments from external period table)
4. Thực tế (actual = TKB - changes + adjustments)

Thực tế formula per sub-column:
  Tiết chính HS1 = TKB(tổng tiết chính) - Nghỉ(K6-8) - Nghỉ(K9) + Thay(K6-8) + Thay(K9) + Phát sinh(tiết chính)
  TNST VY (HS1.3) = from separate tracking
  K9 luyện thi (HS1.5) = from separate tracking
  KH TA = TKB(KH TA) - Nghỉ(KH TA) + Thay(KH TA) + Phát sinh(KH TA)
  Ielts = TKB(Ielts) - Nghỉ(Ielts) + Thay(Ielts) + Phát sinh(Ielts)
  Tổng = (Tiết chính × 1.0) + (TNST VY × 1.3) + (K9 LT × 1.5) + (KH TA × 1.0) + (Ielts × 1.0)
"""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from app.models.tkb import DlTkb, DlThayDoiNguoiDay, DlBccTongTiet, DlTietDayNgoai
from app.models.nhan_vien import NhanVien, NhomNV


class BCCService:
    def __init__(self, db: Session):
        self.db = db

    def calculate_bcc(self, thang: int, nam: int) -> List[Dict]:
        """Calculate BCC summary for all teachers in a given month.

        Returns list of dicts matching BCCTeacherRow schema.
        """
        # Get all GV employees
        teachers = self.db.query(NhanVien).filter(NhanVien.nhom_nv == NhomNV.GV).all()

        results = []
        for teacher in teachers:
            row = self._calculate_teacher_bcc(teacher, thang, nam)
            if row:  # Only include teachers with TKB data
                results.append(row)

        return results

    def _calculate_teacher_bcc(self, teacher: NhanVien, thang: int, nam: int) -> Optional[Dict]:
        """Calculate BCC for a single teacher."""

        # 1. Theo TKB - sum periods by loai_tiet
        tkb_records = self.db.query(DlTkb).filter(
            DlTkb.nhan_vien_id == teacher.id,
            DlTkb.thang == thang,
            DlTkb.nam == nam,
        ).all()

        if not tkb_records:
            return None  # Teacher not in TKB this month

        theo_tkb = self._sum_tkb_periods(tkb_records)

        # 2. Thay đổi - sum changes where teacher is gv_goc (nghỉ) or gv_thay (thay)
        thay_doi = self._calculate_changes(teacher.id, thang, nam)

        # 3. Phát sinh - from dl_tiet_day_ngoai
        phat_sinh = self._calculate_phat_sinh(teacher.id, thang, nam)

        # 4. Thực tế - combine all
        thuc_te = self._calculate_thuc_te(theo_tkb, thay_doi, phat_sinh)

        # Check completeness
        is_complete = True  # Can be more sophisticated

        return {
            "nhan_vien_id": teacher.id,
            "ho_ten": teacher.ho_ten,
            "theo_tkb": theo_tkb,
            "thay_doi": thay_doi,
            "phat_sinh": phat_sinh,
            "thuc_te": thuc_te,
            "is_complete": is_complete,
        }

    def _sum_tkb_periods(self, records) -> Dict[str, float]:
        """Sum TKB periods by type."""
        result = {
            "tong_tiet_chinh": 0.0,
            "kh_ta": 0.0,
            "ielts": 0.0,
            "tnst_vy": 0.0,
            "k9_luyen_thi": 0.0,
        }
        for r in records:
            if r.loai_tiet == "chinh_khoa":
                result["tong_tiet_chinh"] += r.so_tiet
            elif r.loai_tiet == "kh_ta":
                result["kh_ta"] += r.so_tiet
            elif r.loai_tiet == "ielts":
                result["ielts"] += r.so_tiet
            elif r.loai_tiet == "tnst_vy":
                result["tnst_vy"] += r.so_tiet
            elif r.loai_tiet == "k9_luyen_thi":
                result["k9_luyen_thi"] += r.so_tiet
        return result

    def _calculate_changes(self, nv_id: int, thang: int, nam: int) -> Dict[str, float]:
        """Calculate change totals: nghỉ (as gv_goc) and thay (as gv_thay)."""
        result = {
            "nghi_k6_8": 0.0,
            "nghi_k9": 0.0,
            "nghi_kh_ta": 0.0,
            "nghi_ielts": 0.0,
            "thay_k6_8": 0.0,
            "thay_k9": 0.0,
            "thay_kh_ta": 0.0,
            "thay_ielts": 0.0,
        }

        # Nghỉ: records where this teacher is gv_goc
        nghi_records = self.db.query(DlThayDoiNguoiDay).filter(
            DlThayDoiNguoiDay.gv_goc_id == nv_id,
            DlThayDoiNguoiDay.thang == thang,
            DlThayDoiNguoiDay.nam == nam,
        ).all()

        for r in nghi_records:
            # Determine category based on subject/grade
            # Simplified: count as K6-8 by default
            result["nghi_k6_8"] += 1

        # Thay: records where this teacher is gv_thay
        thay_records = self.db.query(DlThayDoiNguoiDay).filter(
            DlThayDoiNguoiDay.gv_thay_id == nv_id,
            DlThayDoiNguoiDay.thang == thang,
            DlThayDoiNguoiDay.nam == nam,
        ).all()

        for r in thay_records:
            result["thay_k6_8"] += 1

        return result

    def _calculate_phat_sinh(self, nv_id: int, thang: int, nam: int) -> Dict[str, float]:
        """Get phát sinh from dl_tiet_day_ngoai (consolidated external periods)."""
        result = {
            "tiet_chinh": 0.0,
            "tnst_vy": 0.0,
            "k9_lt": 0.0,
            "kh_ta": 0.0,
            "ielts": 0.0,
        }

        records = self.db.query(DlTietDayNgoai).filter(
            DlTietDayNgoai.nhan_vien_id == nv_id,
            DlTietDayNgoai.thang == thang,
            DlTietDayNgoai.nam == nam,
        ).all()

        for r in records:
            loai = r.loai.lower() if r.loai else ""
            if "ielts" in loai:
                result["ielts"] += float(r.so_tiet)
            elif "vĩnh yên" in loai or "vy" in loai:
                result["tnst_vy"] += float(r.so_tiet)
            elif "luyện thi" in loai or "k9" in loai:
                result["k9_lt"] += float(r.so_tiet)
            elif "kh" in loai and "ta" in loai:
                result["kh_ta"] += float(r.so_tiet)
            else:
                result["tiet_chinh"] += float(r.so_tiet)

        return result

    def _calculate_thuc_te(
        self, theo_tkb: Dict[str, float], thay_doi: Dict[str, float], phat_sinh: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate actual periods from TKB, changes, and adjustments."""
        tiet_chinh = (
            theo_tkb["tong_tiet_chinh"]
            - thay_doi["nghi_k6_8"]
            - thay_doi["nghi_k9"]
            + thay_doi["thay_k6_8"]
            + thay_doi["thay_k9"]
            + phat_sinh["tiet_chinh"]
        )
        tnst_vy = theo_tkb["tnst_vy"] + phat_sinh["tnst_vy"]
        k9_lt = theo_tkb["k9_luyen_thi"] + phat_sinh["k9_lt"]
        kh_ta = (
            theo_tkb["kh_ta"]
            - thay_doi["nghi_kh_ta"]
            + thay_doi["thay_kh_ta"]
            + phat_sinh["kh_ta"]
        )
        ielts = (
            theo_tkb["ielts"]
            - thay_doi["nghi_ielts"]
            + thay_doi["thay_ielts"]
            + phat_sinh["ielts"]
        )

        # Tổng with weighted coefficients
        tong = (tiet_chinh * 1.0) + (tnst_vy * 1.3) + (k9_lt * 1.5) + (kh_ta * 1.0) + (ielts * 1.0)

        return {
            "tiet_chinh_hs1": round(tiet_chinh, 1),
            "tnst_vy": round(tnst_vy, 1),
            "k9_lt": round(k9_lt, 1),
            "kh_ta": round(kh_ta, 1),
            "ielts": round(ielts, 1),
            "tong": round(tong, 1),
        }
