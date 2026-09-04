"""Shared Streamlit UI helpers."""

from contextlib import contextmanager
from html import escape

import streamlit as st


def param_chips_html(items):
    """Return escaped HTML for compact parameter chips."""
    chips = []
    for label, value in items:
        if value is None:
            continue
        chips.append(
            f'<span class="param-chip">{escape(str(label))}: {escape(str(value))}</span>'
        )
    return f'<div class="param-chips">{" ".join(chips)}</div>'


def render_param_chips(items):
    """Render compact parameter chips using the app CSS."""
    st.markdown(param_chips_html(items), unsafe_allow_html=True)


def normalize_metric_specs(metrics):
    """Normalize metric dictionaries so render_metric_row has a stable shape."""
    normalized = []
    for metric in metrics:
        normalized.append({
            "label": metric["label"],
            "value": metric["value"],
            "help": metric.get("help"),
            "delta": metric.get("delta"),
            "delta_color": metric.get("delta_color", "normal"),
        })
    return normalized


def render_metric_row(metrics, columns=None):
    """Render a row of Streamlit metrics."""
    normalized = normalize_metric_specs(metrics)
    cols = st.columns(columns or len(normalized))
    for col, metric in zip(cols, normalized):
        col.metric(
            metric["label"],
            metric["value"],
            help=metric["help"],
            delta=metric["delta"],
            delta_color=metric["delta_color"],
        )


@contextmanager
def section_panel(title, caption=None):
    """Render a bordered section panel and yield its container."""
    with st.container(border=True) as container:
        st.subheader(title)
        if caption:
            st.caption(caption)
        yield container


def show_input_error(message, location="main"):
    """Display an input error in the sidebar or main page."""
    if location == "sidebar":
        st.sidebar.error(message)
    else:
        st.error(message)


def render_home_nav(label):
    """Render a compact home navigation strip."""
    st.markdown(
        f'<div class="nav-strip"><a href="/" target="_self" class="nav-pill">{escape(str(label))}</a></div>',
        unsafe_allow_html=True,
    )
