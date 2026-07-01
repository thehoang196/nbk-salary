

# KIẾN TRÚC HỆ THỐNG - PHẦN MỀM TÍNH LƯƠNG NBK

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (React.js)                     │
│  ┌──────┐ ┌──────────┐ ┌────────┐ ┌───────┐ ┌───────────┐ │
│  │Login │ │Danh mục  │ │  TKB   │ │Chấm   │ │Bảng lương │ │
│  │      │ │Management│ │Manager │ │Công   │ │& Báo cáo  │ │
│  └──────┘ └──────────┘ └────────┘ └───────┘ └───────────┘ │
└─────────────────────────┬───────────────────────────────────┘
                          │ REST API (JSON)
┌─────────────────────────┴───────────────────────────────────┐
│                    BACKEND (Python FastAPI)                   │
│  ┌────────┐ ┌──────────┐ ┌───────────┐ ┌─────────────────┐ │
│  │Auth &  │ │CRUD APIs │ │Salary     │ │Export Engine    │ │
│  │RBAC    │ │(Danh mục)│ │Calculator │ │(Excel/PDF/Misa) │ │
│  └────────┘ └──────────┘ └───────────┘ └─────────────────┘ │
└─────────────────────────┬───────────────────────────────────┘
                          │ SQLAlchemy ORM
┌─────────────────────────┴───────────────────────────────────┐
│                    DATABASE (PostgreSQL)                      │
│  dm_don_vi | dm_nhan_vien | dm_don_gia | dl_tkb | dl_cham_  │
│  dm_chuc_danh | dl_hop_dong | dl_thay_doi | dl_luong | ...  │
└─────────────────────────────────────────────────────────────┘
```

## Cấu trúc thư mục dự án

```
nbk-salary/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app entry
│   │   ├── config.py            # Settings & env
│   │   ├── database.py          # DB connection
│   │   ├── models/              # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── danh_muc.py
│   │   │   ├── nhan_vien.py
│   │   │   ├── thoi_khoa_bieu.py
│   │   │   ├── cham_cong.py
│   │   │   └── luong.py
│   │   ├── schemas/             # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── danh_muc.py
│   │   │   ├── nhan_vien.py
│   │   │   ├── tkb.py
│   │   │   ├── cham_cong.py
│   │   │   └── luong.py
│   │   ├── routers/             # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── danh_muc.py
│   │   │   ├── nhan_vien.py
│   │   │   ├── tkb.py
│   │   │   ├── cham_cong.py
│   │   │   ├── luong.py
│   │   │   └── bao_cao.py
│   │   ├── services/            # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── tkb_service.py
│   │   │   ├── salary_engine.py # Core calculation
│   │   │   ├── tax_engine.py
│   │   │   └── export_service.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── security.py
│   │       └── excel_parser.py
│   ├── alembic/                 # DB migrations
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── store/
│   │   └── App.jsx
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

