# rules_engine.py

from typing import Dict, Any
from src.app.config import DEFAULT_CAPEX_CWIP_RULES as R

def flag(rule_id, name, value, threshold, flag, reason):
    return {
        "rule_id": rule_id,
        "rule_name": name,
        "value": value,
        "threshold": threshold,
        "flag": flag,
        "reason": reason
    }


def evaluate_rules(metrics, cagr_data):
    flags = []

    capex_int = metrics["capex_intensity"]

    # A1 – Capex Intensity
    if capex_int is not None:
        if capex_int > R["capex_intensity_high"]:
            flags.append(flag("A1", "High Capex Intensity", capex_int, ">0.15", "RED",
                              "Capex intensity exceeds 15%, aggressive expansion."))
        elif capex_int > R["capex_intensity_moderate"]:
            flags.append(flag("A1", "Moderate Capex Intensity", capex_int, "0.10–0.15", "YELLOW",
                              "Capex is elevated versus revenue."))
        else:
            flags.append(flag("A1", "Normal Capex", capex_int, "<0.10", "GREEN",
                              "Capex intensity is healthy."))
    else:
        flags.append(flag("A1", "Capex Intensity", None, "<0.10", "NOT_APPLICABLE",
                          "Insufficient data to evaluate."))

    # A2 – Capex growing faster than revenue
    if cagr_data["capex_cagr"] is not None and cagr_data["revenue_cagr"] is not None:
        if cagr_data["capex_cagr"] > (cagr_data["revenue_cagr"] + R["capex_vs_revenue_gap_warning"]):
            flags.append(flag("A2", "Capex Growing Too Fast", cagr_data["capex_cagr"],
                              "Capex CAGR > Revenue CAGR + 10%", "YELLOW",
                              "Capex growth exceeds revenue growth by more than 10%."))
        else:
            flags.append(flag("A2", "Capex vs Revenue Growth Normal", cagr_data["capex_cagr"],
                              "Capex CAGR ≤ Revenue CAGR + 10%", "GREEN",
                              "Capex growth in line with revenue growth."))
    else:
        flags.append(flag("A2", "Capex vs Revenue Growth", None,
                          "Capex CAGR > Revenue CAGR + 10%", "NOT_APPLICABLE",
                          "Insufficient data to evaluate."))

    # B1 – CWIP %
    cwip_pct = metrics["cwip_pct"]
    if cwip_pct is not None:
        if cwip_pct > R["cwip_pct_critical"]:
            flags.append(flag("B1", "CWIP % Critical", cwip_pct, ">0.40", "RED",
                              "CWIP > 40% of fixed assets."))
        elif cwip_pct > R["cwip_pct_warning"]:
            flags.append(flag("B1", "CWIP % High", cwip_pct, "0.30–0.40", "YELLOW",
                              "Heavy project pipeline indicated."))
        else:
            flags.append(flag("B1", "CWIP % Normal", cwip_pct, "<0.30", "GREEN",
                              "CWIP as % of fixed assets is normal."))
    else:
        flags.append(flag("B1", "CWIP %", None, "<0.30", "NOT_APPLICABLE",
                          "Insufficient data to evaluate."))

    # B2 – CWIP rising 3 years
    if cagr_data["cwip_increasing_3y"]:
        flags.append(flag("B2", "CWIP Increasing 3 Years",
                          None, "Rise 3 consecutive years", "YELLOW",
                          "CWIP has risen 3 consecutive years."))
    else:
        flags.append(flag("B2", "CWIP Trend",
                          None, "Rise 3 consecutive years", "GREEN",
                          "CWIP not increasing for 3 consecutive years."))

    # B3 – CWIP down + NFA up
    if metrics["cwip_yoy"] is not None and metrics["nfa_yoy"] is not None and metrics["cwip_yoy"] < 0 and metrics["nfa_yoy"] > 0:
        flags.append(flag("B3", "CWIP Rollover", None,
                          "CWIP↓ & NFA↑", "GREEN",
                          "Projects capitalized from CWIP into NFA."))
    else:
        flags.append(flag("B3", "CWIP Rollover",
                          None, "CWIP↓ & NFA↑", "NOT_APPLICABLE",
                          "No CWIP rollover pattern detected or insufficient data."))

    # C1 – Asset turnover
    at = metrics["asset_turnover"]
    if at is not None:
        if at < R["asset_turnover_critical"]:
            flags.append(flag("C1", "Asset Turnover Very Low", at, "<0.7", "RED",
                              "Fixed asset turnover extremely weak."))
        elif at < R["asset_turnover_low"]:
            flags.append(flag("C1", "Asset Turnover Low", at, "0.7–1.0", "YELLOW",
                              "Fixed asset utilization below optimal."))
        else:
            flags.append(flag("C1", "Asset Turnover Healthy", at, ">1.0", "GREEN",
                              "Good utilization of fixed assets."))
    else:
        flags.append(flag("C1", "Asset Turnover", None, ">1.0", "NOT_APPLICABLE",
                          "Insufficient data to evaluate."))

    # C2 – NFA rising while revenue stagnant
    if cagr_data["nfa_cagr"] is not None and cagr_data["revenue_cagr"] is not None:
        if cagr_data["nfa_cagr"] > (cagr_data["revenue_cagr"] + 0.10):
            flags.append(flag("C2", "NFA Growing Too Fast",
                               cagr_data["nfa_cagr"],
                               "NFA CAGR > Revenue CAGR + 10%", "RED",
                               "Underutilized capacity or stranded assets."))
        else:
            flags.append(flag("C2", "NFA vs Revenue Growth Normal",
                               cagr_data["nfa_cagr"],
                               "NFA CAGR ≤ Revenue CAGR + 10%", "GREEN",
                               "NFA growth in line with revenue growth."))
    else:
        flags.append(flag("C2", "NFA vs Revenue Growth", None,
                          "NFA CAGR > Revenue CAGR + 10%", "NOT_APPLICABLE",
                          "Insufficient data to evaluate."))

    # D1 – Debt-funded capex
    dfc = metrics["debt_funded_capex"]
    if dfc is not None:
        if dfc >= 1.0:
            flags.append(flag("D1", "Fully Debt Funded Capex", dfc, ">=1.0", "RED",
                              "Capex entirely funded through debt."))
        elif dfc >= R["debt_funded_capex_warning"]:
            flags.append(flag("D1", "Debt-Funded Capex High", dfc, ">=0.5", "YELLOW",
                              "Significant dependency on debt for capex."))
        else:
            flags.append(flag("D1", "Debt-Funded Capex Low", dfc, "<0.5", "GREEN",
                              "Capex mostly internally funded."))
    else:
        flags.append(flag("D1", "Debt-Funded Capex", None, "<0.5", "NOT_APPLICABLE",
                          "Insufficient data to evaluate."))

    # D2 – FCF coverage
    fcf_cov = metrics["fcf_coverage"]
    if fcf_cov is not None:
        if fcf_cov < 0:
            flags.append(flag("D2", "Negative FCF Coverage", fcf_cov, "<0", "RED",
                              "Capex executed despite negative free cash flow."))
        elif fcf_cov < 0.5:
            flags.append(flag("D2", "Weak FCF Coverage", fcf_cov, "0–0.5", "YELLOW",
                              "Limited internal reinvestment capacity."))
        else:
            flags.append(flag("D2", "Strong FCF Coverage", fcf_cov, ">0.5", "GREEN",
                              "Capex well supported by free cash flow."))
    else:
        flags.append(flag("D2", "FCF Coverage", None, ">0.5", "NOT_APPLICABLE",
                          "Insufficient data to evaluate."))

    return flags
