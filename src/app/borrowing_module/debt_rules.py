
# ==============================================================
# debt_rules.py
# Deterministic rule engine for Borrowings Module
# ==============================================================

from src.app.borrowing_module.debt_models import RuleResult


def make(flag, rule_id, name, value, threshold, reason):
    return RuleResult(
        rule_id=rule_id,
        rule_name=name,
        flag=flag,
        value=value,
        threshold=threshold,
        reason=reason,
    )


def default_green(rule_id, name, value, threshold, reason="Healthy"):
    return make("GREEN", rule_id, name, value, threshold, reason)


def apply_rules(financials, metrics, trends):
    results = []

    last_year = max(metrics.keys())
    m = metrics[last_year]

    # ----------------------------------------------------------------------
    # A. DEBT GROWTH & TREND RULES
    # ----------------------------------------------------------------------

    # A1 Rising Debt Faster Than EBITDA
    debt_cagr = trends.get("debt_cagr", 0)
    ebitda_cagr = trends.get("ebitda_cagr", 0)

    if debt_cagr > ebitda_cagr:
        results.append(make(
            "RED", "A1", "Debt CAGR > EBITDA CAGR",
            debt_cagr, f">{ebitda_cagr:.2f}",
            f"Leverage increasing faster than earnings"
        ))
    else:
        results.append(default_green(
            "A1", "Debt CAGR > EBITDA CAGR",
            debt_cagr, f"<={ebitda_cagr:.2f}"
        ))

    # A2 ST Debt Surge Signal
    st_debt_growth = trends.get("st_debt_yoy_growth", [])
    if len(st_debt_growth) >= 2 and all(g > 30 for g in st_debt_growth[-2:]):
        results.append(make(
            "RED", "A2", "ST Debt Surge",
            st_debt_growth[-1], ">30% for 2 yrs",
            "Short-term rollover risk"
        ))
    else:
        val = st_debt_growth[-1] if st_debt_growth else 0
        results.append(default_green("A2", "ST Debt Surge", val, "<=30%"))

    # A3 LT Debt Up, Revenue Flat
    lt_debt_cagr = trends.get("lt_debt_cagr", 0)
    revenue_cagr = trends.get("revenue_cagr", 0)

    if lt_debt_cagr > 10 and revenue_cagr < 5:
        results.append(make(
            "YELLOW", "A3", "LT Debt Up, Revenue Flat",
            lt_debt_cagr, ">10% LT debt & <5% revenue",
            "Possible distress borrowing"
        ))
    else:
        results.append(default_green("A3", "LT Debt Up, Revenue Flat", lt_debt_cagr, "<=10%"))

    # A3b LT Debt + Capex story
    cwip = m.get("cwip", 0)
    total_assets = m.get("total_assets", 1)
    cwip_ratio = cwip / total_assets if total_assets else 0

    if lt_debt_cagr > 0 and cwip_ratio > 0.10:
        results.append(make(
            "GREEN", "A3b", "LT Debt + Capex",
            cwip_ratio, ">10%",
            "Debt funding growth capex"
        ))
    else:
        results.append(default_green("A3b", "LT Debt + Capex", cwip_ratio, "<=10%"))

    # ----------------------------------------------------------------------
    # B. LEVERAGE RATIOS
    # ----------------------------------------------------------------------

    # B1 Debt-to-Equity
    de = m.get("de_ratio", 0)
    if de > 1:
        results.append(make("RED", "B1", "Debt-to-Equity", de, ">1", "Highly leveraged"))
    elif de > 0.5:
        results.append(make("YELLOW", "B1", "Debt-to-Equity", de, "0.5–1", "Moderately leveraged"))
    else:
        results.append(default_green("B1", "Debt-to-Equity", de, "<=0.5"))

    # B2 Debt-to-EBITDA
    debt_ebitda = m.get("debt_ebitda", 0)
    if debt_ebitda > 4:
        results.append(make("RED", "B2", "Debt-to-EBITDA", debt_ebitda, ">4", "Very high leverage"))
    elif debt_ebitda > 2:
        results.append(make("YELLOW", "B2", "Debt-to-EBITDA", debt_ebitda, "2–4", "Slightly stressed"))
    else:
        results.append(default_green("B2", "Debt-to-EBITDA", debt_ebitda, "<=2"))

    # ----------------------------------------------------------------------
    # C. INTEREST COVERAGE RULES
    # ----------------------------------------------------------------------

    icr = m.get("interest_coverage", 0)
    if icr < 1.5:
        results.append(make("RED", "C1", "Interest Coverage", icr, "<1.5", "Unable to service interest"))
    elif icr < 3:
        results.append(make("YELLOW", "C1", "Interest Coverage", icr, "1.5–3", "Tight servicing ability"))
    else:
        results.append(default_green("C1", "Interest Coverage", icr, ">=3", "Comfortable"))

    # C2 Finance Cost Rising Faster Than Debt
    finance_cost_cagr = trends.get("finance_cost_cagr", 0)
    if (finance_cost_cagr - debt_cagr) > 5:
        results.append(make("YELLOW", "C2", "Finance Cost > Debt", finance_cost_cagr, f">{debt_cagr+5:.2f}", "Interest rate pressure"))
    else:
        results.append(default_green("C2", "Finance Cost > Debt", finance_cost_cagr, f"<={debt_cagr+5:.2f}"))

    # ----------------------------------------------------------------------
    # D. MATURITY PROFILE
    # ----------------------------------------------------------------------

    # D1 Refinancing Risk
    refinancing_ratio = m.get("maturity_lt_1y_pct", 0)
    if refinancing_ratio > 0.5:
        results.append(make("RED", "D1", "Refinancing Risk", refinancing_ratio, ">50%", "High refinancing risk"))
    else:
        results.append(default_green("D1", "Refinancing Risk", refinancing_ratio, "<=50%"))

    # D2 Balanced Maturity
    r1 = m.get("maturity_1_3y_pct", 0)
    r2 = m.get("maturity_gt_3y_pct", 0)

    if r1 >= 0.3 and r2 >= 0.2:
        results.append(make("GREEN", "D2", "Balanced Maturity", r1, ">=30% & >=20%", "Good maturity spread"))
    else:
        results.append(default_green("D2", "Balanced Maturity", r1, "<30% or <20%"))

    # ----------------------------------------------------------------------
    # E. FLOATING RATE EXPOSURE
    # ----------------------------------------------------------------------

    floating_pct = m.get("floating_share", 0)
    if floating_pct > 0.6:
        results.append(make("RED", "E1", "Floating Exposure", floating_pct, ">60%", "High rate sensitivity"))
    elif floating_pct > 0.4:
        results.append(make("YELLOW", "E1", "Floating Exposure", floating_pct, "40–60%", "Moderate risk"))
    else:
        results.append(default_green("E1", "Floating Exposure", floating_pct, "<=40%"))

    # ----------------------------------------------------------------------
    # F. WACD
    # ----------------------------------------------------------------------

    wacd = m.get("wacd", 0)
    if wacd > 0.10:
        results.append(make("RED", "F1", "WACD", wacd, ">10%", "Very high cost"))
    elif wacd > 0.07:
        results.append(make("YELLOW", "F1", "WACD", wacd, "7–10%", "Somewhat expensive"))
    else:
        results.append(default_green("F1", "WACD", wacd, "<=7%", "Good borrowing rate"))

    return results