"""Sensitivity Analysis — see how premiums change when one parameter varies."""
import streamlit as st
import pandas as pd
import numpy as np
import os
from mortality import build_life_table, load_table
from premium import (annual_premium, whole_life_annual_premium, endowment_annual_premium,
                     gross_annual_premium)

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

T = {
    'zh': {
        'title': '敏感性分析 · Sensitivity Analysis',
        'caption': '改变一个参数，观察保费如何变化。面试级精算可视化。',
        'base_params': '基准参数',
        'age': '投保年龄', 'sum': '保险金额（元）', 'rate': '基准利率（%）',
        'term': '保险期限（年）', 'product': '产品类型',
        'product_term': '定期寿险', 'product_wl': '终身寿险', 'product_endow': '两全保险',
        'gender': '性别', 'gender_m': '男', 'gender_f': '女',
        'sweep_var': '要分析的参数',
        'sweep_rate': '利率（1% → 6%）',
        'sweep_mortality': '死亡率倍数（0.5× → 2×）',
        'sweep_term': '保险期限（5 → 40年）',
        'sweep_expense': '费用率 β（0% → 10%）',
        'sweep_range': '变化范围',
        'run': '运行分析',
        'chart_title': '敏感性曲线',
        'table_title': '分析明细',
        'col_param': '参数值', 'col_premium': '年毛保费', 'col_delta': '变化',
        'insight': '洞察',
        'insight_text': '当{param}从{lo}变到{hi}，保费从¥{v_lo:,.0f}变到¥{v_hi:,.0f}（变化{v_delta:+.1f}%）。\n\n{direction}',
        'nav_home': '首页',
        'alpha_label': 'α 获取费', 'beta_label': 'β 维持费', 'gamma_label': 'γ 收费费',
    },
    'en': {
        'title': 'Sensitivity Analysis',
        'caption': 'See how premiums shift when one parameter changes. Interview-ready visualisation.',
        'base_params': 'Base Parameters',
        'age': 'Entry Age', 'sum': 'Sum Assured (¥)', 'rate': 'Base Rate (%)',
        'term': 'Term (years)', 'product': 'Product',
        'product_term': 'Term Life', 'product_wl': 'Whole Life', 'product_endow': 'Endowment',
        'gender': 'Gender', 'gender_m': 'Male', 'gender_f': 'Female',
        'sweep_var': 'Parameter to Analyse',
        'sweep_rate': 'Interest Rate (1% → 6%)',
        'sweep_mortality': 'Mortality Multiplier (0.5× → 2×)',
        'sweep_term': 'Policy Term (5 → 40 years)',
        'sweep_expense': 'Expense β (0% → 10%)',
        'sweep_range': 'Range',
        'run': 'Run Analysis',
        'chart_title': 'Sensitivity Curve',
        'table_title': 'Detailed Results',
        'col_param': 'Parameter', 'col_premium': 'Gross Annual', 'col_delta': 'Change',
        'insight': 'Insight',
        'insight_text': 'When {param} changes from {lo} to {hi}, premium changes from ¥{v_lo:,.0f} to ¥{v_hi:,.0f} ({v_delta:+.1f}%).\n\n{direction}',
        'nav_home': 'Home',
        'alpha_label': 'α Acquisition', 'beta_label': 'β Maintenance', 'gamma_label': 'γ Collection',
    },
    'zh-Hant': {
        'title': '敏感性分析 · Sensitivity Analysis',
        'caption': '改變一個參數，觀察保費如何變化。面試級精算可視化。',
        'base_params': '基準參數',
        'age': '投保年齡', 'sum': '保險金額（元）', 'rate': '基準利率（%）',
        'term': '保險期限（年）', 'product': '產品類型',
        'product_term': '定期壽險', 'product_wl': '終身壽險', 'product_endow': '兩全保險',
        'gender': '性別', 'gender_m': '男', 'gender_f': '女',
        'sweep_var': '要分析的參數',
        'sweep_rate': '利率（1% → 6%）',
        'sweep_mortality': '死亡率倍數（0.5× → 2×）',
        'sweep_term': '保險期限（5 → 40年）',
        'sweep_expense': '費用率 β（0% → 10%）',
        'sweep_range': '變化範圍',
        'run': '執行分析',
        'chart_title': '敏感性曲線',
        'table_title': '分析明細',
        'col_param': '參數值', 'col_premium': '年毛保費', 'col_delta': '變化',
        'insight': '洞察',
        'insight_text': '當{param}從{lo}變到{hi}，保費從¥{v_lo:,.0f}變到¥{v_hi:,.0f}（變化{v_delta:+.1f}%）。\n\n{direction}',
        'nav_home': '首頁',
        'alpha_label': 'α 獲取費', 'beta_label': 'β 維持費', 'gamma_label': 'γ 收費費',
    },
}

if 'lang' not in st.session_state:
    st.session_state.lang = 'zh'


def t(key, **kw):
    lang = st.session_state.get('lang', 'zh')
    if lang not in T or key not in T[lang]:
        lang = 'zh'
    text = T[lang][key]
    return text.format(**kw) if kw else text


