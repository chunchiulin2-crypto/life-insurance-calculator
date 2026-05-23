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
    - tpx: one-year survival probability (= lx+1 / lx)
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
