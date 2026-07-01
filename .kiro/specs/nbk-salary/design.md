# Design Document

## Overview

NBK Salary Management System - Full-stack web application for teacher and office staff salary management at THCS Nguyễn Bỉnh Khiêm. The system supports two staff groups: Teachers (GV) with period-based salary and Office Staff (VP) with attendance-based salary (imported from Misa). Key salary components include Lương Khoán (contracted salary from position/level/duties/concurrent roles), teaching income, external periods, support allowances, and tax calculations.

## Tech Stack

- **Frontend:** React 18 + Ant Design 5 + Axios + React Router
- **Backend:** Python FastAPI + SQLAlchemy 2.0 + Alembic
- **Database:** PostgreSQL 15
- **Auth:** JWT (python-jose + passlib[bcrypt])
- **Deploy:** Docker Compose
- **Export:** openpyxl (Excel), Jinja2 (PDF template)

## Architecture

Three-tier web application: React SPA frontend communicates via REST API with FastAPI backend, which persists data in PostgreSQL. All services containerized via Docker Compose.

## Components and Interfaces

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│   React     │────▶│   FastAPI        │────▶│ PostgreSQL  │
│   Frontend  │◀────│   Backend        │◀────│   Database  │
└─────────────┘     └──────────────────┘     └─────────────┘
     :3000               :8000                    :5432
