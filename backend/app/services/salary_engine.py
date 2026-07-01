"""
NBK Salary - Salary Calculation Engine

Provides the SalaryEngine class for calculating salary components:
- Teacher (GV): period-based from BCC summary × unit prices × coefficients
- Office Staff (VP): attendance-based (salary_grade × base) × (actual_days / standard_days)
"""

from typing import Dict, List, Optional, Any
from decimal import Decimal
from sqlalchemy.orm import Session

from app.models.nhan_vien import NhanVien, NhomNV, LoaiHopDong
from app.models.hop_dong import DlHopDong
from app.models.tkb import DlTkb, DlTietDayNgoai, DlBccTongTiet
from app.models.danh_muc import DmDonGiaDay, DmHeSoLuong
from app.models.cham_cong import DlTongHopCong
from app.models.ho_tro_luong import DlHoTroLuong
from app.services.luong_khoan_engine import calculate_luong_khoan, get_luong_khoan_breakdown
from app.services.bcc_service import BCCService
from app.services.tax_engine import TaxEngine


# Coefficients for teaching period types
COEFFICIENT_STANDARD = 1.0
COEFFICIENT_TNST_VY = 1.3
COEFFICIENT_K9_LUYEN_THI = 1.5
COEFFICIENT_KH_TA = 1.0
COEFFICIENT_IELTS = 1.0

# Default standard working days
DEFAULT_STANDARD_DAYS = 26
DEFAULT_PROBATION_PCT = 0.85


