"""
NBK Salary API - FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Hệ thống quản lý lương Trường THCS Nguyễn Bỉnh Khiêm",
    debug=settings.DEBUG,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "app": "NBK Salary API"}


@app.on_event("startup")
def on_startup():
    """Run seed on app startup to ensure admin user exists."""
    try:
        from app.database import SessionLocal, engine, Base
        from app.models.user import User, UserRole
        from passlib.context import CryptContext

        # Ensure all tables exist
        Base.metadata.create_all(bind=engine)

        pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__truncate_error=False)
        db = SessionLocal()
        try:
            existing = db.query(User).filter(User.username == "admin").first()
            if existing:
                existing.password_hash = pwd_ctx.hash("Admin123")
                existing.failed_login_count = 0
                existing.locked_until = None
                existing.is_active = True
                db.commit()
                print("[STARTUP] Admin password reset OK")
            else:
                admin = User(
                    username="admin",
                    password_hash=pwd_ctx.hash("Admin123"),
                    full_name="Quản trị viên",
                    role=UserRole.admin,
                    is_active=True,
                    failed_login_count=0,
                )
                db.add(admin)
                db.commit()
                print("[STARTUP] Admin user created OK")
        except Exception as e:
            db.rollback()
            print(f"[STARTUP] Seed error: {e}")
        finally:
            db.close()
    except Exception as e:
        print(f"[STARTUP] Fatal seed error: {e}")


@app.get("/api/debug/check-admin")
def debug_check_admin():
    """Temporary debug endpoint - remove after fixing login."""
    from app.database import SessionLocal, engine, Base
    from app.models.user import User, UserRole
    from app.utils.auth import verify_password
    from passlib.context import CryptContext

    # Force create tables
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        return {"error": f"create_all failed: {str(e)}"}

    pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__truncate_error=False)
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == "admin").first()
        if not user:
            # Create admin right now
            try:
                user = User(
                    username="admin",
                    password_hash=pwd_ctx.hash("Admin123"),
                    full_name="Quản trị viên",
                    role=UserRole.admin,
                    is_active=True,
                    failed_login_count=0,
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                return {"message": "admin created now", "password_verify": True}
            except Exception as e:
                db.rollback()
                return {"error": f"create failed: {str(e)}"}

        pw_ok = verify_password("Admin123", user.password_hash)
        return {
            "username": user.username,
            "is_active": user.is_active,
            "locked_until": str(user.locked_until) if user.locked_until else None,
            "failed_count": user.failed_login_count,
            "password_verify": pw_ok,
        }
    finally:
        db.close()


# =============================================================================
# Router includes
# Uncomment each router as it is implemented
# =============================================================================

from app.routers import auth
app.include_router(auth.router, prefix="/api", tags=["Auth"])

from app.routers import danh_muc
app.include_router(danh_muc.router, prefix="/api/danh-muc", tags=["Danh mục"])

from app.routers import don_gia_day
app.include_router(don_gia_day.router, prefix="/api/don-gia-day", tags=["Đơn giá dạy"])

from app.routers import chuc_danh
app.include_router(chuc_danh.router, prefix="/api/chuc-danh", tags=["Chức danh"])

from app.routers import nhan_vien
app.include_router(nhan_vien.router, prefix="/api/nhan-vien", tags=["Nhân viên"])

from app.routers import import_nv
app.include_router(import_nv.router, prefix="/api/nhan-vien", tags=["Import NV"])

from app.routers import tkb
app.include_router(tkb.router, prefix="/api/tkb", tags=["Thời khóa biểu"])

from app.routers import ho_tro_luong
app.include_router(ho_tro_luong.router, prefix="/api/ho-tro-luong", tags=["Hỗ trợ lương"])

from app.routers import tiet_ngoai
app.include_router(tiet_ngoai.router, prefix="/api/tiet-ngoai", tags=["Tiết dạy ngoài"])

from app.routers import cham_cong
app.include_router(cham_cong.router, prefix="/api/cham-cong", tags=["Chấm công"])

from app.routers import luong
app.include_router(luong.router, prefix="/api/luong", tags=["Lương"])

from app.routers import bao_cao
app.include_router(bao_cao.router, prefix="/api/bao-cao", tags=["Báo cáo"])

from app.routers import misa_hr
app.include_router(misa_hr.router, prefix="/api/misa-hr", tags=["MISA HR Import"])

# =============================================================================
# Serve frontend static build (for production single-port deployment)
# =============================================================================
import os
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

FRONTEND_BUILD = Path(__file__).resolve().parent.parent.parent / "frontend" / "build"

# Also check Docker path (frontend build copied to /app/build)
if not FRONTEND_BUILD.exists():
    FRONTEND_BUILD = Path(__file__).resolve().parent.parent / "build"

if FRONTEND_BUILD.exists():
    # Serve static assets (JS, CSS, images)
    app.mount("/static", StaticFiles(directory=str(FRONTEND_BUILD / "static")), name="frontend-static")

    # Catch-all route for React SPA (must be last)
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve React SPA index.html for any non-API route."""
        file_path = FRONTEND_BUILD / full_path
        if full_path and file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(FRONTEND_BUILD / "index.html"))
