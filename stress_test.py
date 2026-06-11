"""Stress Testing — scenario-based premium & reserve shock analysis."""
from mortality import build_life_table
from premium import (
    annual_premium, whole_life_annual_premium, endowment_annual_premium,
    gross_annual_premium
)
from reserve import reserve_table, whole_life_reserve_table, endowment_reserve_table

SCENARIOS = {
    "mortality_50": {
        "label_zh": "死亡率 +50%", "label_en": "Mortality +50%",
        "mortality_mult": 1.5, "rate_adj": 0.0, "expense_mult": 1.0,
        "desc_zh": "大流行病 · 战争 · 自然灾害", "desc_en": "Pandemic · War · Natural disaster",
    },
    "lapse_2x": {
        "label_zh": "退保率 ×2", "label_en": "Lapse Rate ×2",
        "mortality_mult": 1.0, "rate_adj": 0.0, "expense_mult": 1.0,
        "desc_zh": "经济危机 · 大规模失业", "desc_en": "Economic crisis · Mass unemployment",
        "is_lapse": True,
    },
    "rate_minus_2": {
        "label_zh": "利率 −2%", "label_en": "Interest Rate −2%",
        "mortality_mult": 1.0, "rate_adj": -0.02, "expense_mult": 1.0,
        "desc_zh": "央行降息 · 资产泡沫破裂", "desc_en": "Rate cut · Asset bubble burst",
    },
    "expense_30": {
        "label_zh": "费用率 +30%", "label_en": "Expense +30%",
        "mortality_mult": 1.0, "rate_adj": 0.0, "expense_mult": 1.3,
        "desc_zh": "通胀 · 运营成本飙升", "desc_en": "Inflation · Operating cost surge",
    },
    "combined": {
        "label_zh": "组合冲击", "label_en": "Combined Shock",
        "mortality_mult": 1.3, "rate_adj": -0.015, "expense_mult": 1.2,
        "desc_zh": "多因素同时恶化 · 1/200年事件", "desc_en": "Multi-factor · 1-in-200 year event",
    },
}


def _build_lt(df, table_col: str, gender: str, risk: float = 1.0):
    """Build a life table DataFrame, optionally applying a risk multiplier to qx."""
    # CLT uses gender, AM92 uses column name directly
    col = gender if table_col == 'clt' else table_col
    lt = build_life_table(df, col, risk_factor=risk)
    return lt


def stress_premium_table(age: int, sum_assured: float, rate: float, term: int,
                         product: str, table_path: str, table_col: str,
                         gender: str = 'M',
                         alpha: float = 0.03, beta: float = 0.02,
                         gamma: float = 0.001) -> dict:
    """Calculate gross premium under base + all stress scenarios."""
    import pandas as pd

    df = pd.read_csv(table_path)

    def calc_gross(risk_mult: float, adj_rate: float, exp_mult: float) -> float:
        lt = _build_lt(df, table_col, gender, risk_mult)
        r = max(0.005, adj_rate)

        if product == "term":
            net = annual_premium(lt, age, sum_assured, term, r)
        elif product == "whole_life":
            net = whole_life_annual_premium(lt, age, sum_assured, r)
        elif product == "endowment":
            net = endowment_annual_premium(lt, age, sum_assured, term, r)
        else:
            net = annual_premium(lt, age, sum_assured, term, r)

        a = alpha * exp_mult
        b = beta * exp_mult
        g = gamma * exp_mult
        gross = (net + a * sum_assured + g * sum_assured / 1000) / max(0.01, 1.0 - b)
        return gross, net

    base_gross, base_net = calc_gross(1.0, rate, 1.0)
    results = {"base": {"gross": base_gross, "net": base_net, "label_zh": "基准", "label_en": "Base"}}

    for key, sc in SCENARIOS.items():
        risk = sc.get("mortality_mult", 1.0)
        adj = rate + sc.get("rate_adj", 0.0)
        exp = sc.get("expense_mult", 1.0)
        gross, net = calc_gross(risk, adj, exp)
        results[key] = {
            "gross": gross, "net": net,
            "label_zh": sc["label_zh"], "label_en": sc["label_en"],
            "desc_zh": sc.get("desc_zh", ""), "desc_en": sc.get("desc_en", ""),
            "delta_pct": (gross - base_gross) / base_gross * 100 if base_gross else 0,
        }

    return results


def stress_reserve_table(age: int, sum_assured: float, rate: float, term: int,
                         product: str, table_path: str, table_col: str,
                         gender: str = 'M') -> dict:
    """Compare reserves: base vs combined shock."""
    import pandas as pd
    df = pd.read_csv(table_path)

    def get_reserves(risk: float, adj_rate: float) -> list:
        lt = _build_lt(df, table_col, gender, risk)
        r = max(0.005, adj_rate)
        if product == "term":
            raw = reserve_table(lt, age, sum_assured, term, r)
        elif product == "whole_life":
            raw = whole_life_reserve_table(lt, age, sum_assured, r)
        elif product == "endowment":
            raw = endowment_reserve_table(lt, age, sum_assured, term, r)
        else:
            raw = reserve_table(lt, age, sum_assured, term, r)
        # Extract reserve values from (year, reserve) tuples
        return [v for _, v in raw]

    base = get_reserves(1.0, rate)
    sc = SCENARIOS["combined"]
    stressed = get_reserves(sc["mortality_mult"], max(0.005, rate + sc["rate_adj"]))

    return {"base": base, "stressed": stressed, "n": min(len(base), len(stressed))}