```

### Backend Structure
```
backend/
├── app/
│   ├── main.py          # FastAPI app entry point
│   ├── config.py        # Settings (env vars)
│   ├── database.py      # SQLAlchemy engine & session
│   ├── models/          # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── danh_muc.py  # dm_don_vi, dm_khoi, dm_lop, dm_mon_hoc, etc.
│   │   ├── chuc_danh.py # dm_chuc_vu, dm_cap_bac_ql, dm_nghiep_vu, dm_kiem_nhiem
│   │   ├── nhan_vien.py # nhan_vien + assignment junction tables
│   │   ├── hop_dong.py
│   │   ├── tkb.py
│   │   ├── cham_cong.py
│   │   ├── bang_luong.py
│   │   ├── ho_tro_luong.py
│   │   └── misa_hr.py   # dl_gia_dinh, dl_lich_su_luong, dl_qua_trinh_cong_tac, dl_bang_cap, dl_nghi_phep
│   ├── schemas/         # Pydantic schemas
│   ├── routers/         # API route handlers
│   │   ├── auth.py
│   │   ├── danh_muc.py
│   │   ├── nhan_vien.py
│   │   ├── import_nv.py
│   │   ├── tkb.py
│   │   ├── cham_cong.py
│   │   ├── luong.py
│   │   ├── ho_tro_luong.py
│   │   ├── tiet_ngoai.py
│   │   ├── misa_hr.py   # MISA HR import endpoints (gia đình, lịch sử lương, etc.)
│   │   └── bao_cao.py
│   ├── services/        # Business logic
│   │   ├── salary_engine.py
│   │   ├── luong_khoan_engine.py
│   │   ├── tax_engine.py
│   │   ├── bcc_service.py
│   │   ├── misa_import_service.py
│   │   └── export_service.py
│   └── utils/           # Helpers
├── alembic/
├── requirements.txt
└── Dockerfile
```

### Frontend Structure
```
frontend/
├── src/
│   ├── components/      # Shared components
│   ├── pages/           # Route pages
│   │   ├── Login.jsx
│   │   ├── Dashboard.jsx
│   │   ├── DanhMuc/
│   │   │   ├── DonVi.jsx
│   │   │   ├── ChucVu.jsx
│   │   │   ├── CapBacQL.jsx
│   │   │   ├── NghiepVu.jsx
│   │   │   ├── KiemNhiem.jsx
│   │   │   ├── MonHoc.jsx
│   │   │   └── HeSoLuong.jsx
│   │   ├── NhanVien.jsx
│   │   ├── ThoiKhoaBieu.jsx   # Unified TKB import form
│   │   ├── TietDayNgoai.jsx   # Consolidated external period table
│   │   ├── HoTroLuong.jsx     # Support allowances table
│   │   ├── BCCTongTiet.jsx
│   │   ├── ChamCong.jsx       # Misa attendance import + manual edit
│   │   ├── BangLuong.jsx
│   │   ├── PhieuLuong.jsx
│   │   ├── MisaImport.jsx     # MISA HR data import page (9 tabs)
│   │   └── BaoCao.jsx
│   ├── services/        # API call functions
│   ├── store/           # State management
│   └── App.jsx
├── package.json
└── Dockerfile
```

## Data Models

### Core Tables (25+ tables)

#### Authentication
- `users` (id, username, password_hash, full_name, role, is_active, failed_login_count, locked_until, created_at, updated_at)

#### Danh mục cơ bản (Basic Catalog)
- `dm_don_vi` (id, ten, mo_ta, is_active, **MISA fields**: ma_don_vi, thuoc_don_vi, dia_chi, cap_to_chuc, truong_don_vi, chuc_nang_nhiem_vu, hach_toan, thu_tu_sap_xep, ma_so_dkkd, ngay_cap_dkkd, noi_cap_dkkd)
- `dm_khoi` (id, ten, thu_tu)
- `dm_lop` (id, ten, khoi_id → dm_khoi)
- `dm_mon_hoc` (id, ten, ma_mon, is_active)
- `dm_he_so_luong` (id, bac, he_so, ngay_hieu_luc, is_active)
- `dm_ky_hieu_cong` (id, ky_hieu, ten, gia_tri_ngay_cong, loai)
- `dm_don_gia_day` (id, nhan_vien_id → nhan_vien, mon_hoc_id → dm_mon_hoc, khoi_id → dm_khoi, don_gia, ngay_bat_dau, ngay_ket_thuc, is_active)
- `dm_loai_tiet_ngoai` (id, ten, is_active) — configurable external period types
- `dm_loai_ho_tro` (id, ten, is_active) — configurable support allowance types
- `dm_vi_tri` (id, ten, mo_ta, **MISA fields**: ma_vi_tri, don_vi_cong_tac, nhom_vi_tri, chuc_danh, trang_thai) — Job positions with MISA compatibility

#### Chức danh & Phân công (Position & Assignment Tables)
- `dm_chuc_vu` (id, ma, ten, don_gia_luong_khoan, is_active)
  - Unique code (e.g., GVCN, PCN, GVu)
  - don_gia_luong_khoan: 0–999,999,999 VND
- `dm_cap_bac_ql` (id, ma, ten, don_gia_luong_khoan, is_active)
  - Unique code
  - don_gia_luong_khoan: 0–999,999,999 VND
- `dm_nghiep_vu` (id, ma, ten, is_active)
  - Each adds fixed 2,000,000 VND to Lương Khoán
- `dm_kiem_nhiem` (id, ma, ten, is_active)
  - Each adds fixed 3,000,000 VND to Lương Khoán

**Junction/Assignment Tables:**
- `nv_nghiep_vu` (id, nhan_vien_id → nhan_vien, nghiep_vu_id → dm_nghiep_vu, mo_ta, ngay_bat_dau, ngay_ket_thuc)
  - Many-to-many: employee ↔ nghiệp vụ
  - mo_ta: description field (not used in salary calculation)
- `nv_kiem_nhiem` (id, nhan_vien_id → nhan_vien, kiem_nhiem_id → dm_kiem_nhiem, mo_ta, ngay_bat_dau, ngay_ket_thuc)
  - Many-to-many: employee ↔ kiêm nhiệm
  - mo_ta: description field (not used in salary calculation)

#### Employee Data
- `nhan_vien` (id, ma_nv, ho_ten, ten_goi, nhom_nv[GV/VP], don_vi_id → dm_don_vi, chuc_vu_id → dm_chuc_vu, cap_bac_ql_id → dm_cap_bac_ql, loai_hop_dong, trang_thai, ngay_sinh, email, sdt, cccd, ngay_vao_lam, so_nguoi_phu_thuoc, **MISA extended fields**: gioi_tinh, noi_sinh, nguyen_quan, tinh_trang_hon_nhan, mst_ca_nhan, dan_toc, ton_giao, quoc_tich, loai_giay_to, so_cmnd_cccd, ngay_cap_cmnd, noi_cap_cmnd, ngay_het_han_cmnd, so_ho_chieu, ngay_cap_ho_chieu, noi_cap_ho_chieu, ngay_het_han_ho_chieu, trinh_do_van_hoa, trinh_do_dao_tao, noi_dao_tao, khoa, chuyen_nganh, nam_tot_nghiep, xep_loai, dt_co_quan, dt_nha_rieng, email_co_quan, so_so_ho_khau, ma_so_ho_gia_dinh, luong_co_ban, bac_luong, tinh_chat_lao_dong, ly_do_nghi, ngay_nghi_viec, noi_lam_viec, so_so_ql_lao_dong, ngay_hoc_viec, ngay_thu_viec, ngay_chinh_thuc, quan_ly_truc_tiep, quan_ly_gian_tiep, luong_dong_bh, tk_ngan_hang, ngan_hang, tham_gia_cong_doan, tham_gia_bao_hiem, ngay_tham_gia_bh, ty_le_dong_bh, ty_le_dong_bhxh, ty_le_dong_bhyt, ty_le_dong_bhtn, so_so_bhxh, ma_so_bhxh, noi_dang_ky_kcb, dia_chi_hktt, dia_chi_hien_nay, thue_suat, giam_tru_ban_than, ma_cham_cong, so_ngay_phep, created_at, updated_at)
  - `ten_goi`: display nickname, only used for GV group (NULL for VP)
  - `chuc_vu_id`: FK to dm_chuc_vu (nullable)
  - `cap_bac_ql_id`: FK to dm_cap_bac_ql (nullable)
  - Nghiệp vụ and Kiêm nhiệm via junction tables
  - MISA extended fields: compatible with "Nhập khẩu hồ sơ" MISA template (all nullable)
- `dl_hop_dong` (id, nhan_vien_id → nhan_vien, loai, luong_dong_bh, he_so_luong_id → dm_he_so_luong, ngay_bat_dau, ngay_ket_thuc, ghi_chu)

#### MISA HR Data (Family, Salary History, Work History, Qualifications, Leave)
- `dl_gia_dinh` (id, nhan_vien_id → nhan_vien, ho_ten_nguoi_than, quan_he, quan_he_chu_ho, gioi_tinh, ngay_sinh, quoc_tich, so_cmnd, sdt, email, nghe_nghiep, mst_ca_nhan, noi_lam_viec, cung_so_ho_khau, da_mat, ngay_mat, ghi_chu, la_nguoi_phu_thuoc, thoi_diem_tinh_gt, thoi_diem_ket_thuc_gt, dia_chi_thuong_tru, cho_o_hien_nay)
  - Family members / dependents for tax deduction
- `dl_lich_su_luong` (id, nhan_vien_id → nhan_vien, ngay_hieu_luc, loai_luong[GROSS/NET], don_vi_cong_tac, vi_tri_cong_viec, bac_luong, luong_co_ban, ty_le_huong_luong, khoan_phu_cap, gia_tri_phu_cap, phu_cap_theo_cong, trang_thai_phu_cap, khoan_khau_tru, gia_tri_khau_tru, khau_tru_theo_cong, trang_thai_khau_tru)
  - Salary history with allowances and deductions
- `dl_qua_trinh_cong_tac` (id, nhan_vien_id → nhan_vien, tu_ngay, loai_thu_tuc, don_vi_cong_tac, bac, trang_thai_lao_dong, tinh_chat_lao_dong, quan_ly_truc_tiep, vi_tri_cong_viec, quan_ly_gian_tiep, so_quyet_dinh, ngay_quyet_dinh, ghi_chu)
  - Employee work history / transfer records
- `dl_bang_cap` (id, nhan_vien_id → nhan_vien, noi_dao_tao, tu_nam, den_nam, khoa, chuyen_nganh, trinh_do_dao_tao, hinh_thuc, xep_loai, da_tot_nghiep, ngay_nhan_bang, ghi_chu)
  - Qualifications and degrees
- `dl_nghi_phep` (id, nhan_vien_id → nhan_vien, nam, so_np_nam_nay, so_np_nam_truoc, so_np_tham_nien, so_np_thuong_khac, so_np_da_huy, so_np_da_su_dung) [UNIQUE: nhan_vien_id + nam]
  - Annual leave balance per employee per year

#### Timetable & Teaching
- `dl_tkb` (id, thang, nam, nhan_vien_id → nhan_vien, mon_hoc_id → dm_mon_hoc, khoi_id → dm_khoi, lop_id → dm_lop, so_tiet, loai_tiet)
  - Data sourced from unified TKB import form (all grades in one upload)
- `dl_thay_doi_nguoi_day` (id, ngay, tiet, lop_id → dm_lop, mon_hoc_id → dm_mon_hoc, gv_goc_id → nhan_vien, gv_thay_id → nhan_vien, ly_do, thang, nam)
- `dl_bcc_tong_tiet` (id, thang, nam, nhan_vien_id → nhan_vien, theo_tkb_json, thay_doi_json, phat_sinh_json, thuc_te_json)
- `dl_tiet_day_ngoai` (id, thang, nam, nhan_vien_id → nhan_vien, loai, so_tiet, don_gia, he_so, thanh_tien)
  - Single consolidated table for ALL external period types (Vĩnh Yên, Bồi dưỡng, IELTS, Luyện thi, Âm nhạc, etc.)
  - `loai` references dm_loai_tiet_ngoai or stores type string
  - `thanh_tien` = so_tiet × don_gia × he_so

#### Support Allowances (NEW)
- `dl_ho_tro_luong` (id, nhan_vien_id → nhan_vien, thang, nam, loai_ho_tro, so_tien, ghi_chu)
  - Per employee per month, one row per allowance type
  - `loai_ho_tro`: ăn trưa, gửi xe, ChatGPT, etc. (references dm_loai_ho_tro)
  - `so_tien`: 0–999,999,999 VND
  - Summed into payslip Section II item 4

#### Attendance (VP - from Misa Import)
- `dl_cham_cong` (id, nhan_vien_id → nhan_vien, ngay, ky_hieu_cong_id → dm_ky_hieu_cong, ghi_chu)
  - Can be populated via Misa Excel import OR manual entry/edit
- `dl_tong_hop_cong` (id, nhan_vien_id → nhan_vien, thang, nam, ngay_cong, ngay_nghi, ngay_phep, lam_them)
  - Auto-calculated from Misa import data or manual attendance entries

#### Salary
- `dl_bang_luong` (id, nhan_vien_id → nhan_vien, thang, nam, trang_thai[draft/reviewed/approved], muc_i_json, muc_ii_json, muc_iii_json, muc_iv_json, muc_v_json, muc_vi_thuc_linh, nguoi_tinh_id → users, nguoi_duyet_id → users, ngay_tinh, ngay_duyet, version)
  - `muc_i_json` includes: ho_ten, ten_goi, chuc_vu, cap_bac_ql, nghiep_vu[], kiem_nhiem[], luong_khoan, luong_dong_bh, ngay_cong
  - `muc_ii_json` includes 9 line items: luong_khoan_prorated, tien_giang_day, tien_de_thi, ho_tro (from dl_ho_tro_luong), sinh_nhat, lam_them, thuong_su_kien, bu_luong, thuong_tet

## API Design

### Authentication
- POST /api/auth/login → {access_token, token_type}
- POST /api/auth/register → {user}
- GET /api/auth/me → {user}

### CRUD Pattern (for each danh mục)
- GET /api/danh-muc/{loai} → list
- POST /api/danh-muc/{loai} → created item
- PUT /api/danh-muc/{loai}/{id} → updated item
- DELETE /api/danh-muc/{loai}/{id} → success

### Position & Assignment Endpoints
- GET /api/chuc-vu → list all chức vụ
- POST /api/chuc-vu → create chức vụ with đơn giá
- PUT /api/chuc-vu/{id} → update
- GET /api/cap-bac-ql → list all cấp bậc QL
- POST /api/cap-bac-ql → create cấp bậc QL with đơn giá
- PUT /api/cap-bac-ql/{id} → update
- GET /api/nghiep-vu → list all nghiệp vụ
- GET /api/kiem-nhiem → list all kiêm nhiệm
- POST /api/nhan-vien/{nv_id}/nghiep-vu → assign nghiệp vụ
- DELETE /api/nhan-vien/{nv_id}/nghiep-vu/{id} → remove assignment
- POST /api/nhan-vien/{nv_id}/kiem-nhiem → assign kiêm nhiệm
- DELETE /api/nhan-vien/{nv_id}/kiem-nhiem/{id} → remove assignment

### TKB (Unified Form)
- POST /api/tkb/import → import from unified Excel/CSV form (all grades)
- GET /api/tkb/{thang}/{nam} → get timetable data
- GET /api/tkb/template → download import template

### External Period (Consolidated)
- GET /api/tiet-ngoai/{thang}/{nam} → list all external periods
- POST /api/tiet-ngoai → add entry
- POST /api/tiet-ngoai/import → bulk import from Excel/CSV
- PUT /api/tiet-ngoai/{id} → update entry
- DELETE /api/tiet-ngoai/{id} → delete entry

### Support Allowances
- GET /api/ho-tro-luong/{thang}/{nam} → list all allowances for month
- POST /api/ho-tro-luong → add entry
- POST /api/ho-tro-luong/batch → batch entry (multiple employees, one type)
- POST /api/ho-tro-luong/import → bulk import from Excel/CSV
- PUT /api/ho-tro-luong/{id} → update entry
- DELETE /api/ho-tro-luong/{id} → delete entry

### Attendance (VP - Misa Import)
- POST /api/cham-cong/import-misa → import from Misa Excel export
- GET /api/cham-cong/{thang}/{nam} → attendance records
- PUT /api/cham-cong/{id} → manual edit
- POST /api/cham-cong → manual entry
- GET /api/tong-hop-cong/{thang}/{nam} → attendance summary

### Salary Endpoints
- POST /api/luong/tinh-luong → calculate all employees
- POST /api/luong/tinh-luong/{nv_id} → calculate single
- GET /api/luong/luong-khoan/{nv_id} → get calculated Lương Khoán breakdown
- PUT /api/luong/duyet/{id} → approve
- GET /api/luong/bang-luong/{thang}/{nam} → salary table
- GET /api/luong/phieu-luong/{nv_id}/{thang}/{nam} → payslip

### Reports & Export
- GET /api/bao-cao/bcc/{thang}/{nam} → BCC tổng tiết report
- GET /api/bao-cao/luong/{thang}/{nam} → monthly salary summary
- GET /api/bao-cao/luong-nam/{nam} → yearly salary summary
- GET /api/bao-cao/cham-cong/{thang}/{nam} → attendance report
- POST /api/export/misa → export to Misa format
- POST /api/export/phieu-luong/{nv_id}/{thang}/{nam} → export payslip (PDF/Excel)

### MISA HR Import
- POST /api/misa-hr/import/gia-dinh → import family/dependents
- POST /api/misa-hr/import/lich-su-luong → import salary history
- POST /api/misa-hr/import/qua-trinh-ct → import work history
- POST /api/misa-hr/import/bang-cap → import qualifications
- POST /api/misa-hr/import/nghi-phep → import leave balance
- POST /api/misa-hr/import/co-cau-to-chuc → import organization structure
- POST /api/misa-hr/import/vi-tri-cong-viec → import job positions
- GET /api/misa-hr/{nv_id}/gia-dinh → list family members
- GET /api/misa-hr/{nv_id}/lich-su-luong → list salary history

## Key Business Logic

### Lương Khoán (Contracted Salary) Formula
```
Lương_Khoán = đơn_giá_chức_vụ + đơn_giá_cấp_bậc_ql + (số_nghiệp_vụ × 2,000,000) + (số_kiêm_nhiệm × 3,000,000)

