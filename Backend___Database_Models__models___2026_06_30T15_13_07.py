
# ============================================================
# FILE: backend/app/models/danh_muc.py
# Database models cho các danh mục
# ============================================================

from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"          # Ban Giám Hiệu
    ACCOUNTANT = "accountant"  # Kế toán
    HR = "hr"                # Nhân sự
    TEACHER = "teacher"      # Giáo viên


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.TEACHER)
    ma_nhan_vien = Column(String(20), ForeignKey("nhan_vien.ma_nv"), nullable=True)
    is_active = Column(Boolean, default=True)


class DonVi(Base):
    """Danh mục đơn vị (phòng ban)"""
    __tablename__ = "dm_don_vi"
    
    id = Column(Integer, primary_key=True, index=True)
    ma_don_vi = Column(String(20), unique=True, nullable=False)
    ten_don_vi = Column(String(100), nullable=False)
    ghi_chu = Column(Text, nullable=True)


class ChucDanh(Base):
    """Danh mục chức danh"""
    __tablename__ = "dm_chuc_danh"
    
    id = Column(Integer, primary_key=True, index=True)
    ma_chuc_danh = Column(String(20), unique=True, nullable=False)
    ten_chuc_danh = Column(String(100), nullable=False)


class Khoi(Base):
    """Danh mục khối (Khối 6, 7, 8, 9)"""
    __tablename__ = "dm_khoi"
    
    id = Column(Integer, primary_key=True, index=True)
    ten_khoi = Column(String(50), nullable=False)
    ghi_chu = Column(Text, nullable=True)


class Lop(Base):
    """Danh mục lớp"""
    __tablename__ = "dm_lop"
    
    id = Column(Integer, primary_key=True, index=True)
    ten_lop = Column(String(20), nullable=False)
    khoi_id = Column(Integer, ForeignKey("dm_khoi.id"), nullable=False)
    khoi = relationship("Khoi")


class MonHoc(Base):
    """Danh mục môn học"""
    __tablename__ = "dm_mon_hoc"
    
    id = Column(Integer, primary_key=True, index=True)
    ma_mon = Column(String(20), unique=True, nullable=False)
    ten_mon = Column(String(100), nullable=False)


class ViTriCongViec(Base):
    """Danh mục vị trí công việc"""
    __tablename__ = "dm_vi_tri"
    
    id = Column(Integer, primary_key=True, index=True)
    ma_vi_tri = Column(String(20), unique=True, nullable=False)
    ten_vi_tri = Column(String(100), nullable=False)
    don_vi_id = Column(Integer, ForeignKey("dm_don_vi.id"))
    khoi_id = Column(Integer, ForeignKey("dm_khoi.id"), nullable=True)
    chuc_danh_id = Column(Integer, ForeignKey("dm_chuc_danh.id"))
    
    don_vi = relationship("DonVi")
    khoi = relationship("Khoi")
    chuc_danh = relationship("ChucDanh")


class HeSoLuong(Base):
    """Danh mục hệ số lương (nhóm + bậc)"""
    __tablename__ = "dm_he_so_luong"
    
    id = Column(Integer, primary_key=True, index=True)
    nhom = Column(String(50), nullable=False)
    bac = Column(Integer, nullable=False)
    he_so = Column(Float, nullable=False)


class KyHieuCong(Base):
    """Danh mục ký hiệu chấm công"""
    __tablename__ = "dm_ky_hieu_cong"
    
    id = Column(Integer, primary_key=True, index=True)
    ma_ky_hieu = Column(String(10), unique=True, nullable=False)  # X, P, Ô, TC, NB...
    so_cong = Column(Float, nullable=False)  # 1, 0.5, 0, 1.5...
    ghi_chu = Column(String(100), nullable=True)


class NhiemVu(Base):
    """Danh mục nhiệm vụ + đơn giá"""
    __tablename__ = "dm_nhiem_vu"
    
    id = Column(Integer, primary_key=True, index=True)
    ma_nhiem_vu = Column(String(20), unique=True, nullable=False)
    ten_nhiem_vu = Column(String(200), nullable=False)
    don_gia = Column(Float, nullable=False, default=0)


