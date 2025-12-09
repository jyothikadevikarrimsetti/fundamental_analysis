# =============================================================
# main.py - UPDATED FOR YOUR NEW REQUEST FORMAT
# =============================================================

import os
import sys
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

# -------------------------------------------
# FIX PATH
# -------------------------------------------
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT)

# -------------------------------------------
# IMPORT MODULES
# -------------------------------------------
from src.app.borrowing_module.debt_models import (
    BorrowingsInput,
    YearFinancialInput,
    IndustryBenchmarks,
    CovenantLimits,
)
from src.app.borrowing_module.debt_orchestrator import run_borrowings_module


# =============================================================
# IMPORT LIQUIDITY MODULE
# =============================================================
from src.app.liquidity_module.liquidity_models import (
    YearFinancials as LiquidityYearFinancials,
    LiquidityThresholds,
    LiquidityModuleInput,
)
from src.app.liquidity_module.liquidity_orchestrator import (
    LiquidityModule
    )

# ---------------------------------------------------------
# REQUEST MODELS FOR BORROWINGS 
# ---------------------------------------------------------

class FinancialYearInput(BaseModel):
    year: int
    short_term_debt: float
    long_term_debt: float
    total_equity: float
    revenue : float
    ebitda: float
    ebit: float
    finance_cost: float
    capex: float
    cwip: float

    total_debt_maturing_lt_1y: Optional[float] = None
    total_debt_maturing_1_3y: Optional[float] = None
    total_debt_maturing_gt_3y: Optional[float] = None

    weighted_avg_interest_rate: Optional[float] = None
    floating_rate_debt: Optional[float] = None
    fixed_rate_debt: Optional[float] = None


class FinancialData(BaseModel):

    financial_years : list[FinancialYearInput]

    
    
    # total_debt_maturing_lt_1y: float
    # total_debt_maturing_1_3y: float
    # total_debt_maturing_gt_3y: float

    # weighted_avg_interest_rate: float
    # floating_rate_debt: float
    # fixed_rate_debt: float


class AnalyzeRequest(BaseModel):
    #year: int  # e.g. "Mar 2024"
    company: str
    financial_data: FinancialData   # <-- EXACT INPUT YOU WANTED


# ---------------------------------------------------------
# REQUEST MODELS FOR LIQUIDITY MODULE
# ---------------------------------------------------------
class LiquidityYearInput(BaseModel):
    year: int
    cash_equivalents: float
    investments: float
    Trade_receivables: float
    inventories: float
    # current_assets: float
    other_liability_items: float
    working_capital_changes: float
    profit_from_operations: float
    direct_taxes: float
    expenses: float
    depreciation: float
    lease_liabilities: float
    other_borrowings: float
    # current_liabilities: float
    short_term_debt: float

    long_term_debt: float
    # operating_cash_flow: float
    interest: float
    # daily_operating_expenses: float
    cash_from_operating_activity: float
    interest_paid_fin: float
    preference_capital: float

class LiquidityData(BaseModel):
    financial_years : list[LiquidityYearInput]


class LiquidityAnalyzeRequest(BaseModel):
    company: str

    # list of 5-year data
    financial_data: LiquidityData
    # industry thresholds
    thresholds: LiquidityThresholds


# ---------------------------------------------------------
# FASTAPI APP
# ---------------------------------------------------------
app = FastAPI(
    title="Financial Analytical Engine",
    version="2.0",
    description="API for Borrowings + Liquidity Analysis"
)




# =============================================================
# 2️⃣  LIQUIDITY ENDPOINT
# =============================================================
@app.post("/analyze/liquidity")
def analyze_liquidity(req: LiquidityAnalyzeRequest):
    try:
        company = req.company.upper()

        # Convert to liquidity models
        fin_list = []
        for fy in req.financial_data.financial_years:
            # Calculate current_assets if not provided
            inventory = fy.inventories
            cash_equivalents = fy.cash_equivalents
            total_debt = fy.short_term_debt  + fy.long_term_debt + fy.lease_liabilities + fy.other_borrowings + fy.preference_capital
            print(f"Processing Year: {fy.year} : {fy.short_term_debt} + {fy.other_liability_items} + {fy.long_term_debt} + {fy.lease_liabilities} + {fy.other_borrowings} + {fy.preference_capital}")
            print("Total Debt Calculated:", total_debt)
            current_assets = fy.investments + fy.inventories + fy.Trade_receivables
            current_liablities = fy.short_term_debt + fy.other_liability_items
            operating_cash_flow = fy.profit_from_operations + fy.working_capital_changes - fy.direct_taxes
            daily_expenses =( fy.expenses - fy.depreciation )/ 365
            marketable_securities = fy.investments
            receivables = fy.Trade_receivables
            fin_list.append(
            LiquidityYearFinancials(
                **{**fy.model_dump(),"inventory": inventory, "cash_and_equivalents": cash_equivalents,
                   "current_assets": current_assets , "current_liabilities": current_liablities , 
                   "operating_cash_flow": operating_cash_flow , "daily_operating_expenses": daily_expenses , 
                   "total_debt" : total_debt, "marketable_securities": marketable_securities,
                   "receivables": receivables , "interest_expense": fy.interest_paid_fin}
            )
            )

        module_input = LiquidityModuleInput(
            company_id=company,
            industry_code="GENERAL",
            financials_5y=fin_list,
            industry_liquidity_thresholds=req.thresholds,
        )

        module = LiquidityModule()

        result = module.run(module_input)
        return result.model_dump()

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# =============================================================
# 1️⃣  BORROWINGS ENDPOINT
# =============================================================
@app.post("/analyze/borrowings")
def analyze_borrowings(req: AnalyzeRequest):
    try:
        company = req.company.upper()
        fd = req.financial_data
        fds = fd.financial_years

        yfis = []
        for fy in fds:
            yfi = YearFinancialInput(
                year=fy.year,
                short_term_debt=fy.short_term_debt,
                long_term_debt=fy.long_term_debt,
                total_equity=fy.total_equity,
                revenue=fy.revenue,
                ebitda=fy.ebitda,
                ebit=fy.ebit,
                finance_cost=fy.finance_cost,
                capex=fy.capex,
                cwip=fy.cwip,
                total_debt_maturing_lt_1y=fy.total_debt_maturing_lt_1y,
                total_debt_maturing_1_3y=fy.total_debt_maturing_1_3y,
                total_debt_maturing_gt_3y=fy.total_debt_maturing_gt_3y,
                weighted_avg_interest_rate=fy.weighted_avg_interest_rate,
                floating_rate_debt=fy.floating_rate_debt,
                fixed_rate_debt=fy.fixed_rate_debt,
            )
            yfis.append(yfi)

        module_input = BorrowingsInput(
            company_id=company,
            industry_code="GENERAL",
            financials_5y=yfis,   # supports multi-year
            industry_benchmarks=IndustryBenchmarks(
                target_de_ratio=1.5,
                max_safe_de_ratio=2.5,
                max_safe_debt_ebitda=4.0,
                min_safe_icr=2.0,
            ),
            covenant_limits=CovenantLimits(
                de_ratio_limit=3.0,
                icr_limit=2.0,
                debt_ebitda_limit=4.0,
            ),
        )

        result = run_borrowings_module(module_input)
        return result.model_dump()

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# ---------------------------------------------------------
# RUN SERVER
# ---------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)