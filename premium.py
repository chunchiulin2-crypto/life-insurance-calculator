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
