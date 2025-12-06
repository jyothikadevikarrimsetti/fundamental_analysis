from .metrics_engine import compute_year_metrics
from .trend_engine import compute_trends
from .rules_engine import apply_rules
from .llm_agent import generate_llm_narrative
from .models import RuleResult

# Safe formatting helper
def fmt(x):
    return f"{x:.2f}" if isinstance(x, (int, float)) else "NA"


class CapexCwipModule:

    def run(self, payload):

        company = payload.company
        finyrs = payload.financial_data.financial_years

        # Convert models → dicts
        financials = sorted(
            [fy.dict() for fy in finyrs],
            key=lambda x: x["year"]
        )

        # 1) Yearly metrics
        per_year_metrics = {}
        prev = None

        for yr in financials:
            metrics = compute_year_metrics(yr, prev)
            per_year_metrics[yr["year"]] = metrics
            prev = yr

        # 2) Trends
        trend_input = {fy["year"]: fy for fy in financials}
        trend_metrics = compute_trends(trend_input)

        # 3) Rules
        rule_results = apply_rules(per_year_metrics, trend_metrics)

        # 4) Latest year
        latest_year = max(per_year_metrics.keys())
        rule_results = [r for r in rule_results if r.year == latest_year]

        # 5) Score
        red_count = sum(1 for r in rule_results if r.flag == "RED")
        yellow_count = sum(1 for r in rule_results if r.flag == "YELLOW")
        base_score = max(0, 100 - red_count * 15 - yellow_count * 5)

        # 6) Key metrics
        latest = per_year_metrics[latest_year]

        key_metrics = {
            "year": latest_year,
            "capex_intensity": latest["capex_intensity"],
            "cwip_pct": latest["cwip_pct"],
            "asset_turnover": latest["asset_turnover"],
            "debt_funded_capex": latest["debt_funded_capex"],
            "fcf_coverage": latest["fcf_coverage"],
            "capex_cagr": trend_metrics["capex_cagr"],
            "cwip_cagr": trend_metrics["cwip_cagr"],
            "nfa_cagr": trend_metrics["nfa_cagr"],
            "revenue_cagr": trend_metrics["revenue_cagr"],
        }

        # 7) Trends summary
        trend_summary = {
            "cwip": {
                "values": trend_metrics["cwip_series"],
                "yoy_growth_pct": trend_metrics["cwip_yoy"],
                "insight": None
            },
            "capex": {
                "values": trend_metrics["capex_series"],
                "yoy_growth_pct": trend_metrics["capex_yoy"],
                "insight": None
            },
            "nfa": {
                "values": trend_metrics["nfa_series"],
                "yoy_growth_pct": trend_metrics["nfa_yoy"],
                "insight": None
            },
        }

        # 8) Deterministic fallback notes
        deterministic_notes = [
            f"Capex intensity {fmt(latest['capex_intensity'])}.",
            f"CWIP ratio {fmt(latest['cwip_pct'])}.",
            f"Asset turnover {fmt(latest['asset_turnover'])}.",
            f"Debt-funded capex {fmt(latest['debt_funded_capex'])}.",
        ]

        # 9) LLM
        narrative, adjusted_score, trend_insights = generate_llm_narrative(
            company_id=company,
            key_metrics=key_metrics,
            rule_results=rule_results,
            deterministic_notes=deterministic_notes,
            base_score=base_score,
            trend_data=trend_summary,
        )

        # Insert insights
        for metric, text in trend_insights.items():
            if metric in trend_summary:
                trend_summary[metric]["insight"] = text

        # 10) Summary
        red_flags = []
        positives = []

        for r in rule_results:
            if r.flag == "RED":
                red_flags.append({
                    "severity": "CRITICAL",
                    "title": r.rule_name,
                    "detail": r.reason
                })
            elif r.flag == "GREEN":
                positives.append(f"{r.rule_name}: {r.reason}")

        # Final output
        return {
            "module": "CapexCWIP",
            "company": company,
            "key_metrics": key_metrics,
            "trends": trend_summary,
            "analysis_narrative": narrative,
            "red_flags": red_flags,
            "positive_points": positives,
            "rules": [r.dict() for r in rule_results],
        }
