# Multi-Product Expansion — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the life insurance calculator from term-only to four products: Term Life, Whole Life, Life Annuity, and Endowment.

**Architecture:** Extend existing premium.py and reserve.py with new functions per product. CLI and Web UI gain a product selector. All new functions follow TDD — test first, then implement.

**Tech Stack:** Python 3.14, numpy, pandas, pytest (unchanged)

---

### Task 1: Whole Life Insurance — premium.py + tests

**Files:**
- Modify: `/Users/linjiaye/Desktop/life-insurance/premium.py` (append new functions)
- Modify: `/Users/linjiaye/Desktop/life-insurance/test_premium.py` (append TestWholeLife class)

- [ ] **Step 1: Write failing tests**

Append to test_premium.py:

```python
class TestWholeLife:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.df = load_table(DATA_PATH)
        self.lt_m = build_life_table(self.df, 'M')

    def test_whole_life_sp_positive(self):
        from premium import whole_life_single_premium
        sp = whole_life_single_premium(self.lt_m, 30, 1000000, 0.035)
        assert sp > 0
        # Whole life > term-20 at same age
        sp_term = single_premium(self.lt_m, 30, 1000000, 20, 0.035)
        assert sp > sp_term

    def test_whole_life_sp_increases_with_age(self):
        from premium import whole_life_single_premium
        sp30 = whole_life_single_premium(self.lt_m, 30, 1000000, 0.035)
        sp50 = whole_life_single_premium(self.lt_m, 50, 1000000, 0.035)
        assert sp50 > sp30

    def test_whole_life_ap_consistency(self):
        from premium import whole_life_single_premium, whole_life_annual_premium, annuity_due_whole_life
        sp = whole_life_single_premium(self.lt_m, 30, 1000000, 0.035)
        ap = whole_life_annual_premium(self.lt_m, 30, 1000000, 0.035)
        a = annuity_due_whole_life(self.lt_m, 30, 0.035)
        assert sp == pytest.approx(ap * a, rel=1e-5)

    def test_whole_life_annuity_due_decreases_with_age(self):
        from premium import annuity_due_whole_life
        a30 = annuity_due_whole_life(self.lt_m, 30, 0.035)
        a60 = annuity_due_whole_life(self.lt_m, 60, 0.035)
        assert a60 < a30
```

- [ ] **Step 2: Run — expect FAIL (4 import errors)**

```bash
cd /Users/linjiaye/Desktop/life-insurance && python3 -m pytest test_premium.py -v 2>&1 | tail -8
```

- [ ] **Step 3: Implement 3 functions in premium.py**

Append to premium.py:

```python
def annuity_due_whole_life(life_table, age, rate):
    """Compute a_x — present value of whole-life annuity-due.
    a_x = sum(t=0 to 105-x-1) v^t * t_p_x
    """
    v = 1 / (1 + rate)
    lt = life_table
    x_idx = lt[lt['age'] == age].index[0]
    lx = lt.loc[x_idx, 'lx']
    max_t = len(lt) - x_idx - 1  # until limit age
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
```

- [ ] **Step 4: Run tests — expect 4 new tests pass + 10 old = 14 passed**

```bash
cd /Users/linjiaye/Desktop/life-insurance && python3 -m pytest test_premium.py -v 2>&1 | tail -5
```

- [ ] **Step 5: Commit**

```bash
cd /Users/linjiaye/Desktop/life-insurance && git add premium.py test_premium.py && git commit -m "feat: add whole life insurance premium functions"
```

---

### Task 2: Endowment Insurance — premium.py + tests

**Files:**
- Modify: `/Users/linjiaye/Desktop/life-insurance/premium.py` (append 3 functions)
- Modify: `/Users/linjiaye/Desktop/life-insurance/test_premium.py` (append TestEndowment class)

- [ ] **Step 1: Write failing tests**

Append to test_premium.py:

