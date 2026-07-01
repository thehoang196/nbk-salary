# Implementation Plan: NBK Salary Management System

## Overview

Full-stack salary management for THCS Nguyễn Bỉnh Khiêm. Tasks 1-5 are completed (project scaffolding, models, Alembic, auth, basic CRUD). Task 6 refactors the position/assignment structure to match updated requirements (dm_chuc_vu, dm_cap_bac_ql, dm_nghiep_vu, dm_kiem_nhiem with junction tables). Tasks 7+ implement remaining features against the new schema.

## Tasks

- [x] 1. Initialize project structure and Docker setup
  - [x] 1.1 Create backend/ and frontend/ directories with Docker Compose for PostgreSQL + FastAPI + React
  - [x] 1.2 Create backend/requirements.txt with all Python dependencies
  - [x] 1.3 Create backend/app/main.py, config.py, database.py
  - [x] 1.4 Create frontend/package.json with React 18, Ant Design 5, Axios, React Router
  - [x] 1.5 Create frontend/src/App.jsx with basic routing
  - [x] 1.6 Create Dockerfiles for backend and frontend

- [x] 2. Create initial SQLAlchemy database models
  - [x] 2.1 Create backend/app/models/user.py with Users table
  - [x] 2.2 Create backend/app/models/danh_muc.py with basic catalog models
  - [x] 2.3 Create backend/app/models/nhan_vien.py with NhanVien model
  - [x] 2.4 Create backend/app/models/hop_dong.py with DlHopDong model
  - [x] 2.5 Create backend/app/models/tkb.py with TKB-related models
  - [x] 2.6 Create backend/app/models/cham_cong.py with attendance models
  - [x] 2.7 Create backend/app/models/bang_luong.py with salary model

- [x] 3. Setup Alembic migrations and seed data
  - [x] 3.1 Initialize Alembic with env.py configured for SQLAlchemy
  - [x] 3.2 Create initial migration (001_initial_tables.py)
  - [x] 3.3 Create backend/app/seed.py with admin user and base data

- [x] 4. Implement JWT authentication
  - [x] 4.1 Create backend/app/utils/auth.py with JWT token functions
  - [x] 4.2 Create backend/app/schemas/auth.py with Pydantic schemas
  - [x] 4.3 Create backend/app/routers/auth.py with login/register/me endpoints
  - [x] 4.4 Create backend/app/utils/dependencies.py with role-based guards
  - [x] 4.5 Implement account lockout (5 failed → 15 min lock)

- [x] 5. Implement basic Danh mục (Catalog) CRUD APIs
  - [x] 5.1 Create backend/app/schemas/danh_muc.py with Pydantic schemas
  - [x] 5.2 Create backend/app/routers/danh_muc.py with generic CRUD for dm_* tables
  - [x] 5.3 Create backend/app/routers/don_gia_day.py with unit price CRUD
  - [x] 5.4 Add duplicate detection and unique constraint validation
  - [x] 5.5 Add referential integrity checks on DELETE

