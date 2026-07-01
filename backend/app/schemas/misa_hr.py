"""
NBK Salary - Pydantic schemas for MISA HR import/export forms.

Covers: Gia đình, Lịch sử lương, Quá trình công tác, Bằng cấp, Nghỉ phép,
        Cơ cấu tổ chức, Vị trí công việc.
"""
from datetime import date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# =============================================================================
# Gia đình (Family / Dependents)
# =============================================================================

class GiaDinhCreate(BaseModel):
    ho_ten_nguoi_than: str = Field(..., max_length=100)
    quan_he: str = Field(..., max_length=50)
    quan_he_chu_ho: Optional[str] = Field(None, max_length=50)
    gioi_tinh: Optional[str] = Field(None, max_length=10)
    ngay_sinh: Optional[date] = None
    quoc_tich: Optional[str] = Field(None, max_length=50)
    so_cmnd: Optional[str] = Field(None, max_length=20)
    sdt: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    nghe_nghiep: Optional[str] = Field(None, max_length=100)
    mst_ca_nhan: Optional[str] = Field(None, max_length=20)
    noi_lam_viec: Optional[str] = Field(None, max_length=200)
    cung_so_ho_khau: Optional[bool] = None
    da_mat: Optional[bool] = None
    la_nguoi_phu_thuoc: Optional[bool] = None
    thoi_diem_tinh_gt: Optional[date] = None
    thoi_diem_ket_thuc_gt: Optional[date] = None
    ghi_chu: Optional[str] = Field(None, max_length=255)


class GiaDinhResponse(BaseModel):
    id: int
    nhan_vien_id: int
    ho_ten_nguoi_than: str
    quan_he: str
    gioi_tinh: Optional[str] = None
    ngay_sinh: Optional[date] = None
    la_nguoi_phu_thuoc: Optional[bool] = None
    mst_ca_nhan: Optional[str] = None
    model_config = {"from_attributes": True}


class GiaDinhImportRow(BaseModel):
    ma_nv: str
    ho_ten_nguoi_than: str
    quan_he: str
    quan_he_chu_ho: Optional[str] = None
    gioi_tinh: Optional[str] = None
    ngay_sinh: Optional[date] = None
    quoc_tich: Optional[str] = None
    so_cmnd: Optional[str] = None
    sdt: Optional[str] = None
    email: Optional[str] = None
    nghe_nghiep: Optional[str] = None
    mst_ca_nhan: Optional[str] = None
    noi_lam_viec: Optional[str] = None
    cung_so_ho_khau: Optional[bool] = None
    da_mat: Optional[bool] = None
    la_nguoi_phu_thuoc: Optional[bool] = None
    thoi_diem_tinh_gt: Optional[date] = None
    thoi_diem_ket_thuc_gt: Optional[date] = None


class GiaDinhImportRequest(BaseModel):
    rows: List[GiaDinhImportRow]


# =============================================================================
# Lịch sử lương (Salary History)
# =============================================================================

class LichSuLuongCreate(BaseModel):
    ngay_hieu_luc: date
    loai_luong: Optional[str] = Field(None, max_length=20)
    don_vi_cong_tac: Optional[str] = Field(None, max_length=100)
    vi_tri_cong_viec: Optional[str] = Field(None, max_length=100)
    bac_luong: Optional[str] = Field(None, max_length=50)
    luong_co_ban: int = Field(..., ge=0)
    ty_le_huong_luong: Optional[float] = Field(None, ge=0, le=100)
    khoan_phu_cap: Optional[str] = Field(None, max_length=100)
    gia_tri_phu_cap: Optional[int] = Field(None, ge=0)
    phu_cap_theo_cong: Optional[bool] = None
    trang_thai_phu_cap: Optional[str] = Field(None, max_length=50)
    khoan_khau_tru: Optional[str] = Field(None, max_length=100)
    gia_tri_khau_tru: Optional[int] = Field(None, ge=0)
    khau_tru_theo_cong: Optional[bool] = None
    trang_thai_khau_tru: Optional[str] = Field(None, max_length=50)


class LichSuLuongResponse(BaseModel):
    id: int
    nhan_vien_id: int
    ngay_hieu_luc: date
    loai_luong: Optional[str] = None
    luong_co_ban: int
    ty_le_huong_luong: Optional[float] = None
    bac_luong: Optional[str] = None
    model_config = {"from_attributes": True}


