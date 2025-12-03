from pydantic import BaseModel
from typing import List, Optional


class YearFinancials(BaseModel):
    year: int
    cash_and_equivalents: float
    marketable_securities: float
    receivables: float
    inventory: float
    current_assets: float
    current_liabilities: float
    short_term_debt: float
    total_debt: float
    operating_cash_flow: float
    interest_expense: float
    daily_operating_expenses: float


class LiquidityThresholds(BaseModel):
    min_current_ratio: float
    min_quick_ratio: float
    min_cash_ratio: float
    min_dir_days: float
    min_ocf_cl: float
    min_ocf_debt: float


class LiquidityModuleInput(BaseModel):
    company_id: str
    industry_code: str
    financials_5y: List[YearFinancials]
    industry_liquidity_thresholds: LiquidityThresholds


class RuleResult(BaseModel):
    rule_id: str
    rule_name: str
    value: float
    threshold: str
    flag: str
    reason: str


class LiquidityModuleOutput(BaseModel):
    module: str
    sub_score_adjusted: int
    analysis_narrative: List[str]
    red_flags: List[dict]
    positive_points: List[str]
    rules: List[RuleResult]