- [x] 6. Refactor Position/Assignment structure (replace dm_chuc_danh with new models)
  Replace the old dm_chuc_danh single-table approach with dm_chuc_vu, dm_cap_bac_ql, dm_nghiep_vu, dm_kiem_nhiem models plus junction tables for Lương Khoán calculation.
  - [x] 6.1 Create backend/app/models/chuc_danh.py with four new models:
    - `DmChucVu` (id, ma, ten, don_gia_luong_khoan, is_active) — unique `ma` constraint
    - `DmCapBacQL` (id, ma, ten, don_gia_luong_khoan, is_active) — unique `ma` constraint
    - `DmNghiepVu` (id, ma, ten, is_active) — unique `ma` constraint, fixed 2M VND supplement
    - `DmKiemNhiem` (id, ma, ten, is_active) — unique `ma` constraint, fixed 3M VND supplement
    - `NvNghiepVu` (id, nhan_vien_id FK, nghiep_vu_id FK, mo_ta, ngay_bat_dau, ngay_ket_thuc) — junction table
    - `NvKiemNhiem` (id, nhan_vien_id FK, kiem_nhiem_id FK, mo_ta, ngay_bat_dau, ngay_ket_thuc) — junction table
    - _Requirements: 1.2, 1.3, 1.4, 1.5, 1.6_

  - [x] 6.2 Update backend/app/models/nhan_vien.py:
    - Replace `chuc_danh_id` FK → add `chuc_vu_id` FK to dm_chuc_vu (nullable)
    - Add `cap_bac_ql_id` FK to dm_cap_bac_ql (nullable)
    - Add `ten_goi` field (String(50), nullable) — display nickname for GV only
    - Add relationships to NvNghiepVu and NvKiemNhiem junction tables
    - Remove relationship to DmChucDanh
    - _Requirements: 1.8, 1.9, 1.10, 1.11_

  - [x] 6.3 Add new catalog tables to backend/app/models/danh_muc.py:
    - `DmLoaiTietNgoai` (id, ten, is_active) — configurable external period types
    - `DmLoaiHoTro` (id, ten, is_active) — configurable support allowance types
    - _Requirements: 5.3, 6.3_

  - [x] 6.4 Create backend/app/models/ho_tro_luong.py with `DlHoTroLuong` model:
    - Fields: id, nhan_vien_id FK, thang, nam, loai_ho_tro (str or FK), so_tien (Numeric 0–999,999,999), ghi_chu
    - _Requirements: 6.1, 6.2_

  - [x] 6.5 Update backend/app/models/__init__.py to import all new models:
    - Import DmChucVu, DmCapBacQL, DmNghiepVu, DmKiemNhiem, NvNghiepVu, NvKiemNhiem
    - Import DmLoaiTietNgoai, DmLoaiHoTro, DlHoTroLuong
    - _Requirements: 1.2, 1.3, 1.4, 1.5_

  - [x] 6.6 Update backend/app/routers/danh_muc.py:
    - Remove "chuc-danh" from LOAI_MAP (replaced by dedicated routers)
    - Add "loai-tiet-ngoai" → DmLoaiTietNgoai to LOAI_MAP
    - Add "loai-ho-tro" → DmLoaiHoTro to LOAI_MAP
    - Update REFERENCE_CHECK_MAP: remove chuc-danh, add chuc-vu/cap-bac-ql refs
    - _Requirements: 1.2, 1.3, 5.3, 6.3_

  - [x] 6.7 Create backend/app/routers/chuc_danh.py with dedicated CRUD endpoints:
    - GET/POST/PUT/DELETE /api/chuc-vu — manage Chức Vụ records (ma, ten, don_gia_luong_khoan)
    - GET/POST/PUT/DELETE /api/cap-bac-ql — manage Cấp Bậc QL records
    - GET/POST/PUT/DELETE /api/nghiep-vu — manage Nghiệp Vụ records
    - GET/POST/PUT/DELETE /api/kiem-nhiem — manage Kiêm Nhiệm records
    - Unique code validation on create/update (reject duplicate ma with 409)
    - Referential integrity check on delete
    - _Requirements: 1.2, 1.3, 1.4, 1.5, 1.18, 1.19_

  - [x] 6.8 Create backend/app/schemas/chuc_danh.py with Pydantic schemas:
    - ChucVuCreate, ChucVuUpdate, ChucVuResponse (include don_gia_luong_khoan)
    - CapBacQLCreate, CapBacQLUpdate, CapBacQLResponse
    - NghiepVuCreate, NghiepVuUpdate, NghiepVuResponse
    - KiemNhiemCreate, KiemNhiemUpdate, KiemNhiemResponse
    - NvNghiepVuCreate, NvNghiepVuResponse, NvKiemNhiemCreate, NvKiemNhiemResponse
    - _Requirements: 1.2, 1.3, 1.4, 1.5_

  - [x] 6.9 Create Alembic migration backend/alembic/versions/002_refactor_position_structure.py:
    - Create tables: dm_chuc_vu, dm_cap_bac_ql, dm_nghiep_vu, dm_kiem_nhiem
    - Create junction tables: nv_nghiep_vu, nv_kiem_nhiem
    - Create tables: dm_loai_tiet_ngoai, dm_loai_ho_tro, dl_ho_tro_luong
    - Alter nhan_vien: drop chuc_danh_id, add chuc_vu_id, cap_bac_ql_id, ten_goi
    - Drop dm_chuc_danh table (or mark deprecated)
    - _Requirements: 1.2, 1.3, 1.4, 1.5, 1.8, 1.10_

  - [x] 6.10 Update backend/app/seed.py to seed new catalog data:
    - Seed dm_chuc_vu with defaults (GVCN, PCN, GVu, etc.)
    - Seed dm_cap_bac_ql with default levels
    - Seed dm_loai_tiet_ngoai (Vĩnh Yên, Bồi dưỡng, IELTS, Luyện thi, Âm nhạc)
    - Seed dm_loai_ho_tro (ăn trưa, gửi xe, ChatGPT)
    - _Requirements: 5.3, 6.3_

  - [x] 6.11 Register new routers in backend/app/main.py:
    - Add router for /api/chuc-vu, /api/cap-bac-ql, /api/nghiep-vu, /api/kiem-nhiem
    - _Requirements: 1.2, 1.3, 1.4, 1.5_

- [x] 7. Implement Nhân viên (Employee) APIs with new position structure
  CRUD for employees with chuc_vu, cap_bac_ql assignments, nghiep_vu/kiem_nhiem junction management, ten_goi for GV, and Lương Khoán calculation endpoint.
  - [x] 7.1 Create backend/app/schemas/nhan_vien.py with updated schemas:
    - NhanVienCreate: ma_nv, ho_ten, nhom_nv (GV/VP), don_vi_id, chuc_vu_id, cap_bac_ql_id, ten_goi (optional, GV only), loai_hop_dong, trang_thai
    - NhanVienUpdate: partial update of all fields
    - NhanVienResponse: include chuc_vu detail, cap_bac_ql detail, nghiep_vu list, kiem_nhiem list, computed luong_khoan
    - HopDongCreate, HopDongResponse for contract management
    - _Requirements: 1.8, 1.9, 1.10, 1.11_

  - [x] 7.2 Create backend/app/routers/nhan_vien.py with endpoints:
    - GET /api/nhan-vien — list with filters (nhom_nv, trang_thai, don_vi_id)
    - POST /api/nhan-vien — create (validate GV/VP required, ten_goi only for GV)
    - PUT /api/nhan-vien/{id} — update (validate ten_goi null for VP)
    - GET /api/nhan-vien/{id} — detail with position/assignment info
    - DELETE /api/nhan-vien/{id} — soft-delete (set trang_thai=nghi_viec)
    - _Requirements: 1.8, 1.9, 1.10, 1.11, 1.18, 1.20_

  - [x] 7.3 Implement assignment endpoints in backend/app/routers/nhan_vien.py:
    - POST /api/nhan-vien/{nv_id}/nghiep-vu — assign nghiệp vụ (with mo_ta, dates)
    - DELETE /api/nhan-vien/{nv_id}/nghiep-vu/{id} — remove assignment
    - POST /api/nhan-vien/{nv_id}/kiem-nhiem — assign kiêm nhiệm
    - DELETE /api/nhan-vien/{nv_id}/kiem-nhiem/{id} — remove assignment
    - _Requirements: 1.4, 1.5, 1.6_

  - [x] 7.4 Implement contract history endpoints:
    - GET /api/nhan-vien/{id}/hop-dong — list contracts with history
    - POST /api/nhan-vien/{id}/hop-dong — create new contract (validate dates)
    - PUT /api/nhan-vien/{id}/hop-dong/{hd_id} — update contract
    - _Requirements: 1.17_

  - [x] 7.5 Create backend/app/routers/import_nv.py:
    - POST /api/nhan-vien/import — Excel/CSV import with validation
    - Validate unique ma_nv, valid nhom_nv, reference checks for don_vi/chuc_vu/cap_bac
    - Return per-row errors (up to 100), preview before commit
    - _Requirements: 11.1, 11.2, 11.4, 11.5_

