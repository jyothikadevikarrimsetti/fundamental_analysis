# liquidity_metrics.py

from typing import Dict
from .liquidity_models import YearFinancials


def safe_div(a, b):
    """Safely divide two numbers, returning None if division is invalid."""
    return a / b if (a is not None and b not in (0, None)) else None


def compute_per_year_metrics(financials_5y: list[YearFinancials]) -> Dict[int, dict]:
    """
    Calculate key liquidity metrics for each year.

    Returns:
        Dict mapping year -> metrics dictionary
    """
    metrics = {}

    sorted_fin = sorted(financials_5y, key=lambda x: x.year)

    for y in sorted_fin:
        total_debt = getattr(y, "total_debt", 0.0) or 0.0
        daily_expenses = getattr(y, "daily_operating_expenses", None) or 0.0

        cash = y.cash_and_equivalents or 0.0
        marketable_sec = y.marketable_securities or 0.0
        receivables = y.receivables or 0.0
        inventory = y.inventory or 0.0

        current_assets = y.current_assets or 0.0
        current_liabilities = y.current_liabilities or 0.0
        short_term_debt = y.short_term_debt or 0.0
        ocf = y.operating_cash_flow or 0.0
        interest = y.interest_expense or 0.0

        liquid_assets = cash + marketable_sec + receivables

        metrics[y.year] = {
            "year": y.year,

            # ---------- Liquidity Ratios ----------
            "current_ratio": safe_div(current_assets, current_liabilities),

            "quick_ratio": safe_div(
                current_assets - inventory,
                current_liabilities
            ),

            "cash_ratio": safe_div(
                cash,
                current_liabilities
            ),

            # ---------- Defensive Interval Ratio ----------
            # How many days the company can operate using liquid assets
            "defensive_interval_ratio_days": safe_div(
                liquid_assets,
                daily_expenses
            ),

            # ---------- Cash Flow Coverage Ratios ----------
            "ocf_to_current_liabilities": safe_div(ocf, current_liabilities),
            "ocf_to_total_debt": safe_div(ocf, total_debt),
            "interest_coverage_ocf": safe_div(ocf, interest),
            "cash_coverage_st_debt": safe_div(cash, short_term_debt),

            # ---------- Core Balances ----------
            "cash_and_equivalents": cash,
            "marketable_securities": marketable_sec,
            "receivables": receivables,
            "inventory": inventory,
            "current_assets": current_assets,
            "current_liabilities": current_liabilities,
            "short_term_debt": short_term_debt,
            "total_debt": total_debt,
            "operating_cash_flow": ocf,
            "daily_operating_expenses": daily_expenses,
        }

    return metrics