# ============================================================
# FILE: backend/app/models/nhan_vien.py
# ============================================================

class NhanVien(Base):
    """Thông tin nhân viên"""
    __tablename__ = "nhan_vien"
    
    id = Column(Integer, primary_key=True, index=True)
    ma_nv = Column(String(20), unique=True, nullable=False)
    ho_ten = Column(String(100), nullable=False)
    ngay_sinh = Column(Date, nullable=True)
    gioi_tinh = Column(String(10), nullable=True)
    don_vi_id = Column(Integer, ForeignKey("dm_don_vi.id"))
    vi_tri_id = Column(Integer, ForeignKey("dm_vi_tri.id"))
    chuc_danh_id = Column(Integer, ForeignKey("dm_chuc_danh.id"))
    ngay_vao = Column(Date, nullable=True)
    ngay_chinh_thuc = Column(Date, nullable=True)
    ngay_thoi_viec = Column(Date, nullable=True)
    so_tai_khoan = Column(String(30), nullable=True)
    ngan_hang = Column(String(100), nullable=True)
    is_giao_vien = Column(Boolean, default=True)  # True=GV, False=VP
    is_active = Column(Boolean, default=True)
    
    don_vi = relationship("DonVi")
    vi_tri = relationship("ViTriCongViec")
    chuc_danh = relationship("ChucDanh")
    hop_dong = relationship("HopDong", back_populates="nhan_vien")


class HopDong(Base):
    """Hợp đồng & Lịch sử lương"""
    __tablename__ = "dl_hop_dong"
    
    id = Column(Integer, primary_key=True, index=True)
    nhan_vien_id = Column(Integer, ForeignKey("nhan_vien.id"), nullable=False)
    so_hop_dong = Column(String(50), nullable=True)
    ngay_bat_dau = Column(Date, nullable=False)
    ngay_ket_thuc = Column(Date, nullable=True)
    luong_co_ban = Column(Float, nullable=False, default=0)
    phu_cap_1 = Column(Float, default=0)  # Phụ cấp chức vụ
    phu_cap_2 = Column(Float, default=0)  # Phụ cấp trách nhiệm
    phu_cap_3 = Column(Float, default=0)  # Phụ cấp thâm niên
    phu_cap_4 = Column(Float, default=0)  # Phụ cấp ăn trưa
    phu_cap_5 = Column(Float, default=0)  # Phụ cấp khác
    ty_le_bhxh = Column(Float, default=8.0)   # % BHXH
    ty_le_bhyt = Column(Float, default=1.5)   # % BHYT
    ty_le_bhtn = Column(Float, default=1.0)   # % BHTN
    
    nhan_vien = relationship("NhanVien", back_populates="hop_dong")


# ============================================================
# FILE: backend/app/models/thoi_khoa_bieu.py
# ============================================================

class DonGiaDay(Base):
    """Bảng đơn giá lương dạy: GV × Môn × Khối"""
    __tablename__ = "dm_don_gia_day"
    
    id = Column(Integer, primary_key=True, index=True)
    nhan_vien_id = Column(Integer, ForeignKey("nhan_vien.id"), nullable=False)
    mon_hoc_id = Column(Integer, ForeignKey("dm_mon_hoc.id"), nullable=False)
    khoi_id = Column(Integer, ForeignKey("dm_khoi.id"), nullable=False)
    don_gia_tiet = Column(Float, nullable=False)  # VNĐ/tiết
    ap_dung_tu = Column(Date, nullable=False)
    ap_dung_den = Column(Date, nullable=True)  # null = hiện tại
    ghi_chu = Column(Text, nullable=True)
    
    nhan_vien = relationship("NhanVien")
    mon_hoc = relationship("MonHoc")
    khoi = relationship("Khoi")


