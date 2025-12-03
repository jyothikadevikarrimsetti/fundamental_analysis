def compute_yoy(values: list[float]):
    """
    Compute year-over-year percentage change.
    Returns list of percentages aligned with input list (first year → None).
    """
    if not values or len(values) < 2:
        return [None] * len(values)

    yoy = [None]  # First year has no YoY
    for i in range(1, len(values)):
        prev = values[i - 1]
        curr = values[i]

        if prev in (0, None):
            yoy.append(None)
        else:
            yoy.append((curr - prev) / prev)

    return yoy


def compute_trends(financials):
    """
    financials: list of objects or dicts having attributes:
        cash_and_equivalents, receivables, inventory, operating_cash_flow, current_liabilities
    Returns YoY % trends for each metric.
    """

    def extract(field):
        return [getattr(y, field) for y in financials]

    cash = extract("cash_and_equivalents")
    receivables = extract("receivables")
    inventory = extract("inventory")
    ocf = extract("operating_cash_flow")
    cl = extract("current_liabilities")

    return {
        "cash_yoy": compute_yoy(cash),
        "receivables_yoy": compute_yoy(receivables),
        "inventory_yoy": compute_yoy(inventory),
        "ocf_yoy": compute_yoy(ocf),
        "cl_yoy": compute_yoy(cl),
    }