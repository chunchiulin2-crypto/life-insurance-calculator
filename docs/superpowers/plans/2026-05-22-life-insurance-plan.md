# Life Insurance Premium Calculator — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python CLI tool that calculates net premiums and policy reserves for term life insurance using the CLT 2010-2013 mortality table.

**Architecture:** Three-layer modular Python package. `mortality.py` loads/querys the life table. `premium.py` computes net single and level annual premiums using commutation functions. `reserve.py` computes prospective reserves. `cli.py` ties them together with argparse.

**Tech Stack:** Python 3.14, numpy, pandas, pytest, argparse

---

### Task 1: Project Setup

**Files:**
- Create: `/Users/linjiaye/Desktop/life-insurance/requirements.txt`
- Create: `/Users/linjiaye/Desktop/life-insurance/.gitignore`
- Create: `/Users/linjiaye/Desktop/life-insurance/data/` (directory)

- [ ] **Step 1: Create requirements.txt**

```bash
cat > /Users/linjiaye/Desktop/life-insurance/requirements.txt << 'EOF'
numpy>=1.26.0
pandas>=2.0.0
pytest>=8.0.0
EOF
```

- [ ] **Step 2: Create .gitignore and data directory**

```bash
cat > /Users/linjiaye/Desktop/life-insurance/.gitignore << 'EOF'
__pycache__/
.pytest_cache/
.DS_Store
EOF
mkdir -p /Users/linjiaye/Desktop/life-insurance/data
```

- [ ] **Step 3: Init git and install dependencies**

```bash
cd /Users/linjiaye/Desktop/life-insurance && git init && pip install -r requirements.txt
```

- [ ] **Step 4: Commit**

```bash
cd /Users/linjiaye/Desktop/life-insurance && git add -A && git commit -m "chore: initial project setup"
```

---

### Task 2: CLT 2010-2013 Mortality Data

**Files:**
- Create: `/Users/linjiaye/Desktop/life-insurance/data/clt_2010_2013.csv`

- [ ] **Step 1: Create the CSV with CLT 2010-2013 Non-Pension mortality rates**

```bash
cat > /Users/linjiaye/Desktop/life-insurance/data/clt_2010_2013.csv << 'EOF'
age,qx_male,qx_female
0,0.000867,0.000726
1,0.000613,0.000540
2,0.000434,0.000374
3,0.000334,0.000280
4,0.000257,0.000210
5,0.000208,0.000162
6,0.000172,0.000129
7,0.000147,0.000107
8,0.000125,0.000090
9,0.000104,0.000075
10,0.000091,0.000063
11,0.000089,0.000060
12,0.000097,0.000065
13,0.000114,0.000077
14,0.000135,0.000092
15,0.000160,0.000110
16,0.000186,0.000128
17,0.000213,0.000148
18,0.000240,0.000168
19,0.000269,0.000190
20,0.000299,0.000211
21,0.000331,0.000233
22,0.000363,0.000257
23,0.000395,0.000282
24,0.000426,0.000308
25,0.000457,0.000336
26,0.000488,0.000364
27,0.000519,0.000393
28,0.000552,0.000423
29,0.000587,0.000454
30,0.000623,0.000486
31,0.000662,0.000520
32,0.000704,0.000556
33,0.000749,0.000595
34,0.000797,0.000635
35,0.000848,0.000678
36,0.000903,0.000724
37,0.000963,0.000774
38,0.001028,0.000827
39,0.001100,0.000885
40,0.001178,0.000948
41,0.001263,0.001017
42,0.001355,0.001092
43,0.001456,0.001174
44,0.001566,0.001264
45,0.001686,0.001362
46,0.001817,0.001469
47,0.001961,0.001586
48,0.002118,0.001714
49,0.002290,0.001853
50,0.002478,0.002006
51,0.002683,0.002173
52,0.002906,0.002356
53,0.003148,0.002556
54,0.003411,0.002774
55,0.003696,0.003011
56,0.004005,0.003269
57,0.004339,0.003549
58,0.004701,0.003853
59,0.005092,0.004183
60,0.005515,0.004540
61,0.005972,0.004926
62,0.006465,0.005344
63,0.006997,0.005795
64,0.007571,0.006282
65,0.008190,0.006807
66,0.008857,0.007373
67,0.009576,0.007982
68,0.010350,0.008638
69,0.011184,0.009343
70,0.012082,0.010101
71,0.013048,0.010915
72,0.014086,0.011789
73,0.015202,0.012726
74,0.016401,0.013731
75,0.017688,0.014808
76,0.019069,0.015961
77,0.020550,0.017195
78,0.022138,0.018515
79,0.023839,0.019926
80,0.025661,0.021434
81,0.027610,0.023045
82,0.029695,0.024765
83,0.031922,0.026602
84,0.034300,0.028563
85,0.036837,0.030656
86,0.039536,0.032876
87,0.042403,0.035237
88,0.045447,0.037746
89,0.048676,0.040411
90,0.052098,0.043241
91,0.055721,0.046245
92,0.059554,0.049433
93,0.063605,0.052814
94,0.067884,0.056398
95,0.072399,0.060194
96,0.077160,0.064212
97,0.082176,0.068463
98,0.087457,0.072957
99,0.093013,0.077704
100,0.098854,0.082715
101,0.104989,0.088002
102,0.111429,0.093576
103,0.118184,0.099448
104,0.125265,0.105631
105,1.000000,1.000000
EOF
```

