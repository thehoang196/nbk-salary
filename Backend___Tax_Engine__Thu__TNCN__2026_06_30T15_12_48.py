
# ============================================================
# FILE: backend/app/main.py
# FastAPI Application Entry Point
# ============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, danh_muc, nhan_vien, tkb, cham_cong, luong, bao_cao

app = FastAPI(
    title="NBK Salary Management System",
    description="Phần mềm tính lương giáo viên trường NBK",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://nbk-salary.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(danh_muc.router, prefix="/api/danh-muc", tags=["Danh mục"])
app.include_router(nhan_vien.router, prefix="/api/nhan-vien", tags=["Nhân viên"])
app.include_router(tkb.router, prefix="/api/tkb", tags=["Thời khóa biểu"])
app.include_router(cham_cong.router, prefix="/api/cham-cong", tags=["Chấm công"])
app.include_router(luong.router, prefix="/api/luong", tags=["Lương"])
app.include_router(bao_cao.router, prefix="/api/bao-cao", tags=["Báo cáo"])


@app.get("/")
def root():
    return {"message": "NBK Salary System API", "version": "1.0.0"}


# ============================================================
# FILE: backend/app/routers/tkb.py
# API Thời khóa biểu & Thay đổi người dạy
# ============================================================

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.tkb import (
    TKBCreate, TKBResponse, ThayDoiCreate, ThayDoiResponse,
    DonGiaCreate, DonGiaResponse, GioGongDayResponse
)
from app.services.tkb_service import TKBService
from app.utils.security import get_current_user, require_role

router = APIRouter()


@router.post("/import", response_model=dict)
async def import_tkb(
    file: UploadFile = File(...),
    nam_hoc: str = "2025-2026",
    hoc_ky: int = 1,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "accountant"]))
):
    """Import TKB từ file Excel"""
    service = TKBService(db)
    result = service.import_from_excel(file, nam_hoc, hoc_ky)
    return result


@router.get("/", response_model=List[TKBResponse])
def get_tkb(
    nam_hoc: str = "2025-2026",
    hoc_ky: int = 1,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Lấy danh sách TKB"""
    service = TKBService(db)
    return service.get_all(nam_hoc, hoc_ky)


@router.get("/thuc-te/{thang}/{nam}", response_model=List[TKBResponse])
def get_tkb_thuc_te(
    thang: int,
    nam: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Lấy TKB thực tế (đã áp dụng thay đổi) cho tháng cụ thể"""
    service = TKBService(db)
    return service.get_tkb_thuc_te(thang, nam)


# --- Thay đổi người dạy ---
@router.post("/thay-doi", response_model=ThayDoiResponse)
def create_thay_doi(
    data: ThayDoiCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "accountant"]))
):
    """Tạo bản ghi thay đổi người dạy"""
    service = TKBService(db)
    return service.create_thay_doi(data)


