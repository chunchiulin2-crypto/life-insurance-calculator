"""Stress Testing — scenario analysis for premiums & reserves."""
import streamlit as st
import pandas as pd
import os

from stress_test import stress_premium_table, SCENARIOS

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

T = {
    'zh': {
        'title': '压力测试 · Stress Testing',
        'caption': '模拟极端市场情景下的保费与准备金变化 · Solvency II 式分析',
        'base_params': '基准参数',
        'age': '投保年龄', 'sum': '保险金额（元）', 'rate': '预定利率（%）',
        'term': '保险期限（年）', 'product': '产品类型',
        'product_term': '定期寿险', 'product_wl': '终身寿险', 'product_endow': '两全保险',
        'gender': '性别', 'gender_m': '男', 'gender_f': '女',
        'run': '运行压力测试',
        'premium_title': '保费压力测试结果',
        'scenario': '情景', 'description': '触发条件',
        'base_premium': '基准保费', 'stress_premium': '压力保费',
        'delta': '变动', 'impact': '影响等级',
        'reserve_title': '准备金对比 · 基准 vs 组合冲击',
        'col_year': '保单年度', 'col_base': '基准准备金',
        'col_stressed': '压力准备金', 'col_delta': '缺口',
        'summary_title': '总结',
        'summary_text': '在{worst}情景下保费涨幅最大（{pct:.0f}%）。组合冲击（1/200年事件）下保费上涨{pct2:.0f}%。',
        'nav_home': '首页',
        'severity_high': '高', 'severity_medium': '中', 'severity_low': '低',
        'alpha_label': 'α 获取费用', 'beta_label': 'β 维持费用', 'gamma_label': 'γ 收费费用',
    },
    'en': {
        'title': 'Stress Testing',
        'caption': 'Simulate extreme market scenarios — Solvency II style analysis',
        'base_params': 'Base Parameters',
        'age': 'Entry Age', 'sum': 'Sum Assured (¥)', 'rate': 'Interest Rate (%)',
        'term': 'Term (years)', 'product': 'Product Type',
        'product_term': 'Term Life', 'product_wl': 'Whole Life', 'product_endow': 'Endowment',
        'gender': 'Gender', 'gender_m': 'Male', 'gender_f': 'Female',
        'run': 'Run Stress Test',
        'premium_title': 'Premium Stress Test Results',
        'scenario': 'Scenario', 'description': 'Trigger',
        'base_premium': 'Base Premium', 'stress_premium': 'Stressed Premium',
        'delta': 'Change', 'impact': 'Severity',
        'reserve_title': 'Reserve Comparison · Base vs Combined Shock',
        'col_year': 'Policy Year', 'col_base': 'Base Reserve',
        'col_stressed': 'Stressed Reserve', 'col_delta': 'Shortfall',
        'summary_title': 'Summary',
        'summary_text': 'Worst case: {worst} (+{pct:.0f}%). Combined shock (1-in-200yr): +{pct2:.0f}%.',
        'nav_home': 'Home',
        'severity_high': 'High', 'severity_medium': 'Medium', 'severity_low': 'Low',
        'alpha_label': 'α Acquisition', 'beta_label': 'β Maintenance', 'gamma_label': 'γ Collection',
    },
    'zh-Hant': {
        'title': '壓力測試 · Stress Testing',
        'caption': '模擬極端市場情景下的保費與準備金變化 · Solvency II 式分析',
        'base_params': '基準參數',
        'age': '投保年齡', 'sum': '保險金額（元）', 'rate': '預定利率（%）',
        'term': '保險期限（年）', 'product': '產品類型',
        'product_term': '定期壽險', 'product_wl': '終身壽險', 'product_endow': '兩全保險',
        'gender': '性別', 'gender_m': '男', 'gender_f': '女',
        'run': '執行壓力測試',
        'premium_title': '保費壓力測試結果',
        'scenario': '情景', 'description': '觸發條件',
        'base_premium': '基準保費', 'stress_premium': '壓力保費',
        'delta': '變動', 'impact': '影響等級',
        'reserve_title': '準備金對比 · 基準 vs 組合衝擊',
        'col_year': '保單年度', 'col_base': '基準準備金',
        'col_stressed': '壓力準備金', 'col_delta': '缺口',
        'summary_title': '總結',
        'summary_text': '在{worst}情景下保費漲幅最大（{pct:.0f}%）。組合衝擊（1/200年事件）下保費上漲{pct2:.0f}%。',
        'nav_home': '首頁',
        'severity_high': '高', 'severity_medium': '中', 'severity_low': '低',
        'alpha_label': 'α 獲取費用', 'beta_label': 'β 維持費用', 'gamma_label': 'γ 收費費用',
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

st.markdown(f"""
<div class="nav-strip">
<a href="/" target="_self" class="nav-pill">{t('nav_home')}</a>
</div>
""", unsafe_allow_html=True)

# ── Parameters ──
with st.container(border=True):
    st.subheader(t('base_params'))
    c1, c2, c3 = st.columns(3)
    with c1:
        age = st.slider(t('age'), 20, 60, 30)
        rate = st.slider(t('rate'), 0.5, 6.0, 3.5, 0.5) / 100.0
    with c2:
        sum_assured = st.number_input(t('sum'), 10000, 10000000, 1000000, 10000)
        term = st.slider(t('term'), 1, 50, 20)
    with c3:
        product = st.selectbox(t('product'),
            [t('product_term'), t('product_wl'), t('product_endow')])
        gender = st.radio(t('gender'), [t('gender_m'), t('gender_f')], horizontal=True)

    with st.expander("⚙️ 费用参数 · Expense Params"):
        ea, eb, eg = st.columns(3)
        with ea:
            alpha = st.slider(t('alpha_label'), 0.0, 0.1, 0.03, 0.005)
        with eb:
            beta = st.slider(t('beta_label'), 0.0, 0.1, 0.02, 0.005)
        with eg:
            gamma = st.slider(t('gamma_label'), 0.0, 0.005, 0.001, 0.0005)

# Map product
prod_map = {t('product_term'): 'term', t('product_wl'): 'whole_life', t('product_endow'): 'endowment'}
prod = prod_map[product]
g = 'M' if gender == t('gender_m') else 'F'

table_path = st.session_state.get('table_path', os.path.join(DATA_DIR, 'clt_2010_2013.csv'))
table_col = st.session_state.get('table_col', 'clt')

# ── Run ──
if st.button(t('run'), type='primary', use_container_width=True):
    results = stress_premium_table(
        age, sum_assured, rate, term, prod,
        table_path, table_col, g,
        alpha=alpha, beta=beta, gamma=gamma
    )

    # ── Premium Table ──
    st.subheader(t('premium_title'))

    base = results.pop('base')
    rows = []
    for key, r in results.items():
        pct = r['delta_pct']
        if abs(pct) > 30:
            severity = '🔴 ' + t('severity_high')
        elif abs(pct) > 15:
            severity = '🟡 ' + t('severity_medium')
        else:
            severity = '🟢 ' + t('severity_low')

        rows.append({
            t('scenario'): r.get(f'label_{st.session_state.lang}', r['label_en']),
            t('description'): r.get(f'desc_{st.session_state.lang}', r['desc_en']),
            t('base_premium'): f"¥{base['gross']:,.0f}",
            t('stress_premium'): f"¥{r['gross']:,.0f}",
            t('delta'): f"{pct:+.1f}%",
            t('impact'): severity,
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # ── Reserve Comparison ──
    st.subheader(t('reserve_title'))
    from stress_test import stress_reserve_table
    reserve_data = stress_reserve_table(age, sum_assured, rate, term, prod, table_path, table_col, g)

    reserve_rows = []
    for i in range(min(reserve_data['n'], 30)):
        base_r = reserve_data['base'][i] if i < len(reserve_data['base']) else 0
        stressed_r = reserve_data['stressed'][i] if i < len(reserve_data['stressed']) else 0
        delta_r = stressed_r - base_r
        reserve_rows.append({
            t('col_year'): i, t('col_base'): f"¥{base_r:,.0f}",
            t('col_stressed'): f"¥{stressed_r:,.0f}", t('col_delta'): f"¥{delta_r:+,.0f}",
        })

    st.dataframe(pd.DataFrame(reserve_rows), use_container_width=True, hide_index=True)

    # ── Summary ──
    worst = max(results.items(), key=lambda x: x[1]['delta_pct'])
    combined = results['combined']
    st.info(t('summary_text',
        worst=worst[1].get(f'label_{st.session_state.lang}', worst[1]['label_en']),
        pct=worst[1]['delta_pct'], pct2=combined['delta_pct']))