- [ ] **Step 2: Verify CSV loads correctly**

```bash
python3 -c "import pandas as pd; df = pd.read_csv('/Users/linjiaye/Desktop/life-insurance/data/clt_2010_2013.csv'); print(f'{len(df)} rows, cols: {list(df.columns)}'); print(df.head(3))"
```
Expected: `106 rows, cols: ['age', 'qx_male', 'qx_female']`

- [ ] **Step 3: Commit**

```bash
cd /Users/linjiaye/Desktop/life-insurance && git add data/ && git commit -m "feat: add CLT 2010-2013 mortality table CSV"
```

---

### Task 3: mortality.py — Life Table Engine

**Files:**
- Create: `/Users/linjiaye/Desktop/life-insurance/mortality.py`
- Create: `/Users/linjiaye/Desktop/life-insurance/test_mortality.py`

- [ ] **Step 1: Write failing test**

```bash
cat > /Users/linjiaye/Desktop/life-insurance/test_mortality.py << 'PYEOF'
import pytest
import pandas as pd
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'clt_2010_2013.csv')

# Import will fail until we create mortality.py
from mortality import load_table, get_qx, build_life_table


class TestLoadTable:
    def test_load_returns_dataframe(self):
        df = load_table(DATA_PATH)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 106
        assert list(df.columns) == ['age', 'qx_male', 'qx_female']

    def test_load_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_table('nonexistent.csv')


class TestGetQx:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.df = load_table(DATA_PATH)

    def test_male_age_30(self):
        qx = get_qx(self.df, 30, 'M')
        assert qx == pytest.approx(0.000623, abs=1e-6)

    def test_female_age_30(self):
        qx = get_qx(self.df, 30, 'F')
        assert qx == pytest.approx(0.000486, abs=1e-6)

    def test_age_105_death_certain(self):
        qx_m = get_qx(self.df, 105, 'M')
        qx_f = get_qx(self.df, 105, 'F')
        assert qx_m == 1.0
        assert qx_f == 1.0

    def test_invalid_gender(self):
        with pytest.raises(ValueError, match='gender'):
            get_qx(self.df, 30, 'X')

    def test_age_out_of_range(self):
        with pytest.raises(ValueError, match='age'):
            get_qx(self.df, 106, 'M')


class TestBuildLifeTable:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.df = load_table(DATA_PATH)

    def test_build_male_table(self):
        lt = build_life_table(self.df, 'M')
        assert 'lx' in lt.columns
        assert 'dx' in lt.columns
        assert 'tpx' in lt.columns
        assert lt.loc[0, 'lx'] == pytest.approx(100000, abs=0.5)
        # At age 105, lx should be near 0
        assert lt.loc[105, 'lx'] < 10

    def test_tpx_range(self):
        lt = build_life_table(self.df, 'M')
        # tpx at age 0 (= 0px) should be 1.0
        assert lt.loc[0, 'tpx'] == pytest.approx(1.0, abs=1e-6)
        # All tpx values should be between 0 and 1
        assert lt['tpx'].between(0, 1).all()

    def test_dx_sums_to_lx0(self):
        lt = build_life_table(self.df, 'M')
        assert lt['dx'].sum() == pytest.approx(lt.loc[0, 'lx'], abs=0.5)
PYEOF
```