@router.get("/thay-doi", response_model=List[ThayDoiResponse])
def get_thay_doi(
    thang: int = None,
    nam: int = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Lấy danh sách thay đổi người dạy"""
    service = TKBService(db)
    return service.get_thay_doi(thang, nam)


# --- Đơn giá dạy ---
@router.post("/don-gia", response_model=DonGiaResponse)
def create_don_gia(
    data: DonGiaCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "accountant"]))
):
    """Tạo/cập nhật đơn giá dạy"""
    service = TKBService(db)
    return service.create_don_gia(data)


@router.get("/don-gia", response_model=List[DonGiaResponse])
def get_don_gia(
    nhan_vien_id: int = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Lấy bảng đơn giá dạy"""
    service = TKBService(db)
    return service.get_don_gia(nhan_vien_id)


@router.get("/gio-cong-day/{thang}/{nam}", response_model=List[GioGongDayResponse])
def get_gio_cong_day(
    thang: int,
    nam: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Tính giờ công dạy cho tất cả GV trong tháng"""
    service = TKBService(db)
    return service.tinh_gio_cong_day(thang, nam)


# ============================================================
# FILE: backend/app/routers/luong.py
# API Tính lương
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.luong import BangLuongResponse, TinhLuongRequest
from app.services.salary_engine import SalaryEngine
from app.utils.security import get_current_user, require_role

router = APIRouter()


@router.post("/tinh-luong", response_model=dict)
def tinh_luong_thang(
    request: TinhLuongRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "accountant"]))
):
    """Tính lương cho tất cả NV trong tháng"""
    engine = SalaryEngine(db)
    result = engine.calculate_all(request.thang, request.nam)
    
    # Lưu vào DB
    for bang_luong in result["results"]:
        bang_luong.nguoi_tinh = current_user.username
        db.add(bang_luong)
    db.commit()
    
    return {
        "success": len(result["results"]),
        "errors": result["errors"],
        "message": f"Đã tính lương cho {len(result['results'])} nhân viên"
    }


@router.post("/tinh-luong/{nhan_vien_id}", response_model=BangLuongResponse)
def tinh_luong_ca_nhan(
    nhan_vien_id: int,
    thang: int,
    nam: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "accountant"]))
):
    """Tính lương cho 1 nhân viên"""
    engine = SalaryEngine(db)
    bang_luong = engine.calculate_salary(nhan_vien_id, thang, nam)
    bang_luong.nguoi_tinh = current_user.username
    db.add(bang_luong)
    db.commit()
    return bang_luong


@router.put("/duyet/{bang_luong_id}")
def duyet_luong(
    bang_luong_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin"]))
):
    """Phê duyệt bảng lương"""
    from app.models.luong import BangLuong
    from datetime import date
    
    bang_luong = db.query(BangLuong).filter(BangLuong.id == bang_luong_id).first()
    if not bang_luong:
        raise HTTPException(status_code=404, detail="Không tìm thấy bảng lương")
    
    bang_luong.trang_thai = "approved"
    bang_luong.nguoi_duyet = current_user.username
    bang_luong.ngay_duyet = date.today()
    db.commit()
    
    return {"message": "Đã phê duyệt bảng lương"}


@router.get("/bang-luong/{thang}/{nam}", response_model=List[BangLuongResponse])
def get_bang_luong(
    thang: int,
    nam: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Lấy bảng lương tháng"""
    from app.models.luong import BangLuong
    
    query = db.query(BangLuong).filter(
        BangLuong.thang == thang,
        BangLuong.nam == nam
    )
    
    # GV chỉ xem lương của mình
    if current_user.role == "teacher":
        query = query.filter(BangLuong.nhan_vien_id == current_user.ma_nhan_vien)
    
    return query.all()


@router.get("/phieu-luong/{nhan_vien_id}/{thang}/{nam}")
def get_phieu_luong(
    nhan_vien_id: int,
    thang: int,
    nam: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Lấy phiếu lương cá nhân (chi tiết)"""
    from app.models.luong import BangLuong
    from app.models.nhan_vien import NhanVien
    from app.services.tax_engine import TaxEngine
    
    # Kiểm tra quyền
    if current_user.role == "teacher" and current_user.ma_nhan_vien != nhan_vien_id:
        raise HTTPException(status_code=403, detail="Không có quyền xem")
    
    bang_luong = db.query(BangLuong).filter(
        BangLuong.nhan_vien_id == nhan_vien_id,
        BangLuong.thang == thang,
        BangLuong.nam == nam
    ).first()
    
    nhan_vien = db.query(NhanVien).filter(NhanVien.id == nhan_vien_id).first()
    
    if not bang_luong or not nhan_vien:
        raise HTTPException(status_code=404, detail="Không tìm thấy dữ liệu")
    
    # Chi tiết thuế
    tax_engine = TaxEngine()
    tax_detail = tax_engine.calculate_pit_detail(
        bang_luong.tong_thu_nhap,
        bang_luong.bhxh, bang_luong.bhyt, bang_luong.bhtn,
        bang_luong.so_nguoi_phu_thuoc
    )
    
    return {
        "nhan_vien": {
            "ma_nv": nhan_vien.ma_nv,
            "ho_ten": nhan_vien.ho_ten,
            "chuc_danh": nhan_vien.chuc_danh.ten_chuc_danh if nhan_vien.chuc_danh else "",
            "don_vi": nhan_vien.don_vi.ten_don_vi if nhan_vien.don_vi else "",
        },
        "thang": thang,
        "nam": nam,
        "thu_nhap": {
            "luong_chuc_danh": bang_luong.luong_chuc_danh,
            "luong_chinh": bang_luong.luong_chinh,
            "luong_day": bang_luong.luong_day,
            "luong_hieu_qua": bang_luong.luong_hieu_qua,
            "phu_cap": [bang_luong.phu_cap_1, bang_luong.phu_cap_2, bang_luong.phu_cap_3,
                       bang_luong.phu_cap_4, bang_luong.phu_cap_5],
            "tang_ca": bang_luong.tang_ca,
            "thuong": bang_luong.thuong,
            "bo_sung": bang_luong.bo_sung,
            "tong_thu_nhap": bang_luong.tong_thu_nhap,
        },
        "khau_tru": {
            "giam_luong": bang_luong.giam_luong,
            "bhxh": bang_luong.bhxh,
            "bhyt": bang_luong.bhyt,
            "bhtn": bang_luong.bhtn,
            "thue_tncn": bang_luong.thue_tncn,
            "tong_khau_tru": bang_luong.tong_khau_tru,
        },
        "thue_detail": tax_detail,
        "thuc_linh": bang_luong.thuc_linh,
        "trang_thai": bang_luong.trang_thai,
    }

