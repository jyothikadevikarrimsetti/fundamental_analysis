
# # ============================================================
# # debt_orchestrator.py
# # Central orchestrator for the Borrowings Module
# # ============================================================

# from collections import Counter

# from .debt_metrics import compute_per_year_metrics
# from .debt_trend import compute_trend_metrics
# from .debt_rules import apply_rules
# from .debt_llm import generate_llm_narrative
# from .debt_models import BorrowingsInput, BorrowingsOutput


# # ============================================================
# # SCORE ENGINE
# # ============================================================
# def compute_sub_score(rule_results):
#     c = Counter([r.flag for r in rule_results])

#     score = 70
#     score -= 10 * c["RED"]
#     score -= 5 * c["YELLOW"]
#     score += 1 * c["GREEN"]

#     return max(0, min(100, score))


# # ============================================================
# # SUMMARY FLAGS
# # ============================================================
# def summarize(results):
#     red_flags = []
#     positives = []

#     for r in results:
#         if r.flag == "RED":
#             red_flags.append({
#                 "severity": "HIGH",
#                 "title": r.rule_name,
#                 "detail": r.reason,
#             })
#         elif r.flag == "GREEN":
#             positives.append(f"{r.rule_name} is healthy.")

#     return red_flags, positives


# # ============================================================
# # RESHAPE METRICS (Your Required Format)
# # ============================================================
# def reshape_metrics(per_year):
#     reshaped = {}

#     # sort years DESC so latest year comes first
#     for year in sorted(per_year.keys(), reverse=True):
#         label = f"Mar {year}"
#         metrics = per_year[year]

#         for metric_key, metric_value in metrics.items():
#             if metric_key not in reshaped:
#                 reshaped[metric_key] = {}
#             reshaped[metric_key][label] = metric_value

#     return reshaped


# # ============================================================
# # MAIN ORCHESTRATION FUNCTION
# # ============================================================
# def run_borrowings_module(bi: BorrowingsInput) -> BorrowingsOutput:

#     per_year_metrics = compute_per_year_metrics(bi.financials_5y, bi.midd)

#     trend_metrics = compute_trend_metrics(bi.financials_5y, per_year_metrics)

#     rule_results = apply_rules(bi.financials_5y, per_year_metrics, trend_metrics)

#     score = compute_sub_score(rule_results)
#     red_flags, positives = summarize(rule_results)

#     narration = generate_llm_narrative(
#         bi.company_id,
#         metrics={"per_year": per_year_metrics, "trends": trend_metrics},
#         rules=rule_results,
#     )

#     narrative_lines = [x.strip() for x in narration.split("\n") if x.strip()]

#     reshaped_metrics = reshape_metrics(per_year_metrics)

#     return BorrowingsOutput(
#         module="Borrowings",
#         sub_score_adjusted=score,
#         analysis_narrative=narrative_lines,
#         red_flags=red_flags,
#         positive_points=positives,
#         rule_results=rule_results,
#         metrics=reshaped_metrics,
#     )

# ============================================================
# debt_orchestrator.py
# Central orchestrator for the Borrowings Module
# ============================================================

from collections import Counter

from .debt_metrics import compute_per_year_metrics
from .debt_trend import compute_trend_metrics
from .debt_rules import apply_rules
from .debt_llm import generate_llm_narrative
from .debt_models import BorrowingsInput, BorrowingsOutput


# ============================================================
# SCORE ENGINE
# ============================================================
def compute_sub_score(rule_results):
    c = Counter([r.flag for r in rule_results])

    score = 70
    score -= 10 * c["RED"]
    score -= 5 * c["YELLOW"]
    score += 1 * c["GREEN"]

    return max(0, min(100, score))


# ============================================================
# SUMMARY FLAGS
# ============================================================
def summarize(results):
    red_flags = []
    positives = []

    for r in results:
        if r.flag == "RED":
            red_flags.append({
                "severity": "HIGH",
                "title": r.rule_name,
                "detail": r.reason,
            })
        elif r.flag == "GREEN":
            positives.append(f"{r.rule_name} is healthy.")

    return red_flags, positives


# ============================================================
# METRIC OUTPUT — ONLY YOY PERCENTAGE CHANGE
# ============================================================
def reshape_metrics(per_year):

    # EXACT metric names present in per_year dict
    AS_IS_METRICS = {
        "floating_share",
        "wacd",
        "maturity_lt_1y_pct",
        "maturity_1_3y_pct",
        "maturity_gt_3y_pct"
    }

    final_output = {}
    years_asc = sorted(per_year.keys())
    years_desc = sorted(per_year.keys(), reverse=True)

    metric_keys = per_year[years_asc[0]].keys()
    latest_year = years_desc[0]
    latest_label = f"Mar {latest_year}"

    for metric in metric_keys:

        # ----------------------------------------------
        # CASE 1: RETURN RAW VALUE (NO YoY CALCULATION)
        # ----------------------------------------------
        if metric in AS_IS_METRICS:

            raw_val = per_year[latest_year].get(metric)

            out = {latest_label: raw_val}

            # All older years = null
            for y in years_desc[1:]:
                out[f"Mar {y}"] = None

            final_output[metric] = out
            continue

        # ----------------------------------------------
        # CASE 2: NORMAL METRICS → YoY %
        # ----------------------------------------------
        prev = None
        yoy = {}

        for y in years_asc:
            label = f"Mar {y}"
            curr = per_year[y][metric]

            if prev is None or prev == 0:
                yoy[label] = None
            else:
                yoy[label] = round(((curr - prev) / prev) * 100, 2)

            prev = curr

        yoy_ordered = {f"Mar {y}": yoy[f"Mar {y}"] for y in years_desc}

        final_output[metric] = yoy_ordered

    return final_output





# ============================================================
# MAIN ORCHESTRATION FUNCTION
# ============================================================
def run_borrowings_module(bi: BorrowingsInput) -> BorrowingsOutput:

    # 1. Compute yearly metrics
    per_year_metrics = compute_per_year_metrics(bi.financials_5y, bi.midd)

    # 2. Compute trends (CAGR, YoY debt surge, etc.)
    trend_metrics = compute_trend_metrics(bi.financials_5y, per_year_metrics)

    # 3. Apply rules
    rule_results = apply_rules(bi.financials_5y, per_year_metrics, trend_metrics)

    # 4. Score
    score = compute_sub_score(rule_results)

    # 5. Flags
    red_flags, positives = summarize(rule_results)

    # 6. LLM narrative
    narration = generate_llm_narrative(
        bi.company_id,
        metrics={"per_year": per_year_metrics, "trends": trend_metrics},
        rules=rule_results,
    )
    narrative_lines = [line.strip() for line in narration.split("\n") if line.strip()]

    # 7. Produce ONLY YoY growth %
    metrics_output = reshape_metrics(per_year_metrics)

    # 8. Final Output
    return BorrowingsOutput(
        module="Borrowings",
        sub_score_adjusted=score,
        analysis_narrative=narrative_lines,
        red_flags=red_flags,
        positive_points=positives,
        rule_results=rule_results,
        metrics=metrics_output,
    )
