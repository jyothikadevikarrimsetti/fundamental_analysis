def safe_div(a, b):
    if b is None or b == 0:
        return None
    return a / b


def compute_year_metrics(y):

    return {

        "current_ratio" : safe_div(y.current_assets, y.current_liabilities),

        "quick_ratio" : safe_div(
            (y.current_assets - y.inventory),
            y.current_liabilities
        ),

        "cash_ratio": safe_div(
            y.cash_and_equivalents,
            y.current_liabilities
        ),

        "defensive_interval_ratio": safe_div(
            (y.cash_and_equivalents + y.marketable_securities + y.receivables),
            y.daily_operating_expenses
        ),

        "ocf_to_current_liabilities": safe_div(
            y.operating_cash_flow,
            y.current_liabilities
        ),

        "ocf_to_total_debt": safe_div(
            y.operating_cash_flow,
            y.total_debt
        ),

        "interest_coverage_ocf": safe_div(
            y.operating_cash_flow,
            y.interest_expense
        ),

        "cash_coverage_st_debt": safe_div(
            y.cash_and_equivalents,
            y.short_term_debt
        ),
    }

    # return {
    #     "current_ratio": cr,
    #     "quick_ratio": qr,
    #     "cash_ratio": cash_ratio,
    #     "dir_days": dir_days,
    #     "ocf_cl": ocf_cl,
    #     "ocf_debt": ocf_debt,
    #     "interest_cov_ocf": interest_cov_ocf,
    #     "cash_cov_st": cash_cov_st,
    # }
