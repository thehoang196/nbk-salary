
# Kiro Tasks - NBK Salary Project

## Phase 1: Project Setup & Database
- [ ] Initialize project structure at D:\NBK\nbk-salary\
- [ ] Setup backend: FastAPI + SQLAlchemy + PostgreSQL
- [ ] Setup frontend: React + Ant Design + React Router
- [ ] Create docker-compose.yml
- [ ] Create all SQLAlchemy models (see KIRO_SPEC.md)
- [ ] Setup Alembic migrations
- [ ] Create seed data script (default users, danh mục cơ bản)

## Phase 2: Authentication & Authorization
- [ ] Implement JWT auth (login, register, token refresh)
- [ ] Role-based access control (admin, accountant, hr, teacher)
- [ ] Protected routes (frontend)
- [ ] API middleware (backend)

## Phase 3: Danh mục Management (CRUD)
- [ ] API: CRUD cho tất cả danh mục (đơn vị, chức danh, khối, lớp, môn, ký hiệu công, nhiệm vụ)
- [ ] Frontend: Trang Danh mục với tabs
- [ ] API + Frontend: Bảng đơn giá dạy (GV × loại_tiết × hệ_số)

## Phase 4: Nhân viên & Hợp đồng
- [ ] API: CRUD nhân viên
- [ ] API: CRUD hợp đồng (lịch sử lương)
- [ ] Frontend: Danh sách NV + Form thêm/sửa
- [ ] Frontend: Chi tiết NV + tab Hợp đồng
- [ ] Import nhân viên từ Excel

## Phase 5: Thời khóa biểu
- [ ] API: Import TKB từ Excel
- [ ] API: CRUD thay đổi người dạy
- [ ] Frontend: Bảng TKB + nút Import
- [ ] Frontend: Modal thay đổi người dạy
- [ ] Auto-calculate TKB thực tế từ TKB gốc + thay đổi

## Phase 6: BCC Tổng tiết GV
- [ ] API: CRUD BCC tổng tiết (4 nhóm cột)
- [ ] API: Auto-calculate từ TKB → Thay đổi → Phát sinh → Thực tế
- [ ] Frontend: Grid editable (inline edit) cho BCC
- [ ] API + Frontend: Tiết dạy ngoài chính khóa

## Phase 7: Chấm công
- [ ] API: Chấm công batch (theo tháng)
- [ ] API: Tổng hợp công tự động
- [ ] Frontend: Calendar grid chấm công
- [ ] Import chấm công từ Excel

## Phase 8: Salary Engine (Core)
- [ ] Implement SalaryEngineV2 (theo Form NBK thực tế)
- [ ] Implement TaxEngine (thuế TNCN lũy tiến 7 bậc)
- [ ] API: Tính lương tất cả NV / 1 NV
- [ ] API: Phê duyệt bảng lương
- [ ] Unit tests cho salary engine

## Phase 9: Bảng lương & Phiếu lương
- [ ] Frontend: Bảng lương tháng (table + summary)
- [ ] Frontend: Nút "Tính lương" + confirm
- [ ] Frontend: Phiếu lương cá nhân (đúng format TB luong)
- [ ] Frontend: Workflow duyệt lương (draft → reviewed → approved)

## Phase 10: Báo cáo & Export
- [ ] Export bảng lương format Misa (Excel)
- [ ] Export phiếu lương PDF (template Jinja2)
- [ ] Báo cáo tổng hợp theo phòng ban
- [ ] Gửi phiếu lương qua email (template từ Tempvtv1)

## Phase 11: Polish & Deploy
- [ ] Error handling & validation
- [ ] Loading states & UX
- [ ] Responsive design
- [ ] Docker build & deploy
- [ ] Documentation
