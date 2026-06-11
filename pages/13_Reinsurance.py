"""Reinsurance — quota share & surplus treaty calculator."""
import streamlit as st
import pandas as pd
import os

from mortality import build_life_table
from reinsurance import quota_share, surplus

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

T = {
    'zh': {
        'title': '再保险 · Reinsurance',
        'caption': '成数再保险 & 溢额再保险 · 保费与风险分出分析',
        'base_params': '基准参数', 're_type': '再保险类型',
        're_quota': '成数再保险 (Quota Share)', 're_surplus': '溢额再保险 (Surplus)',
        'age': '投保年龄', 'sum': '保险金额（元）', 'rate': '预定利率（%）',
        'term': '保险期限（年）', 'product': '产品类型',
        'product_term': '定期寿险', 'product_wl': '终身寿险', 'product_endow': '两全保险',
        'gender': '性别', 'gender_m': '男', 'gender_f': '女',
        'quota_params': '成数参数', 'retention_pct': '自留比例',
        'surplus_params': '溢额参数', 'retention_limit': '自留额（元）',
        'lines': '溢额线数', 'lines_help': '再保承保上限 = 自留额 × (1 + 线数)',
        'commission': '再保佣金率', 'commission_help': '再保公司返还的费用补贴',
        'run': '计算',
        'summary': '分出结果',
        'premium_split': '保费拆分', 'risk_split': '风险拆分',
        'item': '项目', 'value': '金额',
        'gross_premium': '毛保费', 'net_premium': '纯保费',
        'retained_premium': '自留保费', 'ceded_premium': '分出保费',
        'commission_income': '佣金收入', 'net_income': '净收入',
        'retained_risk': '自留风险', 'ceded_risk': '分出风险',
        'unplaced_risk': '未分出风险',
        'max_capacity': '最大承保能力',
        'nav_home': '首页',
        'flow_title': '💡 保费流向', 'flow_insured': '投保人', 'flow_annual': '年缴保费', 'flow_insurer': '保险公司', 'flow_retained': '自留 + ¥{comm:,.0f} 佣金', 'flow_ceded': '分出 ¥{ceded:,.0f} → 再保公司', 'unplaced_warning': '需额外安排', 'col_retention': '自留比例',
        'alpha_label': 'α 获取费用', 'beta_label': 'β 维持费用', 'gamma_label': 'γ 收费费用',
    },
    'en': {
        'title': 'Reinsurance',
        'caption': 'Quota Share & Surplus Treaty · Premium & Risk Cession Analysis',
        'base_params': 'Base Parameters', 're_type': 'Reinsurance Type',
        're_quota': 'Quota Share', 're_surplus': 'Surplus Treaty',
        'age': 'Entry Age', 'sum': 'Sum Assured (¥)', 'rate': 'Interest Rate (%)',
        'term': 'Term (years)', 'product': 'Product',
        'product_term': 'Term Life', 'product_wl': 'Whole Life', 'product_endow': 'Endowment',
        'gender': 'Gender', 'gender_m': 'Male', 'gender_f': 'Female',
        'quota_params': 'Quota Share Settings', 'retention_pct': 'Retention %',
        'surplus_params': 'Surplus Settings', 'retention_limit': 'Retention Limit (¥)',
        'lines': 'Lines', 'lines_help': 'Max capacity = Retention × (1 + Lines)',
        'commission': 'Commission Rate', 'commission_help': 'Reinsurer expense reimbursement',
        'run': 'Calculate',
        'summary': 'Results',
        'premium_split': 'Premium Split', 'risk_split': 'Risk Split',
        'item': 'Item', 'value': 'Amount',
        'gross_premium': 'Gross Premium', 'net_premium': 'Net Premium',
        'retained_premium': 'Retained Premium', 'ceded_premium': 'Ceded Premium',
        'commission_income': 'Commission Income', 'net_income': 'Net Income',
        'retained_risk': 'Retained Risk', 'ceded_risk': 'Ceded Risk',
        'unplaced_risk': 'Unplaced Risk',
        'max_capacity': 'Max Capacity',
        'nav_home': 'Home',
        'flow_title': '💡 Premium Flow', 'flow_insured': 'Policyholder', 'flow_annual': 'Annual Premium', 'flow_insurer': 'Insurer', 'flow_retained': 'Retained + ¥{comm:,.0f} Commission', 'flow_ceded': 'Ceded ¥{ceded:,.0f} → Reinsurer', 'unplaced_warning': 'Needs additional arrangement', 'col_retention': 'Retention',
        'alpha_label': 'α Acquisition', 'beta_label': 'β Maintenance', 'gamma_label': 'γ Collection',
    },
    'zh-Hant': {
        'title': '再保險 · Reinsurance',
        'caption': '成數再保險 & 溢額再保險 · 保費與風險分出分析',
        'base_params': '基準參數', 're_type': '再保險類型',
        're_quota': '成數再保險 (Quota Share)', 're_surplus': '溢額再保險 (Surplus)',
        'age': '投保年齡', 'sum': '保險金額（元）', 'rate': '預定利率（%）',
        'term': '保險期限（年）', 'product': '產品類型',
        'product_term': '定期壽險', 'product_wl': '終身壽險', 'product_endow': '兩全保險',
        'gender': '性別', 'gender_m': '男', 'gender_f': '女',
        'quota_params': '成數參數', 'retention_pct': '自留比例',
        'surplus_params': '溢額參數', 'retention_limit': '自留額（元）',
        'lines': '溢額線數', 'lines_help': '再保承保上限 = 自留額 × (1 + 線數)',
        'commission': '再保佣金率', 'commission_help': '再保公司返還的費用補貼',
        'run': '計算',
        'summary': '分出結果',
        'premium_split': '保費拆分', 'risk_split': '風險拆分',
        'item': '項目', 'value': '金額',
        'gross_premium': '毛保費', 'net_premium': '純保費',
        'retained_premium': '自留保費', 'ceded_premium': '分出保費',
        'commission_income': '佣金收入', 'net_income': '淨收入',
        'retained_risk': '自留風險', 'ceded_risk': '分出風險',
        'unplaced_risk': '未分出風險',
        'max_capacity': '最大承保能力',
        'nav_home': '首頁',
        'flow_title': '💡 保費流向', 'flow_insured': '投保人', 'flow_annual': '年繳保費', 'flow_insurer': '保險公司', 'flow_retained': '自留 + ¥{comm:,.0f} 佣金', 'flow_ceded': '分出 ¥{ceded:,.0f} → 再保公司', 'unplaced_warning': '需額外安排', 'col_retention': '自留比例',
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
c1, c2, c3 = st.columns(3)
with c1:
    re_type = st.radio(t('re_type'), [t('re_quota'), t('re_surplus')])
    age = st.slider(t('age'), 20, 60, 35)
    rate = st.slider(t('rate'), 0.5, 6.0, 3.5, 0.5) / 100.0
with c2:
    sum_assured = st.number_input(t('sum'), 100000, 50000000, 5000000, 100000)
    term = st.slider(t('term'), 1, 50, 20)
    product = st.selectbox(t('product'), [t('product_term'), t('product_wl'), t('product_endow')])
with c3:
    gender = st.radio(t('gender'), [t('gender_m'), t('gender_f')], horizontal=True)
    g = 'M' if gender == t('gender_m') else 'F'

    if re_type == t('re_quota'):
        retention_pct = st.slider(t('retention_pct'), 0.1, 0.9, 0.3, 0.05,
                                  format="%.0f%%")
    else:
        retention_limit = st.number_input(t('retention_limit'), 100000, 10000000, 1000000, 100000)
        lines = st.slider(t('lines'), 1, 10, 5, help=t('lines_help'))

with st.expander("⚙️ 费用参数 · Expense"):
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

table_path = st.session_state.get('table_path', os.path.join(DATA_DIR, 'clt_2010_2013.csv'))
table_col = st.session_state.get('table_col', 'clt')

col = g if table_col == 'clt' else table_col
lt = build_life_table(pd.read_csv(table_path), col)

# ── Calculate ──
if st.button(t('run'), type='primary', use_container_width=True):
    if re_type == t('re_quota'):
        result = quota_share(age, sum_assured, rate, term, prod, lt,
                             retention_pct, alpha, beta, gamma)
    else:
        result = surplus(age, sum_assured, rate, term, prod, lt,
                         retention_limit, lines, alpha, beta, gamma)

    # ── Premium Split ──
    st.subheader(t('premium_split'))
    c1, c2 = st.columns(2)
    with c1:
        st.metric(t('gross_premium'), f"¥{result['gross_premium']:,.0f}")
        st.metric(t('retained_premium'), f"¥{result['retained_premium']:,.0f}")
        st.metric(t('commission_income'), f"¥{result.get('commission_income', 0):,.0f}")
        st.metric(t('net_income'), f"¥{result['net_income']:,.0f}", delta=f"{result['retention_pct']:.0%} retained")

    with c2:
        st.metric(t('ceded_premium'), f"¥{result['ceded_premium']:,.0f}",
                  delta=f"-{result['cede_pct']:.0%}")
        st.metric(t('net_premium'), f"¥{result['net_premium']:,.0f}")

    # ── Risk Split ──
    st.subheader(t('risk_split'))
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(t('retained_risk'), f"¥{result['retained_risk']:,.0f}")
    with c2:
        st.metric(t('ceded_risk'), f"¥{result.get('ceded_risk', result['ceded_premium']):,.0f}")
    with c3:
        if 'unplaced_risk' in result and result['unplaced_risk'] > 0:
            st.metric(t('unplaced_risk'), f"¥{result['unplaced_risk']:,.0f}", delta="⚠️ " + t("unplaced_warning"))
        elif 'max_capacity' in result:
            st.metric(t('max_capacity'), f"¥{result['max_capacity']:,.0f}")
        else:
            st.metric(t('retention_pct') if re_type == t('re_quota') else t('col_retention'),
                      f"{result['retention_pct']:.0%} / {result['cede_pct']:.0%}")

    # ── Flow visualization ──
    st.divider()
    st.caption(t('flow_title'))
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_a:
        st.markdown(f"""
        <div class="apple-card" style="text-align:center">
        <p style="font-size:0.7rem;color:var(--muted)">{t('flow_insured')}</p>
        <h3 style="color:var(--text)">¥{result['gross_premium']:,.0f}</h3>
        <p style="font-size:0.7rem;color:var(--muted)">年缴保费</p>
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        st.markdown("""
        <div style="display:flex;align-items:center;justify-content:center;height:100%">
        <p style="font-size:2rem">→</p>
        </div>
        """, unsafe_allow_html=True)
    with col_c:
        st.markdown(f"""
        <div class="apple-card" style="text-align:center">
        <p style="font-size:0.7rem;color:var(--muted)">保险公司</p>
        <h3>¥{result['retained_premium']:,.0f}</h3>
        <p style="font-size:0.7rem;color:var(--muted)">自留 + ¥{result.get('commission_income',0):,.0f} 佣金</p>
        <p style="font-size:0.65rem;color:var(--muted)">分出 ¥{result['ceded_premium']:,.0f} → 再保公司</p>
        </div>
        """, unsafe_allow_html=True)
