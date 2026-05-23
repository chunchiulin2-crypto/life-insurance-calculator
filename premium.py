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


def single_premium(life_table, age, sum_insured, term, rate, claim_accel=False):
    """Compute net single premium for term life insurance.

    A_x:n * S = S * sum(t=1 to n) v^t * t-1|q_x

    If claim_accel=True: death benefit paid immediately upon death (UDD assumption).
    A_bar_x:n = (1+i)^0.5 * A_x:n
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
    result = sum_insured * total
    if claim_accel:
        result *= (1 + rate) ** 0.5
    return result


def annual_premium(life_table, age, sum_insured, term, rate, claim_accel=False):
    """Compute net level annual premium for term life insurance.

    P = (S * A_x:n) / a_x:n
    """
    sp = single_premium(life_table, age, sum_insured, term, rate, claim_accel)
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


def whole_life_single_premium(life_table, age, sum_insured, rate, claim_accel=False):
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
    result = sum_insured * total
    if claim_accel:
        result *= (1 + rate) ** 0.5
    return result


def whole_life_annual_premium(life_table, age, sum_insured, rate, claim_accel=False):
    """Compute net level annual premium for whole life insurance.

    P = (S * A_x) / a_x
    """
    sp = whole_life_single_premium(life_table, age, sum_insured, rate, claim_accel)
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


def endowment_single_premium(life_table, age, sum_insured, term, rate, claim_accel=False):
    """Compute net single premium for endowment insurance.

    A_x:n(endow) = A_x:n(term) + nEx * S

    If claim_accel=True: only the death benefit part is accelerated.
    The pure endowment (survival benefit) is always paid at maturity.
    """
    sp_term = single_premium(life_table, age, sum_insured, term, rate, claim_accel)
    pe = pure_endowment(life_table, age, term, rate)
    return sp_term + sum_insured * pe


def endowment_annual_premium(life_table, age, sum_insured, term, rate, claim_accel=False):
    """Compute net level annual premium for endowment insurance."""
    sp = endowment_single_premium(life_table, age, sum_insured, term, rate, claim_accel)
    a = annuity_due(life_table, age, term, rate)
    return sp / a if a > 0 else 0


# ---- Life Annuity ----


def annuity_price(life_table, age, annual_payment, term, rate, defer=0, payout_m=1):
    """Compute lump-sum purchase price of a life annuity.

    Pays `annual_payment` total per year, split into `payout_m` payments
    (1=annual, 2=semi, 4=quarterly, 12=monthly). Each payment = annual_payment/payout_m.

    Price = annual_payment * a(m)x:n (deferred if defer > 0)
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
        a_deferred = m_thly_annuity_due(life_table, age + defer, term, rate, payout_m)
        return annual_payment * (v ** defer) * def_px * a_deferred
    a = m_thly_annuity_due(life_table, age, term, rate, payout_m)
    return annual_payment * a


# ---- m-thly Payment Frequency ----


def m_thly_annuity_factor(rate, m):
    """Compute α(m) and β(m) for m-thly annuity-due conversion (UDD).

    ä(m)x:n⌉ = α(m) × äx:n⌉ − β(m) × (1 − nEx)
    """
    if m == 1:
        return 1.0, 0.0
    i = rate
    d = i / (1 + i)
    im = m * ((1 + i) ** (1 / m) - 1)
    dm = m * (1 - (1 - d) ** (1 / m))
    alpha = (i * d) / (im * dm)
    beta = (i - im) / (im * dm)
    return alpha, beta


def m_thly_annuity_due(life_table, age, term, rate, m):
    """Compute ä(m)x:n⌉ — m-thly annuity-due."""
    if m == 1:
        return annuity_due(life_table, age, term, rate)
    a_annual = annuity_due(life_table, age, term, rate)
    alpha, beta = m_thly_annuity_factor(rate, m)
    pe = pure_endowment(life_table, age, term, rate)
    return alpha * a_annual - beta * (1 - pe)


# ---- Gross Premium (α/β/γ) ----


def gross_single_premium(life_table, age, sum_insured, term, rate,
                         alpha=0.0, beta=0.0, gamma=0.0, claim_accel=False):
    """Compute gross single premium with α/β/γ expense loading.

    G = (net_SP + α×S + γ×S×ä) / (1 − β)
    """
    net_sp = single_premium(life_table, age, sum_insured, term, rate, claim_accel)
    a = annuity_due(life_table, age, term, rate)
    expense_pv = alpha * sum_insured + gamma * sum_insured * a
    if beta >= 1.0:
        return float('inf')
    return (net_sp + expense_pv) / (1 - beta)


def gross_annual_premium(life_table, age, sum_insured, term, rate,
                         alpha=0.0, beta=0.0, gamma=0.0, claim_accel=False):
    """Compute gross level annual premium with α/β/γ expense loading.

    G = (Ax:n⌉×S + α×S + γ×S×äx:n⌉) / ((1−β) × äx:n⌉)
    """
    gsp = gross_single_premium(life_table, age, sum_insured, term, rate,
                                alpha, beta, gamma, claim_accel)
    a = annuity_due(life_table, age, term, rate)
    return gsp / a if a > 0 else 0


