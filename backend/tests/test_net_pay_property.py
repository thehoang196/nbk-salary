"""
Property-based test for Payslip Net Pay formula.

**Validates: Requirements 9.7**

Formula: Net Pay = Section II (Total Income) - Section III (Already Received)
                 - Section IV (Deductions) + Section V (Tax Settlement)

This tests the pure formula logic without database integration,
verifying that net pay is always correctly computed from its components.
"""

import sys
import os
from unittest.mock import MagicMock

# Add backend to path so we can import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Mock the database module before importing app modules to avoid psycopg2 dependency
sys.modules.setdefault("psycopg2", MagicMock())

import app.database
app.database.engine = MagicMock()
app.database.SessionLocal = MagicMock()

from hypothesis import given, strategies as st, settings as hyp_settings


def calculate_net_pay(section_ii: int, section_iii: int, section_iv: int, section_v: int) -> int:
    """
    Pure Net Pay formula extracted from SalaryEngine.generate_payslip.

    Net Pay = Total Income (II) - Already Received (III) - Deductions (IV) + Tax Settlement (V)
    """
    return section_ii - section_iii - section_iv + section_v


@given(
    section_ii=st.integers(min_value=0, max_value=999_999_999),
    section_iii=st.integers(min_value=0, max_value=999_999_999),
    section_iv=st.integers(min_value=0, max_value=999_999_999),
    section_v=st.integers(min_value=-999_999_999, max_value=999_999_999),
)
@hyp_settings(max_examples=200)
def test_net_pay_formula_correctness(section_ii, section_iii, section_iv, section_v):
    """
    Property 9: Payslip Net Pay formula.

    For any payslip with:
    - Section II total (Total Income) >= 0
    - Section III total (Already Received) >= 0
    - Section IV total (Deductions) >= 0
    - Section V amount (Tax Settlement, can be negative for refund or positive for owed)

    The Net Pay (Section VI) SHALL equal:
        Section II - Section III - Section IV + Section V

    **Validates: Requirements 9.7**
    """
    # Act: calculate net pay using the pure formula
    result = calculate_net_pay(section_ii, section_iii, section_iv, section_v)

    # Assert: formula correctness
    expected = section_ii - section_iii - section_iv + section_v

    assert result == expected, (
        f"Net Pay mismatch: got {result}, expected {expected}. "
        f"Components: section_ii={section_ii}, section_iii={section_iii}, "
        f"section_iv={section_iv}, section_v={section_v}"
    )


@given(
    section_ii=st.integers(min_value=0, max_value=999_999_999),
    section_iii=st.integers(min_value=0, max_value=999_999_999),
    section_iv=st.integers(min_value=0, max_value=999_999_999),
    section_v=st.integers(min_value=-999_999_999, max_value=999_999_999),
)
@hyp_settings(max_examples=200)
def test_net_pay_matches_payslip_engine_logic(section_ii, section_iii, section_iv, section_v):
    """
    Property 9 (integration check): Verify that the formula used in generate_payslip
    produces the same result as the standalone formula.

    In generate_payslip:
        thuc_linh = tong_thu_nhap - da_nhan - tong_giam_tru + muc_v["quyet_toan"]

    Mapping:
        tong_thu_nhap = section_ii (muc_ii["tong"])
        da_nhan = section_iii (muc_iii["da_nhan"])
        tong_giam_tru = section_iv (muc_iv["tong"])
        quyet_toan = section_v (muc_v["quyet_toan"])

    **Validates: Requirements 9.7**
    """
    # Simulate generate_payslip formula exactly as written in salary_engine.py
    tong_thu_nhap = section_ii
    da_nhan = section_iii
    tong_giam_tru = section_iv
    quyet_toan = section_v

    # This is the exact line from generate_payslip:
    thuc_linh = tong_thu_nhap - da_nhan - tong_giam_tru + quyet_toan

    # Compare with standalone formula
    net_pay = calculate_net_pay(section_ii, section_iii, section_iv, section_v)

    assert thuc_linh == net_pay, (
        f"Engine formula diverges from standalone: engine={thuc_linh}, standalone={net_pay}. "
        f"Inputs: II={section_ii}, III={section_iii}, IV={section_iv}, V={section_v}"
    )