- [ ] **Step 2: Run test — expect FAIL**

```bash
cd /Users/linjiaye/Desktop/life-insurance && python3 -m pytest test_mortality.py -v 2>&1 | tail -5
```
Expected: ImportError or ModuleNotFoundError

- [ ] **Step 3: Implement mortality.py**

```bash
cat > /Users/linjiaye/Desktop/life-insurance/mortality.py << 'PYEOF'
"""Life table loading, querying, and construction (CLT 2010-2013)."""

import pandas as pd
import numpy as np

LIMIT_AGE = 105
RADIX = 100000


def load_table(path):
    """Load mortality CSV. Returns DataFrame with age, qx_male, qx_female."""
    df = pd.read_csv(path)
    required = {'age', 'qx_male', 'qx_female'}
    if not required.issubset(df.columns):
        raise ValueError(f'CSV must have columns: {required}')
    return df


def get_qx(df, age, gender):
    """Get qx (mortality rate) for given age and gender ('M' or 'F')."""
    if gender not in ('M', 'F'):
        raise ValueError(f"gender must be 'M' or 'F', got '{gender}'")
    if age < 0 or age > LIMIT_AGE:
        raise ValueError(f'age must be 0-{LIMIT_AGE}, got {age}')

    col = 'qx_male' if gender == 'M' else 'qx_female'
    row = df[df['age'] == age]
    if row.empty:
        raise ValueError(f'age {age} not found in table')
    return float(row[col].iloc[0])


def build_life_table(df, gender):
    """Build full life table: lx, dx, tpx from qx for given gender.

    Returns DataFrame with columns: age, qx, lx, dx, tpx
    - lx: number alive at exact age x (radix = 100,000)
    - dx: number dying between age x and x+1
    - tpx: probability that a life aged x survives t more years (= lx+t / lx)
    """
    col = 'qx_male' if gender == 'M' else 'qx_female'
    ages = df['age'].values
    qx = df[col].values

    lx = np.zeros(len(ages))
    lx[0] = RADIX

    for i in range(len(ages) - 1):
        dx_i = lx[i] * qx[i]
        lx[i + 1] = lx[i] - dx_i

    dx = lx * qx
    dx[-1] = lx[-1]  # last age: all remaining die

    # tpx: probability of surviving from age x to age x+t
    # tpx at row i = lx[i] / lx[0] ... no, tpx for each age:
    # Actually tpx = probability (x) survives to x+t. We store "px" = one-year survival
    tpx = np.zeros(len(ages))
    for i in range(len(ages) - 1):
        tpx[i] = lx[i + 1] / lx[i] if lx[i] > 0 else 0
    tpx[-1] = 0.0

    return pd.DataFrame({
        'age': ages,
        'qx': qx,
        'lx': lx,
        'dx': dx,
        'tpx': tpx,
    })
PYEOF
```

- [ ] **Step 4: Run tests — expect PASS**

```bash
cd /Users/linjiaye/Desktop/life-insurance && python3 -m pytest test_mortality.py -v
```
Expected: 9 passed

- [ ] **Step 5: Commit**

```bash
cd /Users/linjiaye/Desktop/life-insurance && git add mortality.py test_mortality.py && git commit -m "feat: add mortality.py — life table loading and querying"
```

---

### Task 4: premium.py — Premium Calculation

**Files:**
- Create: `/Users/linjiaye/Desktop/life-insurance/premium.py`
- Create: `/Users/linjiaye/Desktop/life-insurance/test_premium.py`