```python
class TestEndowment:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.df = load_table(DATA_PATH)
        self.lt_m = build_life_table(self.df, 'M')

    def test_endowment_sp_greater_than_term(self):
        from premium import endowment_single_premium, single_premium
        sp_term = single_premium(self.lt_m, 30, 1000000, 20, 0.035)
        sp_endow = endowment_single_premium(self.lt_m, 30, 1000000, 20, 0.035)
        assert sp_endow > sp_term  # endowment = term + pure endowment

    def test_pure_endowment_between_0_and_1(self):
        from premium import pure_endowment
        pe = pure_endowment(self.lt_m, 30, 20, 0.035)
        assert 0 < pe < 1

    def test_endowment_ap_consistency(self):
        from premium import endowment_single_premium, endowment_annual_premium, annuity_due
        sp = endowment_single_premium(self.lt_m, 30, 1000000, 20, 0.035)
        ap = endowment_annual_premium(self.lt_m, 30, 1000000, 20, 0.035)
        a = annuity_due(self.lt_m, 30, 20, 0.035)
        assert sp == pytest.approx(ap * a, rel=1e-5)

    def test_endowment_reserve_at_maturity_equals_sum_insured(self):
        from premium import endowment_annual_premium
        # We test this indirectly: at maturity, endowment pays sum_insured
        # This is verified in reserve tests later
        ap = endowment_annual_premium(self.lt_m, 30, 1000000, 20, 0.035)
        assert ap > 0
```

- [ ] **Step 2: Run — expect FAIL**

```bash
cd /Users/linjiaye/Desktop/life-insurance && python3 -m pytest test_premium.py::TestEndowment -v 2>&1 | tail -5
```

- [ ] **Step 3: Implement 3 functions in premium.py**

Append to premium.py:

```python
def pure_endowment(life_table, age, term, rate):
    """Compute nEx = v^n * npx — present value of 1 paid at end of n years if alive."""
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
    A_x:n(endow) = A_x:n(term) + nEx
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
```

- [ ] **Step 4: Run tests — expect 4 new + 14 old = 18 passed**

```bash
cd /Users/linjiaye/Desktop/life-insurance && python3 -m pytest test_premium.py -v 2>&1 | tail -3
```

- [ ] **Step 5: Commit**

```bash
cd /Users/linjiaye/Desktop/life-insurance && git add premium.py test_premium.py && git commit -m "feat: add endowment insurance premium functions"
```

---

### Task 3: Life Annuity — premium.py + tests

**Files:**
- Modify: `/Users/linjiaye/Desktop/life-insurance/premium.py` (append 1 function)
- Modify: `/Users/linjiaye/Desktop/life-insurance/test_premium.py` (append TestAnnuity class)

- [ ] **Step 1: Write failing tests**

Append to test_premium.py:

```python
class TestAnnuity:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.df = load_table(DATA_PATH)
        self.lt_m = build_life_table(self.df, 'M')

    def test_annuity_price_positive(self):
        from premium import annuity_price
        price = annuity_price(self.lt_m, 30, 50000, 20, 0.035)
        assert price > 0

    def test_annuity_price_equals_annuity_due_times_payment(self):
        from premium import annuity_price, annuity_due
        payment = 50000
        price = annuity_price(self.lt_m, 30, payment, 20, 0.035)
        a = annuity_due(self.lt_m, 30, 20, 0.035)
        expected = payment * a
        assert price == pytest.approx(expected, rel=1e-5)

    def test_annuity_price_decreases_with_age(self):
        from premium import annuity_price
        p30 = annuity_price(self.lt_m, 30, 50000, 10, 0.035)
        p60 = annuity_price(self.lt_m, 60, 50000, 10, 0.035)
        assert p60 < p30  # older = fewer expected payments = cheaper for insurer
```

- [ ] **Step 2: Run — expect FAIL**

