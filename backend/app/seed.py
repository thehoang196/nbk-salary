"""
NBK Salary - Database Seed Script

Seeds the database with initial/default data:
- Default admin user
- Khối (grades 6-9)
- Ký hiệu công (attendance symbols)
- Đơn vị (departments)
- Chức vụ (position titles)
- Cấp bậc quản lý (management levels)
- Loại tiết ngoài (external period types)
- Loại hỗ trợ (support allowance types)

Idempotent: skips data that already exists.
Run via: python -m app.seed (from backend/ directory)
"""

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.models.danh_muc import DmKhoi, DmKyHieuCong, DmDonVi, DmLoaiTietNgoai, DmLoaiHoTro
from app.models.chuc_danh import DmChucVu, DmCapBacQL

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__truncate_error=False)


def seed_admin(db: Session) -> None:
    """Create default admin user if not exists, or reset password if exists."""
    existing = db.query(User).filter(User.username == "admin").first()
    if existing:
        # Always reset password and unlock on deploy
        existing.password_hash = pwd_context.hash("Admin123")
        existing.failed_login_count = 0
        existing.locked_until = None
        existing.is_active = True
        db.commit()
        print("  [OK] Reset admin password and unlocked account.")
        return

    admin = User(
        username="admin",
        password_hash=pwd_context.hash("Admin123"),
        full_name="Quản trị viên",
        role=UserRole.admin,
        is_active=True,
    )
    db.add(admin)
    db.commit()
    print("  [OK] Created admin user.")


def seed_khoi(db: Session) -> None:
    """Create default khối (grades) if not exists."""
    khoi_data = [
        {"ten": "Khối 6", "thu_tu": 1},
        {"ten": "Khối 7", "thu_tu": 2},
        {"ten": "Khối 8", "thu_tu": 3},
        {"ten": "Khối 9", "thu_tu": 4},
    ]

    for item in khoi_data:
        existing = db.query(DmKhoi).filter(DmKhoi.ten == item["ten"]).first()
        if existing:
            print(f"  [SKIP] Khối '{item['ten']}' already exists.")
            continue
        db.add(DmKhoi(**item))
        print(f"  [OK] Created khối '{item['ten']}'.")

    db.commit()


def seed_ky_hieu_cong(db: Session) -> None:
    """Create default attendance symbols if not exists."""
    symbols = [
        {"ky_hieu": "X", "ten": "Đi làm", "gia_tri_ngay_cong": 1.0, "loai": "present"},
        {"ky_hieu": "P", "ten": "Nghỉ phép", "gia_tri_ngay_cong": 0.0, "loai": "leave"},
        {"ky_hieu": "Ô", "ten": "Nghỉ ốm", "gia_tri_ngay_cong": 0.0, "loai": "leave"},
        {"ky_hieu": "TC", "ten": "Tăng ca", "gia_tri_ngay_cong": 0.5, "loai": "overtime"},
        {"ky_hieu": "KP", "ten": "Không phép", "gia_tri_ngay_cong": 0.0, "loai": "leave"},
        {"ky_hieu": "NL", "ten": "Nghỉ lễ", "gia_tri_ngay_cong": 1.0, "loai": "holiday"},
        {"ky_hieu": "CN", "ten": "Chủ nhật", "gia_tri_ngay_cong": 0.0, "loai": "weekend"},
        {"ky_hieu": "0.5", "ten": "Nửa ngày", "gia_tri_ngay_cong": 0.5, "loai": "present"},
    ]

    for item in symbols:
        existing = db.query(DmKyHieuCong).filter(
            DmKyHieuCong.ky_hieu == item["ky_hieu"]
        ).first()
        if existing:
            print(f"  [SKIP] Ký hiệu công '{item['ky_hieu']}' already exists.")
            continue
        db.add(DmKyHieuCong(**item))
        print(f"  [OK] Created ký hiệu công '{item['ky_hieu']}' ({item['ten']}).")

    db.commit()


def seed_don_vi(db: Session) -> None:
    """Create default departments (đơn vị) if not exists."""
    don_vi_list = [
        "Ban Giám Hiệu",
        "Tổ Toán - Tin",
        "Tổ Văn - Sử - Địa",
        "Tổ Ngoại Ngữ",
        "Tổ KHTN",
        "Tổ Văn phòng",
    ]

    for ten in don_vi_list:
        existing = db.query(DmDonVi).filter(DmDonVi.ten == ten).first()
        if existing:
            print(f"  [SKIP] Đơn vị '{ten}' already exists.")
            continue
        db.add(DmDonVi(ten=ten, is_active=True))
        print(f"  [OK] Created đơn vị '{ten}'.")

    db.commit()


