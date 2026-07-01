"""
NBK Salary - Tax Engine

Personal Income Tax (PIT / Thuế TNCN) calculation with 7-bracket progressive rates.
Based on Vietnam tax regulations.
"""

from app.config import settings


# 7-bracket progressive PIT table (Vietnam)
# Each tuple: (bracket_amount, rate)
TAX_BRACKETS = [
    (5_000_000, 0.05),    # Up to 5M: 5%
    (5_000_000, 0.10),    # 5M to 10M: 10%
    (8_000_000, 0.15),    # 10M to 18M: 15%
    (14_000_000, 0.20),   # 18M to 32M: 20%
    (14_000_000, 0.25),   # 32M to 46M: 25%
    (18_000_000, 0.30),   # 46M to 64M: 30%
    (None, 0.35),          # Over 64M: 35%
]


class TaxEngine:
    """Personal Income Tax (PIT) calculation engine."""
    
    def __init__(
        self,
        personal_deduction: int = None,
        dependent_deduction: int = None,
    ):
        self.personal_deduction = personal_deduction or settings.PERSONAL_DEDUCTION
        self.dependent_deduction = dependent_deduction or settings.DEPENDENT_DEDUCTION

    def calculate_monthly_pit(
        self,
        total_income: int,
        insurance: int,
        dependents: int = 0,
    ) -> int:
        """Calculate monthly Personal Income Tax.
        
        Args:
            total_income: Gross monthly income (VND)
            insurance: Total insurance deductions (BHXH + BHYT + BHTN)
            dependents: Number of dependents
        
        Returns:
            Monthly PIT amount (VND, rounded to integer)
        """
        # Calculate taxable income
        taxable = (
            total_income
            - insurance
            - self.personal_deduction
            - (dependents * self.dependent_deduction)
        )
        
        if taxable <= 0:
            return 0
        
        return self._apply_progressive_rate(taxable)

    def _apply_progressive_rate(self, taxable: int) -> int:
        """Apply 7-bracket progressive tax rate.
        
        Brackets:
        - Up to 5M: 5%
        - 5M to 10M: 10%
        - 10M to 18M: 15%
        - 18M to 32M: 20%
        - 32M to 46M: 25%
        - 46M to 64M: 30%
        - Over 64M: 35%
        """
        tax = 0
        remaining = taxable
        
        for bracket_amount, rate in TAX_BRACKETS:
            if bracket_amount is None:
                # Last bracket - apply to all remaining
                tax += int(remaining * rate)
                break
            
            if remaining <= 0:
                break
            
            taxed_in_bracket = min(remaining, bracket_amount)
            tax += int(taxed_in_bracket * rate)
            remaining -= taxed_in_bracket
        
        return tax

    def calculate_annual_settlement(
        self,
        annual_income: int,
        annual_insurance: int,
        annual_pit_paid: int,
        dependents: int = 0,
    ) -> int:
        """Calculate year-end tax settlement adjustment.
        
        Returns:
            Positive = employee owes more tax
            Negative = employee gets a refund
        """
        # Annual taxable
        annual_taxable = (
            annual_income
            - annual_insurance
            - (self.personal_deduction * 12)
            - (dependents * self.dependent_deduction * 12)
        )
        
        if annual_taxable <= 0:
            # All PIT paid should be refunded
            return -annual_pit_paid
        
        # Calculate annual PIT liability
        annual_liability = self._apply_progressive_rate(annual_taxable)
        
        # Settlement = liability - already paid
        return annual_liability - annual_pit_paid