class LichSuLuongImportRow(BaseModel):
    ma_nv: str
    ngay_hieu_luc: date
    loai_luong: Optional[str] = None
    don_vi_cong_tac: Optional[str] = None
    vi_tri_cong_viec: Optional[str] = None
    bac_luong: Optional[str] = None
    luong_co_ban: int = Field(..., ge=0)
    ty_le_huong_luong: Optional[float] = None
    khoan_phu_cap: Optional[str] = None
    gia_tri_phu_cap: Optional[int] = None
    phu_cap_theo_cong: Optional[bool] = None
    trang_thai_phu_cap: Optional[str] = None
    khoan_khau_tru: Optional[str] = None
    gia_tri_khau_tru: Optional[int] = None
    khau_tru_theo_cong: Optional[bool] = None
    trang_thai_khau_tru: Optional[str] = None


class LichSuLuongImportRequest(BaseModel):
    rows: List[LichSuLuongImportRow]


# =============================================================================
# Quá trình công tác (Work History)
# =============================================================================

class QuaTrinhCTCreate(BaseModel):
    tu_ngay: date
    loai_thu_tuc: Optional[str] = Field(None, max_length=100)
    don_vi_cong_tac: Optional[str] = Field(None, max_length=100)
    bac: Optional[str] = Field(None, max_length=50)
    trang_thai_lao_dong: Optional[str] = Field(None, max_length=50)
    tinh_chat_lao_dong: Optional[str] = Field(None, max_length=50)
    quan_ly_truc_tiep: Optional[str] = Field(None, max_length=100)
    vi_tri_cong_viec: Optional[str] = Field(None, max_length=100)
    quan_ly_gian_tiep: Optional[str] = Field(None, max_length=100)
    so_quyet_dinh: Optional[str] = Field(None, max_length=50)
    ngay_quyet_dinh: Optional[date] = None
    ghi_chu: Optional[str] = Field(None, max_length=255)


class QuaTrinhCTResponse(BaseModel):
    id: int
    nhan_vien_id: int
    tu_ngay: date
    loai_thu_tuc: Optional[str] = None
    don_vi_cong_tac: Optional[str] = None
    vi_tri_cong_viec: Optional[str] = None
    trang_thai_lao_dong: Optional[str] = None
    ghi_chu: Optional[str] = None
    model_config = {"from_attributes": True}


class QuaTrinhCTImportRow(BaseModel):
    ma_nv: str
    tu_ngay: date
    loai_thu_tuc: Optional[str] = None
    don_vi_cong_tac: Optional[str] = None
    bac: Optional[str] = None
    trang_thai_lao_dong: Optional[str] = None
    tinh_chat_lao_dong: Optional[str] = None
    quan_ly_truc_tiep: Optional[str] = None
    vi_tri_cong_viec: Optional[str] = None
    quan_ly_gian_tiep: Optional[str] = None
    so_quyet_dinh: Optional[str] = None
    ngay_quyet_dinh: Optional[date] = None
    ghi_chu: Optional[str] = None


class QuaTrinhCTImportRequest(BaseModel):
    rows: List[QuaTrinhCTImportRow]


# =============================================================================
# Bằng cấp (Qualifications)
# =============================================================================

class BangCapCreate(BaseModel):
    noi_dao_tao: str = Field(..., max_length=200)
    tu_nam: Optional[int] = None
    den_nam: Optional[int] = None
    khoa: Optional[str] = Field(None, max_length=100)
    chuyen_nganh: Optional[str] = Field(None, max_length=100)
    trinh_do_dao_tao: Optional[str] = Field(None, max_length=100)
    hinh_thuc: Optional[str] = Field(None, max_length=50)
    xep_loai: Optional[str] = Field(None, max_length=50)
    da_tot_nghiep: Optional[bool] = None
    ngay_nhan_bang: Optional[date] = None
    ghi_chu: Optional[str] = Field(None, max_length=255)


class BangCapResponse(BaseModel):
    id: int
    nhan_vien_id: int
    noi_dao_tao: str
    tu_nam: Optional[int] = None
    den_nam: Optional[int] = None
    chuyen_nganh: Optional[str] = None
    trinh_do_dao_tao: Optional[str] = None
    xep_loai: Optional[str] = None
    model_config = {"from_attributes": True}