Where:
- đơn_giá_chức_vụ = dm_chuc_vu.don_gia_luong_khoan (from employee's assigned chức vụ)
- đơn_giá_cấp_bậc_ql = dm_cap_bac_ql.don_gia_luong_khoan (from employee's assigned cấp bậc)
- số_nghiệp_vụ = count of active nv_nghiep_vu assignments
- số_kiêm_nhiệm = count of active nv_kiem_nhiem assignments

Prorated for payslip: Lương_Khoán × (ngày_công_hưởng_lương / ngày_công_chuẩn_tháng)
```

### Teacher Salary Calculation
```
Section II Total Income:
  Item 1: Lương Khoán (prorated)
  Item 2: Teaching Income = Regular Teaching + External Teaching
  Item 3: Exam fees
  Item 4: Support Allowances (from dl_ho_tro_luong)
  Item 5–9: Bonuses

Regular Teaching Income = Σ(actual_periods × unit_price × coefficient)
  - Standard periods: coefficient 1.0
  - TNST VY: coefficient 1.3
  - K9 luyện thi: coefficient 1.5
  - KH bằng TA: coefficient 1.0
  - Ielts: coefficient 1.0

External Teaching Income = Σ(dl_tiet_day_ngoai entries: số_tiết × đơn_giá × hệ_số)
```

### Office Staff Salary Calculation
```
Section II Total Income:
  Item 1: Lương Khoán (prorated by actual working days / standard days)
  Item 2: Attendance-based salary = (hệ_số_lương × lương_cơ_sở) × (ngày_công / ngày_chuẩn)
  Item 4: Support Allowances (from dl_ho_tro_luong)
  Item 5–9: Bonuses

VP Attendance Data Source: Misa Excel import → dl_cham_cong / dl_tong_hop_cong
  - Supports manual entry/edit for corrections
  - Standard working days default: 26 (configurable per month)
  - Probation: 85% salary (configurable)
  - Mid-month transition: pro-rata calculation
```

### Net Pay Formula
```
Net Pay = Total Income (II) - Already Received (III) - Deductions (IV) ± Tax Settlement (V)

Deductions (IV):
  1. Insurance + Union fees (BH+CĐ)
  2. Đoàn phí
  3. Accumulation deductions (Tích lũy)
  4. Personal Income Tax (Thuế TNCN)
  5. Recovery amounts (Truy thu)
```

### Tax Engine (7-bracket progressive PIT)
```
Taxable = Total Income - Insurance - Personal deduction (11M) - Dependent deduction (4.4M each)
Tax = apply 7-bracket progressive rate (5%, 10%, 15%, 20%, 25%, 30%, 35%)
Year-end settlement: annual PIT liability - total PIT already deducted
```

### Unified TKB Import Flow
```
1. User uploads single Excel/CSV file (all grades in one form)
2. System parses and maps columns to grade/class/subject/period structure
3. Validation against master data (teacher, subject, grade, class)
4. Preview with error reporting
5. User confirms → data written to dl_tkb table
6. System calculates per-teacher period totals (Theo TKB columns)
```

### Misa Attendance Import Flow (VP)
```
1. User uploads Misa Excel export file
2. System parses rows, matches employees by code/name
3. Validates format and employee references
4. Maps data to dl_cham_cong / dl_tong_hop_cong tables
5. Auto-calculates: ngày_công, ngày_nghỉ, ngày_phép, làm_thêm
6. Supports manual corrections after import
```

### BCC Summary Calculation
```
Thực tế columns per teacher:
  Tiết chính HS1 = TKB(Tổng tiết chính) - Nghỉ(K6-8) - Nghỉ(K9) + Thay(K6-8) + Thay(K9) + Phát sinh(tiết chính)
  TNST VY (HS1.3) = TKB(TNST VY) - Nghỉ(TNST VY) + Thay(TNST VY) + Phát sinh(TNST VY)
  K9 luyện thi (HS1.5) = TKB(K9 LT) - Nghỉ(K9 LT) + Thay(K9 LT) + Phát sinh(K9 LT)
  KH TA = TKB(KH TA) - Nghỉ(KH TA) + Thay(KH TA) + Phát sinh(KH TA)
  Ielts = TKB(Ielts) - Nghỉ(Ielts) + Thay(Ielts) + Phát sinh(Ielts)
  
Tổng = (Tiết chính × 1.0) + (TNST VY × 1.3) + (K9 LT × 1.5) + (KH TA × 1.0) + (Ielts × 1.0)

Phát sinh sourced from: dl_tiet_day_ngoai (consolidated external period table)
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Lương Khoán formula correctness

*For any* employee with a valid Chức_Vụ (đơn_giá ∈ [0, 999,999,999]), a valid Cấp_Bậc_QL (đơn_giá ∈ [0, 999,999,999]), any number of Nghiệp_Vụ assignments (n ≥ 0), and any number of Kiêm_Nhiệm assignments (m ≥ 0), the calculated Lương_Khoán SHALL equal: đơn_giá_chức_vụ + đơn_giá_cấp_bậc + (n × 2,000,000) + (m × 3,000,000)

**Validates: Requirements 1.7, 7.6, 8.10**

### Property 2: BCC Thực tế period calculation

*For any* teacher with scheduled periods (TKB), absence periods (Nghỉ), substitution periods (Thay), and adjustment periods (Phát sinh), each Thực tế sub-column SHALL equal: TKB value − corresponding Nghỉ value + corresponding Thay value + corresponding Phát sinh value, for each period type independently.

**Validates: Requirements 4.2**

### Property 3: BCC Tổng weighted sum

*For any* set of Thực tế period values (Tiết chính, TNST VY, K9 luyện thi, KH TA, Ielts), the Tổng SHALL equal: (Tiết chính × 1.0) + (TNST VY × 1.3) + (K9 luyện thi × 1.5) + (KH TA × 1.0) + (Ielts × 1.0)

**Validates: Requirements 4.6**

### Property 4: External period amount calculation

*For any* external period entry with số_tiết > 0, đơn_giá > 0, and hệ_số > 0, the thành_tiền SHALL equal: số_tiết × đơn_giá × hệ_số

**Validates: Requirements 5.2**

### Property 5: Support allowance aggregation

*For any* set of dl_ho_tro_luong entries belonging to the same employee in the same month, the payslip Section II item 4 value SHALL equal the sum of all so_tien values in those entries.

**Validates: Requirements 6.7**

### Property 6: Teacher teaching income calculation

*For any* teacher with actual period counts and corresponding Unit_Prices across multiple Subject×Grade combinations, the total teaching income SHALL equal the sum of (period_count × unit_price × coefficient) for each combination, where coefficient is 1.0 for standard, 1.3 for TNST VY, and 1.5 for K9 luyện thi.

**Validates: Requirements 7.1, 7.2, 7.5**

### Property 7: VP salary from attendance

*For any* Office_Staff member with a valid salary coefficient, base salary, actual working days (≥ 0), and standard working days (> 0), the attendance-based salary SHALL equal: (coefficient × base_salary) × (actual_days / standard_days)

**Validates: Requirements 8.5**

### Property 8: Mid-month probation transition pro-rata

*For any* Office_Staff member transitioning from probation to official status on day D within a month of N standard days, the total salary SHALL equal: (days_before_D × daily_rate × probation_pct) + (days_from_D × daily_rate × 1.0), and this total SHALL always be between (full_salary × probation_pct) and full_salary.

**Validates: Requirements 8.7**

### Property 9: Payslip Net Pay formula

*For any* payslip with Section II total (Total Income), Section III total (Already Received), Section IV total (Deductions), and Section V amount (Tax Settlement), the Net Pay (Section VI) SHALL equal: Section II − Section III − Section IV + Section V

**Validates: Requirements 9.7**

### Property 10: Uniqueness constraint enforcement

*For any* entity type with a uniqueness constraint (employee code, chức vụ code, cấp bậc code, nghiệp vụ code, kiêm nhiệm code, or active Unit_Price per Teacher×Subject×Grade), inserting a record with a duplicate key SHALL be rejected with an error indicating the conflict.

**Validates: Requirements 1.12, 1.18**

### Property 11: TKB record validation against master data

*For any* TKB record referencing a teacher_id, subject_id, grade_id, or class_id, if any referenced ID does not exist in the corresponding master data table, the record SHALL be rejected with a validation error specifying the unmatched field and value.

**Validates: Requirements 2.2, 2.3**

## Error Handling

- **Validation errors**: Return 422 with field-level error details
- **Duplicate conflicts**: Return 409 with conflict description
- **Missing references**: Return 400 with specific missing field/value
- **Concurrent edit conflicts**: Return 409 with current saved values
- **Auth failures**: Return 401/403 with access denied message
- **Account lockout**: 5 failed attempts → 15-minute lock with message
- **Import errors**: Return per-row error list (up to 100 entries)
- **Missing salary data**: Block finalization, list missing items by name/section

## Testing Strategy

### Property-Based Tests (Hypothesis - Python)
- Library: **Hypothesis** for Python property-based testing
- Minimum **100 iterations** per property test
- Each test tagged: **Feature: nbk-salary, Property {N}: {title}**
- Covers: Lương Khoán formula, BCC calculations, teaching income, VP salary, net pay formula, external period amounts, support allowance aggregation, validation rules
- Focus on pure calculation logic in `salary_engine.py`, `luong_khoan_engine.py`, `tax_engine.py`, `bcc_service.py`

### Unit Tests (pytest)
- Specific examples for edge cases: zero assignments, probation transitions, missing unit prices
- Tax bracket boundary cases
- Password validation edge cases
- Error condition verification (missing data blocking finalization)

### Integration Tests
- API endpoint testing with test database
- Excel/CSV import parsing (TKB unified form, Misa attendance export, external periods, support allowances)
- Concurrent edit conflict detection
- Authentication and authorization flows
- Misa export format verification

### Frontend Tests
- React Testing Library for key forms (employee CRUD, TKB import, allowance batch entry)
- Form validation behavior
- Role-based UI element visibility

### E2E Tests
- Critical workflow paths: TKB import → BCC generate → salary calculate → approve → export
- Misa attendance import → VP salary calculation → payslip generation
