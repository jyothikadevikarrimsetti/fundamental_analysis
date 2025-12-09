"""
Generate data-driven insights for Liquidity Module (fallback when LLM is unavailable)
"""

from typing import Dict


def generate_liquidity_fallback_insight(metric_name: str, values: Dict[str, float], yoy_growth_pct: Dict[str, float]) -> str:
    """
    Generate intelligent liquidity insights based on historical data patterns.
    Covers cash, receivables, inventory, OCF, and current liabilities.
    """

    # Extract valid YoY values
    growth_values = [v for v in yoy_growth_pct.values() if v is not None]

    if not growth_values:
        return f"{metric_name.replace('_', ' ').title()} data is insufficient for liquidity trend analysis."

    # Basic stats
    avg_growth = sum(growth_values) / len(growth_values)
    max_growth = max(growth_values)
    min_growth = min(growth_values)
    volatility = max_growth - min_growth

    # Recent 2-year trend
    recent_growth = [yoy_growth_pct.get("Y_vs_Y-1"), yoy_growth_pct.get("Y-1_vs_Y-2")]
    recent_growth = [v for v in recent_growth if v is not None]
    recent_avg = sum(recent_growth) / len(recent_growth) if recent_growth else 0

    # Pattern detection
    is_volatile = volatility > 30
    is_high_growth = avg_growth > 15
    is_declining = avg_growth < -5
    is_accelerating = len(growth_values) >= 3 and growth_values[0] > growth_values[1] > growth_values[2]
    is_decelerating = len(growth_values) >= 3 and growth_values[0] < growth_values[1] < growth_values[2]

    insights = []

    # ----------------------------------------------------------------------
    # METRIC-SPECIFIC LIQUIDITY LOGIC
    # ----------------------------------------------------------------------

    # 1️⃣ CASH
    if metric_name == "cash":
        if is_declining:
            insights.append("Cash levels are contracting YoY, signalling tightening liquidity buffers.")
        if is_high_growth:
            insights.append("Cash reserves show healthy YoY improvement, strengthening immediate liquidity.")
        if is_volatile:
            insights.append("Cash position is highly volatile, indicating unstable near-term liquidity.")
        if recent_avg < 0:
            insights.append("Recent negative trend in cash indicates weakening cash cushion.")

    # 2️⃣ RECEIVABLES
    elif metric_name == "receivables":
        if is_high_growth:
            insights.append("Receivables are rising sharply, indicating potential collection delays.")
            if max_growth > 25:
                insights.append("Significant YoY spike suggests deteriorating credit discipline or customer stress.")
        if is_declining:
            insights.append("Receivables are reducing YoY, indicating better collections.")
        if is_volatile:
            insights.append("Receivables trend is unstable, pointing to inconsistent collection cycles.")

    # 3️⃣ INVENTORY
    elif metric_name == "inventory":
        if is_high_growth:
            insights.append("Inventory build-up visible, which may lock working capital and pressure cash flows.")
        if is_declining:
            insights.append("Inventory reduction may indicate improved working capital efficiency.")
        if max_growth > 20:
            insights.append("Large inventory spike suggests slow-moving stock or demand mismatch.")

    # 4️⃣ OPERATING CASH FLOW (OCF)
    elif metric_name == "operating_cash_flow":
        if is_declining:
            insights.append("OCF is weakening, reducing the company's ability to self-fund operations.")
        if is_high_growth:
            insights.append("OCF shows strong positive YoY momentum, enhancing internal liquidity strength.")
        if recent_avg < 0:
            insights.append("Recent OCF decline indicates short-term stress in core operations.")
        if is_volatile:
            insights.append("OCF volatility suggests inconsistent operating performance.")

    # 5️⃣ CURRENT LIABILITIES
    elif metric_name == "current_liabilities":
        if is_high_growth:
            insights.append("Current liabilities are rising, increasing short-term funding pressure.")
        if is_declining:
            insights.append("Current liabilities decreasing YoY indicates reduced short-term obligations.")
        if max_growth > 20:
            insights.append("Sharp YoY increase in current liabilities suggests reliance on short-term credit.")
        if recent_avg < 0:
            insights.append("Recent slowdown in CL growth indicates stabilizing short-term obligations.")

    # ----------------------------------------------------------------------
    # GENERIC PATTERNS IF NOTHING SPECIFIC TRIGGERED
    # ----------------------------------------------------------------------
    if not insights:
        if is_accelerating:
            insights.append(f"{metric_name.replace('_', ' ').title()} shows accelerating trend (avg YoY {avg_growth:.1f}%).")
        elif is_decelerating:
            insights.append(f"{metric_name.replace('_', ' ').title()} shows decelerating trend (avg YoY {avg_growth:.1f}%).")
        else:
            insights.append(f"{metric_name.replace('_', ' ').title()} shows mixed YoY behavior with average growth of {avg_growth:.1f}%.")

    return " ".join(insights)