```bash
cd /Users/linjiaye/Desktop/life-insurance && python3 -m pytest test_premium.py::TestAnnuity -v 2>&1 | tail -5
```

- [ ] **Step 3: Implement annuity_price in premium.py**

Append to premium.py:

```python
def annuity_price(life_table, age, annual_payment, term, rate, defer=0):
    """Compute lump-sum purchase price of a life annuity.
    
    Pays `annual_payment` at the beginning of each year while (x) is alive,
    for `term` years (or whole-life if term reaches limit age).
    
    Price = annual_payment * a_x:n (with defer period if applicable)
    """
    if defer > 0:
        v = 1 / (1 + rate)
        lt = life_table
        x_idx = lt[lt['age'] == age].index[0]
        lx = lt.loc[x_idx, 'lx']
        lx_def = lt.loc[x_idx + defer, 'lx'] if x_idx + defer < len(lt) else 0
        def_px = lx_def / lx if lx > 0 else 0
        a_deferred = annuity_due(life_table, age + defer, term, rate)
        return annual_payment * (v ** defer) * def_px * a_deferred
    a = annuity_due(life_table, age, term, rate)
    return annual_payment * a
```

- [ ] **Step 4: Run tests — expect 3 new + 18 old = 21 passed for premium**

```bash
cd /Users/linjiaye/Desktop/life-insurance && python3 -m pytest test_premium.py -v 2>&1 | tail -3
```

- [ ] **Step 5: Commit**

```bash
cd /Users/linjiaye/Desktop/life-insurance && git add premium.py test_premium.py && git commit -m "feat: add life annuity pricing function"
```

---

### Task 4: Whole Life + Endowment Reserves — reserve.py + tests

**Files:**
- Modify: `/Users/linjiaye/Desktop/life-insurance/reserve.py` (append 2 functions)
- Modify: `/Users/linjiaye/Desktop/life-insurance/test_reserve.py` (append 2 test classes)

- [ ] **Step 1: Write failing tests**

Append to test_reserve.py:

```python
class TestWholeLifeReserve:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.df = load_table(DATA_PATH)
        self.lt_m = build_life_table(self.df, 'M')

    def test_wl_reserve_starts_at_zero(self):
        from reserve import whole_life_reserve_table
        tbl = whole_life_reserve_table(self.lt_m, 30, 1000000, 0.035)
        assert tbl[0][1] == pytest.approx(0.0, abs=1e-6)

    def test_wl_reserve_increases_over_time(self):
        from reserve import whole_life_reserve_table
        tbl = whole_life_reserve_table(self.lt_m, 30, 1000000, 0.035)
        # Whole life reserves increase monotonically toward sum_insured
        r10 = [v for y, v in tbl if y == 10][0]
        r30 = [v for y, v in tbl if y == 30][0]
        assert r30 > r10


class TestEndowmentReserve:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.df = load_table(DATA_PATH)
        self.lt_m = build_life_table(self.df, 'M')

    def test_endow_reserve_ends_at_sum_insured(self):
        from reserve import endowment_reserve_table
        tbl = endowment_reserve_table(self.lt_m, 30, 1000000, 20, 0.035)
        assert tbl[0][1] == pytest.approx(0.0, abs=1e-6)
        assert tbl[-1][1] == pytest.approx(1000000, rel=1e-5)
        # At maturity, reserve = sum_insured (unlike term where it = 0)
```

- [ ] **Step 2: Run — expect FAIL**

```bash
cd /Users/linjiaye/Desktop/life-insurance && python3 -m pytest test_reserve.py -v -k "WholeLife or Endowment" 2>&1 | tail -5
```

- [ ] **Step 3: Implement 2 functions in reserve.py**

Append to reserve.py:

```python
def whole_life_reserve_table(life_table, age, sum_insured, rate):
    """Compute reserves for whole life insurance (all policy years).
    kV = S * A_{x+k} - P * a_{x+k}
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


def endowment_reserve_table(life_table, age, sum_insured, term, rate):
    """Compute reserves for endowment insurance.
    kV = S * A_{x+k:n-k}(endow) - P * a_{x+k:n-k}
    At maturity (k=n): reserve = sum_insured
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
```