def seed_chuc_vu(db: Session) -> None:
    """Create default chức vụ (position titles) if not exists."""
    chuc_vu_data = [
        {"ma": "GVCN", "ten": "Giáo viên chủ nhiệm", "don_gia_luong_khoan": 5000000},
        {"ma": "PCN", "ten": "Phó chủ nhiệm", "don_gia_luong_khoan": 4000000},
        {"ma": "GVu", "ten": "Giáo vụ", "don_gia_luong_khoan": 4500000},
        {"ma": "GV", "ten": "Giáo viên", "don_gia_luong_khoan": 0},
        {"ma": "NV", "ten": "Nhân viên", "don_gia_luong_khoan": 0},
    ]

    for item in chuc_vu_data:
        existing = db.query(DmChucVu).filter(DmChucVu.ma == item["ma"]).first()
        if existing:
            print(f"  [SKIP] Chức vụ '{item['ma']}' already exists.")
            continue
        db.add(DmChucVu(**item))
        print(f"  [OK] Created chức vụ '{item['ma']}' ({item['ten']}).")

    db.commit()


def seed_cap_bac_ql(db: Session) -> None:
    """Create default cấp bậc quản lý (management levels) if not exists."""
    cap_bac_data = [
        {"ma": "HT", "ten": "Hiệu trưởng", "don_gia_luong_khoan": 10000000},
        {"ma": "PHT", "ten": "Phó hiệu trưởng", "don_gia_luong_khoan": 8000000},
        {"ma": "TT", "ten": "Tổ trưởng", "don_gia_luong_khoan": 3000000},
        {"ma": "TP", "ten": "Tổ phó", "don_gia_luong_khoan": 2000000},
    ]

    for item in cap_bac_data:
        existing = db.query(DmCapBacQL).filter(DmCapBacQL.ma == item["ma"]).first()
        if existing:
            print(f"  [SKIP] Cấp bậc QL '{item['ma']}' already exists.")
            continue
        db.add(DmCapBacQL(**item))
        print(f"  [OK] Created cấp bậc QL '{item['ma']}' ({item['ten']}).")

    db.commit()


def seed_loai_tiet_ngoai(db: Session) -> None:
    """Create default loại tiết ngoài (external period types) if not exists."""
    loai_list = [
        "Vĩnh Yên",
        "Bồi dưỡng",
        "IELTS",
        "Luyện thi",
        "Âm nhạc",
        "CLB",
        "BDHSG",
        "Quản lý",
    ]

    for ten in loai_list:
        existing = db.query(DmLoaiTietNgoai).filter(DmLoaiTietNgoai.ten == ten).first()
        if existing:
            print(f"  [SKIP] Loại tiết ngoài '{ten}' already exists.")
            continue
        db.add(DmLoaiTietNgoai(ten=ten, is_active=True))
        print(f"  [OK] Created loại tiết ngoài '{ten}'.")

    db.commit()


def seed_loai_ho_tro(db: Session) -> None:
    """Create default loại hỗ trợ (support allowance types) if not exists."""
    loai_list = [
        "Ăn trưa",
        "Gửi xe",
        "ChatGPT",
        "Điện thoại",
        "Xăng xe",
    ]

    for ten in loai_list:
        existing = db.query(DmLoaiHoTro).filter(DmLoaiHoTro.ten == ten).first()
        if existing:
            print(f"  [SKIP] Loại hỗ trợ '{ten}' already exists.")
            continue
        db.add(DmLoaiHoTro(ten=ten, is_active=True))
        print(f"  [OK] Created loại hỗ trợ '{ten}'.")

    db.commit()


def run_seed() -> None:
    """Run all seed functions."""
    print("=" * 50)
    print("NBK Salary - Seeding database...")
    print("=" * 50)

    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("\n[1/8] Seeding admin user...")
        seed_admin(db)

        print("\n[2/8] Seeding khối (grades)...")
        seed_khoi(db)

        print("\n[3/8] Seeding ký hiệu công (attendance symbols)...")
        seed_ky_hieu_cong(db)

        print("\n[4/8] Seeding đơn vị (departments)...")
        seed_don_vi(db)

        print("\n[5/8] Seeding chức vụ (position titles)...")
        seed_chuc_vu(db)

        print("\n[6/8] Seeding cấp bậc quản lý (management levels)...")
        seed_cap_bac_ql(db)

        print("\n[7/8] Seeding loại tiết ngoài (external period types)...")
        seed_loai_tiet_ngoai(db)

        print("\n[8/8] Seeding loại hỗ trợ (support allowance types)...")
        seed_loai_ho_tro(db)

        print("\n" + "=" * 50)
        print("Seeding complete!")
        print("=" * 50)
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
