# Multi-Product Expansion Design

## Summary

扩展寿险计算器从单一"定期寿险"到四种产品：定期寿险、终身寿险、生存年金、两全保险。扩展现有 premium.py 和 reserve.py，CLI 和 Web 均支持产品切换。

## Products

| 产品 | 英文 | 核心公式 |
|------|------|---------|
| 定期寿险 | Term Life | Ax:n⌉ × S, äx:n⌉ |
| 终身寿险 | Whole Life | Ax × S, äx |
| 生存年金 | Life Annuity | äx:n⌉ × R (年领金额) |
| 两全保险 | Endowment | Ax:n⌉(endow) = Ax:n⌉(term) + v^n × npx |

## New Functions

### premium.py additions

- `whole_life_single_premium(lt, age, sum_insured, rate)`
- `whole_life_annual_premium(lt, age, sum_insured, rate)`
- `annuity_due_whole_life(lt, age, rate)` — äx without term limit
- `annuity_price(lt, age, annual_payment, term, rate, defer=0)` — purchase price of annuity
- `endowment_single_premium(lt, age, sum_insured, term, rate)`
- `endowment_annual_premium(lt, age, sum_insured, term, rate)`
- `pure_endowment(lt, age, term, rate)` — v^n × npx

### reserve.py additions

- `whole_life_reserve_table(lt, age, sum_insured, rate)`
- `endowment_reserve_table(lt, age, sum_insured, term, rate)`

### app.py changes

- Sidebar: `st.selectbox('产品类型', [...])` at top
- Parameter panel adapts: annuity shows "年领金额", whole life hides "期限"
- Calculation dispatches to correct product functions

### cli.py changes

- Add `--product` argument: choices term/whole_life/annuity/endowment, default term
- Dispatch calculation based on product

## Not in Scope

- Deferred annuities (beyond defer parameter)
- Variable/equity-linked products
- Gross premium with expenses
- Multiple premium payment frequencies (only annual)

## Testing

Add ~15 new tests covering each new product's core formulas and edge cases.
