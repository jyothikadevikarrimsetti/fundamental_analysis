# orchestrator.py

from .metrics_engine import compute_year_metrics
from .trend_engine import compute_trends
from .rules_engine import evaluate_rules
from .llm_agent import generate_llm_narrative

def run_capex_cwip_module(payload):
    """
    llm → function(prompt) → text
    """
    print('hi')
    company = payload.company
    financial_data = payload.financial_data.dict()
    print(financial_data)
    financials = sorted(financial_data['financial_years'], key=lambda x: x["year"], reverse=True)
    print(financials)

    # ------------------------------------------------
    # 1️⃣ Compute metrics for each year
    # ------------------------------------------------
    yearly_results = []
    for i, year_data in enumerate(financials):
        prev = financials[i - 1] if i > 0 else None
        metrics = compute_year_metrics(year_data, prev)
        yearly_results.append({
            "year": year_data["year"],
            "metrics": metrics
        })

    # ------------------------------------------------
    # 2️⃣ Compute multi-year CAGRs & Trend Signals
    # ------------------------------------------------
    cagr_data = compute_trends(financials)

    # ------------------------------------------------
    # 3️⃣ Apply Rules for Each Year
    # ------------------------------------------------
    all_year_flags = []
    for item in yearly_results:
        flags = evaluate_rules(item["metrics"], cagr_data)
        for f in flags:
            all_year_flags.append({
                "year": item["year"],
                **f
            })

    # ------------------------------------------------
    # 3️⃣a Filter rules for latest year only
    # ------------------------------------------------
    latest_year = max([item["year"] for item in yearly_results])
    all_year_flags = [f for f in all_year_flags if f["year"] == latest_year]

    # ------------------------------------------------
    # 4️⃣ Classify flags into red/yellow/green
    # ------------------------------------------------
    red_flags = []
    yellow_flags = []
    green_flags = []

    for f in all_year_flags:
        if f["flag"] == "RED":
            red_flags.append(f)
        elif f["flag"] == "YELLOW":
            yellow_flags.append(f)
        else:
            green_flags.append(f)

    # ------------------------------------------------
    # 5️⃣ Normalize Output Flags (as per schema)
    # ------------------------------------------------
    formatted_red_flags = [{
        "severity": "CRITICAL" if rf["flag"] == "RED" else "HIGH",
        "title": rf["rule_name"],
        "detail": rf["reason"]
    } for rf in red_flags]

    # Positive points → from green rule messages
    positive_points = [
        f["reason"]
        for f in green_flags
    ]

    # ------------------------------------------------
    # 6️⃣ Compute Sub-score
    # ------------------------------------------------
    red_score = len(red_flags) * 15
    yellow_score = len(yellow_flags) * 5
    sub_score = max(0, 100 - red_score - yellow_score)

    # ------------------------------------------------
    # 7️⃣ Build LLM Narrative
    # ------------------------------------------------
    metrics_table_text = "\n".join([str(x) for x in yearly_results])
    narrative = generate_llm_narrative(company, metrics_table_text, all_year_flags) 
    narrative_list =[line.strip() for line in narrative.split("\n") if line.strip()]

    # ------------------------------------------------
    # 8️⃣ Final Output Schema
    # ------------------------------------------------
    result = {
        "module": "CapexCWIP",
        "sub_score_adjusted": sub_score,
        "analysis_narrative": narrative_list,
        "red_flags": formatted_red_flags,
        "positive_points": positive_points,
        "rules": all_year_flags,
        "yearly_metrics": yearly_results,
    }

    return result
