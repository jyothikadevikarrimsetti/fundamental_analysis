0# src/app/config.py

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")


def get_llm_client():


    return OpenAI(api_key=OPENAI_API_KEY)


# config.py

DEFAULT_CAPEX_CWIP_RULES = {
    "capex_intensity_high": 0.15,
    "capex_intensity_moderate": 0.10,

    "cwip_pct_critical": 0.40,
    "cwip_pct_warning": 0.30,

    "asset_turnover_critical": 0.7,
    "asset_turnover_low": 1.0,

    "capex_vs_revenue_gap_warning": 0.10,
    "cwip_growth_warning": 0.25,

    "debt_funded_capex_warning": 0.50
}