st.set_page_config(page_title=t('title'), layout='wide', initial_sidebar_state='expanded')
st.title(t('title'))
st.caption(t('caption'))

st.markdown(f"""<div class="nav-strip"><a href="/" target="_self" class="nav-pill">{t('nav_home')}</a></div>""",
            unsafe_allow_html=True)

# ── Base Parameters ──
c1, c2, c3 = st.columns(3)
with c1:
    age = st.slider(t('age'), 20, 60, 30)
    rate = st.slider(t('rate'), 0.5, 6.0, 3.5, 0.5) / 100.0
with c2:
    sum_assured = st.number_input(t('sum'), 100000, 10000000, 1000000, 100000)
    term = st.slider(t('term'), 1, 50, 20)
with c3:
    product = st.selectbox(t('product'), [t('product_term'), t('product_wl'), t('product_endow')])
    gender = st.radio(t('gender'), [t('gender_m'), t('gender_f')], horizontal=True)
    g = 'M' if gender == t('gender_m') else 'F'

# ── Sweep Parameter ──
sweep_choice = st.selectbox(t('sweep_var'),
    [t('sweep_rate'), t('sweep_mortality'), t('sweep_term'), t('sweep_expense')])

if sweep_choice == t('sweep_rate'):
    lo, hi, steps, default_range = 0.01, 0.06, 12, (0.01, 0.06)
    param_name = 'Interest Rate'
    param_fmt = '{:.1%}'
elif sweep_choice == t('sweep_mortality'):
    lo, hi, steps, default_range = 0.5, 2.0, 8, (0.5, 2.0)
    param_name = 'Mortality Multiplier'
    param_fmt = '{:.1f}×'
elif sweep_choice == t('sweep_term'):
    lo, hi, steps, default_range = 5, 40, 8, (5, 40)
    param_name = 'Term (years)'
    param_fmt = '{:.0f}'
else:
    lo, hi, steps, default_range = 0.0, 0.10, 6, (0.0, 0.10)
    param_name = 'Expense β'
    param_fmt = '{:.1%}'

range_lo, range_hi = st.slider(t('sweep_range'), lo, hi, default_range, step=(hi - lo) / 20.0)

# ── Calculate ──
if st.button(t('run'), type='primary', use_container_width=True):
    table_path = st.session_state.get('table_path', os.path.join(DATA_DIR, 'clt_2010_2013.csv'))
    table_col = st.session_state.get('table_col', 'clt')
    col = g if table_col == 'clt' else table_col

    prod_map = {t('product_term'): 'term', t('product_wl'): 'whole_life', t('product_endow'): 'endowment'}
    prod = prod_map[product]

    values = np.linspace(range_lo, range_hi, steps)
    premiums = []

    for v in values:
        lt = build_life_table(load_table(table_path), col,
                              risk_factor=v if sweep_choice == t('sweep_mortality') else 1.0)
        adj_rate = v if sweep_choice == t('sweep_rate') else rate
        adj_rate = max(0.005, adj_rate)
        adj_term = int(v) if sweep_choice == t('sweep_term') else term
        beta = v if sweep_choice == t('sweep_expense') else 0.02

        if prod == 'term':
            net = annual_premium(lt, age, sum_assured, adj_term, adj_rate)
        elif prod == 'whole_life':
            net = whole_life_annual_premium(lt, age, sum_assured, adj_rate)
        else:
            net = endowment_annual_premium(lt, age, sum_assured, adj_term, adj_rate)

        gross = (net + 0.03 * sum_assured + 0.001 * sum_assured / 1000) / max(0.01, 1.0 - beta)
        premiums.append(gross)

    base_premium = premiums[0] if premiums else 0

    # ── Chart ──
    st.subheader(t('chart_title'))
    chart_data = pd.DataFrame({'x': values, 'Premium (¥)': premiums})
    st.line_chart(chart_data.set_index('x'), height=400)

    # ── Table ──
    st.subheader(t('table_title'))
    rows = []
    for v, p in zip(values, premiums):
        rows.append({
            t('col_param'): param_fmt.format(v),
            t('col_premium'): f"¥{p:,.0f}",
            t('col_delta'): f"{(p - base_premium) / base_premium * 100:+.1f}%",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # ── Insight ──
    v_lo, v_hi = premiums[0], premiums[-1]
    pct = (v_hi - v_lo) / v_lo * 100
    if abs(pct) < 2:
        direction = '保费对该参数不敏感——小幅波动对定价影响有限。'
    elif pct > 0:
        direction = f'参数越大保费越高——每增加一个单位，保费约增加 {pct / len(values):.1f}%。'
    else:
        direction = f'参数越大保费越低——呈反向关系，每单位变化约影响 {-pct / len(values):.1f}%。'

    st.info(t('insight_text',
        param=param_name, lo=param_fmt.format(values[0]), hi=param_fmt.format(values[-1]),
        v_lo=v_lo, v_hi=v_hi, v_delta=pct) + '\n\n' + direction)
