"""
Property-based test for Lương Khoán formula correctness.

**Validates: Requirements 1.7, 7.6, 8.10**

Formula: Lương_Khoán = đơn_giá_chức_vụ + đơn_giá_cấp_bậc + (n × 2,000,000) + (m × 3,000,000)
Where:
- đơn_giá_chức_vụ: unit price from DmChucVu via nhan_vien.chuc_vu_id
- đơn_giá_cấp_bậc: unit price from DmCapBacQL via nhan_vien.cap_bac_ql_id
- n: count of active NvNghiepVu assignments (ngay_ket_thuc is None)
- m: count of active NvKiemNhiem assignments (ngay_ket_thuc is None)
"""

import sys
import os
from unittest.mock import MagicMock, patch

# Add backend to path so we can import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Mock the database module before importing app modules to avoid psycopg2 dependency
sys.modules.setdefault("psycopg2", MagicMock())

# Patch database.Base and engine before importing models
import app.database
app.database.engine = MagicMock()
app.database.SessionLocal = MagicMock()

from hypothesis import given, strategies as st, settings as hyp_settings
from app.services.luong_khoan_engine import calculate_luong_khoan_from_employee
from app.models.chuc_danh import DmChucVu, DmCapBacQL, NvNghiepVu, NvKiemNhiem


# Constants matching production config
NGHIEP_VU_SUPPLEMENT = 2_000_000
KIEM_NHIEM_SUPPLEMENT = 3_000_000


@given(
    don_gia_cv=st.integers(min_value=0, max_value=999_999_999),
    don_gia_cb=st.integers(min_value=0, max_value=999_999_999),
    n_nghiep_vu=st.integers(min_value=0, max_value=10),
    m_kiem_nhiem=st.integers(min_value=0, max_value=10),
)
@hyp_settings(max_examples=200)
def test_luong_khoan_formula_correctness(don_gia_cv, don_gia_cb, n_nghiep_vu, m_kiem_nhiem):
    """
    Property 1: Lương Khoán formula correctness.

    For any valid combination of chuc_vu don_gia, cap_bac don_gia,
    count of nghiep_vu, and count of kiem_nhiem, the calculated
    Lương Khoán must equal:
        don_gia_cv + don_gia_cb + (n × 2,000,000) + (m × 3,000,000)

    **Validates: Requirements 1.7, 7.6, 8.10**
    """
    # Setup: mock NhanVien with chuc_vu_id and cap_bac_ql_id
    mock_nhan_vien = MagicMock()
    mock_nhan_vien.id = 1
    mock_nhan_vien.chuc_vu_id = 100  # Always set so we test the formula path
    mock_nhan_vien.cap_bac_ql_id = 200

    # Setup: mock DmChucVu
    mock_chuc_vu = MagicMock()
    mock_chuc_vu.don_gia_luong_khoan = don_gia_cv

    # Setup: mock DmCapBacQL
    mock_cap_bac = MagicMock()
    mock_cap_bac.don_gia_luong_khoan = don_gia_cb

    # Setup: mock DB session
    mock_db = MagicMock()

    # Configure query chains for DmChucVu
    chuc_vu_query = MagicMock()
    chuc_vu_filter = MagicMock()
    chuc_vu_filter.first.return_value = mock_chuc_vu
    chuc_vu_query.filter.return_value = chuc_vu_filter

    # Configure query chains for DmCapBacQL
    cap_bac_query = MagicMock()
    cap_bac_filter = MagicMock()
    cap_bac_filter.first.return_value = mock_cap_bac
    cap_bac_query.filter.return_value = cap_bac_filter

    # Configure query chains for NvNghiepVu count
    nghiep_vu_query = MagicMock()
    nghiep_vu_filter = MagicMock()
    nghiep_vu_filter.count.return_value = n_nghiep_vu
    nghiep_vu_query.filter.return_value = nghiep_vu_filter

    # Configure query chains for NvKiemNhiem count
    kiem_nhiem_query = MagicMock()
    kiem_nhiem_filter = MagicMock()
    kiem_nhiem_filter.count.return_value = m_kiem_nhiem
    kiem_nhiem_query.filter.return_value = kiem_nhiem_filter

    # Route db.query() to the correct mock based on model class
    def query_side_effect(model):
        if model is DmChucVu:
            return chuc_vu_query
        elif model is DmCapBacQL:
            return cap_bac_query
        elif model is NvNghiepVu:
            return nghiep_vu_query
        elif model is NvKiemNhiem:
            return kiem_nhiem_query
        return MagicMock()

    mock_db.query.side_effect = query_side_effect

    # Act: call the function under test with patched supplement constants
    with patch("app.services.luong_khoan_engine.NGHIEP_VU_SUPPLEMENT", NGHIEP_VU_SUPPLEMENT), \
         patch("app.services.luong_khoan_engine.KIEM_NHIEM_SUPPLEMENT", KIEM_NHIEM_SUPPLEMENT):
        result = calculate_luong_khoan_from_employee(mock_nhan_vien, mock_db)

    # Assert: formula correctness
    expected = don_gia_cv + don_gia_cb + (n_nghiep_vu * NGHIEP_VU_SUPPLEMENT) + (m_kiem_nhiem * KIEM_NHIEM_SUPPLEMENT)

    assert result == expected, (
        f"Lương Khoán mismatch: got {result}, expected {expected}. "
        f"Components: cv={don_gia_cv}, cb={don_gia_cb}, "
        f"nghiep_vu={n_nghiep_vu}×{NGHIEP_VU_SUPPLEMENT}, "
        f"kiem_nhiem={m_kiem_nhiem}×{KIEM_NHIEM_SUPPLEMENT}"
    )
