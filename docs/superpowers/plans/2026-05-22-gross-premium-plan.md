# Gross Premium & m-thly Payments — Implementation Plan

> **For agentic workers:** Use subagent-driven-development or inline execution. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add gross premium (α/β/γ expenses) and m-thly payment frequency to the life insurance calculator.

**Architecture:** New functions in premium.py for expense loading and m-thly conversion. Each product page gets expense/frequency controls. CLI gets matching flags.

**Tech Stack:** Python 3.14, numpy, existing premium/reserve modules.

---

### Task 1: m-thly conversion + gross premium functions (premium.py + tests)

**Files:**
- Modify: `/Users/linjiaye/Desktop/life-insurance/premium.py` (append 5 functions)
- Modify: `/Users/linjiaye/Desktop/life-insurance/test_premium.py` (append TestMthly + TestGross classes)

- [ ] **Step 1: Write failing tests**

Append to test_premium.py:

```python
class TestMthly:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.df = load_table(DATA_PATH)
        self.lt_m = build_life_table(self.df, 'M')

    def test_m1_equals_annual(self):
        from premium import m_thly_annuity_due
        a1 = m_thly_annuity_due(self.lt_m, 30, 20, 0.035, 1)
        a = annuity_due(self.lt_m, 30, 20, 0.035)
        assert a1 == pytest.approx(a, rel=1e-6)

    def test_m12_greater_than_annual(self):
        from premium import m_thly_annuity_due
        a12 = m_thly_annuity_due(self.lt_m, 30, 20, 0.035, 12)
        a = annuity_due(self.lt_m, 30, 20, 0.035)
        assert a12 > a  # more frequent = higher PV (payments start sooner)

    def test_m12_positive(self):
        from premium import m_thly_annuity_due
        a12 = m_thly_annuity_due(self.lt_m, 30, 20, 0.035, 12)
        assert a12 > 0


class TestGrossPremium:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.df = load_table(DATA_PATH)
        self.lt_m = build_life_table(self.df, 'M')

    def test_gross_equals_net_when_expenses_zero(self):
        from premium import gross_annual_premium, annual_premium
        gap = gross_annual_premium(self.lt_m, 30, 1000000, 20, 0.035, alpha=0, beta=0, gamma=0)
        ap = annual_premium(self.lt_m, 30, 1000000, 20, 0.035)
        assert gap == pytest.approx(ap, rel=1e-5)

    def test_gross_greater_than_net(self):
        from premium import gross_annual_premium, annual_premium
        gap = gross_annual_premium(self.lt_m, 30, 1000000, 20, 0.035, alpha=0.05, beta=0.02, gamma=0.0005)
        ap = annual_premium(self.lt_m, 30, 1000000, 20, 0.035)
        assert gap > ap

    def test_periodic_premium(self):
        from premium import gross_annual_premium, periodic_premium
        gap = gross_annual_premium(self.lt_m, 30, 1000000, 20, 0.035, alpha=0.05, beta=0.02, gamma=0.0005)
        monthly = periodic_premium(gap, 12)
        yearly = periodic_premium(gap, 1)
        assert monthly * 12 > yearly  # monthly total slightly > annual
        assert pytest.approx(monthly, rel=0.01) == gap / 12
```

- [ ] **Step 2: Run — expect FAIL**

```bash
cd /Users/linjiaye/Desktop/life-insurance && python3 -m pytest test_premium.py -v -k "Mthly or Gross" 2>&1 | tail -5
```

- [ ] **Step 3: Implement 5 functions in premium.py**

Append to premium.py:

```python
# ---- m-thly Payment Frequency ----


def m_thly_annuity_factor(rate, m):
    """Compute α(m) and β(m) for m-thly annuity-due conversion (UDD assumption).

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
    """Compute ä(m)x:n⌉ — m-thly annuity-due.

    Payments made m times per year at beginning of each 1/m-th period.
    Uses UDD assumption for fractional-age survival.
    """
    from premium import annuity_due, pure_endowment
    a_annual = annuity_due(life_table, age, term, rate)
    alpha, beta = m_thly_annuity_factor(rate, m)
    pe = pure_endowment(life_table, age, term, rate)
    return alpha * a_annual - beta * (1 - pe)


# ---- Gross Premium (α/β/γ expense loading) ----


def gross_single_premium(life_table, age, sum_insured, term, rate,
                         alpha=0.0, beta=0.0, gamma=0.0, claim_accel=False):
    """Compute gross single premium with expense loading.

    G_SP = (Ax:n⌉ × S + α × S) / (1 − β)
           + γ × S × äx:n⌉ / (1 − β)

    Simplified: expense PV loaded onto net single premium.
    """
    from premium import single_premium, annuity_due
    net_sp = single_premium(life_table, age, sum_insured, term, rate, claim_accel)
    a = annuity_due(life_table, age, term, rate)
    # G × (1 − β) = net_sp + α × S + γ × S × a
    expense_pv = alpha * sum_insured + gamma * sum_insured * a
    if beta >= 1.0:
        return float('inf')
    return (net_sp + expense_pv) / (1 - beta)


def gross_annual_premium(life_table, age, sum_insured, term, rate,
                         alpha=0.0, beta=0.0, gamma=0.0, claim_accel=False):
    """Compute gross level annual premium with expense loading.

    G = (Ax:n⌉ × S + α × S + γ × S × äx:n⌉) / ((1 − β) × äx:n⌉)
    """
    from premium import annuity_due
    gsp = gross_single_premium(life_table, age, sum_insured, term, rate,
                                alpha, beta, gamma, claim_accel)
    a = annuity_due(life_table, age, term, rate)
    if a == 0:
        return 0
    return gsp / a


def periodic_premium(gross_annual, m):
    """Convert gross annual premium to m-thly periodic payment.

    P(m) = G / m  (approximate; for more precision use m_thly_annuity_due)
    """
    return gross_annual / m
```

- [ ] **Step 4: Run — expect 6 new + 30 old = 36 tests (premium only)**

```bash
cd /Users/linjiaye/Desktop/life-insurance && python3 -m pytest test_premium.py -v 2>&1 | tail -3
```

- [ ] **Step 5: Commit**

```bash
git add premium.py test_premium.py && git commit -m "feat: add m-thly conversion and gross premium (α/β/γ) functions"
```

---

### Task 2: Update 4 product pages — add expense + frequency controls

**Files:**
- Modify: `/Users/linjiaye/Desktop/life-insurance/pages/1_定期寿险.py`
- Modify: `/Users/linjiaye/Desktop/life-insurance/pages/2_终身寿险.py`
- Modify: `/Users/linjiaye/Desktop/life-insurance/pages/4_两全保险.py`

(Annuity page doesn't get expense/frequency — it's a payout product)

For each of the 3 pages, add to sidebar (after payment timing, before validation):

```python
# ---- Expense Parameters ----
st.sidebar.divider()
st.sidebar.caption("费用参数 / Expense Loading")
alpha = st.sidebar.slider("α 获取费 (% × 保额)", 0.0, 15.0, 5.0, 0.5) / 100
beta  = st.sidebar.slider("β 维持费 (% × 保费)", 0.0, 10.0, 2.0, 0.5) / 100
gamma = st.sidebar.slider("γ 收费费 (‰ × 保额)", 0.0, 5.0, 0.5, 0.1) / 1000

# ---- Payment Frequency ----
freq_label = st.sidebar.radio(
    "缴费频率 / Payment Frequency",
    ["年缴", "半年缴", "季缴", "月缴"],
    horizontal=True
)
freq_map = {"年缴": 1, "半年缴": 2, "季缴": 4, "月缴": 12}
freq_m = freq_map[freq_label]
```

Replace sp/ap calculation to use gross functions:

```python
from premium import gross_annual_premium, periodic_premium

gap = gross_annual_premium(lt, age, sum_insured, term, rate,
                           alpha=alpha, beta=beta, gamma=gamma, claim_accel=claim_accel)
per_payment = periodic_premium(gap, freq_m)

# Show per-payment amount as main metric
c1.metric(f'每期保费 ({freq_label})', f'¥{per_payment:,.0f}',
          help=f'每次缴费金额 · 年毛保费 ¥{gap:,.0f}')
c2.metric(t('ap'), f'¥{gap:,.0f}', help='年缴毛保费（含费用）')
```

For English, add matching i18n keys or just use bilingual labels inline.

- [ ] **Step 2: Verify all pages import and run**

```bash
cd /Users/linjiaye/Desktop/life-insurance && python3 -m pytest -q
```

- [ ] **Step 3: Commit**

```bash
git add pages/ && git commit -m "feat: add expense (α/β/γ) and payment frequency controls to product pages"
```

---

### Task 3: Update CLI

**Files:**
- Modify: `/Users/linjiaye/Desktop/life-insurance/cli.py`

- [ ] **Step 1: Add expense and frequency args, wire up calculation**

Add args:
```python
p.add_argument('--alpha', type=float, default=0.0, help='获取费 (× 保额, 默认 0)')
p.add_argument('--beta', type=float, default=0.0, help='维持费 (× 保费, 默认 0)')
p.add_argument('--gamma', type=float, default=0.0, help='收费费 (× 保额, 默认 0)')
p.add_argument('--freq', type=int, choices=[1, 2, 4, 12], default=1,
               help='年缴费次数 (1/2/4/12, 默认 1)')
```

Replace sp/ap calculation with gross functions:

```python
from premium import gross_annual_premium, periodic_premium

gap = gross_annual_premium(lt, age, sum_insured, term, rate,
                           alpha=args.alpha, beta=args.beta, gamma=args.gamma,
                           claim_accel=ca)
sp = gap  # for display consistency
ap = periodic_premium(gap, args.freq)
```

Update output header to show frequency and expense info.

- [ ] **Step 2: Test CLI**

```bash
python3 cli.py --age 30 --sum 1000000 --term 20 --alpha 0.05 --beta 0.02 --gamma 0.0005 --freq 12 2>&1 | head -15
```

- [ ] **Step 3: Commit**

```bash
git add cli.py && git commit -m "feat: add α/β/γ and --freq flags to CLI"
```

---

### Task 4: End-to-End Verification

- [ ] **Step 1: All tests pass**

```bash
cd /Users/linjiaye/Desktop/life-insurance && python3 -m pytest -v 2>&1 | tail -3
```
Expected: 46+ passed

- [ ] **Step 2: Verify gross > net**

```bash
python3 -c "
from mortality import load_table, build_life_table
from premium import annual_premium, gross_annual_premium
df = load_table('data/clt_2010_2013.csv')
lt = build_life_table(df, 'M')
net = annual_premium(lt, 30, 1000000, 20, 0.035)
gross = gross_annual_premium(lt, 30, 1000000, 20, 0.035, alpha=0.05, beta=0.02, gamma=0.0005)
print(f'Net: ¥{net:,.0f} → Gross: ¥{gross:,.0f} (+{(gross/net-1)*100:.1f}%)')
assert gross > net, 'Gross must exceed net!'
print('PASS')
"
```

- [ ] **Step 3: Verify m=12 monthly > annual**

```bash
python3 -c "
from mortality import load_table, build_life_table
from premium import annuity_due, m_thly_annuity_due
df = load_table('data/clt_2010_2013.csv')
lt = build_life_table(df, 'M')
a1 = annuity_due(lt, 30, 20, 0.035)
a12 = m_thly_annuity_due(lt, 30, 20, 0.035, 12)
print(f'a(1)={a1:.6f}, a(12)={a12:.6f}, diff={a12-a1:.6f}')
assert a12 > a1
print('PASS')
"
```

- [ ] **Step 4: Web smoke test**

Streamlit should auto-reload. Open each product page, verify expense sliders and frequency selector appear, change values, verify premiums update.