class ThoiKhoaBieu(Base):
    """Thời khóa biểu gốc"""
    __tablename__ = "dl_tkb"
    
    id = Column(Integer, primary_key=True, index=True)
    nam_hoc = Column(String(20), nullable=False)  # "2025-2026"
    hoc_ky = Column(Integer, nullable=False)       # 1 hoặc 2
    nhan_vien_id = Column(Integer, ForeignKey("nhan_vien.id"), nullable=False)
    mon_hoc_id = Column(Integer, ForeignKey("dm_mon_hoc.id"), nullable=False)
    khoi_id = Column(Integer, ForeignKey("dm_khoi.id"), nullable=False)
    lop_id = Column(Integer, ForeignKey("dm_lop.id"), nullable=False)
    so_tiet_tuan = Column(Integer, nullable=False)  # Số tiết/tuần
    thu_trong_tuan = Column(Integer, nullable=True)  # 2-7 (T2-T7)
    tiet_bat_dau = Column(Integer, nullable=True)
    
    nhan_vien = relationship("NhanVien")
    mon_hoc = relationship("MonHoc")
    khoi = relationship("Khoi")
    lop = relationship("Lop")


class ThayDoiNguoiDay(Base):
    """Bảng thay đổi người dạy"""
    __tablename__ = "dl_thay_doi_nguoi_day"
    
    id = Column(Integer, primary_key=True, index=True)
    tkb_id = Column(Integer, ForeignKey("dl_tkb.id"), nullable=False)
    ngay_bat_dau = Column(Date, nullable=False)
    ngay_ket_thuc = Column(Date, nullable=True)  # null = vĩnh viễn
    gv_thay_the_id = Column(Integer, ForeignKey("nhan_vien.id"), nullable=False)
    ly_do = Column(Text, nullable=True)
    
    tkb_goc = relationship("ThoiKhoaBieu")
    gv_thay_the = relationship("NhanVien")


# ============================================================
# FILE: backend/app/models/cham_cong.py
# ============================================================

class ChamCong(Base):
    """Chấm công theo ngày"""
    __tablename__ = "dl_cham_cong"
    
    id = Column(Integer, primary_key=True, index=True)
    nhan_vien_id = Column(Integer, ForeignKey("nhan_vien.id"), nullable=False)
    ngay = Column(Date, nullable=False)
    ky_hieu = Column(String(10), nullable=True)  # X, P, Ô, TC...
    so_gio_tang_ca = Column(Float, default=0)
    ghi_chu = Column(Text, nullable=True)
    
    nhan_vien = relationship("NhanVien")


class TongHopCong(Base):
    """Tổng hợp công theo tháng (auto-calculated)"""
    __tablename__ = "dl_tong_hop_cong"
    
    id = Column(Integer, primary_key=True, index=True)
    nhan_vien_id = Column(Integer, ForeignKey("nhan_vien.id"), nullable=False)
    thang = Column(Integer, nullable=False)  # 1-12
    nam = Column(Integer, nullable=False)
    so_cong_chuan = Column(Float, default=22)  # Số ngày làm việc chuẩn
    so_cong_thu_viec = Column(Float, default=0)
    so_cong_chinh_thuc = Column(Float, default=0)
    so_gio_tang_ca = Column(Float, default=0)
    so_ngay_nghi_phep = Column(Float, default=0)
    so_ngay_nghi_khong_luong = Column(Float, default=0)
    
    nhan_vien = relationship("NhanVien")


# ============================================================
# FILE: backend/app/models/luong.py
# ============================================================

