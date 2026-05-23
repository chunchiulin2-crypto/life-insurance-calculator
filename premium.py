"""Net premium calculations for term life insurance."""

import numpy as np


def annuity_due(life_table, age, term, rate):
    """Compute a_x:n — present value of annuity-due.

    Pays 1 at beginning of each year while (x) is alive, for n years
    or until death, whichever comes first.

    a_x:n = sum(t=0 to n-1) v^t * t_p_x
    """
    v = 1 / (1 + rate)
    lt = life_table
    x_idx = lt[lt['age'] == age].index[0]
    total = 0.0
    lx = lt.loc[x_idx, 'lx']
    for t in range(term):
        if x_idx + t >= len(lt):
            break
        lxt = lt.loc[x_idx + t, 'lx']
        tpx = lxt / lx if lx > 0 else 0
        total += (v ** t) * tpx
    return total


def single_premium(life_table, age, sum_insured, term, rate):
    """Compute net single premium for term life insurance.

    A_x:n * S = S * sum(t=1 to n) v^t * t-1|q_x

    where t-1|q_x = (l_x+t-1 - l_x+t) / l_x
    """
    v = 1 / (1 + rate)
    lt = life_table
    x_idx = lt[lt['age'] == age].index[0]
    lx = lt.loc[x_idx, 'lx']
    total = 0.0
    for t in range(1, term + 1):
        if x_idx + t >= len(lt):
            break
        lx_t1 = lt.loc[x_idx + t - 1, 'lx']
        lx_t = lt.loc[x_idx + t, 'lx']
        t_minus_1_qx = (lx_t1 - lx_t) / lx if lx > 0 else 0
        total += (v ** t) * t_minus_1_qx
    return sum_insured * total


def annual_premium(life_table, age, sum_insured, term, rate):
    """Compute net level annual premium for term life insurance.

    P = (S * A_x:n) / a_x:n
    """
    sp = single_premium(life_table, age, sum_insured, term, rate)
    a = annuity_due(life_table, age, term, rate)
    if a == 0:
        return 0
    return sp / a


# ---- Whole Life Insurance ----


def annuity_due_whole_life(life_table, age, rate):
    """Compute a_x — whole-life annuity-due.

    a_x = sum(t=0 to 105-x-1) v^t * t_p_x
    """
    v = 1 / (1 + rate)
    lt = life_table
    x_idx = lt[lt['age'] == age].index[0]
    lx = lt.loc[x_idx, 'lx']
    max_t = len(lt) - x_idx - 1
    total = 0.0
    for t in range(max_t):
        lxt = lt.loc[x_idx + t, 'lx']
        tpx = lxt / lx if lx > 0 else 0
        total += (v ** t) * tpx
    return total


def whole_life_single_premium(life_table, age, sum_insured, rate):
    """Compute net single premium for whole life insurance.

    A_x * S = S * sum(t=1 to 105-x) v^t * t-1|q_x
    """
    v = 1 / (1 + rate)
    lt = life_table
    x_idx = lt[lt['age'] == age].index[0]
    lx = lt.loc[x_idx, 'lx']
    max_t = len(lt) - x_idx - 1
    total = 0.0
    for t in range(1, max_t + 1):
        lx_t1 = lt.loc[x_idx + t - 1, 'lx']
        lx_t = lt.loc[x_idx + t, 'lx']
        t_minus_1_qx = (lx_t1 - lx_t) / lx if lx > 0 else 0
        total += (v ** t) * t_minus_1_qx
    return sum_insured * total


def whole_life_annual_premium(life_table, age, sum_insured, rate):
    """Compute net level annual premium for whole life insurance.

    P = (S * A_x) / a_x
    """
    sp = whole_life_single_premium(life_table, age, sum_insured, rate)
    a = annuity_due_whole_life(life_table, age, rate)
    return sp / a if a > 0 else 0


# ---- Endowment Insurance ----


def pure_endowment(life_table, age, term, rate):
    """Compute nEx = v^n * npx — PV of 1 paid at end of n years if alive."""
    v = 1 / (1 + rate)
    lt = life_table
    x_idx = lt[lt['age'] == age].index[0]
    lx = lt.loc[x_idx, 'lx']
    if x_idx + term >= len(lt):
        return 0.0
    lx_n = lt.loc[x_idx + term, 'lx']
    npx = lx_n / lx if lx > 0 else 0
    return (v ** term) * npx


def endowment_single_premium(life_table, age, sum_insured, term, rate):
    """Compute net single premium for endowment insurance.

    A_x:n(endow) = A_x:n(term) + nEx * S
    Death benefit + survival benefit at maturity.
    """
    sp_term = single_premium(life_table, age, sum_insured, term, rate)
    pe = pure_endowment(life_table, age, term, rate)
    return sp_term + sum_insured * pe


def endowment_annual_premium(life_table, age, sum_insured, term, rate):
    """Compute net level annual premium for endowment insurance."""
    sp = endowment_single_premium(life_table, age, sum_insured, term, rate)
    a = annuity_due(life_table, age, term, rate)
    return sp / a if a > 0 else 0


# ---- Life Annuity ----


def annuity_price(life_table, age, annual_payment, term, rate, defer=0):
    """Compute lump-sum purchase price of a life annuity.

    Pays `annual_payment` at the beginning of each year while (x) is alive,
    for `term` years. Supports deferred annuities via `defer` parameter.

    Price = annual_payment * a_x:n (deferred if defer > 0)
    """
    if defer > 0:
        v = 1 / (1 + rate)
        lt = life_table
        x_idx = lt[lt['age'] == age].index[0]
        lx = lt.loc[x_idx, 'lx']
        if x_idx + defer >= len(lt):
            return 0.0
        lx_def = lt.loc[x_idx + defer, 'lx']
        def_px = lx_def / lx if lx > 0 else 0
        a_deferred = annuity_due(life_table, age + defer, term, rate)
        return annual_payment * (v ** defer) * def_px * a_deferred
    a = annuity_due(life_table, age, term, rate)
    return annual_payment * a