- [ ] **Step 1: Write failing test**

```bash
cat > /Users/linjiaye/Desktop/life-insurance/test_premium.py << 'PYEOF'
import pytest
from mortality import load_table, build_life_table
from premium import annuity_due, single_premium, annual_premium
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'clt_2010_2013.csv')


class TestAnnuityDue:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.df = load_table(DATA_PATH)
        self.lt_m = build_life_table(self.df, 'M')

    def test_one_year_annuity(self):
        # äx:1⌉ = 1 (single payment at beginning, no survival needed for year 0)
        result = annuity_due(self.lt_m, 30, 1, 0.035)
        assert result == pytest.approx(1.0, abs=1e-6)

    def test_annuity_decreases_with_age(self):
        a30 = annuity_due(self.lt_m, 30, 10, 0.035)
        a50 = annuity_due(self.lt_m, 50, 10, 0.035)
        assert a50 < a30  # older = less time to live = fewer payments


class TestSinglePremium:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.df = load_table(DATA_PATH)
        self.lt_m = build_life_table(self.df, 'M')

    def test_premium_positive(self):
        sp = single_premium(self.lt_m, 30, 1000000, 20, 0.035)
        assert sp > 0

    def test_premium_increases_with_age(self):
        sp30 = single_premium(self.lt_m, 30, 1000000, 10, 0.035)
        sp50 = single_premium(self.lt_m, 50, 1000000, 10, 0.035)
        assert sp50 > sp30

    def test_term_matters(self):
        sp10 = single_premium(self.lt_m, 30, 1000000, 10, 0.035)
        sp20 = single_premium(self.lt_m, 30, 1000000, 20, 0.035)
        assert sp20 > sp10  # longer term = more risk

    def test_zero_interest_rate(self):
        sp = single_premium(self.lt_m, 30, 1000000, 20, 0.0)
        # With i=0, premium = sum_insured * prob(death in term)
        assert 0 < sp < 1000000

    def test_very_high_rate(self):
        sp = single_premium(self.lt_m, 30, 1000000, 20, 0.20)
        assert sp < 100000  # high discount greatly reduces premium


class TestAnnualPremium:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.df = load_table(DATA_PATH)
        self.lt_m = build_life_table(self.df, 'M')

    def test_consistency_with_single_premium(self):
        # P × äx:n⌉ = Ax:n⌉ × S  →  P = SP / ä
        sp = single_premium(self.lt_m, 30, 1000000, 20, 0.035)
        ap = annual_premium(self.lt_m, 30, 1000000, 20, 0.035)
        a = annuity_due(self.lt_m, 30, 20, 0.035)
        assert sp == pytest.approx(ap * a, rel=1e-5)

    def test_annual_less_than_single(self):
        sp = single_premium(self.lt_m, 30, 1000000, 20, 0.035)
        ap = annual_premium(self.lt_m, 30, 1000000, 20, 0.035)
        assert ap < sp
PYEOF
```

- [ ] **Step 2: Run test — expect FAIL**

```bash
cd /Users/linjiaye/Desktop/life-insurance && python3 -m pytest test_premium.py -v 2>&1 | tail -5
```

- [ ] **Step 3: Implement premium.py**

```bash
cat > /Users/linjiaye/Desktop/life-insurance/premium.py << 'PYEOF'
"""Net premium calculations for term life insurance."""

import numpy as np


def annuity_due(life_table, age, term, rate):
    """Compute äx:n⌉ — present value of annuity-due.

    Pays 1 at beginning of each year while (x) is alive, for n years
    or until death, whichever comes first.

    äx:n⌉ = Σ(t=0→n-1) v^t × tpx
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

    Ax:n⌉ × S = S × Σ(t=1→n) v^t × t-1|qx

    where t-1|qx = (lx+t-1 - lx+t) / lx = probability of dying in year t
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

    P = (S × Ax:n⌉) / äx:n⌉
    """
    sp = single_premium(life_table, age, sum_insured, term, rate)
    a = annuity_due(life_table, age, term, rate)
    if a == 0:
        return 0
    return sp / a
PYEOF
```