class SalaryEngine:
    def __init__(self, db: Session):
        self.db = db

    def calculate_teacher_salary(self, nhan_vien_id: int, thang: int, nam: int) -> Dict[str, Any]:
        """Calculate teacher salary from BCC summary and unit prices.
        
        Returns dict with:
        - luong_khoan: int (contracted salary)
        - teaching_income: int (regular teaching from BCC × unit prices)
        - external_income: int (from dl_tiet_day_ngoai)
        - total_teaching: int (teaching + external)
        - breakdown: detailed component list
        - missing_prices: list of Teacher×Subject×Grade combos without unit prices
        """
        nhan_vien = self.db.query(NhanVien).filter(NhanVien.id == nhan_vien_id).first()
        if not nhan_vien or nhan_vien.nhom_nv != NhomNV.GV:
            return {"error": "Nhân viên không tồn tại hoặc không phải GV"}
        
        # Lương khoán
        luong_khoan = calculate_luong_khoan(nhan_vien_id, self.db)
        
        # Regular teaching income from unit prices
        teaching_income, missing_prices, breakdown = self._calc_regular_teaching(nhan_vien_id, thang, nam)
        
        # External teaching income from dl_tiet_day_ngoai
        external_income = self._calc_external_teaching(nhan_vien_id, thang, nam)
        
        return {
            "luong_khoan": luong_khoan,
            "teaching_income": teaching_income,
            "external_income": external_income,
            "total_teaching": teaching_income + external_income,
            "breakdown": breakdown,
            "missing_prices": missing_prices,
        }

    def _calc_regular_teaching(self, nv_id: int, thang: int, nam: int):
        """Calculate regular teaching income from BCC actual periods × unit prices.
        
        For each Teacher×Subject×Grade in the TKB:
        - Get actual periods from BCC thực tế
        - Multiply by Unit_Price × coefficient
        """
        total = 0
        missing = []
        breakdown = []
        
        # Get BCC for this teacher
        bcc_service = BCCService(self.db)
        nhan_vien = self.db.query(NhanVien).filter(NhanVien.id == nv_id).first()
        if not nhan_vien:
            return 0, [], []
        
        bcc_data = bcc_service._calculate_teacher_bcc(nhan_vien, thang, nam)
        if not bcc_data:
            return 0, [], []
        
        thuc_te = bcc_data["thuc_te"]
        
        # Get all active unit prices for this teacher
        unit_prices = self.db.query(DmDonGiaDay).filter(
            DmDonGiaDay.nhan_vien_id == nv_id,
            DmDonGiaDay.is_active == True,
        ).all()
        
        # Calculate using BCC thực tế values
        # Standard teaching periods
        if thuc_te["tiet_chinh_hs1"] > 0:
            avg_price = self._get_avg_unit_price(unit_prices)
            amount = int(thuc_te["tiet_chinh_hs1"] * avg_price * COEFFICIENT_STANDARD)
            total += amount
            breakdown.append({"type": "Tiết chính HS1", "periods": thuc_te["tiet_chinh_hs1"], "coefficient": 1.0, "amount": amount})
        
        # TNST VY
        if thuc_te["tnst_vy"] > 0:
            avg_price = self._get_avg_unit_price(unit_prices)
            amount = int(thuc_te["tnst_vy"] * avg_price * COEFFICIENT_TNST_VY)
            total += amount
            breakdown.append({"type": "TNST VY (HS1.3)", "periods": thuc_te["tnst_vy"], "coefficient": 1.3, "amount": amount})
        
        # K9 luyện thi
        if thuc_te["k9_lt"] > 0:
            avg_price = self._get_avg_unit_price(unit_prices)
            amount = int(thuc_te["k9_lt"] * avg_price * COEFFICIENT_K9_LUYEN_THI)
            total += amount
            breakdown.append({"type": "K9 luyện thi (HS1.5)", "periods": thuc_te["k9_lt"], "coefficient": 1.5, "amount": amount})
        
        # KH TA
        if thuc_te["kh_ta"] > 0:
            avg_price = self._get_avg_unit_price(unit_prices)
            amount = int(thuc_te["kh_ta"] * avg_price * COEFFICIENT_KH_TA)
            total += amount
            breakdown.append({"type": "KH bằng TA", "periods": thuc_te["kh_ta"], "coefficient": 1.0, "amount": amount})
        
        # IELTS
        if thuc_te["ielts"] > 0:
            avg_price = self._get_avg_unit_price(unit_prices)
            amount = int(thuc_te["ielts"] * avg_price * COEFFICIENT_IELTS)
            total += amount
            breakdown.append({"type": "IELTS", "periods": thuc_te["ielts"], "coefficient": 1.0, "amount": amount})
        
        if not unit_prices:
            missing.append({"nhan_vien_id": nv_id, "note": "Không có đơn giá dạy nào"})
        
        return total, missing, breakdown

    def _get_avg_unit_price(self, unit_prices) -> int:
        """Get average unit price from a list of DmDonGiaDay records."""
        if not unit_prices:
            return 0
        total = sum(int(up.don_gia) for up in unit_prices)
        return total // len(unit_prices)

    def _calc_external_teaching(self, nv_id: int, thang: int, nam: int) -> int:
        """Sum external teaching income from dl_tiet_day_ngoai (thanh_tien)."""
        records = self.db.query(DlTietDayNgoai).filter(
            DlTietDayNgoai.nhan_vien_id == nv_id,
            DlTietDayNgoai.thang == thang,
            DlTietDayNgoai.nam == nam,
        ).all()
        
        total = 0
        for r in records:
            if r.thanh_tien:
                total += int(r.thanh_tien)
            else:
                total += int(float(r.so_tiet) * int(r.don_gia) * float(r.he_so))
        
        return total

    def calculate_vp_salary(self, nhan_vien_id: int, thang: int, nam: int) -> Dict[str, Any]:
        """Calculate office staff (VP) salary from attendance data.
        
        Formula: (salary_grade × base) × (actual_days / standard_days)
        With probation percentage if applicable.
        """
        nhan_vien = self.db.query(NhanVien).filter(NhanVien.id == nhan_vien_id).first()
        if not nhan_vien or nhan_vien.nhom_nv != NhomNV.VP:
            return {"error": "Nhân viên không tồn tại hoặc không phải VP"}
        
        # Lương khoán
        luong_khoan = calculate_luong_khoan(nhan_vien_id, self.db)
        
        # Get attendance summary
        tong_hop = self.db.query(DlTongHopCong).filter(
            DlTongHopCong.nhan_vien_id == nhan_vien_id,
            DlTongHopCong.thang == thang,
            DlTongHopCong.nam == nam,
        ).first()
        
        if not tong_hop:
            return {
                "error": "Chưa có dữ liệu chấm công",
                "luong_khoan": luong_khoan,
                "attendance_salary": 0,
            }
        
        actual_days = float(tong_hop.ngay_cong)
        standard_days = tong_hop.cong_chuan or DEFAULT_STANDARD_DAYS
        
        # Get latest contract for salary grade info
        contract = self.db.query(DlHopDong).filter(
            DlHopDong.nhan_vien_id == nhan_vien_id,
            DlHopDong.ngay_ket_thuc == None,  # Active contract
        ).order_by(DlHopDong.ngay_bat_dau.desc()).first()
        
        # Calculate base salary from hệ số
        he_so = 1.0
        luong_co_so = 1_800_000  # Base salary (lương cơ sở)
        if contract and contract.he_so_luong_id:
            he_so_record = self.db.query(DmHeSoLuong).filter(
                DmHeSoLuong.id == contract.he_so_luong_id
            ).first()
            if he_so_record:
                he_so = float(he_so_record.he_so)
        
        # Calculate attendance-based salary
        if standard_days > 0:
            attendance_salary = int((he_so * luong_co_so) * (actual_days / standard_days))
        else:
            attendance_salary = 0
        
        # Apply probation percentage
        probation_pct = 1.0
        if nhan_vien.loai_hop_dong == LoaiHopDong.thu_viec:
            probation_pct = DEFAULT_PROBATION_PCT
            attendance_salary = int(attendance_salary * probation_pct)
        
        return {
            "luong_khoan": luong_khoan,
            "he_so": he_so,
            "actual_days": actual_days,
            "standard_days": standard_days,
            "attendance_salary": attendance_salary,
            "probation_pct": probation_pct,
        }

    def get_support_allowances(self, nhan_vien_id: int, thang: int, nam: int) -> int:
        """Sum all support allowances for an employee in a month."""
        records = self.db.query(DlHoTroLuong).filter(
            DlHoTroLuong.nhan_vien_id == nhan_vien_id,
            DlHoTroLuong.thang == thang,
            DlHoTroLuong.nam == nam,
        ).all()
        return sum(int(r.so_tien) for r in records)

    def calculate_insurance(self, luong_dong_bh: int) -> Dict[str, int]:
        """Calculate insurance deductions from luong_dong_bh.
        
        BH = luong_dong_bh × (8% BHXH + 1.5% BHYT + 1% BHTN) + 1% CĐ
        """
        if not luong_dong_bh:
            return {"bhxh": 0, "bhyt": 0, "bhtn": 0, "cd": 0, "total": 0}
        
        bhxh = int(luong_dong_bh * 0.08)
        bhyt = int(luong_dong_bh * 0.015)
        bhtn = int(luong_dong_bh * 0.01)
        cd = int(luong_dong_bh * 0.01)
        
        return {
            "bhxh": bhxh,
            "bhyt": bhyt,
            "bhtn": bhtn,
            "cd": cd,
            "total": bhxh + bhyt + bhtn + cd,
        }

    def generate_payslip(self, nhan_vien_id: int, thang: int, nam: int,
                         manual_inputs: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate a complete payslip with all 6 sections.
        
        Args:
            nhan_vien_id: Employee ID
            thang, nam: Month/year
            manual_inputs: Optional dict with manually entered values:
                - tien_de_thi: Exam fees (Section II item 3)
                - sinh_nhat: Birthday bonus (item 5)
                - lam_them_thuong: Overtime/efficiency bonus (item 6)
                - thuong_su_kien: Event bonus (item 7)
                - bu_luong: Salary supplement (item 8)
                - thuong_tet: Tet bonus (item 9)
                - da_nhan: Bonuses already received (Section III)
                - doan_phi: Union fee (Section IV item 2)
                - tich_luy: Accumulation (Section IV item 3)
                - truy_thu: Recovery (Section IV item 5)
        
        Returns dict with all 6 sections as JSON-serializable data.
        """
        nhan_vien = self.db.query(NhanVien).filter(NhanVien.id == nhan_vien_id).first()
        if not nhan_vien:
            return {"error": "Nhân viên không tồn tại"}

        manual = manual_inputs or {}

        # Get active contract
        contract = self.db.query(DlHopDong).filter(
            DlHopDong.nhan_vien_id == nhan_vien_id,
            DlHopDong.ngay_ket_thuc == None,
        ).order_by(DlHopDong.ngay_bat_dau.desc()).first()

        luong_dong_bh = int(contract.luong_dong_bh or 0) if contract else 0
        luong_khoan = calculate_luong_khoan(nhan_vien_id, self.db)

        # Get attendance data
        tong_hop = self.db.query(DlTongHopCong).filter(
            DlTongHopCong.nhan_vien_id == nhan_vien_id,
            DlTongHopCong.thang == thang,
            DlTongHopCong.nam == nam,
        ).first()

        ngay_cong = float(tong_hop.ngay_cong) if tong_hop else 0
        cong_chuan = (tong_hop.cong_chuan if tong_hop else DEFAULT_STANDARD_DAYS) or DEFAULT_STANDARD_DAYS

        # Section I: Employee Info
        luong_khoan_breakdown = get_luong_khoan_breakdown(nhan_vien_id, self.db)
        muc_i = {
            "ho_ten": nhan_vien.ho_ten,
            "ten_goi": nhan_vien.ten_goi,
            "ma_nv": nhan_vien.ma_nv,
            "nhom_nv": nhan_vien.nhom_nv.value,
            "luong_khoan": luong_khoan,
            "luong_dong_bh": luong_dong_bh,
            "ngay_cong": ngay_cong,
            "cong_chuan": cong_chuan,
            "luong_khoan_breakdown": luong_khoan_breakdown,
        }

        # Section II: Total Income (9 items)
        # Item 1: Lương khoán prorated
        luong_khoan_prorated = int(luong_khoan * ngay_cong / cong_chuan) if cong_chuan > 0 else 0

        # Item 2: Teaching income (GV) or attendance salary (VP)
        if nhan_vien.nhom_nv == NhomNV.GV:
            salary_data = self.calculate_teacher_salary(nhan_vien_id, thang, nam)
            tien_giang_day = salary_data.get("total_teaching", 0)
        else:
            salary_data = self.calculate_vp_salary(nhan_vien_id, thang, nam)
            tien_giang_day = salary_data.get("attendance_salary", 0)

        # Item 3: Exam fees (manual)
        tien_de_thi = manual.get("tien_de_thi", 0)

        # Item 4: Support allowances (from dl_ho_tro_luong)
        ho_tro = self.get_support_allowances(nhan_vien_id, thang, nam)

        # Items 5-9: Manual inputs
        sinh_nhat = manual.get("sinh_nhat", 0)
        lam_them_thuong = manual.get("lam_them_thuong", 0)
        thuong_su_kien = manual.get("thuong_su_kien", 0)
        bu_luong = manual.get("bu_luong", 0)
        thuong_tet = manual.get("thuong_tet", 0)

        tong_thu_nhap = (luong_khoan_prorated + tien_giang_day + tien_de_thi +
                         ho_tro + sinh_nhat + lam_them_thuong +
                         thuong_su_kien + bu_luong + thuong_tet)

        muc_ii = {
            "luong_khoan_prorated": luong_khoan_prorated,
            "tien_giang_day": tien_giang_day,
            "tien_de_thi": tien_de_thi,
            "ho_tro": ho_tro,
            "sinh_nhat": sinh_nhat,
            "lam_them_thuong": lam_them_thuong,
            "thuong_su_kien": thuong_su_kien,
            "bu_luong": bu_luong,
            "thuong_tet": thuong_tet,
            "tong": tong_thu_nhap,
        }

        # Section III: Bonuses Already Received
        da_nhan = manual.get("da_nhan", 0)
        muc_iii = {"da_nhan": da_nhan}

        # Section IV: Deductions
        insurance = self.calculate_insurance(luong_dong_bh)
        doan_phi = manual.get("doan_phi", 0)
        tich_luy = manual.get("tich_luy", 0)
        # Calculate PIT using tax engine
        tax_engine = TaxEngine()
        thue_tncn = tax_engine.calculate_monthly_pit(
            total_income=tong_thu_nhap,
            insurance=insurance["total"],
            dependents=nhan_vien.so_nguoi_phu_thuoc,
        )
        truy_thu = manual.get("truy_thu", 0)

        tong_giam_tru = insurance["total"] + doan_phi + tich_luy + thue_tncn + truy_thu

        muc_iv = {
            "bh_cd": insurance["total"],
            "bh_detail": insurance,
            "doan_phi": doan_phi,
            "tich_luy": tich_luy,
            "thue_tncn": thue_tncn,
            "truy_thu": truy_thu,
            "tong": tong_giam_tru,
        }

        # Section V: Tax Settlement (zero unless year-end)
        muc_v = {"quyet_toan": 0}

        # Section VI: Net Pay
        thuc_linh = tong_thu_nhap - da_nhan - tong_giam_tru + muc_v["quyet_toan"]

        return {
            "nhan_vien_id": nhan_vien_id,
            "thang": thang,
            "nam": nam,
            "muc_i": muc_i,
            "muc_ii": muc_ii,
            "muc_iii": muc_iii,
            "muc_iv": muc_iv,
            "muc_v": muc_v,
            "muc_vi_thuc_linh": thuc_linh,
        }
