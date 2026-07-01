"""
Unit tests for Tax Engine - Personal Income Tax (PIT) calculation.

Tests 7-bracket progressive rate boundaries, zero/negative taxable income,
and dependent deduction scenarios.

**Validates: Requirements 9.5**
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

from app.services.tax_engine import TaxEngine


# Use fixed deductions for predictable test calculations
PERSONAL_DEDUCTION = 11_000_000
DEPENDENT_DEDUCTION = 4_400_000


def make_engine():
    """Create a TaxEngine with known deduction values."""
    return TaxEngine(
        personal_deduction=PERSONAL_DEDUCTION,
        dependent_deduction=DEPENDENT_DEDUCTION,
    )


class TestZeroAndNegativeTaxable:
    """Test cases where taxable income is zero or negative (should return 0)."""

    def test_zero_income_returns_zero(self):
        """Test 1: Zero total income → tax = 0."""
        engine = make_engine()
        result = engine.calculate_monthly_pit(
            total_income=0, insurance=0, dependents=0
        )
        assert result == 0

    def test_income_below_personal_deduction_returns_zero(self):
        """Test 2: Income below deductions (negative taxable) → tax = 0."""
        engine = make_engine()
        # total_income = 10M, insurance = 0 → taxable = 10M - 11M = -1M
        result = engine.calculate_monthly_pit(
            total_income=10_000_000, insurance=0, dependents=0
        )
        assert result == 0

    def test_income_exactly_equal_deduction_returns_zero(self):
        """Taxable = total - insurance - personal = 11M - 0 - 11M = 0 → tax = 0."""
        engine = make_engine()
        result = engine.calculate_monthly_pit(
            total_income=11_000_000, insurance=0, dependents=0
        )
        assert result == 0


class TestBracketBoundaries:
    """Test exact bracket boundary values for progressive tax calculation.

    To isolate bracket testing, set insurance=0 and adjust total_income
    so that taxable = total_income - 11M equals the desired bracket boundary.
    """

    def test_exactly_5m_bracket(self):
        """Test 3: Taxable = 5,000,000 → tax = 5M × 5% = 250,000."""
        engine = make_engine()
        # taxable = 16M - 0 - 11M = 5M
        result = engine.calculate_monthly_pit(
            total_income=16_000_000, insurance=0, dependents=0
        )
        assert result == 250_000

    def test_exactly_10m_bracket(self):
        """Test 4: Taxable = 10,000,000 → tax = 5M×5% + 5M×10% = 250K + 500K = 750,000."""
        engine = make_engine()
        # taxable = 21M - 0 - 11M = 10M
        result = engine.calculate_monthly_pit(
            total_income=21_000_000, insurance=0, dependents=0
        )
        assert result == 750_000

    def test_exactly_18m_bracket(self):
        """Test 5: Taxable = 18,000,000 → 250K + 500K + 1,200K = 1,950,000."""
        engine = make_engine()
        # taxable = 29M - 0 - 11M = 18M
        # Tax: 5M×5% + 5M×10% + 8M×15% = 250K + 500K + 1,200K = 1,950,000
        result = engine.calculate_monthly_pit(
            total_income=29_000_000, insurance=0, dependents=0
        )
        assert result == 1_950_000

    def test_exactly_32m_bracket(self):
        """Test 6: Taxable = 32,000,000 → up through 20% bracket.

        Tax: 5M×5% + 5M×10% + 8M×15% + 14M×20%
           = 250K + 500K + 1,200K + 2,800K = 4,750,000
        """
        engine = make_engine()
        # taxable = 43M - 0 - 11M = 32M
        result = engine.calculate_monthly_pit(
            total_income=43_000_000, insurance=0, dependents=0
        )
        assert result == 4_750_000

    def test_exactly_46m_bracket(self):
        """Taxable = 46,000,000 → up through 25% bracket.

        Tax: 5M×5% + 5M×10% + 8M×15% + 14M×20% + 14M×25%
           = 250K + 500K + 1,200K + 2,800K + 3,500K = 8,250,000
        """
        engine = make_engine()
        # taxable = 57M - 0 - 11M = 46M
        result = engine.calculate_monthly_pit(
            total_income=57_000_000, insurance=0, dependents=0
        )
        assert result == 8_250_000

    def test_exactly_52m_in_30_percent_bracket(self):
        """Test 7: Taxable = 52,000,000 → up through 30% bracket (partially).

        Tax: 5M×5% + 5M×10% + 8M×15% + 14M×20% + 14M×25% + 6M×30%
           = 250K + 500K + 1,200K + 2,800K + 3,500K + 1,800K = 10,050,000
        """
        engine = make_engine()
        # taxable = 63M - 0 - 11M = 52M
        result = engine.calculate_monthly_pit(
            total_income=63_000_000, insurance=0, dependents=0
        )
        assert result == 10_050_000

    def test_exactly_64m_bracket(self):
        """Taxable = 64,000,000 → end of 30% bracket.

        Tax: 5M×5% + 5M×10% + 8M×15% + 14M×20% + 14M×25% + 18M×30%
           = 250K + 500K + 1,200K + 2,800K + 3,500K + 5,400K = 13,650,000
        """
        engine = make_engine()
        # taxable = 75M - 0 - 11M = 64M
        result = engine.calculate_monthly_pit(
            total_income=75_000_000, insurance=0, dependents=0
        )
        assert result == 13_650_000

    def test_above_80m_hits_35_percent_bracket(self):
        """Test 8: Taxable = 80,000,000 → 35% bracket kicks in.

        Tax: 5M×5% + 5M×10% + 8M×15% + 14M×20% + 14M×25% + 18M×30% + 16M×35%
           = 250K + 500K + 1,200K + 2,800K + 3,500K + 5,400K + 5,600K = 19,250,000
        """
        engine = make_engine()
        # taxable = 91M - 0 - 11M = 80M
        result = engine.calculate_monthly_pit(
            total_income=91_000_000, insurance=0, dependents=0
        )
        assert result == 19_250_000


class TestWithDependents:
    """Test tax calculation with dependents reducing taxable income."""

    def test_dependents_reduce_taxable(self):
        """Test 9: 2 dependents → reduces taxable by 8.8M (2 × 4.4M).

        total_income=30M, insurance=0, dependents=2
        taxable = 30M - 0 - 11M - 8.8M = 10,200,000
        Tax: 5M×5% + 5M×10% + 200K×15% = 250K + 500K + 30K = 780,000
        """
        engine = make_engine()
        result = engine.calculate_monthly_pit(
            total_income=30_000_000, insurance=0, dependents=2
        )
        assert result == 780_000

    def test_dependents_making_taxable_negative_returns_zero(self):
        """Test 10: Dependents push taxable below zero → returns 0.

        total_income=20M, insurance=0, dependents=3
        taxable = 20M - 0 - 11M - 13.2M = -4,200,000 → returns 0
        """
        engine = make_engine()
        result = engine.calculate_monthly_pit(
            total_income=20_000_000, insurance=0, dependents=3
        )
        assert result == 0

    def test_dependents_making_taxable_exactly_zero_returns_zero(self):
        """Dependents that zero out taxable → returns 0.

        total_income=15.4M, insurance=0, dependents=1
        taxable = 15.4M - 0 - 11M - 4.4M = 0 → returns 0
        """
        engine = make_engine()
        result = engine.calculate_monthly_pit(
            total_income=15_400_000, insurance=0, dependents=1
        )
        assert result == 0


class TestWithInsurance:
    """Test that insurance deduction is correctly applied."""

    def test_insurance_reduces_taxable(self):
        """Insurance deduction reduces taxable income.

        total_income=25M, insurance=3M, dependents=0
        taxable = 25M - 3M - 11M = 11M
        Tax: 5M×5% + 5M×10% + 1M×15% = 250K + 500K + 150K = 900,000
        """
        engine = make_engine()
        result = engine.calculate_monthly_pit(
            total_income=25_000_000, insurance=3_000_000, dependents=0
        )
        assert result == 900_000

    def test_insurance_and_dependents_combined(self):
        """Both insurance and dependents reduce taxable.

        total_income=40M, insurance=4M, dependents=1
        taxable = 40M - 4M - 11M - 4.4M = 20,600,000
        Tax: 5M×5% + 5M×10% + 8M×15% + 2.6M×20%
           = 250K + 500K + 1,200K + 520K = 2,470,000
        """
        engine = make_engine()
        result = engine.calculate_monthly_pit(
            total_income=40_000_000, insurance=4_000_000, dependents=1
        )
        assert result == 2_470_000