- [ ] **Step 4: Run tests — expect PASS**

```bash
cd /Users/linjiaye/Desktop/life-insurance && python3 -m pytest test_premium.py -v
```
Expected: 8 passed

- [ ] **Step 5: Commit**

```bash
cd /Users/linjiaye/Desktop/life-insurance && git add premium.py test_premium.py && git commit -m "feat: add premium.py — net single and annual premium calculation"
```

---

### Task 5: reserve.py — Policy Reserve Calculation

**Files:**
- Create: `/Users/linjiaye/Desktop/life-insurance/reserve.py`
- Create: `/Users/linjiaye/Desktop/life-insurance/test_reserve.py`

- [ ] **Step 1: Write failing test**

```bash
cat > /Users/linjiaye/Desktop/life-insurance/test_reserve.py << 'PYEOF'
import pytest
from mortality import load_table, build_life_table
from premium import single_premium, annual_premium
from reserve import prospective_reserve, reserve_table
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'clt_2010_2013.csv')


class TestProspectiveReserve:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.df = load_table(DATA_PATH)
        self.lt_m = build_life_table(self.df, 'M')

    def test_reserve_at_time_zero_equals_zero(self):
        r = prospective_reserve(self.lt_m, 30, 1000000, 20, 0.035, 0)
        assert r == pytest.approx(0.0, abs=1e-6)

    def test_reserve_at_maturity_equals_zero(self):
        r = prospective_reserve(self.lt_m, 30, 1000000, 20, 0.035, 20)
        assert r == pytest.approx(0.0, abs=1e-6)

    def test_reserve_positive_mid_term(self):
        r = prospective_reserve(self.lt_m, 30, 1000000, 20, 0.035, 10)
        assert r > 0

    def test_reserve_increases_then_decreases(self):
        # Reserves for term insurance typically increase then decrease to 0
        r5 = prospective_reserve(self.lt_m, 30, 1000000, 20, 0.035, 5)
        r10 = prospective_reserve(self.lt_m, 30, 1000000, 20, 0.035, 10)
        r15 = prospective_reserve(self.lt_m, 30, 1000000, 20, 0.035, 15)
        # For term: rises then falls; 15 should be lower than 10
        assert r15 < r10

    def test_reserve_equals_future_benefit_minus_future_premium(self):
        from premium import annuity_due
        age, S, n, i = 30, 1000000, 20, 0.035
        k = 7
        P = annual_premium(self.lt_m, age, S, n, i)
        # Prospective: kV = S × Ax+k:n-k⌉ - P × äx+k:n-k⌉
        future_benefit = single_premium(self.lt_m, age + k, S, n - k, i)
        future_premium_pv = P * annuity_due(self.lt_m, age + k, n - k, i)
        expected = future_benefit - future_premium_pv
        actual = prospective_reserve(self.lt_m, age, S, n, i, k)
        assert actual == pytest.approx(expected, rel=1e-5)


class TestReserveTable:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.df = load_table(DATA_PATH)
        self.lt_m = build_life_table(self.df, 'M')

    def test_table_length(self):
        tbl = reserve_table(self.lt_m, 30, 1000000, 20, 0.035)
        assert len(tbl) == 21  # years 0..20 inclusive

    def test_table_first_and_last_zero(self):
        tbl = reserve_table(self.lt_m, 30, 1000000, 20, 0.035)
        assert tbl[0][1] == pytest.approx(0.0, abs=1e-6)
        assert tbl[-1][1] == pytest.approx(0.0, abs=1e-6)
PYEOF
```

- [ ] **Step 2: Run test — expect FAIL**

```bash
cd /Users/linjiaye/Desktop/life-insurance && python3 -m pytest test_reserve.py -v 2>&1 | tail -5
```

- [ ] **Step 3: Implement reserve.py**

