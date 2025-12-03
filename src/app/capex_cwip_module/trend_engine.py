# trend_engine.py
from .metrics_engine import compute_cagr
def is_increasing_3y(values):
    if len(values) < 3:
        return False
    return values[-1] > values[-2] > values[-3]


def compute_trends(financials):
    # Extract 5-year series
    cwip_series = [y["cwip"] for y in financials]
    capex_series = [y["capex"] for y in financials]
    nfa_series = [y["net_fixed_assets"] for y in financials]
    rev_series = [y["revenue"] for y in financials]

    return {
        "cwip_cagr": compute_cagr(cwip_series),
        "capex_cagr": compute_cagr(capex_series),
        "nfa_cagr": compute_cagr(nfa_series),
        "revenue_cagr": compute_cagr(rev_series),
        "cwip_increasing_3y": is_increasing_3y(cwip_series)
    }
