
# ============================================================
# FILE: backend/app/services/tax_engine.py
# Tính thuế Thu nhập cá nhân theo biểu lũy tiến
# ============================================================


class TaxEngine:
    """
    Tính thuế TNCN theo quy định Việt Nam
    - Giảm trừ bản thân: 11,000,000 VNĐ/tháng
    - Giảm trừ người phụ thuộc: 4,400,000 VNĐ/người/tháng
    - Biểu thuế lũy tiến từng phần 7 bậc
    """
    
    GIAM_TRU_BAN_THAN = 11_000_000  # VNĐ/tháng
    GIAM_TRU_NPT = 4_400_000        # VNĐ/người/tháng
    
    # Biểu thuế lũy tiến từng phần (VNĐ/tháng)
    TAX_BRACKETS = [
        (5_000_000, 0.05),      # Bậc 1: đến 5tr → 5%
        (10_000_000, 0.10),     # Bậc 2: 5tr - 10tr → 10%
        (18_000_000, 0.15),     # Bậc 3: 10tr - 18tr → 15%
        (32_000_000, 0.20),     # Bậc 4: 18tr - 32tr → 20%
        (52_000_000, 0.25),     # Bậc 5: 32tr - 52tr → 25%
        (80_000_000, 0.30),     # Bậc 6: 52tr - 80tr → 30%
        (float('inf'), 0.35),   # Bậc 7: trên 80tr → 35%
    ]
    
    def calculate_pit(
        self,
        tong_thu_nhap: float,
        bhxh: float,
        bhyt: float,
        bhtn: float,
        so_nguoi_phu_thuoc: int = 0
    ) -> float:
        """
        Tính thuế TNCN tháng
        
        Công thức:
        Thu nhập chịu thuế = Tổng TN - BH bắt buộc - Giảm trừ bản thân - Giảm trừ NPT
        Thuế = Áp dụng biểu lũy tiến lên Thu nhập chịu thuế
        """
        
        # Tổng giảm trừ
        tong_giam_tru = (
            self.GIAM_TRU_BAN_THAN +
            (self.GIAM_TRU_NPT * so_nguoi_phu_thuoc) +
            bhxh + bhyt + bhtn
        )
        
        # Thu nhập chịu thuế
        thu_nhap_chiu_thue = tong_thu_nhap - tong_giam_tru
        
        if thu_nhap_chiu_thue <= 0:
            return 0
        
        # Áp dụng biểu thuế lũy tiến
        thue = 0
        remaining = thu_nhap_chiu_thue
        prev_limit = 0
        
        for limit, rate in self.TAX_BRACKETS:
            bracket_amount = min(remaining, limit - prev_limit)
            if bracket_amount <= 0:
                break
            thue += bracket_amount * rate
            remaining -= bracket_amount
            prev_limit = limit
        
        return round(thue, 0)
    
    def calculate_pit_detail(
        self,
        tong_thu_nhap: float,
        bhxh: float,
        bhyt: float,
        bhtn: float,
        so_nguoi_phu_thuoc: int = 0
    ) -> dict:
        """Trả về chi tiết tính thuế (cho phiếu lương)"""
        
        tong_bh = bhxh + bhyt + bhtn
        giam_tru_npt = self.GIAM_TRU_NPT * so_nguoi_phu_thuoc
        tong_giam_tru = self.GIAM_TRU_BAN_THAN + giam_tru_npt + tong_bh
        thu_nhap_chiu_thue = max(0, tong_thu_nhap - tong_giam_tru)
        thue = self.calculate_pit(tong_thu_nhap, bhxh, bhyt, bhtn, so_nguoi_phu_thuoc)
        
        return {
            "tong_thu_nhap": tong_thu_nhap,
            "tong_bao_hiem": tong_bh,
            "giam_tru_ban_than": self.GIAM_TRU_BAN_THAN,
            "giam_tru_npt": giam_tru_npt,
            "so_nguoi_phu_thuoc": so_nguoi_phu_thuoc,
            "tong_giam_tru": tong_giam_tru,
            "thu_nhap_chiu_thue": thu_nhap_chiu_thue,
            "thue_tncn": thue
        }

