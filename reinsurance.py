"""Reinsurance — quota share & surplus treaty calculations."""
from premium import annual_premium, gross_annual_premium, whole_life_annual_premium, endowment_annual_premium


def quota_share(age: int, sum_assured: float, rate: float, term: int,
                product: str, life_table, retention_pct: float,
                alpha: float = 0.03, beta: float = 0.02, gamma: float = 0.001) -> dict:
    """Quota share reinsurance — fixed percentage ceded.

    retention_pct: portion you keep (0.3 = keep 30%, cede 70%)
    Returns dict with ceded/retained premiums, commissions, and net positions.
    """
    cede_pct = 1.0 - retention_pct

    if product == "term":
        net = annual_premium(life_table, age, sum_assured, term, rate)
    elif product == "whole_life":
        net = whole_life_annual_premium(life_table, age, sum_assured, rate)
    elif product == "endowment":
        net = endowment_annual_premium(life_table, age, sum_assured, term, rate)
    else:
        net = annual_premium(life_table, age, sum_assured, term, rate)

    gross = (net + alpha * sum_assured + gamma * sum_assured / 1000) / max(0.01, 1.0 - beta)

    # Reinsurance commission — reinsurer pays you a share of expenses
    commission_rate = 0.02  # typical: 2% of ceded premium
    ceded_premium = gross * cede_pct
    retained_premium = gross * retention_pct
    commission = ceded_premium * commission_rate

    return {
        "gross_premium": gross,
        "net_premium": net,
        "retention_pct": retention_pct,
        "cede_pct": cede_pct,
        "retained_premium": retained_premium,
        "ceded_premium": ceded_premium,
        "commission_income": commission,
        "net_income": retained_premium + commission,
        "retained_risk": sum_assured * retention_pct,
        "ceded_risk": sum_assured * cede_pct,
    }


def surplus(age: int, sum_assured: float, rate: float, term: int,
            product: str, life_table, retention_limit: float,
            lines: int = 5,
            alpha: float = 0.03, beta: float = 0.02, gamma: float = 0.001) -> dict:
    """Surplus reinsurance — cede amounts above retention limit.

    retention_limit: max you keep per life (e.g., 500,000)
    lines: max multiple of retention_limit the reinsurer accepts
           (e.g., 5 lines = reinsurer covers up to 5×500k = 2.5M extra)
    """
    if product == "term":
        net = annual_premium(life_table, age, sum_assured, term, rate)
    elif product == "whole_life":
        net = whole_life_annual_premium(life_table, age, sum_assured, rate)
    elif product == "endowment":
        net = endowment_annual_premium(life_table, age, sum_assured, term, rate)
    else:
        net = annual_premium(life_table, age, sum_assured, term, rate)

    gross = (net + alpha * sum_assured + gamma * sum_assured / 1000) / max(0.01, 1.0 - beta)

    # Surplus calculation
    max_capacity = retention_limit * (1 + lines)
    retained_risk = min(sum_assured, retention_limit)
    ceded_risk = min(sum_assured - retention_limit, retention_limit * lines)
    if ceded_risk < 0:
        ceded_risk = 0.0
    unplaced_risk = max(0.0, sum_assured - max_capacity)

    cede_pct = ceded_risk / sum_assured if sum_assured > 0 else 0.0
    retention_pct = 1.0 - cede_pct

    ceded_premium = gross * cede_pct
    retained_premium = gross * retention_pct
    commission_rate = 0.025
    commission = ceded_premium * commission_rate

    return {
        "gross_premium": gross,
        "net_premium": net,
        "retention_limit": retention_limit,
        "lines": lines,
        "max_capacity": max_capacity,
        "retained_risk": retained_risk,
        "ceded_risk": ceded_risk,
        "unplaced_risk": unplaced_risk,
        "retention_pct": retention_pct,
        "cede_pct": cede_pct,
        "retained_premium": retained_premium,
        "ceded_premium": ceded_premium,
        "commission_income": commission,
        "net_income": retained_premium + commission,
    }