- [x] 8. Implement Unified TKB Import and Change Log APIs
  Import timetable from single unified form (all grades), manage change log, and calculate BCC summary.
  - [x] 8.1 Create backend/app/schemas/tkb.py with schemas:
    - TKBImportRow: nhan_vien (code/name), mon_hoc, khoi, lop, so_tiet, loai_tiet
    - TKBImportResponse: imported_count, errors per row
    - ThayDoiCreate: ngay, tiet (1-10), lop_id, mon_hoc_id, gv_goc_id, gv_thay_id, ly_do (max 200 chars)
    - ThayDoiResponse, BCCResponse
    - _Requirements: 2.1, 3.1_

  - [x] 8.2 Create backend/app/routers/tkb.py with endpoints:
    - POST /api/tkb/import — upload unified Excel/CSV (all grades in one file)
    - Parse file, validate each row against master data (teacher, subject, grade, class)
    - Reject unmatched rows with specific error per field
    - Handle existing month: prompt replacement (return 409 if exists, client confirms)
    - Support partial import (only valid rows) or cancel entire import
    - GET /api/tkb/{thang}/{nam} — return TKB data
    - GET /api/tkb/template — download import template
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9_

  - [x] 8.3 Implement change log endpoints in backend/app/routers/tkb.py:
    - POST /api/tkb/thay-doi — create single change record
    - Validate: original teacher in current TKB, period 1-10, required fields
    - Subtract period from original teacher, add to substitute teacher
    - GET /api/tkb/thay-doi/{thang}/{nam} — list changes for month
    - PUT /api/tkb/thay-doi/{id} — edit (reverse old adjustment, apply new)
    - DELETE /api/tkb/thay-doi/{id} — delete (reverse adjustment)
    - POST /api/tkb/thay-doi/import — bulk import (max 500 rows, reject all if any fail)
    - Duplicate detection: same gv_goc, ngay, tiet, lop → warning
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_

  - [x] 8.4 Create backend/app/services/bcc_service.py with BCC calculation:
    - Calculate 4 column groups per teacher: Theo TKB, Thay đổi, Phát sinh, Thực tế
    - Thực tế sub-columns: Tiết chính HS1, TNST VY (HS1.3), K9 luyện thi (HS1.5), KH TA, Ielts
    - Tổng = (Tiết chính × 1.0) + (TNST VY × 1.3) + (K9 LT × 1.5) + (KH TA × 1.0) + (Ielts × 1.0)
    - Source Phát sinh from dl_tiet_day_ngoai (consolidated table)
    - Mark incomplete rows (missing thay_doi or phat_sinh data)
    - All period values rounded to 1 decimal place
    - _Requirements: 4.1, 4.2, 4.3, 4.6, 4.7, 4.8, 4.9_

  - [x] 8.5 Implement BCC API endpoint:
    - GET /api/bao-cao/bcc/{thang}/{nam} — generate and return BCC summary
    - POST /api/tkb/phat-sinh — manual adjustments (-50.0 to +50.0) with audit trail (user, timestamp, reason max 200 chars)
    - Recalculate on each generation from current source data
    - _Requirements: 4.4, 4.5, 4.8_

- [x] 9. Implement External Period and Support Allowance APIs
  Consolidated external period table and dedicated support allowance table.
  - [x] 9.1 Create backend/app/schemas/tiet_ngoai.py with schemas:
    - TietNgoaiCreate: nhan_vien_id, thang, nam, loai (type from dm_loai_tiet_ngoai), so_tiet, don_gia, he_so
    - TietNgoaiResponse: include computed thanh_tien (so_tiet × don_gia × he_so)
    - TietNgoaiImportRow for bulk import
    - _Requirements: 5.1, 5.2_

  - [x] 9.2 Create backend/app/routers/tiet_ngoai.py with endpoints:
    - GET /api/tiet-ngoai/{thang}/{nam} — list all external periods for month
    - POST /api/tiet-ngoai — add single entry (validate teacher exists, loai recognized)
    - PUT /api/tiet-ngoai/{id} — update entry
    - DELETE /api/tiet-ngoai/{id} — delete entry
    - POST /api/tiet-ngoai/import — bulk import from Excel/CSV with validation
    - Auto-calculate thanh_tien = so_tiet × don_gia × he_so on save
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_

  - [x] 9.3 Create backend/app/schemas/ho_tro_luong.py with schemas:
    - HoTroLuongCreate: nhan_vien_id, thang, nam, loai_ho_tro, so_tien (0–999,999,999), ghi_chu
    - HoTroLuongResponse, HoTroLuongBatchCreate (multiple employees, one type, one month)
    - _Requirements: 6.1, 6.2_

  - [x] 9.4 Create backend/app/routers/ho_tro_luong.py with endpoints:
    - GET /api/ho-tro-luong/{thang}/{nam} — list all allowances for month
    - POST /api/ho-tro-luong — add single entry (validate employee, type recognized)
    - POST /api/ho-tro-luong/batch — batch entry (list of employees, one type, one month)
    - POST /api/ho-tro-luong/import — bulk import from Excel/CSV
    - PUT /api/ho-tro-luong/{id} — update entry
    - DELETE /api/ho-tro-luong/{id} — delete entry
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8_

  - [x] 9.5 Register new routers in backend/app/main.py:
    - Add /api/tiet-ngoai router
    - Add /api/ho-tro-luong router
    - _Requirements: 5.1, 6.1_

