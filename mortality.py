"""Life table loading, querying, and construction (CLT 2010-2013 + AM92)."""

import os
import pandas as pd
import numpy as np

LIMIT_AGE = 120
RADIX = 100000

# Ensure session state defaults exist for Streamlit deep-link navigation
try:
    import streamlit as st
    if 'table_col' not in st.session_state:
        st.session_state.table_col = 'clt'
    if 'table_path' not in st.session_state:
        st.session_state.table_path = os.path.join(
            os.path.dirname(__file__), 'data', 'clt_2010_2013.csv'
        )
except ImportError:
    pass  # CLI / pytest — streamlit not available, skip

AM92_COLUMNS = ['qx_am92ult', 'qx_am92sel', 'qx_am92sel_plusone']


def table_max_age(table_col):
    """Return the maximum insurable age for the given life table column."""
    return 120 if table_col.startswith('am92') else 105


def load_table(path):
    """Load mortality CSV. Returns DataFrame."""
    return pd.read_csv(path)


def resolve_column(df, gender_or_column):
    """Resolve the qx column name from gender or explicit column name.

    - 'M' → 'qx_male' (CLT table)
    - 'F' → 'qx_female' (CLT table)
    - 'am92ult' / 'am92sel' / 'am92sel_plusone' → corresponding AM92 column
    """
    # Direct column name match
    am92_map = {
        'am92ult': 'qx_am92ult',
        'am92sel': 'qx_am92sel',
        'am92sel_plusone': 'qx_am92sel_plusone',
    }
    if gender_or_column in am92_map:
        col = am92_map[gender_or_column]
        if col in df.columns:
            return col
        raise ValueError(f'AM92 column {col} not found in CSV')

    # CLT gender-based
    if gender_or_column in ('M', 'F'):
        col = 'qx_male' if gender_or_column == 'M' else 'qx_female'
        if col in df.columns:
            return col
        raise ValueError(f'CLT column {col} not found in CSV')

    raise ValueError(f"Unknown table/column: {gender_or_column}")


def build_life_table(df, gender_or_column, risk_factor=1.0):
    """Build full life table from qx.

    Parameters:
        gender_or_column: 'M'/'F' for CLT, or 'am92ult'/'am92sel'/'am92sel_plusone' for AM92
        risk_factor: multiplier on qx. 0.7 = preferred, 1.0 = standard, 2.0 = substandard.

    Returns DataFrame with columns: age, qx, lx, dx, tpx
    """
    col = resolve_column(df, gender_or_column)
    ages = df['age'].values
    qx = df[col].values * risk_factor
    qx = np.clip(qx, 0.0, 1.0)

    lx = np.zeros(len(ages))
    lx[0] = RADIX

    for i in range(len(ages) - 1):
        dx_i = lx[i] * qx[i]
        lx[i + 1] = lx[i] - dx_i

    dx = lx * qx
    dx[-1] = lx[-1]

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
