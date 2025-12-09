# liquidity_llm_v2.py
import json
from typing import List, Tuple, Optional

from src.app.config import OPENAI_MODEL, get_llm_client
from .liquidity_models import RuleResult  # Assume similar to debt_models

client = get_llm_client()
model = OPENAI_MODEL


def generate_liquidity_narrative(
    company_id: str,
    key_metrics: dict,
    rule_results: List[RuleResult],
    deterministic_notes: Optional[List[str]] = None,
    trend_data: Optional[dict] = None,
) -> Tuple[List[str], dict]:
    """
    Generate a structured LLM-powered liquidity analysis.
    Returns:
        - narrative_list: list of 4 sections
        - trend_insights: dict with insights per metric (cash, receivables, inventory, OCF, current liabilities)
    """
    deterministic_notes = deterministic_notes or []

    if client is None:
        # fallback if LLM client not available
        return deterministic_notes, {}

    prompt_payload = {
        "company_id": company_id,
        "key_metrics": key_metrics,
        "rules": [r.dict() for r in rule_results],
        "deterministic_narrative": deterministic_notes,
        "trend_data": trend_data or {},
    }

    prompt = f"""
You are a senior financial analyst specializing in short-term liquidity assessment.

TASK 1: Generate a structured Liquidity Analysis with EXACTLY four sections:
1. Overall liquidity health
2. Key concerns (highlight RED/YELLOW flags)
3. Strengths & positives
4. Final liquidity conclusion & risk view

TASK 2: Analyze the trend_data for each metric (cash, receivables, inventory, OCF, current liabilities)
and generate dynamic, data-driven insights:
- Patterns of growth or decline over 5 years
- YoY volatility or consistency
- Potential vulnerabilities (e.g., shrinking cash, rising CL, declining OCF)
- Strategic implications (stress vs growth-driven changes)

Return a JSON object with:
{{
    "analysis_narrative": [list of 4 strings matching the sections],
    "trend_insights": {{
        "cash": "insight string",
        "receivables": "insight string",
        "inventory": "insight string",
        "ocf": "insight string",
        "current_liabilities": "insight string"
    }}
}}

Only return valid JSON.

INPUT:
{json.dumps(prompt_payload, ensure_ascii=False)}
"""

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    content = response.choices[0].message.content
    print("LLM Raw Response:", content, flush=True)

    # Strip markdown code blocks if present
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
        if content.endswith("```"):
            content = content[:-3]
    content = content.strip()


    try:
        print("Parsing LLM liquidity narrative response...", flush=True)
        parsed = json.loads(content)
        narrative = parsed.get("analysis_narrative") or deterministic_notes
        trend_insights = parsed.get("trend_insights") or {}

        return narrative, trend_insights
    except json.JSONDecodeError as e:
        print(f"❌ JSON Parse Error: {e}", flush=True)
        print(f"Content was: {content[:500]}", flush=True)
        return deterministic_notes, {}
