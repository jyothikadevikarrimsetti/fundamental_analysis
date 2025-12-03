from src.app.config import LIQUIDITY_RULES


# -----------------------------------------------------------
# Helper function to classify value into RED / YELLOW / GREEN
# -----------------------------------------------------------
def flag_color(value, critical, moderate):
    if value is None:
        return "RED"
    if value < critical:
        return "RED"
    if value < moderate:
        return "YELLOW"
    return "GREEN"


# -----------------------------------------------------------
# Main Rule Evaluation
# -----------------------------------------------------------
def evaluate_rules(metrics, trends):
    rules = []
    r = LIQUIDITY_RULES["generic"]

    # ------------------------------
    # 1. Current Ratio
    # ------------------------------
    cr = metrics.get("current_ratio")
    cr_flag = flag_color(cr, r["critical_current_ratio"], r["moderate_current_ratio"])

    rules.append({
        "rule_id": "A1",
        "rule_name": "Current Ratio Check",
        "value": cr,
        "threshold": f"<{r['critical_current_ratio']} RED, <{r['moderate_current_ratio']} YELLOW",
        "flag": cr_flag,
        "reason": f"Current ratio is {round(cr, 2) if cr is not None else 'N/A'}"
    })

    # ------------------------------
    # 2. Quick Ratio
    # ------------------------------
    qr = metrics.get("quick_ratio")
    qr_flag = flag_color(qr, r["critical_quick_ratio"], r["moderate_quick_ratio"])

    rules.append({
        "rule_id": "A2",
        "rule_name": "Quick Ratio Check",
        "value": qr,
        "threshold": f"<{r['critical_quick_ratio']} RED, <{r['moderate_quick_ratio']} YELLOW",
        "flag": qr_flag,
        "reason": f"Quick ratio is {round(qr, 2) if qr is not None else 'N/A'}"
    })

    # ------------------------------
    # 3. Cash Ratio
    # ------------------------------
    cash_r = metrics.get("cash_ratio")
    cash_flag = flag_color(cash_r, r["critical_cash_ratio"], r["moderate_cash_ratio"])

    rules.append({
        "rule_id": "A3",
        "rule_name": "Cash Ratio Check",
        "value": cash_r,
        "threshold": f"<{r['critical_cash_ratio']} RED, <{r['moderate_cash_ratio']} YELLOW",
        "flag": cash_flag,
        "reason": f"Cash ratio is {round(cash_r, 2) if cash_r is not None else 'N/A'}"
    })

    # ------------------------------
    # 4. Defensive Interval Ratio (DIR Days)
    # ------------------------------
    dir_days = metrics.get("defensive_interval_ratio")
    dir_flag = flag_color(dir_days, r["dir_critical_days"], r["dir_moderate_days"])

    rules.append({
        "rule_id": "B",
        "rule_name": "Defensive Interval Ratio",
        "value": dir_days,
        "threshold": f"<{r['dir_critical_days']} RED, <{r['dir_moderate_days']} YELLOW",
        "flag": dir_flag,
        "reason": f"DIR days = {round(dir_days, 2) if dir_days is not None else 'N/A'}"
    })

    # ------------------------------
    # 5. OCF / Current Liabilities
    # ------------------------------
    ocf_cl = metrics.get("ocf_to_current_liabilities")
    ocf_cl_flag = flag_color(ocf_cl, r["ocf_cl_critical"], r["ocf_cl_moderate"])

    rules.append({
        "rule_id": "C1",
        "rule_name": "OCF to Current Liabilities",
        "value": ocf_cl,
        "threshold": f"<{r['ocf_cl_critical']} RED, <{r['ocf_cl_moderate']} YELLOW",
        "flag": ocf_cl_flag,
        "reason": f"OCF/CL is {round(ocf_cl, 2) if ocf_cl is not None else 'N/A'}"
    })

    # ------------------------------
    # 6. OCF / Total Debt
    # ------------------------------
    ocf_debt = metrics.get("ocf_to_total_debt")
    ocf_debt_flag = flag_color(ocf_debt, r["ocf_debt_critical"], r["ocf_debt_moderate"])

    rules.append({
        "rule_id": "C2",
        "rule_name": "OCF to Total Debt",
        "value": ocf_debt,
        "threshold": f"<{r['ocf_debt_critical']} RED, <{r['ocf_debt_moderate']} YELLOW",
        "flag": ocf_debt_flag,
        "reason": f"OCF/Debt is {round(ocf_debt, 2) if ocf_debt is not None else 'N/A'}"
    })

    # ------------------------------
    # 7. Interest Coverage (OCF-based)
    # ------------------------------
    ic_ocf = metrics.get("interest_coverage_ocf")
    ic_ocf_flag = "GREEN" if ic_ocf is not None and ic_ocf >= 3 else ("YELLOW" if ic_ocf and ic_ocf >= 1 else "RED")

    rules.append({
        "rule_id": "C3",
        "rule_name": "OCF Interest Coverage",
        "value": ic_ocf,
        "threshold": "RED <1, YELLOW <3, GREEN ≥3",
        "flag": ic_ocf_flag,
        "reason": f"Interest coverage from OCF is {round(ic_ocf, 2) if ic_ocf is not None else 'N/A'}"
    })

    # ------------------------------
    # 8. Cash Coverage of Short-Term Debt
    # ------------------------------
    cash_cov = metrics.get("cash_coverage_st_debt")
    cash_cov_flag = "GREEN" if cash_cov is not None and cash_cov >= 1 else ("YELLOW" if cash_cov and cash_cov >= 0.2 else "RED")

    rules.append({
        "rule_id": "D",
        "rule_name": "Cash Coverage of Short-Term Debt",
        "value": cash_cov,
        "threshold": "RED <0.2, YELLOW <1, GREEN ≥1",
        "flag": cash_cov_flag,
        "reason": f"Cash coverage ST debt is {round(cash_cov, 2) if cash_cov is not None else 'N/A'}"
    })

    return rules