```bash
cat > /Users/linjiaye/Desktop/life-insurance/reserve.py << 'PYEOF'
"""Policy reserve (benefit reserve) calculations using the prospective method."""

from premium import single_premium, annual_premium, annuity_due


def prospective_reserve(life_table, age, sum_insured, term, rate, year_k):
    """Compute prospective reserve at end of policy year k.

    kV = S × Ax+k:n-k⌉ - P × äx+k:n-k⌉

    where P is the net level annual premium.

    At k=0: reserve = 0 (no time has passed, premium just paid)
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
PYEOF
```

- [ ] **Step 4: Run tests — expect PASS**

```bash
cd /Users/linjiaye/Desktop/life-insurance && python3 -m pytest test_reserve.py -v
```
Expected: 7 passed

- [ ] **Step 5: Commit**

```bash
cd /Users/linjiaye/Desktop/life-insurance && git add reserve.py test_reserve.py && git commit -m "feat: add reserve.py — prospective policy reserve calculation"
```

---

### Task 6: cli.py — Command-Line Interface

**Files:**
- Create: `/Users/linjiaye/Desktop/life-insurance/cli.py`

- [ ] **Step 1: Implement cli.py**

```bash
cat > /Users/linjiaye/Desktop/life-insurance/cli.py << 'PYEOF'
#!/usr/bin/env python3
"""Term Life Insurance Premium Calculator — CLI entry point."""

import argparse
import os
import sys
from mortality import load_table, build_life_table
from premium import single_premium, annual_premium
from reserve import reserve_table

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'clt_2010_2013.csv')
LIMIT_AGE = 105


def parse_args():
    p = argparse.ArgumentParser(
        description='定期寿险保费计算器 · Term Life Premium Calculator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python cli.py --age 30 --sum 1000000 --term 20
  python cli.py --age 40 --sum 500000 --term 10 --rate 0.03 --gender F
        ''',
    )
    p.add_argument('--age', type=int, required=True, help='投保年龄')
    p.add_argument('--sum', type=int, required=True, help='保险金额 (元)')
    p.add_argument('--term', type=int, required=True, help='保险期限 (年)')
    p.add_argument('--rate', type=float, default=0.035, help='预定利率 (默认: 0.035)')
    p.add_argument('--gender', choices=['M', 'F'], default='M', help='性别 M/F (默认: M)')
    return p.parse_args()


def validate(args):
    errors = []
    if args.age < 0:
        errors.append('年龄不能为负数')
    if args.age >= LIMIT_AGE:
        errors.append(f'年龄不能超过 {LIMIT_AGE} 岁')
    if args.age + args.term > LIMIT_AGE:
        errors.append(f'年龄 + 保险期限 ({args.age}+{args.term}={args.age+args.term}) 超过极限年龄 {LIMIT_AGE}')
    if args.sum <= 0:
        errors.append('保险金额必须大于 0')
    if args.term <= 0:
        errors.append('保险期限必须大于 0')
    if args.rate < 0:
        errors.append('利率不能为负数')
    if args.rate > 0.5:
        errors.append(f'利率 {args.rate} 异常高，请确认')
    return errors


def fmt_yuan(val):
    """Format as Chinese yuan with comma separators."""
    return f'¥{val:,.2f}'


def main():
    args = parse_args()

    errs = validate(args)
    if errs:
        print('错误:')
        for e in errs:
            print(f'  ✗ {e}')
        sys.exit(1)

    gender_label = '男性' if args.gender == 'M' else '女性'

    print()
    print('╔══════════════════════════════════════════════╗')
    print('║     定期寿险保费计算器 · Term Life         ║')
    print('╚══════════════════════════════════════════════╝')
    print()
    print(f'  被保险人年龄: {args.age} 岁 ({gender_label})')
    print(f'  保险金额:      {fmt_yuan(args.sum)}')
    print(f'  保险期限:      {args.term} 年')
    print(f'  预定利率:      {args.rate:.2%}')
    print(f'  生命表:        CLT 2010-2013 (非养老类)')
    print()

    df = load_table(DATA_PATH)
    lt = build_life_table(df, args.gender)

    sp = single_premium(lt, args.age, args.sum, args.term, args.rate)
    ap = annual_premium(lt, args.age, args.sum, args.term, args.rate)

    print('  ────────────────────────────────────────────')
    print(f'  趸缴纯保费:     {fmt_yuan(sp)}')
    print(f'  年缴纯保费:     {fmt_yuan(ap)}')
    print('  ────────────────────────────────────────────')
    print()

    reserves = reserve_table(lt, args.age, args.sum, args.term, args.rate)

    print('  📊 各年末责任准备金:')
    print(f'  {"Year":<6} {"Reserve":>12}')
    print(f'  {"─────":<6} {"───────────":>12}')
    for year, reserve in reserves:
        print(f'  {year:<6} {fmt_yuan(reserve):>12}')
    print()
    print('  💡 趸缴 = 单次付清 | 年缴 = 每年初支付')
    print(f'  💡 利率 i = {args.rate}')
    print()


if __name__ == '__main__':
    main()
PYEOF
```

