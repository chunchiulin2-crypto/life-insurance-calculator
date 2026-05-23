"""Policy reserve (benefit reserve) calculations using the prospective method."""

from premium import (single_premium, annual_premium, annuity_due,
                     whole_life_single_premium, whole_life_annual_premium,
                     annuity_due_whole_life)


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


# ---- Whole Life Reserves ----


def whole_life_reserve_table(life_table, age, sum_insured, rate):
    """Compute reserves for whole life insurance (all policy years).

    kV = S * A_{x+k} - P * a_{x+k}
    Reserve increases monotonically, approaching sum_insured at limit age.
    """
    P = whole_life_annual_premium(life_table, age, sum_insured, rate)
    max_years = 105 - age
    result = [(0, 0.0)]
    for k in range(1, max_years + 1):
        future_age = age + k
        if future_age >= 105:
            result.append((k, sum_insured))
            break
        future_benefit = whole_life_single_premium(life_table, future_age, sum_insured, rate)
        future_premium_pv = P * annuity_due_whole_life(life_table, future_age, rate)
        result.append((k, future_benefit - future_premium_pv))
    return result


# ---- Endowment Reserves ----


def endowment_reserve_table(life_table, age, sum_insured, term, rate):
    """Compute reserves for endowment insurance.

    kV = S * A_{x+k:n-k}(endow) - P * a_{x+k:n-k}
    At maturity (k=n): reserve = sum_insured (survival benefit).
    """
    from premium import endowment_single_premium, endowment_annual_premium
    P = endowment_annual_premium(life_table, age, sum_insured, term, rate)
    result = [(0, 0.0)]
    for k in range(1, term):
        remaining = term - k
        future_benefit = endowment_single_premium(life_table, age + k, sum_insured, remaining, rate)
        future_premium_pv = P * annuity_due(life_table, age + k, remaining, rate)
        result.append((k, future_benefit - future_premium_pv))
    result.append((term, sum_insured))
    return result
