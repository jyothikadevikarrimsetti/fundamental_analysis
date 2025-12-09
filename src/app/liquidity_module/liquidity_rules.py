from .liquidity_config import LIQUIDITY_RULES


# ===========================================================
# Helper: Standardized result builder (borrowings-style)
# ===========================================================
def _make(rule_id, name, value, threshold, flag, reason):
    return {
        "rule_id": rule_id,
        "rule_name": name,
        "value": value,
        "threshold": threshold,
        "flag": flag,
        "reason": reason,
    }


# ===========================================================
# Helper: apply RED / YELLOW / GREEN (borrowings-style)
# ===========================================================
def _flag_basic(value, critical, moderate):
    """
    RED     → value < critical
    YELLOW  → critical ≤ value < moderate
    GREEN   → ≥ moderate
    """
    if value is None:
        return "RED"

    if value < critical:
        return "RED"
    if value < moderate:
        return "YELLOW"
    return "GREEN"


# ===========================================================
# Main Rule Engine
# ===========================================================
def evaluate_rules(metrics, trends):
    rules = []
    cfg = LIQUIDITY_RULES["generic"]

    # -------------------------------------------------------
    # A-Series: Liquidity Ratios (Current, Quick, Cash)
    # -------------------------------------------------------
    # A1 — Current Ratio
    cr = metrics.get("current_ratio")
    cr_flag = _flag_basic(cr, cfg["critical_current_ratio"], cfg["moderate_current_ratio"])
    rules.append(_make(
        "A1",
        "Current Ratio Adequacy",
        cr,
        f"RED < {cfg['critical_current_ratio']}, YELLOW < {cfg['moderate_current_ratio']}",
        cr_flag,
        f"Current ratio is {round(cr, 2) if cr is not None else 'N/A'}, indicating the firm’s ability to meet short-term liabilities."
    ))

    # A2 — Quick Ratio
    qr = metrics.get("quick_ratio")
    qr_flag = _flag_basic(qr, cfg["critical_quick_ratio"], cfg["moderate_quick_ratio"])
    rules.append(_make(
        "A2",
        "Quick Ratio Strength",
        qr,
        f"RED < {cfg['critical_quick_ratio']}, YELLOW < {cfg['moderate_quick_ratio']}",
        qr_flag,
        f"Quick ratio is {round(qr, 2) if qr is not None else 'N/A'}, assessing liquidity excluding inventory."
    ))

    # A3 — Cash Ratio
    cash_r = metrics.get("cash_ratio")
    cash_flag = _flag_basic(cash_r, cfg["critical_cash_ratio"], cfg["moderate_cash_ratio"])
    rules.append(_make(
        "A3",
        "Cash Ratio Position",
        cash_r,
        f"RED < {cfg['critical_cash_ratio']}, YELLOW < {cfg['moderate_cash_ratio']}",
        cash_flag,
        f"Cash ratio stands at {round(cash_r, 2) if cash_r is not None else 'N/A'}, showing immediate liquidity cover."
    ))

    # -------------------------------------------------------
    # B-Series: Liquidity Coverage Days
    # -------------------------------------------------------
    # B1 — DIR (Defensive Interval)
    dir_days = metrics.get("defensive_interval_ratio_days")
    dir_flag = _flag_basic(dir_days, cfg["dir_critical_days"], cfg["dir_moderate_days"])
    rules.append(_make(
        "B1",
        "Defensive Interval Ratio (Days)",
        dir_days,
        f"RED < {cfg['dir_critical_days']} days, YELLOW < {cfg['dir_moderate_days']} days",
        dir_flag,
        f"DIR days = {round(dir_days, 2) if dir_days is not None else 'N/A'}, showing how long the company can operate using liquid assets alone."
    ))

    # -------------------------------------------------------
    # C-Series: Cash Flow-based Liquidity Strength
    # -------------------------------------------------------
    # C1 — OCF / Current Liabilities
    ocf_cl = metrics.get("ocf_to_current_liabilities")
    ocf_cl_flag = _flag_basic(ocf_cl, cfg["ocf_cl_critical"], cfg["ocf_cl_moderate"])
    rules.append(_make(
        "C1",
        "OCF Coverage of Current Liabilities",
        ocf_cl,
        f"RED < {cfg['ocf_cl_critical']}, YELLOW < {cfg['ocf_cl_moderate']}",
        ocf_cl_flag,
        f"OCF/CL = {round(ocf_cl, 2) if ocf_cl is not None else 'N/A'}, measuring if operating cash flow can cover near-term obligations."
    ))

    # C2 — OCF / Total Debt
    ocf_debt = metrics.get("ocf_to_total_debt")
    ocf_debt_flag = _flag_basic(ocf_debt, cfg["ocf_debt_critical"], cfg["ocf_debt_moderate"])
    rules.append(_make(
        "C2",
        "OCF Coverage of Total Debt",
        ocf_debt,
        f"RED < {cfg['ocf_debt_critical']}, YELLOW < {cfg['ocf_debt_moderate']}",
        ocf_debt_flag,
        f"OCF/Debt = {round(ocf_debt, 2) if ocf_debt is not None else 'N/A'}, showing long-term liquidity and repayment strength."
    ))

    # C3 — Interest Coverage (OCF-based)
    ic_ocf = metrics.get("interest_coverage_ocf")
    if ic_ocf is None:
        ic_ocf_flag = "RED"
    elif ic_ocf < 1:
        ic_ocf_flag = "RED"
    elif ic_ocf < 3:
        ic_ocf_flag = "YELLOW"
    else:
        ic_ocf_flag = "GREEN"

    rules.append(_make(
        "C3",
        "OCF-based Interest Coverage",
        ic_ocf,
        "RED <1, YELLOW <3, GREEN ≥3",
        ic_ocf_flag,
        f"OCF interest coverage = {round(ic_ocf, 2) if ic_ocf is not None else 'N/A'}, evaluating ability to service interest purely from cash flow."
    ))

    # -------------------------------------------------------
    # D-Series: Immediate Debt Repayment Ability
    # -------------------------------------------------------
    # D1 — Cash Coverage of Short-Term Debt
    cash_cov = metrics.get("cash_coverage_st_debt")

    if cash_cov is None:
        cash_cov_flag = "RED"
    elif cash_cov < 0.2:
        cash_cov_flag = "RED"
    elif cash_cov < 1:
        cash_cov_flag = "YELLOW"
    else:
        cash_cov_flag = "GREEN"

    rules.append(_make(
        "D1",
        "Cash Coverage of Short-Term Debt",
        cash_cov,
        "RED <0.2, YELLOW <1, GREEN ≥1",
        cash_cov_flag,
        f"Cash/ST debt = {round(cash_cov, 2) if cash_cov is not None else 'N/A'}, showing if cash can immediately cover short-term borrowings."
    ))


    # -------------------------------------------------------
    # E-Series: Working Capital Stress Rules
    # -------------------------------------------------------

    # E1 — Receivables Growing Faster Than OCF
    recv_yoy = None
    ocf_yoy = None

    try:
        recv_yoy_list = trends.get("yoy", {}).get("receivables_yoy", [])
        ocf_yoy_list = trends.get("yoy", {}).get("ocf_yoy", [])

        if recv_yoy_list:
            recv_yoy = recv_yoy_list[-1]
        if ocf_yoy_list:
            ocf_yoy = ocf_yoy_list[-1]
    except:
        pass

    # Flag logic for E1
    if recv_yoy is None or ocf_yoy is None:
        e1_flag = "RED"
        e1_reason = "Insufficient data to analyse receivables vs OCF trend."
    elif recv_yoy > 25 and ocf_yoy < 0:
        e1_flag = "YELLOW"
        e1_reason = "Receivables are growing faster than cash generation, indicating potential collection issues."
    elif recv_yoy <= 10 and ocf_yoy > 0:
        e1_flag = "GREEN"
        e1_reason = "Receivables growth is controlled and supported by improving operating cash flow."
    elif recv_yoy > 40 and ocf_yoy < -10:
        e1_flag = "RED"
        e1_reason = "Sharp receivables growth with significant OCF decline indicates serious collection risk."
    else:
        e1_flag = "GREEN"
        e1_reason = "Receivables and cash flow trends appear balanced."

    rules.append(_make(
        "E1",
        "Receivables vs OCF Trend Risk",
        recv_yoy,
        "YELLOW if Receivables YoY > 25% and OCF declining",
        e1_flag,
        e1_reason
    ))

    # -------------------------------------------------------

    # E2 — Inventory Build-up Without Cash Flow Support
    inv_yoy = None

    try:
        inv_yoy_list = trends.get("yoy", {}).get("inventory_yoy", [])
        cash_yoy_list = trends.get("yoy", {}).get("cash_yoy", [])

        if inv_yoy_list:
            inv_yoy = inv_yoy_list[-1]
        if cash_yoy_list:
            cash_yoy = cash_yoy_list[-1]
        else:
            cash_yoy = None
    except:
        cash_yoy = None

    # Flag logic for E2
    if inv_yoy is None:
        e2_flag = "RED"
        e2_reason = "Insufficient data to analyse inventory trend."
    elif inv_yoy > 25 and (cash_yoy is None or cash_yoy <= 0):
        e2_flag = "YELLOW"
        e2_reason = "Inventory is rising without supporting cash improvement, indicating over-stocking risk."
    elif inv_yoy > 40 and (cash_yoy is None or cash_yoy < -10):
        e2_flag = "RED"
        e2_reason = "Sharp inventory build-up combined with deteriorating cash position signals high over-stocking risk."
    elif inv_yoy <= 10:
        e2_flag = "GREEN"
        e2_reason = "Inventory growth is controlled and aligned with business activity."
    else:
        e2_flag = "GREEN"
        e2_reason = "Inventory levels appear stable and supported by liquidity."

    rules.append(_make(
        "E2",
        "Inventory vs Cash Flow Stress Check",
        inv_yoy,
        "YELLOW if Inventory YoY > 25% without cash improvement",
        e2_flag,
        e2_reason
    ))

    return rules