class BangCapImportRow(BaseModel):
    ma_nv: str
    noi_dao_tao: str
    tu_nam: Optional[int] = None
    den_nam: Optional[int] = None
    khoa: Optional[str] = None
    chuyen_nganh: Optional[str] = None
    trinh_do_dao_tao: Optional[str] = None
    hinh_thuc: Optional[str] = None
    xep_loai: Optional[str] = None
    da_tot_nghiep: Optional[bool] = None
    ngay_nhan_bang: Optional[date] = None
    ghi_chu: Optional[str] = None


class BangCapImportRequest(BaseModel):
    rows: List[BangCapImportRow]


# =============================================================================
# Nghỉ phép (Leave Balance)
# =============================================================================

class NghiPhepCreate(BaseModel):
    nam: int = Field(..., ge=2020, le=2099)
    so_np_nam_nay: Optional[float] = Field(None, ge=0)
    so_np_nam_truoc: Optional[float] = Field(None, ge=0)
    so_np_tham_nien: Optional[float] = Field(None, ge=0)
    so_np_thuong_khac: Optional[float] = Field(None, ge=0)
    so_np_da_huy: Optional[float] = Field(None, ge=0)
    so_np_da_su_dung: Optional[float] = Field(None, ge=0)


class NghiPhepResponse(BaseModel):
    id: int
    nhan_vien_id: int
    nam: int
    so_np_nam_nay: Optional[float] = None
    so_np_nam_truoc: Optional[float] = None
    so_np_tham_nien: Optional[float] = None
    so_np_thuong_khac: Optional[float] = None
    so_np_da_huy: Optional[float] = None
    so_np_da_su_dung: Optional[float] = None
    model_config = {"from_attributes": True}


class NghiPhepImportRow(BaseModel):
    ma_nv: str
    so_np_nam_nay: Optional[float] = None
    so_np_nam_truoc: Optional[float] = None
    so_np_tham_nien: Optional[float] = None
    so_np_thuong_khac: Optional[float] = None
    so_np_da_huy: Optional[float] = None
    so_np_da_su_dung: Optional[float] = None


class NghiPhepImportRequest(BaseModel):
    nam: int = Field(..., ge=2020, le=2099)
    rows: List[NghiPhepImportRow]


# =============================================================================
# Generic MISA Import Response
# =============================================================================

class MisaImportResponse(BaseModel):
    imported_count: int
    total_rows: int
    errors: List[Dict[str, Any]] = []


# =============================================================================
# Cơ cấu tổ chức (Organization Structure) - extended DonVi
# =============================================================================

class DonViMisaCreate(BaseModel):
    ten: str = Field(..., max_length=100)
    ma_don_vi: Optional[str] = Field(None, max_length=20)
    thuoc_don_vi: Optional[str] = Field(None, max_length=20)
    dia_chi: Optional[str] = Field(None, max_length=300)
    cap_to_chuc: Optional[str] = Field(None, max_length=50)
    truong_don_vi: Optional[str] = Field(None, max_length=100)
    chuc_nang_nhiem_vu: Optional[str] = Field(None, max_length=500)
    hach_toan: Optional[str] = Field(None, max_length=50)
    thu_tu_sap_xep: Optional[int] = None


class DonViMisaImportRow(BaseModel):
    ten: str
    ma_don_vi: str
    thuoc_don_vi: Optional[str] = None
    dia_chi: Optional[str] = None
    cap_to_chuc: Optional[str] = None
    truong_don_vi: Optional[str] = None
    chuc_nang_nhiem_vu: Optional[str] = None
    hach_toan: Optional[str] = None
    thu_tu_sap_xep: Optional[int] = None
    trang_thai: Optional[str] = None


class DonViMisaImportRequest(BaseModel):
    rows: List[DonViMisaImportRow]


# =============================================================================
# Vị trí công việc (Job Position) - extended ViTri
# =============================================================================

class ViTriMisaCreate(BaseModel):
    ten: str = Field(..., max_length=100)
    ma_vi_tri: Optional[str] = Field(None, max_length=20)
    don_vi_cong_tac: Optional[str] = Field(None, max_length=100)
    nhom_vi_tri: Optional[str] = Field(None, max_length=100)
    chuc_danh: Optional[str] = Field(None, max_length=100)
    trang_thai: Optional[str] = Field(None, max_length=50)


class ViTriMisaImportRow(BaseModel):
    ma_vi_tri: str
    ten: str
    don_vi_cong_tac: Optional[str] = None
    nhom_vi_tri: Optional[str] = None
    chuc_danh: Optional[str] = None
    trang_thai: Optional[str] = None


class ViTriMisaImportRequest(BaseModel):
    rows: List[ViTriMisaImportRow]