class BangLuong(Base):
    """Bảng lương theo tháng"""
    __tablename__ = "dl_bang_luong"
    
    id = Column(Integer, primary_key=True, index=True)
    nhan_vien_id = Column(Integer, ForeignKey("nhan_vien.id"), nullable=False)
    thang = Column(Integer, nullable=False)
    nam = Column(Integer, nullable=False)
    
    # Thu nhập
    luong_chuc_danh = Column(Float, default=0)
    luong_chinh = Column(Float, default=0)      # Lương theo công
    luong_day = Column(Float, default=0)         # Lương dạy (GV)
    luong_hieu_qua = Column(Float, default=0)    # Lương hiệu quả/KPI
    phu_cap_1 = Column(Float, default=0)
    phu_cap_2 = Column(Float, default=0)
    phu_cap_3 = Column(Float, default=0)
    phu_cap_4 = Column(Float, default=0)
    phu_cap_5 = Column(Float, default=0)
    tang_ca = Column(Float, default=0)
    thuong = Column(Float, default=0)
    bo_sung = Column(Float, default=0)
    
    # Khấu trừ
    giam_luong = Column(Float, default=0)
    bhxh = Column(Float, default=0)
    bhyt = Column(Float, default=0)
    bhtn = Column(Float, default=0)
    
    # Thuế
    so_nguoi_phu_thuoc = Column(Integer, default=0)
    thue_tncn = Column(Float, default=0)
    
    # Kết quả
    tong_thu_nhap = Column(Float, default=0)
    tong_khau_tru = Column(Float, default=0)
    thuc_linh = Column(Float, default=0)
    
    # Trạng thái
    trang_thai = Column(String(20), default="draft")  # draft, reviewed, approved
    nguoi_tinh = Column(String(50), nullable=True)
    nguoi_duyet = Column(String(50), nullable=True)
    ngay_duyet = Column(Date, nullable=True)
    
    nhan_vien = relationship("NhanVien")
