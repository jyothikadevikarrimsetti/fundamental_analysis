# llm_agent.py
from src.app.config import get_llm_client, OPENAI_MODEL

client = get_llm_client()
model = OPENAI_MODEL



def generate_llm_narrative(company, metrics_table, flags):

    prompt = f"""
You are a financial analyst. Analyze the company: {company}

Data (5 years):
{metrics_table}

Deterministic flags:
{flags}

Provide:
- 3–6 bullet point narrative
- Key red flags
- Positive signals
- Final module risk score (LOW / MEDIUM / HIGH)
"""

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content
