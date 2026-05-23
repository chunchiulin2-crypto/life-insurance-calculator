"""Policy reserve (benefit reserve) calculations using the prospective method."""

from premium import single_premium, annual_premium, annuity_due


def prospective_reserve(life_table, age, sum_insured, term, rate, year_k):
    """Compute prospective reserve at end of policy year k.

    k_V = S * A_{x+k:n-k} - P * a_{x+k:n-k}

    where P is the net level annual premium.
    At k=0: reserve = 0 (no time has passed)
    At k=n: reserve = 0 (policy expired)
    """
    if year_k == 0 or year_k == term:
        return 0.0

    P = annual_premium(life_table, age, sum_insured, term, rate)
    remaining_term = term - year_k
    future_benefit = single_premium(life_table, age + year_k, sum_insured, remaining_term, rate)
    future_premium_pv = P * annuity_due(life_table, age + year_k, remaining_term, rate)
    return future_benefit - future_premium_pv


def reserve_table(life_table, age, sum_insured, term, rate):
    """Compute reserves for all policy years 0 through n.

    Returns list of (year, reserve) tuples.
    """
    return [(k, prospective_reserve(life_table, age, sum_insured, term, rate, k))
            for k in range(term + 1)]
