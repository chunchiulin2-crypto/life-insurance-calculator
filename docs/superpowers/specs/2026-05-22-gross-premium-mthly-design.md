# Gross Premium & m-thly Payment Frequency Design

## Summary

从纯保费升级到毛保费（α/β/γ 费用三分法），加入月缴/季缴/半年缴/年缴精确转换，展示费用构成。

## Gross Premium Formula

```
G × äx:n⌉ = Ax:n⌉ × S + α × S + β × G × äx:n⌉ + γ × S × äx:n⌉

→ G = (Ax:n⌉ × S + α × S + γ × S × äx:n⌉) / ((1 − β) × äx:n⌉)
```

| Parameter | Meaning | Typical | Applied To | When |
|-----------|---------|---------|-----------|------|
| α | 获取费用 (Acquisition) | 3-8% | 保额 S | 首年一次性 |
| β | 维持费用 (Maintenance) | 1-3% | 毛保费 G | 每年 |
| γ | 收费费用 (Collection) | 0.3-1‰ | 保额 S | 每次缴费 |

## m-thly Payment Conversion

UDD assumption:

```
ä(m)x:n⌉ = α(m) × äx:n⌉ − β(m) × (1 − nEx)

where:
  i(m) = m × ((1+i)^(1/m) − 1)
  d(m) = m × (1 − (1−d)^(1/m))
  α(m) = i × d / (i(m) × d(m))
  β(m) = (i − i(m)) / (i(m) × d(m))
```

m-thly gross premium: P(m) = G / m

## New Functions (premium.py)

- `m_thly_annuity_factor(life_table, age, term, rate, m)` → (α(m), β(m))
- `m_thly_annuity_due(life_table, age, term, rate, m)` → ä(m)x:n⌉
- `gross_single_premium(life_table, age, sum_insured, term, rate, alpha, beta, gamma, claim_accel)` → G_SP
- `gross_annual_premium(life_table, age, sum_insured, term, rate, alpha, beta, gamma, claim_accel)` → G_AP
- `periodic_premium(gross_annual, m)` → P(m), 每期缴费金额

## UI Changes

Each product page gains:
- α/β/γ sliders in sidebar (with defaults and tooltips)
- Payment frequency selector: 月缴/季缴/半年缴/年缴
- Cost breakdown display: 总保费 vs 纯风险保费 vs 费用附加

## CLI Changes

```
--alpha 0.05 --beta 0.02 --gamma 0.0005 --freq monthly
```

## Testing

Add tests for:
- m_thly factor correctness (known values at m=1,12)
- Gross premium > net premium (always)
- Periodicity: P(12) × 12 > P(1) (monthly total > annual due to interest)
- α/β/γ = 0 → G = net premium (degenerate case)