- [ ] **Step 2: Test CLI runs without errors**

```bash
cd /Users/linjiaye/Desktop/life-insurance && python3 cli.py --age 30 --sum 1000000 --term 20
```
Expected: Formatted output with premium and reserve table

- [ ] **Step 3: Test validation catches errors**

```bash
cd /Users/linjiaye/Desktop/life-insurance && python3 cli.py --age 30 --sum 1000000 --term 100 2>&1 | head -3
```
Expected: `错误:` with message about exceeding limit age

- [ ] **Step 4: Commit**

```bash
cd /Users/linjiaye/Desktop/life-insurance && git add cli.py && git commit -m "feat: add cli.py — command-line interface with formatted output"
```

---

### Task 7: End-to-End Verification

**不提交，仅验证**

- [ ] **Step 1: Run all tests**

```bash
cd /Users/linjiaye/Desktop/life-insurance && python3 -m pytest -v
```
Expected: 24 tests passed (9 mortality + 8 premium + 7 reserve)

- [ ] **Step 2: Test realistic scenarios**

```bash
# 30-year-old male, ¥1M coverage, 20-year term
python3 cli.py --age 30 --sum 1000000 --term 20

# 25-year-old female, ¥500K coverage, 10-year term, 3% rate
python3 cli.py --age 25 --sum 500000 --term 10 --rate 0.03 --gender F

# 45-year-old male, ¥2M coverage, 15-year term
python3 cli.py --age 45 --sum 2000000 --term 15
```

Expected: All three produce reasonable premiums (higher age → higher premium, lower rate → higher premium)

- [ ] **Step 3: Verify sanity check**

```bash
# Premium should increase with age
python3 -c "
from mortality import load_table, build_life_table
from premium import single_premium
df = load_table('data/clt_2010_2013.csv')
lt = build_life_table(df, 'M')
sp25 = single_premium(lt, 25, 1000000, 20, 0.035)
sp35 = single_premium(lt, 35, 1000000, 20, 0.035)
sp45 = single_premium(lt, 45, 1000000, 20, 0.035)
print(f'Age 25: ¥{sp25:,.0f}')
print(f'Age 35: ¥{sp35:,.0f}')
print(f'Age 45: ¥{sp45:,.0f}')
assert sp25 < sp35 < sp45, 'Premium should increase with age!'
print('Sanity check PASSED')
"
```
Expected: `Sanity check PASSED`

---

### Task 8: Final Commit

- [ ] **Step 1: Verify git status**

```bash
cd /Users/linjiaye/Desktop/life-insurance && git status
```
Expected: clean working tree

- [ ] **Step 2: Show final project structure**

```bash
cd /Users/linjiaye/Desktop/life-insurance && find . -type f -not -path './.git/*' | sort
```

---

## Verification Checklist

- [ ] All 24 pytest tests pass
- [ ] CLI runs with required args and produces formatted output
- [ ] Premium increases with age (sanity check)
- [ ] Reserve at year 0 and year n are both 0
- [ ] Validation rejects invalid inputs (negative age, excessive term, etc.)
- [ ] Gender M/F correctly uses different mortality rates
