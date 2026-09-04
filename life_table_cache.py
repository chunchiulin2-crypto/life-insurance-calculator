"""Cached mortality table loading and life table construction."""

from functools import lru_cache

import pandas as pd

from app_utils import table_column_for_gender
from mortality import build_life_table


try:
    import streamlit as st
except ImportError:  # pragma: no cover - exercised in non-Streamlit contexts
    st = None


@lru_cache(maxsize=8)
def _load_table_lru(path):
    return pd.read_csv(path)


def _copy_df(df):
    """Return a copy so callers cannot mutate cached DataFrames."""
    return df.copy(deep=True)


if st is not None:
    @st.cache_data(show_spinner=False)
    def _load_table_streamlit(path):
        return pd.read_csv(path)
else:
    _load_table_streamlit = None


def cached_load_table(path):
    """Load a mortality CSV through Streamlit cache or an lru cache fallback."""
    if _load_table_streamlit is not None:
        return _copy_df(_load_table_streamlit(path))
    return _copy_df(_load_table_lru(path))


if st is not None:
    @st.cache_data(show_spinner=False)
    def _life_table_streamlit(path, table_col, gender_code, risk_factor):
        table = _load_table_streamlit(path)
        column = table_column_for_gender(table_col, gender_code)
        return build_life_table(table, column, risk_factor=risk_factor)
else:
    _life_table_streamlit = None


@lru_cache(maxsize=64)
def _life_table_lru(path, table_col, gender_code, risk_factor):
    table = _load_table_lru(path)
    column = table_column_for_gender(table_col, gender_code)
    return build_life_table(table, column, risk_factor=risk_factor)


def cached_life_table(path, table_col, gender_code, risk_factor=1.0):
    """Build a life table from the active CSV/table selection."""
    risk_factor = float(risk_factor)
    if _life_table_streamlit is not None:
        return _copy_df(_life_table_streamlit(path, table_col, gender_code, risk_factor))
    return _copy_df(_life_table_lru(path, table_col, gender_code, risk_factor))
