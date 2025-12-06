from typing import List, Dict, Any
from .models import RuleResult

# -----------------------------------------
# Safe formatting helper for metric values
# -----------------------------------------
def fmt(x):
    return f"{x:.2f}" if isinstance(x, (int, float)) else "NA"


def apply_rules(
    metrics_by_year: Dict[int, Dict[str, Any]],
    trends: Dict[str, Any]
) -> List[RuleResult]:

    results: List[RuleResult] = []

    # -------------------------------
    # Identify latest year
    # -------------------------------
    latest_year = max(metrics_by_year.keys())
    latest = metrics_by_year[latest_year]

    capex_intensity = latest.get("capex_intensity")
    cwip_pct = latest.get("cwip_pct")
    asset_turnover = latest.get("asset_turnover")
    debt_funded_capex = latest.get("debt_funded_capex")
    fcf_coverage = latest.get("fcf_coverage")

    # CAGR values (not used in rule flags yet)
    capex_cagr = trends.get("capex_cagr")
    cwip_cagr = trends.get("cwip_cagr")
    nfa_cagr = trends.get("nfa_cagr")
    revenue_cagr = trends.get("revenue_cagr")

    # -------------------------------
    # RULES
    # -------------------------------

    # A1 — Capex Intensity
    if capex_intensity is not None:
        if capex_intensity > 0.15:
            results.append(RuleResult(
                rule_id="A1",
                rule_name="High Capex Intensity",
                metric="capex_intensity",
                year=latest_year,
                flag="RED",
                value=capex_intensity,
                threshold=">0.15",
                reason=f"Capex intensity {fmt(capex_intensity)} is very high."
            ))
        elif capex_intensity > 0.10:
            results.append(RuleResult(
                rule_id="A1",
                rule_name="Moderate Capex Intensity",
                metric="capex_intensity",
                year=latest_year,
                flag="YELLOW",
                value=capex_intensity,
                threshold="0.10–0.15",
                reason="Capex intensity is elevated."
            ))
        else:
            results.append(RuleResult(
                rule_id="A1",
                rule_name="Normal Capex",
                metric="capex_intensity",
                year=latest_year,
                flag="GREEN",
                value=capex_intensity,
                threshold="<0.10",
                reason="Capex intensity is normal."
            ))

    # B1 — CWIP %
    if cwip_pct is not None:
        if cwip_pct > 0.40:
            results.append(RuleResult(
                rule_id="B1",
                rule_name="CWIP % Critical",
                metric="cwip_pct",
                year=latest_year,
                flag="RED",
                value=cwip_pct,
                threshold=">40%",
                reason=f"CWIP extremely high ({fmt(cwip_pct)})."
            ))
        elif cwip_pct > 0.30:
            results.append(RuleResult(
                rule_id="B1",
                rule_name="CWIP % High",
                metric="cwip_pct",
                year=latest_year,
                flag="YELLOW",
                value=cwip_pct,
                threshold="30–40%",
                reason=f"CWIP level elevated ({fmt(cwip_pct)})."
            ))
        else:
            results.append(RuleResult(
                rule_id="B1",
                rule_name="CWIP % Normal",
                metric="cwip_pct",
                year=latest_year,
                flag="GREEN",
                value=cwip_pct,
                threshold="<30%",
                reason="CWIP level normal."
            ))

    # C1 — Asset Turnover
    if asset_turnover is not None:
        if asset_turnover < 0.7:
            results.append(RuleResult(
                rule_id="C1",
                rule_name="Asset Turnover Very Low",
                metric="asset_turnover",
                year=latest_year,
                flag="RED",
                value=asset_turnover,
                threshold="<0.7",
                reason=f"Very poor utilization of fixed assets ({fmt(asset_turnover)})."
            ))
        elif asset_turnover < 1.0:
            results.append(RuleResult(
                rule_id="C1",
                rule_name="Asset Turnover Low",
                metric="asset_turnover",
                year=latest_year,
                flag="YELLOW",
                value=asset_turnover,
                threshold="0.7–1.0",
                reason=f"Asset turnover slightly weak ({fmt(asset_turnover)})."
            ))
        else:
            results.append(RuleResult(
                rule_id="C1",
                rule_name="Asset Turnover Healthy",
                metric="asset_turnover",
                year=latest_year,
                flag="GREEN",
                value=asset_turnover,
                threshold=">1.0",
                reason="Good asset utilization."
            ))

    # D1 — Debt-funded capex
    if debt_funded_capex is not None:
        if debt_funded_capex >= 1.0:
            results.append(RuleResult(
                rule_id="D1",
                rule_name="Fully Debt Funded Capex",
                metric="debt_funded_capex",
                year=latest_year,
                flag="RED",
                value=debt_funded_capex,
                threshold=">=1.0",
                reason="Capex entirely funded by debt."
            ))
        elif debt_funded_capex >= 0.5:
            results.append(RuleResult(
                rule_id="D1",
                rule_name="High Debt-Funded Capex",
                metric="debt_funded_capex",
                year=latest_year,
                flag="YELLOW",
                value=debt_funded_capex,
                threshold=">=0.5",
                reason="Significant dependency on debt for capex."
            ))
        else:
            results.append(RuleResult(
                rule_id="D1",
                rule_name="Low Debt-Funded Capex",
                metric="debt_funded_capex",
                year=latest_year,
                flag="GREEN",
                value=debt_funded_capex,
                threshold="<0.5",
                reason="Capex mostly internally funded."
            ))

    # D2 — FCF Coverage
    if fcf_coverage is not None:
        if fcf_coverage < 0:
            results.append(RuleResult(
                rule_id="D2",
                rule_name="Negative FCF Coverage",
                metric="fcf_coverage",
                year=latest_year,
                flag="RED",
                value=fcf_coverage,
                threshold="<0",
                reason=f"Capex executed despite negative FCF ({fmt(fcf_coverage)})."
            ))
        elif fcf_coverage < 0.5:
            results.append(RuleResult(
                rule_id="D2",
                rule_name="Weak FCF Coverage",
                metric="fcf_coverage",
                year=latest_year,
                flag="YELLOW",
                value=fcf_coverage,
                threshold="0–0.5",
                reason=f"Limited internal reinvestment capacity ({fmt(fcf_coverage)})."
            ))
        else:
            results.append(RuleResult(
                rule_id="D2",
                rule_name="Strong FCF Coverage",
                metric="fcf_coverage",
                year=latest_year,
                flag="GREEN",
                value=fcf_coverage,
                threshold=">0.5",
                reason="Capex well funded by FCF."
            ))

    return results
