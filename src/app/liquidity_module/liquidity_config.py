# src/app/config/liquidity_config.py

from dataclasses import dataclass
from typing import Optional

@dataclass
class LiquidityRuleThresholds:
    # ------------------------------
    # Current / Quick / Cash Ratios
    # ------------------------------
    critical_current_ratio: float = 0.8
    moderate_current_ratio: float = 1.2
    critical_quick_ratio: float = 0.5
    moderate_quick_ratio: float = 1.0
    critical_cash_ratio: float = 0.2
    moderate_cash_ratio: float = 0.5

    # ------------------------------
    # Defensive Interval Ratio (Days)
    # ------------------------------
    dir_critical_days: float = 15
    dir_moderate_days: float = 30

    # ------------------------------
    # OCF / Current Liabilities
    # ------------------------------
    ocf_cl_critical: float = 0.0
    ocf_cl_moderate: float = 0.2

    # ------------------------------
    # OCF / Total Debt
    # ------------------------------
    ocf_debt_critical: float = 0.0
    ocf_debt_moderate: float = 0.15

    # ------------------------------
    # Trend Analysis Thresholds (YoY % / Years)
    # ------------------------------
    cash_shrink_yoy_pct: float = -5            # Cash declining >5% YoY → Stress
    receivables_growth_yoy_pct: float = 10    # Receivables rising >10% YoY → Collection issue
    inventory_growth_yoy_pct: float = 10      # Inventory rising >10% YoY → Overstock
    ocf_decline_years: int = 2                # OCF declining ≥2 consecutive years → Weak internal funding
    cl_rise_yoy_pct: float = 5                # Current Liabilities rising >5% YoY → Stress

@dataclass
class LiquidityRuleConfig:
    generic: LiquidityRuleThresholds

DEFAULT_LIQUIDITY_CONFIG = LiquidityRuleConfig(generic=LiquidityRuleThresholds())

def load_liquidity_config(_: Optional[str] = None) -> LiquidityRuleConfig:
    """
    Placeholder for industry-specific overrides.
    Currently returns the generic configuration but can be extended
    to fetch YAML / DB-backed thresholds keyed by industry_code.
    """
    return DEFAULT_LIQUIDITY_CONFIG
# src/app/config.py

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")


def get_llm_client():


    return OpenAI(api_key=OPENAI_API_KEY)

# -----------------------------
# Liquidity Rules (Thresholds)
# -----------------------------

LIQUIDITY_RULES = {
    "generic": {
        "critical_current_ratio": 0.8,
        "moderate_current_ratio": 1.0,

        "critical_quick_ratio": 0.6,
        "moderate_quick_ratio": 0.8,

        "critical_cash_ratio": 0.1,
        "moderate_cash_ratio": 0.2,

        "dir_critical_days": 30,
        "dir_moderate_days": 45,

        "ocf_cl_critical": 0.5,
        "ocf_cl_moderate": 1.0,

        "ocf_debt_critical": 0.1,
        "ocf_debt_moderate": 0.2,

        "high_receivable_growth": 0.25,
        "high_inventory_growth": 0.25
    }
}    