- [x] 10. Implement VP Attendance (Misa Import) APIs
  Import VP attendance from Misa Excel export, manual entry/edit, and auto-summary calculation.
  - [x] 10.1 Create backend/app/schemas/cham_cong.py with schemas:
    - MisaImportRow: employee code/name, ngay_cong, ngay_nghi, ngay_phep, lam_them
    - MisaImportResponse: imported_count, errors per row
    - ChamCongManualCreate: nhan_vien_id, ngay, ky_hieu_cong_id, ghi_chu
    - TongHopCongResponse: nhan_vien_id, thang, nam, ngay_cong, ngay_nghi, ngay_phep, lam_them
    - _Requirements: 8.1, 8.2_

  - [x] 10.2 Create backend/app/services/misa_import_service.py:
    - Parse Misa Excel export file format (column mapping)
    - Match rows to employees by ma_nv or ho_ten
    - Validate: reject unmatched employees, unrecognizable format
    - Return valid rows + error rows with reasons
    - Map data to dl_tong_hop_cong (ngay_cong, ngay_nghi, ngay_phep, lam_them)
    - _Requirements: 8.1, 8.2, 8.3_

  - [x] 10.3 Create backend/app/routers/cham_cong.py with endpoints:
    - POST /api/cham-cong/import-misa — upload Misa Excel, parse, validate, import
    - GET /api/cham-cong/{thang}/{nam} — list attendance records for month
    - POST /api/cham-cong — manual entry (single record)
    - PUT /api/cham-cong/{id} — manual edit (correction)
    - GET /api/tong-hop-cong/{thang}/{nam} — attendance summary per employee
    - Flag incomplete records (fewer days than working days in month)
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.8, 8.9_

  - [x] 10.4 Implement attendance summary auto-calculation:
    - On import or manual entry, recalculate dl_tong_hop_cong for affected employee/month
    - Standard working days default: 26 (configurable per month via system settings)
    - _Requirements: 8.4, 8.5_

- [x] 11. Implement Salary Engine (Lương Khoán + Teaching + VP)
  Core salary calculation service covering Lương Khoán formula, teacher teaching income, and VP attendance-based salary.
  - [x] 11.1 Create backend/app/services/luong_khoan_engine.py:
    - Function `calculate_luong_khoan(nhan_vien_id, db)` → int (VND)
    - Formula: đơn_giá_chức_vụ + đơn_giá_cấp_bậc + (count_nghiep_vu × 2,000,000) + (count_kiem_nhiem × 3,000,000)
    - Query dm_chuc_vu.don_gia_luong_khoan via nhan_vien.chuc_vu_id
    - Query dm_cap_bac_ql.don_gia_luong_khoan via nhan_vien.cap_bac_ql_id
    - Count active nv_nghiep_vu and nv_kiem_nhiem assignments
    - Handle null chuc_vu_id or cap_bac_ql_id (treat as 0)
    - _Requirements: 1.7, 7.6, 8.10_

  - [x] 11.2 Create backend/app/services/salary_engine.py with SalaryEngine class:
    - Method `calculate_teacher_salary(nhan_vien_id, thang, nam, db)`:
      - Get BCC Thực tế data for teacher
      - For each Subject×Grade: actual_periods × unit_price × coefficient (1.0/1.3/1.5)
      - Sum regular teaching income
      - Sum external teaching income from dl_tiet_day_ngoai
      - Return breakdown: luong_khoan, teaching_income, external_income
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.7, 7.8_

  - [x] 11.3 Implement VP salary calculation in salary_engine.py:
    - Method `calculate_vp_salary(nhan_vien_id, thang, nam, db)`:
      - Get dl_tong_hop_cong for employee/month
      - Calculate: (he_so_luong × luong_co_so) × (ngay_cong / ngay_chuan)
      - Apply probation percentage (default 85%) if employee is thu_viec
      - Handle mid-month transition: pro-rata calculation
      - Standard days configurable (default 26)
    - _Requirements: 8.5, 8.6, 8.7_

  - [x] 11.4 Implement payslip generation in salary_engine.py:
    - Method `generate_payslip(nhan_vien_id, thang, nam, db)`:
      - Section I: employee info, ten_goi (GV), chuc_vu, cap_bac_ql, nghiep_vu[], kiem_nhiem[], luong_khoan, ngay_cong
      - Section II: 9 line items (luong_khoan prorated, teaching, exam fees, support allowances from dl_ho_tro_luong, birthday, overtime, events, supplement, tet)
      - Section III: manually entered already-received bonuses
      - Section IV: 5 deductions (insurance, đoàn phí, accumulation, PIT, recovery)
      - Section V: tax settlement (year-end only)
      - Section VI: Net = II - III - IV ± V
    - Validate all required data present; list missing items if incomplete
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8, 9.9_

  - [x] 11.5 Implement support allowance integration:
    - Query dl_ho_tro_luong for employee/month → sum so_tien for Section II item 4
    - _Requirements: 6.7_

  - [x] 11.6 Implement insurance calculation helper:
    - 8% BHXH + 1.5% BHYT + 1% BHTN + 1% CĐ on luong_dong_bh (from hop_dong)
    - _Requirements: 9.5_

  - [x]* 11.7 Write property test for Lương Khoán formula:
    - **Property 1: Lương Khoán formula correctness**
    - Generate random chuc_vu don_gia (0–999,999,999), cap_bac don_gia (0–999,999,999), n nghiep_vu (0–10), m kiem_nhiem (0–10)
    - Assert: result == don_gia_cv + don_gia_cb + (n × 2,000,000) + (m × 3,000,000)
    - **Validates: Requirements 1.7, 7.6, 8.10**

  - [x]* 11.8 Write property test for teacher teaching income:
    - **Property 6: Teacher teaching income calculation**
    - Generate random period counts and unit prices across Subject×Grade combos
    - Assert: total == sum of (periods × price × coefficient) for each combo
    - **Validates: Requirements 7.1, 7.2, 7.5**

  - [x]* 11.9 Write property test for VP salary from attendance:
    - **Property 7: VP salary from attendance**
    - Generate random coefficient, base_salary, actual_days, standard_days (>0)
    - Assert: result == (coefficient × base_salary) × (actual_days / standard_days)
    - **Validates: Requirements 8.5**

  - [x]* 11.10 Write property test for Net Pay formula:
    - **Property 9: Payslip Net Pay formula**
    - Generate random Section II, III, IV, V amounts
    - Assert: net_pay == section_ii - section_iii - section_iv + section_v
    - **Validates: Requirements 9.7**

