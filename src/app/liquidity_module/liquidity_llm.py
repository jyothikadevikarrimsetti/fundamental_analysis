# liquidity_llm.py  
# src/app/liquidity_module/liquidity_llm.py

from src.app.config import OPENAI_MODEL, get_llm_client

client = get_llm_client()
model = OPENAI_MODEL


def generate_liquidity_narrative(company_id, metrics, rules):
    """
    Generate a structured liquidity analysis using LLM,
    similar to the format used in debt_llm.py.
    """

    prompt = f"""
You are a senior financial analyst specializing in short-term liquidity assessment.

Generate a structured **Liquidity Analysis** for company {company_id}.

Metrics:
{metrics}

Rule Flags:
{rules}

Write ONLY these 4 sections:

1. Overall liquidity health
2. Key concerns (red/yellow flags)
3. Strengths & positives
4. Final liquidity conclusion & risk view

Make the summary clear, analytical, and suitable for financial reporting.
"""


    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content