</parameter>
</invoke>```python

# ============================================================
# FILE: backend/app/services/salary_engine.py
# Core Engine tính lương - Logic nghiệp vụ chính
# ============================================================

from datetime import date, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.luong import BangLuong
from app.models.nhan_vien import NhanVien, HopDong
from app.models.thoi_khoa_bieu import ThoiKhoaBieu, ThayDoiNguoiDay, DonGiaDay
from app.models.cham_cong import ChamCong, TongHopCong
from app.services.tax_engine import TaxEngine
import calendar


class SalaryEngine:
    """Engine tính lương cho cả khối GV và VP"""
    
    def __init__(self, db: Session):
        self.db = db
        self.tax_engine = TaxEngine()
    
    # ========================================================
    # MAIN: Tính lương cho 1 nhân viên, 1 tháng
    # ========================================================
    def calculate_salary(self, nhan_vien_id: int, thang: int, nam: int) -> BangLuong:
        """Tính lương đầy đủ cho 1 NV trong 1 tháng"""
        
        nv = self.db.query(NhanVien).filter(NhanVien.id == nhan_vien_id).first()
        if not nv:
            raise ValueError(f"Không tìm thấy nhân viên ID: {nhan_vien_id}")
        
        # Lấy hợp đồng hiện hành
        hop_dong = self._get_active_contract(nhan_vien_id, thang, nam)
        if not hop_dong:
            raise ValueError(f"Không có hợp đồng cho NV {nv.ho_ten} tháng {thang}/{nam}")
        
        # Khởi tạo bảng lương
        bang_luong = BangLuong(
            nhan_vien_id=nhan_vien_id,
            thang=thang,
            nam=nam,
            trang_thai="draft"
        )
        
        # 1. Lương chức danh (theo hợp đồng)
        bang_luong.luong_chuc_danh = hop_dong.luong_co_ban
        
        # 2. Lương chính (theo công)
        tong_hop_cong = self._get_tong_hop_cong(nhan_vien_id, thang, nam)
        bang_luong.luong_chinh = self._tinh_luong_chinh(hop_dong, tong_hop_cong)
        
        # 3. Lương dạy (chỉ cho GV)
        if nv.is_giao_vien:
            bang_luong.luong_day = self._tinh_luong_day(nhan_vien_id, thang, nam)
        
        # 4. Lương hiệu quả (nhập tay - lấy từ DB nếu đã có)
        # bang_luong.luong_hieu_qua = manual input
        
        # 5. Phụ cấp (từ hợp đồng)
        bang_luong.phu_cap_1 = hop_dong.phu_cap_1
        bang_luong.phu_cap_2 = hop_dong.phu_cap_2
        bang_luong.phu_cap_3 = hop_dong.phu_cap_3
        bang_luong.phu_cap_4 = hop_dong.phu_cap_4
        bang_luong.phu_cap_5 = hop_dong.phu_cap_5
        
        # 6. Tăng ca
        if tong_hop_cong:
            bang_luong.tang_ca = self._tinh_tang_ca(hop_dong, tong_hop_cong)
        
        # 7. Tổng thu nhập
        bang_luong.tong_thu_nhap = (
            bang_luong.luong_chinh +
            bang_luong.luong_day +
            bang_luong.luong_hieu_qua +
            bang_luong.phu_cap_1 +
            bang_luong.phu_cap_2 +
            bang_luong.phu_cap_3 +
            bang_luong.phu_cap_4 +
            bang_luong.phu_cap_5 +
            bang_luong.tang_ca +
            bang_luong.thuong +
            bang_luong.bo_sung
        )
        
        # 8. Bảo hiểm (khấu trừ)
        luong_dong_bh = hop_dong.luong_co_ban  # Lương đóng BH
        bang_luong.bhxh = luong_dong_bh * hop_dong.ty_le_bhxh / 100
        bang_luong.bhyt = luong_dong_bh * hop_dong.ty_le_bhyt / 100
        bang_luong.bhtn = luong_dong_bh * hop_dong.ty_le_bhtn / 100
        
        # 9. Thuế TNCN
        bang_luong.thue_tncn = self.tax_engine.calculate_pit(
            tong_thu_nhap=bang_luong.tong_thu_nhap,
            bhxh=bang_luong.bhxh,
            bhyt=bang_luong.bhyt,
            bhtn=bang_luong.bhtn,
            so_nguoi_phu_thuoc=bang_luong.so_nguoi_phu_thuoc
        )
        
        # 10. Tổng khấu trừ
        bang_luong.tong_khau_tru = (
            bang_luong.giam_luong +
            bang_luong.bhxh +
            bang_luong.bhyt +
            bang_luong.bhtn +
            bang_luong.thue_tncn
        )
        
        # 11. Thực lĩnh
        bang_luong.thuc_linh = bang_luong.tong_thu_nhap - bang_luong.tong_khau_tru
        
        return bang_luong
    
    # ========================================================
    # Tính lương cho TOÀN BỘ nhân viên trong 1 tháng
    # ========================================================
    def calculate_all(self, thang: int, nam: int) -> List[BangLuong]:
        """Tính lương cho tất cả NV active trong tháng"""
        
        nhan_viens = self.db.query(NhanVien).filter(
            NhanVien.is_active == True,
            (NhanVien.ngay_thoi_viec == None) | (NhanVien.ngay_thoi_viec >= date(nam, thang, 1))
        ).all()
        
        results = []
        errors = []
        
        for nv in nhan_viens:
            try:
                bang_luong = self.calculate_salary(nv.id, thang, nam)
                results.append(bang_luong)
            except Exception as e:
                errors.append({"nhan_vien": nv.ho_ten, "error": str(e)})
        
        return {"results": results, "errors": errors}
    
    # ========================================================
    # PRIVATE: Tính lương dạy từ TKB
    # ========================================================
    def _tinh_luong_day(self, nhan_vien_id: int, thang: int, nam: int) -> float:
        """
        Tính lương dạy = Σ(Số tiết thực dạy × Đơn giá)
        Có tính đến bảng thay đổi người dạy
        """
        
        # Xác định khoảng thời gian tháng
        ngay_dau = date(nam, thang, 1)
        ngay_cuoi = date(nam, thang, calendar.monthrange(nam, thang)[1])
        
        # Số tuần trong tháng (tính chính xác)
        so_tuan = self._dem_so_tuan(ngay_dau, ngay_cuoi)
        
        tong_luong_day = 0.0
        
        # --- PHẦN 1: Tiết dạy theo TKB gốc (trừ các tiết đã bị thay) ---
        tkb_entries = self.db.query(ThoiKhoaBieu).filter(
            ThoiKhoaBieu.nhan_vien_id == nhan_vien_id
        ).all()
        
        for entry in tkb_entries:
            # Kiểm tra có bị thay thế trong tháng này không
            thay_doi = self.db.query(ThayDoiNguoiDay).filter(
                ThayDoiNguoiDay.tkb_id == entry.id,
                ThayDoiNguoiDay.ngay_bat_dau <= ngay_cuoi,
                (ThayDoiNguoiDay.ngay_ket_thuc == None) | 
                (ThayDoiNguoiDay.ngay_ket_thuc >= ngay_dau)
            ).first()
            
            if thay_doi:
                # Tính số tuần GV gốc vẫn dạy (trước khi bị thay)
                tuan_day = self._tinh_tuan_day_goc(
                    ngay_dau, ngay_cuoi, 
                    thay_doi.ngay_bat_dau, thay_doi.ngay_ket_thuc
                )
            else:
                tuan_day = so_tuan
            
            # Lấy đơn giá
            don_gia = self._get_don_gia(nhan_vien_id, entry.mon_hoc_id, entry.khoi_id, ngay_dau)
            
            # Lương dạy cho entry này
            so_tiet = entry.so_tiet_tuan * tuan_day
            tong_luong_day += so_tiet * don_gia
        
        # --- PHẦN 2: Tiết dạy thay thế (GV này thay người khác) ---
        thay_the_entries = self.db.query(ThayDoiNguoiDay).filter(
            ThayDoiNguoiDay.gv_thay_the_id == nhan_vien_id,
            ThayDoiNguoiDay.ngay_bat_dau <= ngay_cuoi,
            (ThayDoiNguoiDay.ngay_ket_thuc == None) | 
            (ThayDoiNguoiDay.ngay_ket_thuc >= ngay_dau)
        ).all()
        
        for thay_the in thay_the_entries:
            tkb_goc = thay_the.tkb_goc
            tuan_thay = self._tinh_tuan_thay_the(
                ngay_dau, ngay_cuoi,
                thay_the.ngay_bat_dau, thay_the.ngay_ket_thuc
            )
            
            # Đơn giá của GV thay thế (có thể khác GV gốc)
            don_gia = self._get_don_gia(
                nhan_vien_id, tkb_goc.mon_hoc_id, tkb_goc.khoi_id, ngay_dau
            )
            
            so_tiet = tkb_goc.so_tiet_tuan * tuan_thay
            tong_luong_day += so_tiet * don_gia
        
        return tong_luong_day
    
    # ========================================================
    # PRIVATE: Tính lương chính theo công
    # ========================================================
    def _tinh_luong_chinh(self, hop_dong: HopDong, tong_hop_cong: Optional[TongHopCong]) -> float:
        """Lương chính = Lương CB × (Công thực / Công chuẩn)"""
        
        if not tong_hop_cong:
            return hop_dong.luong_co_ban
        
        so_cong_chuan = tong_hop_cong.so_cong_chuan or 22
        so_cong_thuc = tong_hop_cong.so_cong_chinh_thuc + (tong_hop_cong.so_cong_thu_viec * 0.85)
        
        if so_cong_chuan == 0:
            return 0
        
        return hop_dong.luong_co_ban * (so_cong_thuc / so_cong_chuan)
    
    # ========================================================
    # PRIVATE: Tính tăng ca
    # ========================================================
    def _tinh_tang_ca(self, hop_dong: HopDong, tong_hop_cong: TongHopCong) -> float:
        """Tăng ca = Số giờ TC × (Lương CB / Công chuẩn / 8) × 150%"""
        
        if tong_hop_cong.so_gio_tang_ca <= 0:
            return 0
        
        luong_gio = hop_dong.luong_co_ban / (tong_hop_cong.so_cong_chuan * 8)
        return tong_hop_cong.so_gio_tang_ca * luong_gio * 1.5
    
    # ========================================================
    # PRIVATE: Helper functions
    # ========================================================
    def _get_active_contract(self, nhan_vien_id: int, thang: int, nam: int) -> Optional[HopDong]:
        """Lấy hợp đồng đang hiệu lực trong tháng"""
        ngay_trong_thang = date(nam, thang, 15)
        return self.db.query(HopDong).filter(
            HopDong.nhan_vien_id == nhan_vien_id,
            HopDong.ngay_bat_dau <= ngay_trong_thang,
            (HopDong.ngay_ket_thuc == None) | (HopDong.ngay_ket_thuc >= ngay_trong_thang)
        ).order_by(HopDong.ngay_bat_dau.desc()).first()
    
    def _get_tong_hop_cong(self, nhan_vien_id: int, thang: int, nam: int) -> Optional[TongHopCong]:
        """Lấy tổng hợp công tháng"""
        return self.db.query(TongHopCong).filter(
            TongHopCong.nhan_vien_id == nhan_vien_id,
            TongHopCong.thang == thang,
            TongHopCong.nam == nam
        ).first()
    
    def _get_don_gia(self, nhan_vien_id: int, mon_hoc_id: int, khoi_id: int, ngay: date) -> float:
        """Lấy đơn giá dạy theo GV × Môn × Khối tại thời điểm"""
        don_gia = self.db.query(DonGiaDay).filter(
            DonGiaDay.nhan_vien_id == nhan_vien_id,
            DonGiaDay.mon_hoc_id == mon_hoc_id,
            DonGiaDay.khoi_id == khoi_id,
            DonGiaDay.ap_dung_tu <= ngay,
            (DonGiaDay.ap_dung_den == None) | (DonGiaDay.ap_dung_den >= ngay)
        ).order_by(DonGiaDay.ap_dung_tu.desc()).first()
        
        return don_gia.don_gia_tiet if don_gia else 0
    
    def _dem_so_tuan(self, ngay_dau: date, ngay_cuoi: date) -> float:
        """Đếm số tuần làm việc trong tháng"""
        # Đếm số ngày T2-T7 trong tháng / 6 = số tuần
        count = 0
        current = ngay_dau
        while current <= ngay_cuoi:
            if current.weekday() < 6:  # T2(0) -> T7(5)
                count += 1
            current += timedelta(days=1)
        return count / 6  # 6 ngày/tuần
    
    def _tinh_tuan_day_goc(self, ngay_dau_thang, ngay_cuoi_thang, ngay_thay_bat_dau, ngay_thay_ket_thuc):
        """Tính số tuần GV gốc vẫn dạy (phần không bị thay)"""
        # Phần trước khi bị thay
        if ngay_thay_bat_dau > ngay_dau_thang:
            end = min(ngay_thay_bat_dau - timedelta(days=1), ngay_cuoi_thang)
            return self._dem_so_tuan(ngay_dau_thang, end)
        # Phần sau khi hết thay
        if ngay_thay_ket_thuc and ngay_thay_ket_thuc < ngay_cuoi_thang:
            start = max(ngay_thay_ket_thuc + timedelta(days=1), ngay_dau_thang)
            return self._dem_so_tuan(start, ngay_cuoi_thang)
        return 0
    
    def _tinh_tuan_thay_the(self, ngay_dau_thang, ngay_cuoi_thang, ngay_bat_dau, ngay_ket_thuc):
        """Tính số tuần GV thay thế dạy"""
        start = max(ngay_dau_thang, ngay_bat_dau)
        end = min(ngay_cuoi_thang, ngay_ket_thuc) if ngay_ket_thuc else ngay_cuoi_thang
        if start > end:
            return 0
        return self._dem_so_tuan(start, end)