- [x] 12. Checkpoint - Verify salary engine
  - Ensure all tests pass, ask the user if questions arise.

- [x] 13. Implement Tax Engine
  Personal Income Tax (PIT) calculation with 7-bracket progressive rates and year-end settlement.
  - [x] 13.1 Create backend/app/services/tax_engine.py with TaxEngine class:
    - Method `calculate_monthly_pit(total_income, insurance, personal_deduction=11_000_000, dependents=0)`:
      - Taxable = total_income - insurance - 11M - (dependents × 4.4M)
      - If taxable <= 0: return 0
      - Apply 7-bracket progressive rate: 5M×5%, 5M×10%, 8M×15%, 14M×20%, 14M×25%, 18M×30%, remainder×35%
      - Return tax amount (rounded to integer)
    - _Requirements: 9.5 (item 4 of Section IV)_

  - [x] 13.2 Implement year-end tax settlement:
    - Method `calculate_annual_settlement(nhan_vien_id, nam, db)`:
      - Sum all monthly incomes for the year
      - Calculate annual PIT liability
      - Subtract total PIT already deducted monthly
      - Return adjustment amount (positive = owe more, negative = refund)
    - _Requirements: 9.6_

  - [x] 13.3 Integrate tax_engine into salary_engine.py payslip generation:
    - Call calculate_monthly_pit for Section IV item 4
    - Call calculate_annual_settlement for Section V (when year-end month)
    - _Requirements: 9.5, 9.6, 9.7_

  - [x]* 13.4 Write unit tests for tax engine:
    - Test bracket boundaries (exactly at 5M, 10M, 18M, etc.)
    - Test zero income, negative taxable (returns 0)
    - Test with dependents reducing taxable below zero
    - _Requirements: 9.5_

- [x] 14. Implement Salary API Endpoints
  API routes for salary calculation, approval workflow, Lương Khoán query, and payslip retrieval.
  - [x] 14.1 Create backend/app/schemas/luong.py with schemas:
    - TinhLuongRequest: thang, nam, nhan_vien_ids (optional, all if empty)
    - BangLuongResponse: list of salary records with status
    - PhieuLuongResponse: full 6-section payslip data
    - LuongKhoanResponse: breakdown (chuc_vu, cap_bac, nghiep_vu count, kiem_nhiem count, total)
    - _Requirements: 9.1, 9.3_

  - [x] 14.2 Create backend/app/routers/luong.py with endpoints:
    - POST /api/luong/tinh-luong — calculate all employees for month/year
    - POST /api/luong/tinh-luong/{nv_id} — calculate single employee
    - GET /api/luong/luong-khoan/{nv_id} — return Lương Khoán breakdown
    - PUT /api/luong/duyet/{id} — approve (draft→reviewed→approved with version conflict detection)
    - GET /api/luong/bang-luong/{thang}/{nam} — salary table for month
    - GET /api/luong/phieu-luong/{nv_id}/{thang}/{nam} — individual payslip
    - _Requirements: 7.6, 9.1, 9.7, 9.8, 13.2, 14.1_

  - [x] 14.3 Implement salary calculation workflow:
    - Check all prerequisites (BCC complete, attendance complete, unit prices defined)
    - Flag missing data with specific items and prevent finalization
    - Store result in dl_bang_luong with all JSON sections
    - Support version-based conflict detection on approval
    - _Requirements: 7.4, 9.9, 13.2, 14.1_

  - [x] 14.4 Implement audit trail for salary calculations:
    - Record: calculation date, user who calculated, user who approved
    - Snapshot input data (salary grade, unit prices, luong_khoan components, allowances, attendance)
    - Immutable once approved; corrections create new revision linked to original
    - _Requirements: 14.1, 14.2, 14.3, 14.4_

