from .liquidity_metrics import compute_year_metrics
from .liquidity_trend import compute_trends
from .liquidity_rules import evaluate_rules, flag_color
from .liquidity_llm import generate_liquidity_narrative
from .liquidity_models import LiquidityModuleOutput, RuleResult


def run_liquidity_module(input_data):
    financials = input_data.financials_5y

    # compute latest year metrics
    latest = financials[-1]
    metrics = compute_year_metrics(latest)

    # compute trends
    trends = compute_trends(financials)

    # evaluate rules
    rules = evaluate_rules(metrics, trends)

    # scoring (simple: deduct 5 for yellow, 10 for red)
    score = 100
    for r in rules:
        if r["flag"] == "RED":
            score -= 10
        elif r["flag"] == "YELLOW":
            score -= 5

    # narratives
    narrative = [generate_liquidity_narrative( 
        input_data.company_id,      
        metrics, 
        rules
    )]


    # red flags summary
    red_flags = []
    for r in rules:
        if r["flag"] in ("RED", "YELLOW"):
            # Map severity based on flag
            severity = "CRITICAL" if r["flag"] == "RED" else "HIGH"
            red_flags.append({
                "severity": severity,
                "title": r["rule_name"],
                "detail": r["reason"]
            })

    # positive points
    positive = [
        "Marketable securities help liquidity strength.",
        "Receivables provide partial operational cushion."
    ]

    rule_results = []
    for r in rules:
        rule_results.append(RuleResult(
            rule_id=r.get("rule_id", ""),
            rule_name=r.get("rule_name", ""),
            value=r.get("value", 0.0) or 0.0,
            threshold=r.get("threshold", ""),
            flag=r.get("flag", ""),
            reason=r.get("reason", "")
        ))


    return LiquidityModuleOutput(
        module="Liquidity",
        sub_score_adjusted=max(score, 0),
        analysis_narrative=narrative,
        red_flags=red_flags,
        positive_points=positive,
        rules=rule_results
    )