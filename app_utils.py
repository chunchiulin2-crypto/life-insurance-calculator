"""Shared app helpers for table selection and formatting."""

import os


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def default_table_path():
    """Return the default CLT table path."""
    return os.path.join(DATA_DIR, "clt_2010_2013.csv")


def init_session_defaults(session_state):
    """Initialize Streamlit session defaults used across pages."""
    session_state.setdefault("lang", "zh")
    session_state.setdefault("table_col", "clt")
    session_state.setdefault("table_path", default_table_path())


def selected_table_state(session_state):
    """Return the active mortality table path and column key."""
    init_session_defaults(session_state)
    return session_state.table_path, session_state.table_col


def table_column_for_gender(table_col, gender_code):
    """Resolve CLT gender vs AM92 column keys for life table construction."""
    return gender_code if table_col == "clt" else table_col


def format_currency(value, symbol="¥", decimals=0):
    """Format a currency amount with thousands separators."""
    return f"{symbol}{value:,.{decimals}f}"