Note: These functions need `whole_life_single_premium`, `whole_life_annual_premium`, `annuity_due_whole_life` from premium.py. Add this import at the top of reserve.py if not already using `from premium import ...`:

```python
from premium import (single_premium, annual_premium, annuity_due,
                     whole_life_single_premium, whole_life_annual_premium, annuity_due_whole_life)
```

- [ ] **Step 4: Run tests — expect all reserve tests pass**

```bash
cd /Users/linjiaye/Desktop/life-insurance && python3 -m pytest test_reserve.py -v 2>&1 | tail -3
```

- [ ] **Step 5: Commit**

```bash
cd /Users/linjiaye/Desktop/life-insurance && git add reserve.py test_reserve.py && git commit -m "feat: add whole life and endowment reserve functions"
```

---

### Task 5: Update CLI with --product flag

**Files:**
- Modify: `/Users/linjiaye/Desktop/life-insurance/cli.py`

- [ ] **Step 1: Add --product to argument parser**

Read cli.py. Add to `parse_args()`:

```python
p.add_argument('--product', choices=['term', 'whole_life', 'annuity', 'endowment'],
               default='term', help='产品类型 (默认: term)')
```

And add product-specific dispatch in `main()`. After parsing args, add:

```python
if args.product == 'whole_life':
    sp = whole_life_single_premium(lt, args.age, args.sum, args.rate)
    ap = whole_life_annual_premium(lt, args.age, args.sum, args.rate)
    reserves = whole_life_reserve_table(lt, args.age, args.sum, args.rate)
elif args.product == 'annuity':
    sp = annuity_price(lt, args.age, args.sum, args.term, args.rate)
    ap = None  # annuities don't have annual premium in same sense
    reserves = []
elif args.product == 'endowment':
    sp = endowment_single_premium(lt, args.age, args.sum, args.term, args.rate)
    ap = endowment_annual_premium(lt, args.age, args.sum, args.term, args.rate)
    reserves = endowment_reserve_table(lt, args.age, args.sum, args.term, args.rate)
else:  # term (default)
    sp = single_premium(lt, args.age, args.sum, args.term, args.rate)
    ap = annual_premium(lt, args.age, args.sum, args.term, args.rate)
    reserves = reserve_table(lt, args.age, args.sum, args.term, args.rate)
```

Update the output section to handle annuity case (ap may be None).

- [ ] **Step 2: Test CLI with each product**

```bash
python3 cli.py --age 30 --sum 1000000 --term 20 --product whole_life 2>&1 | head -10
python3 cli.py --age 30 --sum 50000 --term 20 --product annuity 2>&1 | head -10
python3 cli.py --age 30 --sum 1000000 --term 20 --product endowment 2>&1 | head -10
```

- [ ] **Step 3: Commit**

```bash
cd /Users/linjiaye/Desktop/life-insurance && git add cli.py && git commit -m "feat: add --product flag to CLI for multi-product support"
```

---

### Task 6: Update Web UI with product selector

**Files:**
- Modify: `/Users/linjiaye/Desktop/life-insurance/app.py`

- [ ] **Step 1: Add i18n strings for new products**

Add to both `zh` and `en` dictionaries in T:

```python
# zh additions
'product_label': '产品类型',
'product_term': '定期寿险',
'product_whole_life': '终身寿险',
'product_annuity': '生存年金',
'product_endowment': '两全保险',
'annual_payment': '年领金额（元）',
# en additions
'product_label': 'Product Type',
'product_term': 'Term Life',
'product_whole_life': 'Whole Life',
'product_annuity': 'Life Annuity',
'product_endowment': 'Endowment',
'annual_payment': 'Annual Payment (¥)',
```

