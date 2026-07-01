"""
NBK Salary API - Báo cáo (Reports) Router

Report generation and export endpoints.
"""
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.bang_luong import DlBangLuong
from app.models.nhan_vien import NhanVien
from app.models.cham_cong import DlTongHopCong
from app.models.user import UserRole
from app.services.export_service import MisaExporter
from app.services.bcc_service import BCCService
from app.utils.dependencies import get_current_user, require_role

router = APIRouter()
REPORT_ROLES = [UserRole.admin, UserRole.accountant]


@router.get("/export-misa/{thang}/{nam}")
def export_misa(thang: int, nam: int, db: Session = Depends(get_db), _=Depends(require_role(REPORT_ROLES))):
    """Export salary to Misa format (Excel download)."""
    exporter = MisaExporter(db)
    output = exporter.export_salary_to_misa(thang, nam)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=misa_luong_T{thang}_{nam}.xlsx"},
    )


@router.get("/tong-hop/{thang}/{nam}")
def export_tong_hop(thang: int, nam: int, db: Session = Depends(get_db), _=Depends(require_role(REPORT_ROLES))):
    """Export monthly salary summary (Excel download)."""
    exporter = MisaExporter(db)
    output = exporter.export_salary_summary(thang, nam)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=tong_hop_luong_T{thang}_{nam}.xlsx"},
    )


@router.get("/phieu-luong-pdf/{nv_id}/{thang}/{nam}")
def export_phieu_luong_pdf(nv_id: int, thang: int, nam: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Export individual payslip as HTML (rendered from Jinja2 template).
    Note: For production PDF, integrate with weasyprint or wkhtmltopdf.
    """
    import os
    record = db.query(DlBangLuong).filter(
        DlBangLuong.nhan_vien_id == nv_id,
        DlBangLuong.thang == thang, DlBangLuong.nam == nam,
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Chưa có phiếu lương")

    # Load Jinja2 template
    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("phieu_luong.html")

    html = template.render(
        thang=thang, nam=nam,
        muc_i=record.muc_i_json or {},
        muc_ii=record.muc_ii_json or {},
        muc_iii=record.muc_iii_json or {},
        muc_iv=record.muc_iv_json or {},
        muc_v=record.muc_v_json or {},
        muc_vi_thuc_linh=int(record.muc_vi_thuc_linh or 0),
        ngay_tinh=str(record.ngay_tinh) if record.ngay_tinh else None,
        nguoi_tinh=None,
    )

    return StreamingResponse(
        BytesIO(html.encode("utf-8")),
        media_type="text/html",
        headers={"Content-Disposition": f"attachment; filename=phieu_luong_{nv_id}_T{thang}_{nam}.html"},
    )


@router.get("/bcc/{thang}/{nam}")
def export_bcc(thang: int, nam: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Get BCC summary report data (JSON)."""
    service = BCCService(db)
    rows = service.calculate_bcc(thang, nam)
    return {"thang": thang, "nam": nam, "rows": rows, "total_teachers": len(rows)}


@router.get("/cham-cong/{thang}/{nam}")
def report_cham_cong(thang: int, nam: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Monthly attendance summary report (JSON)."""
    records = db.query(DlTongHopCong).filter(
        DlTongHopCong.thang == thang, DlTongHopCong.nam == nam
    ).all()
    return {
        "thang": thang, "nam": nam,
        "total_employees": len(records),
        "records": [{"nhan_vien_id": r.nhan_vien_id, "ngay_cong": float(r.ngay_cong), "ngay_nghi": float(r.ngay_nghi), "ngay_phep": float(r.ngay_phep), "lam_them": float(r.lam_them)} for r in records],
    }