- [x] 15. Implement Export and Reports
  Excel/PDF export for Misa format, payslips, and summary reports.
  - [x] 15.1 Create backend/app/services/export_service.py:
    - Class MisaExporter: generate Excel matching Misa bulk import column structure
    - Method export_salary_to_misa(thang, nam, db) → BytesIO (xlsx)
    - _Requirements: 10.2_

  - [x] 15.2 Create backend/app/routers/bao_cao.py with report endpoints:
    - GET /api/bao-cao/bcc/{thang}/{nam} — BCC tổng tiết report
    - GET /api/bao-cao/luong/{thang}/{nam} — monthly salary summary
    - GET /api/bao-cao/luong-nam/{nam} — yearly salary summary
    - GET /api/bao-cao/cham-cong/{thang}/{nam} — monthly attendance summary
    - POST /api/export/misa — export to Misa format (Excel download)
    - POST /api/export/phieu-luong/{nv_id}/{thang}/{nam}?format=pdf|xlsx — export payslip
    - Include generation date, period, user in all reports
    
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 10.9_

  - [x] 15.3 Create payslip PDF template:
    - Create backend/app/templates/phieu_luong.html (Jinja2 template)
    - 6 sections: Employee Info, Total Income (9 items), Already Received, Deductions (5 items), Tax Settlement, Net Pay
    - Include ten_goi for GV, chuc_vu, cap_bac_ql, nghiep_vu, kiem_nhiem in Section I
    - _Requirements: 10.1, 10.7, 9.1_

  - [x] 15.4 Implement Excel export for reports:
    - Use openpyxl to generate formatted Excel files
    - BCC report: teacher rows × 4 column groups
    - Salary summary: all employees × salary components
    - _Requirements: 10.7, 10.8_

- [x] 16. Checkpoint - Backend complete
  - Ensure all tests pass, ask the user if questions arise.