- [ ] **Step 2: Add product selector to sidebar (top, after language)**

```python
product = st.sidebar.selectbox(
    t('product_label'),
    [t('product_term'), t('product_whole_life'), t('product_annuity'), t('product_endowment')],
)
```

- [ ] **Step 3: Make parameters adaptive**

```python
# Only show term slider for term, annuity, endowment (not whole life)
if product != t('product_whole_life'):
    term = st.sidebar.slider(t('term'), ...)
else:
    term = 105 - age  # implicit for whole life

# Annuity: "保险金额" → "年领金额"
if product == t('product_annuity'):
    sum_insured = st.sidebar.number_input(t('annual_payment'), ...)
else:
    sum_insured = st.sidebar.number_input(t('sum_insured'), ...)
```

- [ ] **Step 4: Dispatch calculation by product**

```python
if product == t('product_whole_life'):
    sp = whole_life_single_premium(lt, age, sum_insured, rate)
    ap = whole_life_annual_premium(lt, age, sum_insured, rate)
    reserves = whole_life_reserve_table(lt, age, sum_insured, rate)
elif product == t('product_annuity'):
    # For annuities: "premium" = price, no annual premium
    sp = annuity_price(lt, age, sum_insured, term, rate)
    ap = None
    reserves = []
elif product == t('product_endowment'):
    sp = endowment_single_premium(lt, age, sum_insured, term, rate)
    ap = endowment_annual_premium(lt, age, sum_insured, term, rate)
    reserves = endowment_reserve_table(lt, age, sum_insured, term, rate)
else:  # term
    sp = single_premium(lt, age, sum_insured, term, rate)
    ap = annual_premium(lt, age, sum_insured, term, rate)
    reserves = reserve_table(lt, age, sum_insured, term, rate)
```

- [ ] **Step 5: Handle annuity display (no annual premium column, no reserve chart)**

```python
if product == t('product_annuity'):
    st.metric(t('single_premium'), f'¥{sp:,.0f}',
              help='趸缴购买价格 / Lump-sum purchase price')
    # No second column, no reserve chart/table for annuity
else:
    col1, col2 = st.columns(2)
    with col1:
        st.metric(t('single_premium'), f'¥{sp:,.0f}', help=t('single_premium_help'))
    with col2:
        st.metric(t('annual_premium'), f'¥{ap:,.0f}', help=t('annual_premium_help'))
    # Reserve chart + table ...
```

- [ ] **Step 6: Re-verify Streamlit loads**

```bash
python3 -m pytest -q
curl -s http://localhost:8501 | head -1
```

- [ ] **Step 7: Commit**

```bash
cd /Users/linjiaye/Desktop/life-insurance && git add app.py && git commit -m "feat: add product selector to Web UI"
```

---

### Task 7: End-to-End Verification

- [ ] **Step 1: All tests pass**

```bash
cd /Users/linjiaye/Desktop/life-insurance && python3 -m pytest -v
```
Expected: ~30+ tests all pass

- [ ] **Step 2: CLI all products**

```bash
python3 cli.py --age 30 --sum 1000000 --term 20 --product term | head -5
python3 cli.py --age 30 --sum 1000000 --term 20 --product whole_life | head -5
python3 cli.py --age 30 --sum 50000 --term 20 --product annuity | head -5
python3 cli.py --age 30 --sum 1000000 --term 20 --product endowment | head -5
```

- [ ] **Step 3: Web UI — verify product switcher**
Open http://localhost:8501, cycle through all 4 products, verify:
- Term: shows term slider, both premium cards, reserve chart
- Whole Life: hides term slider, both premium cards, reserve increases to sum_insured
- Annuity: shows term slider, "年领金额" label, one premium card, no reserve section
- Endowment: shows term slider, both premium cards, reserve chart ending at sum_insured

- [ ] **Step 4: Language toggle still works with new products**
Switch to English — all product names and labels translate correctly.
