"""Dynamic Premium Optimizer — Bayesian search for optimal pricing.

Given internal cost structure and competitor benchmarks, finds the premium
rate that maximizes a composite score: profitability × competitiveness.

Uses scipy.optimize for constrained optimization.
"""

import numpy as np
from scipy.optimize import minimize_scalar


def optimize_premium(net_premium, alpha=0.05, beta=0.02, gamma=0.0005,
                     competitor_premiums=None, min_margin=0.05, max_margin=0.40,
                     competitiveness_weight=0.5):
    """Find the optimal gross premium markup over net premium.

    Parameters:
        net_premium: pure risk premium (actuarial fair price)
        alpha, beta, gamma: expense parameters
        competitor_premiums: list of competitor prices for similar product
        min_margin, max_margin: profit margin bounds
        competitiveness_weight: 0 = pure profit, 1 = pure market share

    Returns:
        dict with optimal premium, margin, profit_score, market_score, composite
    """
    if competitor_premiums is None:
        competitor_premiums = []

    expense_load = net_premium * (alpha + gamma) / (1 - beta)
    cost_base = net_premium + expense_load

    def composite_score(margin):
        """Score to maximize: balance profit vs competitiveness."""
        gross = cost_base / (1 - margin)
        profit = gross - cost_base
        profit_score = profit / cost_base

        if not competitor_premiums:
            market_score = 1.0
        else:
            median_comp = np.median(competitor_premiums)
            market_score = min(2.0, median_comp / max(gross, 1))

        return -(profit_score * (1 - competitiveness_weight) +
                 market_score * competitiveness_weight)

    result = minimize_scalar(
        composite_score,
        bounds=(min_margin, max_margin),
        method='bounded',
    )

    opt_margin = result.x
    opt_gross = cost_base / (1 - opt_margin)
    opt_profit = opt_gross - cost_base

    return {
        'optimal_premium': round(opt_gross, 2),
        'optimal_margin': round(opt_margin * 100, 1),
        'cost_base': round(cost_base, 2),
        'profit_per_policy': round(opt_profit, 2),
        'profit_score': round(opt_profit / cost_base, 4),
        'price_vs_median': round(opt_gross / np.median(competitor_premiums), 2) if competitor_premiums else 1.0,
    }


def compare_scenarios(net_premium, competitor_premiums, alpha=0.05, beta=0.02, gamma=0.0005):
    """Compare different pricing strategies side-by-side."""
    results = []

    # Conservative (max margin)
    cons = optimize_premium(net_premium, alpha, beta, gamma, competitor_premiums,
                            min_margin=0.15, max_margin=0.40, competitiveness_weight=0.2)
    cons['label'] = '保守定价'
    results.append(cons)

    # Balanced
    bal = optimize_premium(net_premium, alpha, beta, gamma, competitor_premiums,
                           min_margin=0.05, max_margin=0.30, competitiveness_weight=0.5)
    bal['label'] = '均衡定价'
    results.append(bal)

    # Aggressive
    agg = optimize_premium(net_premium, alpha, beta, gamma, competitor_premiums,
                           min_margin=0.02, max_margin=0.20, competitiveness_weight=0.8)
    agg['label'] = '激进定价'
    results.append(agg)

    return results


def optimal_vs_competitors(net_premium, competitors, alpha=0.05, beta=0.02, gamma=0.0005):
    """Generate a price positioning analysis vs each competitor."""
    opt = optimize_premium(net_premium, alpha, beta, gamma, competitors)
    analysis = []
    for i, comp_price in enumerate(competitors):
        diff_pct = (opt['optimal_premium'] - comp_price) / comp_price * 100
        analysis.append({
            'competitor': f'Competitor {i+1}',
            'their_price': comp_price,
            'our_price': opt['optimal_premium'],
            'diff_pct': round(diff_pct, 1),
            'position': 'below' if diff_pct < -2 else ('above' if diff_pct > 2 else 'parity'),
        })
    analysis.sort(key=lambda x: x['their_price'])
    return analysis