- [x] 17. Frontend - Login, Layout, and Routing
  React app with authentication, Ant Design Pro Layout, and route guards.
  - [x] 17.1 Create frontend/src/services/api.js:
    - Axios instance with baseURL (env var), token interceptor
    - Auto-redirect to login on 401
    - _Requirements: 12.1_

  - [x] 17.2 Create frontend/src/store/authStore.js:
    - Login/logout state management (localStorage token)
    - User info (role, full_name) from /api/auth/me
    - _Requirements: 12.1_

  - [x] 17.3 Create frontend/src/pages/Login.jsx:
    - Ant Design Form: username + password fields
    - Handle account lockout message display
    - Redirect to dashboard on success
    - _Requirements: 12.1, 12.8_

  - [x] 17.4 Create frontend/src/components/Layout.jsx:
    - Ant Design ProLayout with sidebar navigation
    - Menu items based on user role (Admin sees all, Accountant sees data/salary, Viewer sees reports)
    - Header with user info and logout button
    - _Requirements: 12.2_

  - [x] 17.5 Create frontend/src/components/ProtectedRoute.jsx:
    - Role-based route guard component
    - Redirect unauthorized access to appropriate page
    - _Requirements: 12.2, 12.3, 12.4_

  - [x] 17.6 Update frontend/src/App.jsx with all routes:
    - /login, /dashboard, /danh-muc/*, /nhan-vien, /tkb, /tiet-ngoai, /ho-tro-luong, /cham-cong, /bang-luong, /phieu-luong, /bao-cao
    - Wrap routes in ProtectedRoute with appropriate roles
    - _Requirements: 12.2_

- [x] 18. Frontend - Danh mục and Position Management
  Catalog CRUD pages including new Chức Vụ, Cấp Bậc QL, Nghiệp Vụ, Kiêm Nhiệm management.
  - [x] 18.1 Create frontend/src/components/CrudTable.jsx:
    - Reusable CRUD table with Ant Design Table + Modal for add/edit + Popconfirm delete
    - Support columns config, form fields config, API endpoints config
    - _Requirements: 1.1_

  - [x] 18.2 Create frontend/src/pages/DanhMuc/DonVi.jsx:
    - Department management using CrudTable
    - _Requirements: 1.1_

  - [x] 18.3 Create frontend/src/pages/DanhMuc/ChucVu.jsx:
    - Chức Vụ management: ma (unique code), ten, don_gia_luong_khoan
    - Input validation: don_gia 0–999,999,999 VND
    - _Requirements: 1.2_

  - [x] 18.4 Create frontend/src/pages/DanhMuc/CapBacQL.jsx:
    - Cấp Bậc QL management: ma, ten, don_gia_luong_khoan
    - _Requirements: 1.3_

  - [x] 18.5 Create frontend/src/pages/DanhMuc/NghiepVu.jsx:
    - Nghiệp Vụ management: ma, ten (display "mỗi NV +2,000,000 VND")
    - _Requirements: 1.4_

  - [x] 18.6 Create frontend/src/pages/DanhMuc/KiemNhiem.jsx:
    - Kiêm Nhiệm management: ma, ten (display "mỗi KN +3,000,000 VND")
    - _Requirements: 1.5_

  - [x] 18.7 Create frontend/src/pages/DanhMuc/MonHoc.jsx and HeSoLuong.jsx:
    - Subject and salary grade management pages
    - _Requirements: 1.1, 1.14_

  - [x] 18.8 Create frontend/src/pages/DonGiaDay.jsx:
    - Unit price management: Teacher × Subject × Grade grid
    - History tracking display (previous values with date ranges)
    - _Requirements: 1.12, 1.13_

  - [x] 18.9 Create frontend/src/services/danhMucApi.js:
    - API calls for all catalog CRUD operations
    - Include chuc-vu, cap-bac-ql, nghiep-vu, kiem-nhiem endpoints
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 19. Frontend - Nhân viên Management
  Employee list with position assignments, Lương Khoán display, and Excel import.
  - [x] 19.1 Create frontend/src/pages/NhanVien.jsx:
    - Searchable employee table (filter by nhom_nv, trang_thai, don_vi)
    - Columns: ma_nv, ho_ten, ten_goi (GV only), nhom_nv, chuc_vu, cap_bac_ql, luong_khoan, trang_thai
    - Add/Edit drawer with conditional fields (ten_goi shown only when nhom_nv=GV)
    - _Requirements: 1.8, 1.9, 1.10, 1.11_

  - [x] 19.2 Create frontend/src/pages/NhanVienDetail.jsx:
    - Tabs: Thông tin, Hợp đồng, Nghiệp vụ, Kiêm nhiệm
    - Nghiệp vụ tab: list assigned NV + add/remove with mo_ta and dates
    - Kiêm nhiệm tab: list assigned KN + add/remove with mo_ta and dates
    - Display computed Lương Khoán breakdown
    - _Requirements: 1.4, 1.5, 1.6, 1.7, 1.8_

  - [x] 19.3 Create frontend/src/components/ImportExcel.jsx:
    - Reusable Excel/CSV upload component
    - File validation (max 10MB, .xlsx/.xls/.csv)
    - Preview first 20 rows, show total count
    - Display per-row errors (up to 100)
    - Confirm/cancel buttons
    - _Requirements: 11.1, 11.2, 11.4, 11.5_

  - [x] 19.4 Create frontend/src/services/nhanVienApi.js:
    - CRUD + assignment + import API calls
    - _Requirements: 1.8_

- [x] 20. Frontend - Thời khóa biểu (Unified TKB)
  Timetable import from unified form, change log management, and BCC display.
  - [x] 20.1 Create frontend/src/pages/ThoiKhoaBieu.jsx:
    - Month/year selector + TKB data table
    - Import button → upload unified Excel (all grades)

    - Show import summary after success
    - Handle existing month warning (confirm replace)
    - _Requirements: 2.1, 2.4, 2.5, 2.6, 2.8_

  - [x] 20.2 Create frontend/src/components/TKBImport.jsx:
    - File upload with drag-and-drop
    - Validation error display per row (field + value)
    - Option to import only valid rows or cancel
    - Download template button
    - _Requirements: 2.1, 2.2, 2.3, 2.7, 2.9_

  - [x] 20.3 Create frontend/src/components/ThayDoiModal.jsx:
    - Form: original teacher, substitute, date, period (1-10), class, subject, reason
    - Bulk import option for change records
    - Duplicate warning display
    - _Requirements: 3.1, 3.4, 3.5, 3.6_

  - [x] 20.4 Create frontend/src/pages/BCCTongTiet.jsx:
    - BCC summary table: 4 column groups (Theo TKB, Thay đổi, Phát sinh, Thực tế)
    - Thực tế sub-columns: Tiết chính, TNST VY, K9 LT, KH TA, Ielts, Tổng
    - Inline edit for Phát sinh adjustments (with reason input)
    - Highlight incomplete rows
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

  - [x] 20.5 Create frontend/src/services/tkbApi.js:
    - Import, TKB data, change log, BCC API calls
    - _Requirements: 2.1, 3.1, 4.1_

- [x] 21. Frontend - Tiết dạy ngoài & Hỗ trợ lương
  External period consolidated table and support allowance management pages.
  - [x] 21.1 Create frontend/src/pages/TietDayNgoai.jsx:
    - Month/year selector + table of all external periods
    - Add/edit form: teacher, loai (dropdown from dm_loai_tiet_ngoai), so_tiet, don_gia, he_so
    - Auto-display thanh_tien = so_tiet × don_gia × he_so
    - Excel import button
    - _Requirements: 5.1, 5.2, 5.3, 5.6_

  - [x] 21.2 Create frontend/src/pages/HoTroLuong.jsx:
    - Month/year selector + table of all support allowances
    - Add single entry: employee, loai_ho_tro (dropdown from dm_loai_ho_tro), so_tien, ghi_chu
    - Batch entry mode: select type + month → enter amounts for multiple employees
    - Excel import button
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.6, 6.8_

  - [x] 21.3 Create frontend/src/services/tietNgoaiApi.js and hoTroLuongApi.js:
    - API calls for external period and support allowance CRUD + import
    - _Requirements: 5.1, 6.1_

- [x] 22. Frontend - Chấm công (VP Attendance with Misa Import)
  Attendance management with Misa import and manual editing.
  - [x] 22.1 Create frontend/src/pages/ChamCong.jsx:
    - Month/year selector + employee attendance table
    - "Import từ Misa" button → upload Misa Excel export
    - Display import results (matched/unmatched employees)
    - Manual edit capability for corrections
    - Summary display: ngày công, ngày nghỉ, ngày phép, làm thêm per employee
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.8_

  - [x] 22.2 Implement attendance grid with editable cells:
    - Rows = VP employees, columns = summary fields
    - Flag incomplete records visually (yellow/red highlight)
    - _Requirements: 8.8, 8.9_

  - [x] 22.3 Create frontend/src/services/chamCongApi.js:
    - Misa import, manual CRUD, summary API calls
    - _Requirements: 8.1_

- [x] 23. Frontend - Bảng lương & Phiếu lương
  Salary table, calculation trigger, approval workflow, and payslip display.
  - [x] 23.1 Create frontend/src/pages/BangLuong.jsx:
    - Month/year selector + salary summary table (all employees)
    - "Tính lương" button with confirmation dialog
    - Status badges: draft (gray), reviewed (blue), approved (green)
    - Action buttons based on status and user role
    - _Requirements: 9.8, 13.2, 14.1_

  - [x] 23.2 Implement approval workflow UI:
    - Draft → "Duyệt" button (Accountant/Admin) → Reviewed → "Phê duyệt" (Admin) → Approved
    - Conflict detection: show warning if version changed since load
    - _Requirements: 13.2, 14.1_

  - [x] 23.3 Create frontend/src/pages/PhieuLuong.jsx:
    - Full 6-section payslip display
    - Section I: employee info with ten_goi, chuc_vu, cap_bac, nghiep_vu, kiem_nhiem, luong_khoan
    - Section II: 9 income items with amounts
    - Section III: already received
    - Section IV: 5 deduction items
    - Section V: tax settlement (if applicable)
    - Section VI: net pay (highlighted)
    - Export buttons: PDF, Excel
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8_

  - [x] 23.4 Create frontend/src/services/luongApi.js:
    - Calculate, approve, payslip, export API calls
    - _Requirements: 9.1_

- [x] 24. Frontend - Báo cáo & Export
  Report generation, export to Misa format, and file downloads.
  - [x] 24.1 Create frontend/src/pages/BaoCao.jsx:
    - Report type selector: BCC tổng tiết, Tổng hợp lương tháng, Tổng hợp lương năm, Chấm công
    - Month/year picker based on report type
    - Generate button → display report or trigger download
    - _Requirements: 10.1, 10.3, 10.4, 10.5, 10.6_

  - [x] 24.2 Implement Misa export UI:
    - "Xuất Misa" button on salary page
    - Download Excel file in Misa-compatible format
    - _Requirements: 10.2_

  - [x] 24.3 Implement file download for PDF and Excel:
    - Payslip PDF download (individual employee)
    - Report Excel download (summary reports)
    - _Requirements: 10.7_

  - [x] 24.4 Create frontend/src/services/baoCaoApi.js:
    - Report generation and export API calls
    - _Requirements: 10.1_

- [x] 25. Frontend - Admin and User Management
  User management page and system configuration for Admin role.
  - [x] 25.1 Create frontend/src/pages/UserManagement.jsx:
    - User table: username, full_name, role, is_active
    - Add user form: username, password (validation), full_name, role
    - Deactivate/activate toggle (prevent deactivating last admin)
    - Admin-only access
    - _Requirements: 12.2, 12.5, 12.9, 12.10_

  - [x] 25.2 Create frontend/src/pages/Dashboard.jsx:
    - Summary cards: total employees (GV/VP), current month salary status, pending approvals
    - Quick links to common actions
    - Role-based content visibility
    - _Requirements: 12.2_

- [x] 26. Final checkpoint - Full system verification
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional property-based tests and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints (tasks 12, 16, 26) ensure incremental validation
- Property tests validate universal correctness properties from the design document
- Tasks 1-5 are completed; task 6 refactors existing code to match updated requirements
- The dm_chuc_danh table is deprecated and replaced by dm_chuc_vu + dm_cap_bac_ql + dm_nghiep_vu + dm_kiem_nhiem
- Lương Khoán formula: đơn_giá_chức_vụ + đơn_giá_cấp_bậc + (số_NV × 2M) + (số_KN × 3M)
- ten_goi field is GV-only; VP employees must have ten_goi = NULL
- External periods use a single consolidated table (dl_tiet_day_ngoai) for all types
- Support allowances use dedicated table (dl_ho_tro_luong) summed into payslip Section II item 4
- VP attendance is primarily imported from Misa Excel export with manual edit fallback

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["6.1", "6.3", "6.4"] },
    { "id": 1, "tasks": ["6.2", "6.5", "6.8"] },
    { "id": 2, "tasks": ["6.6", "6.7", "6.9"] },
    { "id": 3, "tasks": ["6.10", "6.11"] },
    { "id": 4, "tasks": ["7.1", "8.1", "10.1"] },
    { "id": 5, "tasks": ["7.2", "7.3", "7.4", "9.1", "9.3"] },
    { "id": 6, "tasks": ["7.5", "8.2", "9.2", "9.4", "9.5"] },
    { "id": 7, "tasks": ["8.3", "10.2"] },
    { "id": 8, "tasks": ["8.4", "10.3", "10.4"] },
    { "id": 9, "tasks": ["8.5", "11.1"] },
    { "id": 10, "tasks": ["11.2", "11.3"] },
    { "id": 11, "tasks": ["11.4", "11.5", "11.6"] },
    { "id": 12, "tasks": ["11.7", "11.8", "11.9", "11.10"] },
    { "id": 13, "tasks": ["13.1"] },
    { "id": 14, "tasks": ["13.2", "13.3", "13.4"] },
    { "id": 15, "tasks": ["14.1"] },
    { "id": 16, "tasks": ["14.2", "14.3", "14.4"] },
    { "id": 17, "tasks": ["15.1", "15.3"] },
    { "id": 18, "tasks": ["15.2", "15.4"] },
    { "id": 19, "tasks": ["17.1", "17.2"] },
    { "id": 20, "tasks": ["17.3", "17.4", "17.5"] },
    { "id": 21, "tasks": ["17.6", "18.1"] },
    { "id": 22, "tasks": ["18.2", "18.3", "18.4", "18.5", "18.6", "18.7"] },
    { "id": 23, "tasks": ["18.8", "18.9"] },
    { "id": 24, "tasks": ["19.1", "19.2", "19.3", "19.4"] },
    { "id": 25, "tasks": ["20.1", "20.2", "20.3", "20.4", "20.5"] },
    { "id": 26, "tasks": ["21.1", "21.2", "21.3"] },
    { "id": 27, "tasks": ["22.1", "22.2", "22.3"] },
    { "id": 28, "tasks": ["23.1", "23.2", "23.3", "23.4"] },
    { "id": 29, "tasks": ["24.1", "24.2", "24.3", "24.4"] },
    { "id": 30, "tasks": ["25.1", "25.2"] }
  ]
}
```
