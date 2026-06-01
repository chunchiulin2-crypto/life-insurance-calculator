"""Policy reserve (benefit reserve) calculations using the prospective method."""

from premium import (single_premium, annual_premium, annuity_due,
                     whole_life_single_premium, whole_life_annual_premium,
                     annuity_due_whole_life,
                     annuity_price,
                     deferred_term_single_premium, deferred_term_annual_premium,
                     deferred_whole_life_single_premium, deferred_whole_life_annual_premium,
                     pure_endowment_single_premium, pure_endowment_annual_premium,
                     endowment_single_premium, endowment_annual_premium)


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
    table_max = int(life_table['age'].max())
    max_years = table_max - age
    result = [(0, 0.0)]
    for k in range(1, max_years + 1):
        future_age = age + k
        if future_age >= table_max:
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
    P = endowment_annual_premium(life_table, age, sum_insured, term, rate)
    result = [(0, 0.0)]
    for k in range(1, term):
        remaining = term - k
        future_benefit = endowment_single_premium(life_table, age + k, sum_insured, remaining, rate)
        future_premium_pv = P * annuity_due(life_table, age + k, remaining, rate)
        result.append((k, future_benefit - future_premium_pv))
    result.append((term, sum_insured))
    return result


# ---- Life Annuity Reserves ----


def annuity_reserve_table(life_table, age, annual_payment, term, rate, payout_m=1):
    """Compute reserves for a life annuity (prospective method).

    kV = PV of remaining payments at age x+k.
    At k=0: reserve = lump-sum purchase price.
    Reserve decreases as payments are made, reaching 0 at end of term.
    """
    result = [(0, annuity_price(life_table, age, annual_payment, term, rate, payout_m=payout_m))]
    for k in range(1, term + 1):
        remaining = term - k
        if remaining <= 0:
            result.append((k, 0.0))
        else:
            rv = annuity_price(life_table, age + k, annual_payment, remaining, rate, payout_m=payout_m)
            result.append((k, rv))
    return result


# ---- Deferred Assurance Reserves ----


def deferred_assurance_reserve_table(life_table, age, defer, sum_insured, rate,
                                     coverage=None, claim_accel=False):
    """Compute reserves for deferred assurance (term or whole life).

    Premiums are paid during the deferral period only.

    During deferral (k < defer):
      kV = S × (defer-k)|Ax+k - P × äx+k:defer-k|
      Reserve grows as premiums accumulate.

    At coverage start (k = defer):
      kV = S × Ax+defer (full net single premium for the coverage).

    During coverage (k > defer):
      kV follows the underlying term/whole life reserve pattern.
      Reserve decreases toward 0 (for term) or approaches S (for whole life).

    If coverage is None, deferred whole life is assumed.
    """
    table_max = int(life_table['age'].max())
    if coverage is not None:
        P = deferred_term_annual_premium(life_table, age, defer, coverage,
                                          sum_insured, rate, claim_accel)
        total_years = defer + coverage
    else:
        P = deferred_whole_life_annual_premium(life_table, age, defer,
                                                sum_insured, rate, claim_accel)
        total_years = table_max - age

    result = [(0, 0.0)]
    for k in range(1, total_years + 1):
        if k < defer:
            rem_def = defer - k
            if coverage is not None:
                future_benefit = deferred_term_single_premium(
                    life_table, age + k, rem_def, coverage,
                    sum_insured, rate, claim_accel)
            else:
                future_benefit = deferred_whole_life_single_premium(
                    life_table, age + k, rem_def,
                    sum_insured, rate, claim_accel)
            future_premium_pv = P * annuity_due(life_table, age + k, rem_def, rate)
            result.append((k, max(future_benefit - future_premium_pv, 0)))
        elif k == defer:
            if coverage is not None:
                future_benefit = single_premium(life_table, age + k, sum_insured,
                                                coverage, rate, claim_accel)
            else:
                future_benefit = whole_life_single_premium(life_table, age + k,
                                                            sum_insured, rate, claim_accel)
            result.append((k, future_benefit))
        else:
            elapsed_cov = k - defer
            if coverage is not None:
                rem_cov = coverage - elapsed_cov
                if rem_cov <= 0:
                    result.append((k, 0.0))
                else:
                    future_benefit = single_premium(life_table, age + k, sum_insured,
                                                    rem_cov, rate, claim_accel)
                    result.append((k, future_benefit))
            else:
                if age + k >= table_max:
                    result.append((k, sum_insured))
                    break
                future_benefit = whole_life_single_premium(life_table, age + k,
                                                            sum_insured, rate, claim_accel)
                result.append((k, future_benefit))
    return result


# ---- Pure Endowment Reserves ----


def pure_endowment_reserve_table(life_table, age, sum_insured, term, rate):
    """Compute reserves for pure endowment insurance.

    kV = S × n-kEx+k - P × äx+k:n-k⌉
    At k=0: reserve = 0 (just issued).
    At k=n: reserve = sum_insured (maturity benefit).
    Reserve steadily increases from 0 to sum_insured over the term —
    a distinguishing feature of pure endowment.
    """
    P = pure_endowment_annual_premium(life_table, age, sum_insured, term, rate)
    result = [(0, 0.0)]
    for k in range(1, term):
        remaining = term - k
        future_benefit = pure_endowment_single_premium(life_table, age + k,
                                                        sum_insured, remaining, rate)
        future_premium_pv = P * annuity_due(life_table, age + k, remaining, rate)
        result.append((k, future_benefit - future_premium_pv))
    result.append((term, sum_insured))
    return result
