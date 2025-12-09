from pydantic import BaseModel
from typing import List


# ---------------------------------------------------------
# 1. YEARLY FINANCIALS (clean structure)
# ---------------------------------------------------------
class YearFinancials(BaseModel):
    year: int
    cash_and_equivalents: float
    receivables: float
    inventory: float
    current_assets: float
    current_liabilities: float
    short_term_debt: float

    preference_capital: float   
    total_debt: float
    operating_cash_flow: float
    interest_expense: float
    daily_operating_expenses: float
    other_liability_items: float
    working_capital_changes: float
    profit_from_operations: float
    direct_taxes: float
    expenses: float
    depreciation: float
    marketable_securities: float


# ---------------------------------------------------------
# 2. INDUSTRY LIQUIDITY THRESHOLDS
# ---------------------------------------------------------
class LiquidityThresholds(BaseModel):

    min_current_ratio: float
    min_quick_ratio: float
    min_cash_ratio: float
    min_dir_days: float
    min_ocf_cl: float
    min_ocf_debt: float


# ---------------------------------------------------------
# 3. MODULE INPUT
# ---------------------------------------------------------
class LiquidityModuleInput(BaseModel):
    company_id: str
    industry_code: str
    financials_5y: List[YearFinancials]
    # industry_liquidity_thresholds: LiquidityThresholds


# ---------------------------------------------------------
# 4. RULE RESULT
# ---------------------------------------------------------
class RuleResult(BaseModel):
    rule_id: str
    rule_name: str
    value: float
    threshold: str
    flag: str
    reason: str


# ---------------------------------------------------------
# 5. FINAL OUTPUT
# ---------------------------------------------------------
class LiquidityModuleOutput(BaseModel):
    module: str
    sub_score_adjusted: int
    key_metrics: dict
    trends: dict
    analysis_narrative: List[str]
    red_flags: List[dict]
    positive_points: List[str]
    rules: List[RuleResult]
    summary_color: str
    def to_dict(self):
        return {
            "module": self.module,
            "sub_score_adjusted": self.sub_score_adjusted,
            "key_metrics": self.key_metrics,
            "trends": self.trends,
            "analysis_narrative": self.analysis_narrative,
            "red_flags": self.red_flags,
            "positive_points": self.positive_points,
            "rules": [r.dict() for r in self.rules],
            "summary_color": self.summary_color,
        }