def periodic_premium(gross_annual, m):
    """Convert gross annual premium to per-payment amount. P(m) = G / m."""
    return gross_annual / m


# ---- Deferred Annuity ----


def deferred_annuity_premium(life_table, age, defer, annual_payment, rate, m=1, payout_m=1):
    """Compute annual premium for a deferred whole-life annuity.

    Accumulation phase: pay premium P for `defer` years, `m` times per year.
    Payout phase: receive `annual_payment` per year (paid `payout_m` times/year)
    for life, starting at age+defer.

    P × ä(m)age:defer⌉ = annual_payment × defer|ä(payout_m)(age+defer)
    """
    v = 1 / (1 + rate)
    lt = life_table
    x_idx = lt[lt['age'] == age].index[0]
    lx = lt.loc[x_idx, 'lx']

    if x_idx + defer >= len(lt):
        return float('inf')
    lx_def = lt.loc[x_idx + defer, 'lx']
    def_px = lx_def / lx if lx > 0 else 0

    # m-thly whole-life annuity-due from payout age
    # approximate via UDD: ä(m)x ≈ äx - (m-1)/2m
    a_payout_annual = annuity_due_whole_life(life_table, age + defer, rate)
    if payout_m > 1:
        adj = (payout_m - 1) / (2 * payout_m)
        a_payout = a_payout_annual - adj
    else:
        a_payout = a_payout_annual

    pv_benefits = (v ** defer) * def_px * a_payout * annual_payment
    a_accum = m_thly_annuity_due(life_table, age, defer, rate, m)

    if a_accum == 0:
        return float('inf')

    return pv_benefits / a_accum


def deferred_annuity_lump_sum(life_table, age, defer, annual_payment, rate, payout_m=1):
    """Compute lump-sum purchase price of a deferred whole-life annuity.

    Single payment now → receive annual_payment for life (paid payout_m times/yr),
    starting at age+defer.

    Price = annual_payment × v^defer × defer_p_x × ä(payout_m)(age+defer)
    """
    v = 1 / (1 + rate)
    lt = life_table
    x_idx = lt[lt['age'] == age].index[0]
    lx = lt.loc[x_idx, 'lx']

    if x_idx + defer >= len(lt):
        return float('inf')
    lx_def = lt.loc[x_idx + defer, 'lx']
    def_px = lx_def / lx if lx > 0 else 0

    a_payout_annual = annuity_due_whole_life(life_table, age + defer, rate)
    if payout_m > 1:
        adj = (payout_m - 1) / (2 * payout_m)
        a_payout = a_payout_annual - adj
    else:
        a_payout = a_payout_annual

    return annual_payment * (v ** defer) * def_px * a_payout


# ---- Deferred Life Assurance ----


def deferred_whole_life_single_premium(life_table, age, defer, sum_insured, rate, claim_accel=False):
    """Net single premium for deferred whole life assurance.

    n|Ax × S = v^n × npx × Ax+n × S

    Coverage begins at age+defer, continues for life.
    No benefit if death occurs during deferment.
    """
    v = 1 / (1 + rate)
    lt = life_table
    x_idx = lt[lt['age'] == age].index[0]
    lx = lt.loc[x_idx, 'lx']
    if x_idx + defer >= len(lt):
        return float('inf')
    lx_def = lt.loc[x_idx + defer, 'lx']
    npx = lx_def / lx if lx > 0 else 0
    axn = whole_life_single_premium(life_table, age + defer, sum_insured, rate, claim_accel)
    return (v ** defer) * npx * axn


def deferred_whole_life_annual_premium(life_table, age, defer, sum_insured, rate, claim_accel=False):
    """Annual premium for deferred whole life assurance, paid during deferment.

    P = (S × n|Ax) / äx:defer⌉
    """
    sp = deferred_whole_life_single_premium(life_table, age, defer, sum_insured, rate, claim_accel)
    a = annuity_due(life_table, age, defer, rate)
    return sp / a if a > 0 else 0


def deferred_term_single_premium(life_table, age, defer, coverage, sum_insured, rate, claim_accel=False):
    """Net single premium for deferred term assurance.

    n|Ax:m⌉ × S = v^n × npx × Ax+n:m⌉ × S

    Coverage from age+defer for `coverage` years.
    """
    v = 1 / (1 + rate)
    lt = life_table
    x_idx = lt[lt['age'] == age].index[0]
    lx = lt.loc[x_idx, 'lx']
    if x_idx + defer >= len(lt):
        return float('inf')
    lx_def = lt.loc[x_idx + defer, 'lx']
    npx = lx_def / lx if lx > 0 else 0
    axn = single_premium(life_table, age + defer, sum_insured, coverage, rate, claim_accel)
    return (v ** defer) * npx * axn


def deferred_term_annual_premium(life_table, age, defer, coverage, sum_insured, rate, claim_accel=False):
    """Annual premium for deferred term assurance, paid during deferment.

    P = (S × n|Ax:m⌉) / äx:defer⌉
    """
    sp = deferred_term_single_premium(life_table, age, defer, coverage, sum_insured, rate, claim_accel)
    a = annuity_due(life_table, age, defer, rate)
    return sp / a if a > 0 else 0
