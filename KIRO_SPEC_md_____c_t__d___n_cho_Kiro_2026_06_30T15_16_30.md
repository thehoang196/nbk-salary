
# NBK Salary Management System - Kiro Specification

## Project Overview
Phần mềm tính lương giáo viên trường THCS Nguyễn Bỉnh Khiêm (NBK Diamond).
Web App full-stack: React + FastAPI + PostgreSQL.

## Tech Stack
- **Frontend:** React 18 + Ant Design 5 + Axios
- **Backend:** Python FastAPI + SQLAlchemy 2.0 + Alembic
- **Database:** PostgreSQL 15
- **Auth:** JWT (python-jose + passlib)
- **Deploy:** Docker Compose
- **Export:** openpyxl (Excel), Jinja2 (PDF template)

## User Roles
| Role | Quyền |
|------|--------|
| admin | Full access (BGH) |
| accountant | CRUD lương, chấm công, TKB, xuất báo cáo |
| hr | Quản lý nhân viên, hợp đồng |
| teacher | Xem phiếu lương cá nhân |

## Core Business Logic

### Công thức tính lương (Phiếu lương 6 mục)
```
MỤC II: TỔNG THU NHẬP = (1) + (2) + (3) + (4) + (5) + (6) + (7) + (8) + (9)
  (1) Lương khoán theo ngày công = Lương_khoán_HĐ × (Ngày_công / Công_chuẩn)
  (2) Tiền giảng dạy = Σ(tiết_thực_tế × đơn_giá × hệ_số)
      - Tiết chính tại trường: HS 1.0
      - TNST tại VY: HS 1.3
      - Ôn K9 luyện thi: HS 1.5
      - Khoa học bằng TA: đơn giá riêng
      - Ielts/AN: đơn giá riêng
      + Thu nhập tiết dạy ngoài chính khóa
  (3) Ra đề, duyệt đề, chấm thi (nhập tay)
  (4) Khoán chi hỗ trợ (ăn trưa, gửi xe, ChatGPT)
  (5) Chi sinh nhật (auto: check tháng sinh)
  (6) Thưởng hiệu quả (nhập tay)
  (7) Thưởng sự kiện/tuyển sinh/cuối năm (nhập tay)
  (8) Bổ sung lương (nhập tay)
  (9) Thưởng Tết (nhập tay)

MỤC IV: GIẢM TRỪ = BH_CĐ + Đoàn_phí + Tích_lũy + Thuế_TNCN + Truy_thu
  - BH = Lương_đóng_BH × (8% BHXH + 1.5% BHYT + 1% BHTN) + 1% CĐ
  - Thuế TNCN: biểu lũy tiến 7 bậc VN

MỤC VI: THỰC LĨNH = II - III - IV + V
```

### BCC Tổng tiết GV (4 nhóm)
```
Theo TKB → Thay đổi (Nghỉ/Thay) → Phát sinh (+/-) → Thực tế
```

### Tiết dạy ngoài chính khóa
- Nhiều loại đơn giá/GV: Quản lý, Chính khóa, Ielts/AN/GTS
- Nhóm HS 1: cá nhân hóa, CLB, BDHSG, ngoài chính khóa
- Nhóm HS 1.3: Huấn luyện đội tuyển, VY
- Nhóm HS 1.5: Ôn thi lớp 9
- IELTS tách nhóm: đơn giá riêng

## Database Tables (14 tables)

### Danh mục (dm_*)
- `dm_don_vi` - Đơn vị/phòng ban
- `dm_chuc_danh` - Chức danh
- `dm_khoi` - Khối (6,7,8,9)
- `dm_lop` - Lớp
- `dm_mon_hoc` - Môn học
- `dm_vi_tri` - Vị trí công việc
- `dm_he_so_luong` - Hệ số lương
- `dm_ky_hieu_cong` - Ký hiệu chấm công (X, P, Ô, TC...)
- `dm_nhiem_vu` - Nhiệm vụ + đơn giá
- `dm_don_gia_day` - Đơn giá dạy (GV × loại_tiết × hệ_số)

### Dữ liệu (dl_*)
- `nhan_vien` - Nhân viên
- `dl_hop_dong` - Hợp đồng & lương
- `dl_tkb` - Thời khóa biểu gốc
- `dl_thay_doi_nguoi_day` - Thay đổi người dạy
- `dl_bcc_tong_tiet` - BCC tổng tiết GV (4 nhóm cột)
- `dl_tiet_day_ngoai` - Tiết dạy ngoài chính khóa
- `dl_cham_cong` - Chấm công theo ngày
- `dl_tong_hop_cong` - Tổng hợp công tháng
- `dl_bang_luong` - Bảng lương (phiếu lương 6 mục)
- `users` - Tài khoản đăng nhập

## API Endpoints

### Auth
- POST /api/auth/login
- POST /api/auth/register
- GET /api/auth/me

### Danh mục (CRUD cho mỗi loại)
- GET/POST/PUT/DELETE /api/danh-muc/{loai}

### Nhân viên
- GET/POST/PUT /api/nhan-vien
- GET/POST /api/nhan-vien/{id}/hop-dong

### Thời khóa biểu
- POST /api/tkb/import (Excel upload)
- GET /api/tkb
- POST/GET /api/tkb/thay-doi
- POST/GET /api/tkb/don-gia
- GET /api/tkb/bcc/{thang}/{nam}

### Chấm công
- POST /api/cham-cong/batch
- GET /api/cham-cong/{thang}/{nam}
- GET /api/cham-cong/tong-hop/{thang}/{nam}

### Lương
- POST /api/luong/tinh-luong (tính cho tất cả NV)
- POST /api/luong/tinh-luong/{nv_id}
- PUT /api/luong/duyet/{id}
- GET /api/luong/bang-luong/{thang}/{nam}
- GET /api/luong/phieu-luong/{nv_id}/{thang}/{nam}

### Báo cáo
- GET /api/bao-cao/export-misa/{thang}/{nam}
- GET /api/bao-cao/tong-hop/{thang}/{nam}
- GET /api/bao-cao/phieu-luong-pdf/{nv_id}/{thang}/{nam}

## Frontend Pages
1. Login
2. Dashboard (tổng quan)
3. Danh mục (tabs: Đơn vị, Chức danh, Khối, Lớp, Môn, Ký hiệu công)
4. Nhân viên (list + detail + hợp đồng)
5. Thời khóa biểu (import, xem, thay đổi người dạy, đơn giá)
6. BCC Tổng tiết (grid 4 nhóm cột, edit inline)
7. Tiết dạy ngoài (grid, edit inline)
8. Chấm công (calendar grid)
9. Bảng lương (tính, xem, duyệt, export)
10. Phiếu lương cá nhân (view + PDF)
11. Báo cáo (tổng hợp, export Misa)

## File Structure
```
D:\NBK\nbk-salary\
├── backend\
│   ├── app\
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models\
│   │   ├── schemas\
│   │   ├── routers\
│   │   ├── services\
│   │   └── utils\
│   ├── alembic\
│   ├── requirements.txt
│   └── Dockerfile
├── frontend\
│   ├── src\
│   │   ├── components\
│   │   ├── pages\
│   │   ├── services\
│   │   ├── store\
│   │   └── App.jsx
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```
