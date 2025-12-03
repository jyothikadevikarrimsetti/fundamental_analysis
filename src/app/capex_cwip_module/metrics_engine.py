# metrics_engine.py

import numpy as np

def safe_div(a, b):
    try:
        if b in (0, None):
            return None
        return a / b
    except:
        return None

def compute_year_metrics(curr, prev):
    """
    Computes all core metrics for a single year.
    curr = current year dict
    prev = previous year dict (may be None)
    """

    capex = curr["capex"]
    revenue = curr["revenue"]
    cwip = curr["cwip"]
    nfa = curr["net_fixed_assets"]
    ocf = curr["operating_cash_flow"]
    fcf = curr["free_cash_flow"]

    lt_debt = curr["long_term_debt"]
    lt_debt_prev = prev["long_term_debt"] if prev else None

    metrics = {}

    # A. Capex & CWIP metrics
    metrics["capex_intensity"] = safe_div(capex, revenue)
    metrics["cwip_pct"] = safe_div(cwip, (cwip + nfa)) if (cwip is not None and nfa is not None) else None
    metrics["nfa_cwip_total"] = (cwip or 0) + (nfa or 0)

    # YoY growths
    metrics["cwip_yoy"] = safe_div((cwip - prev["cwip"]), prev["cwip"]) if prev else None
    metrics["capex_yoy"] = safe_div((capex - prev["capex"]), prev["capex"]) if prev else None
    metrics["revenue_yoy"] = safe_div((revenue - prev["revenue"]), prev["revenue"]) if prev else None
    metrics["nfa_yoy"] = safe_div((nfa - prev["net_fixed_assets"]), prev["net_fixed_assets"]) if prev else None

    # B. Asset efficiency
    metrics["asset_turnover"] = safe_div(revenue, nfa)
    metrics["fcf_coverage"] = safe_div(fcf, capex)

    # C. Debt-funded capex
    if prev and lt_debt_prev is not None:
        debt_growth = lt_debt - lt_debt_prev
        metrics["debt_funded_capex"] = safe_div(debt_growth, capex)
    else:
        metrics["debt_funded_capex"] = None

    return metrics


def compute_cagr(series):
    """Computes CAGR for list of values."""
    series = [v for v in series if v is not None]
    if len(series) < 2:
        return None
    start, end = series[0], series[-1]
    if start <= 0:
        return None
    n = len(series) - 1
    return (end / start) ** (1 / n) - 1
