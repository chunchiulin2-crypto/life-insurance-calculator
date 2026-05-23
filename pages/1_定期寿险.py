"""定期寿险 · Term Life Insurance"""

import streamlit as st
import pandas as pd
import os
from mortality import load_table, build_life_table
from premium import single_premium, annual_premium
from reserve import reserve_table

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'clt_2010_2013.csv')

T = {
    'zh': {
        'title': '定期寿险 · Term Life',
        'caption': '约定期限内死亡赔付 · Net Single & Annual Premiums · Policy Reserves',
        'age': '投保年龄', 'sum': '保险金额（元）', 'term': '保险期限（年）',
        'rate': '预定利率（%）', 'gender': '性别', 'gender_m': '男', 'gender_f': '女',
        'risk_label': '核保等级',
        'risk_pref': '优选体 (×0.7)', 'risk_std': '标准体 (×1.0)', 'risk_sub': '次标准体 (×2.0)',
        'risk_hint': '健康不吸烟 → 优选 | 吸烟/超重 → 次标准',
        'payment_label': '赔付时点',
        'pay_eoy': '死亡年末付款', 'pay_imm': '死亡立即付款 (UDD)',
        'pay_hint': '立即付款 = (1+i)^0.5 × 年末付款',
        'expense_alpha': 'α 获取费 (% × 保额)',
        'expense_beta': 'β 维持费 (% × 保费)',
        'expense_gamma': 'γ 收费费 (‰ × 保额)',
        'expense_formula': '毛保费 = (纯保费 + 费用现值) ÷ (1 − β)',
        'freq_label': '缴费频率',
        'freq_annual': '年缴', 'freq_semi': '半年缴', 'freq_quarterly': '季缴', 'freq_monthly': '月缴',
        'per_payment': '每期保费', 'gross_annual': '年毛保费',
        'net_premium': '纯保费 (净)', 'net_premium_help': '纯风险保费',
        'reserve_chart': '责任准备金曲线', 'reserve_table': '各年末准备金明细',
        'col_year': '保单年度', 'col_reserve': '准备金',
        'footer': '{age}岁 {gender} · 保额¥{sum:,} · {term}年 · 利率{rate:.1%} · {risk} · {payment}',
    },
    'en': {
        'title': 'Term Life Insurance',
        'caption': 'Death benefit within a fixed term · Net Premiums · Reserves',
        'age': 'Issue Age', 'sum': 'Sum Insured (¥)', 'term': 'Policy Term (years)',
        'rate': 'Interest Rate (%)', 'gender': 'Gender', 'gender_m': 'Male', 'gender_f': 'Female',
        'risk_label': 'Underwriting Class',
        'risk_pref': 'Preferred (×0.7)', 'risk_std': 'Standard (×1.0)', 'risk_sub': 'Substandard (×2.0)',
        'risk_hint': 'Healthy non-smoker → Preferred | Smoker → Substandard',
        'payment_label': 'Death Benefit Timing',
        'pay_eoy': 'End of Year of Death', 'pay_imm': 'Immediate on Death (UDD)',
        'pay_hint': 'Immediate = (1+i)^0.5 × End-of-Year',
        'expense_alpha': 'α Acquisition (% × Sum Insured)',
        'expense_beta': 'β Maintenance (% × Premium)',
        'expense_gamma': 'γ Collection (‰ × Sum Insured)',
        'expense_formula': 'Gross = (Net + Expense PV) ÷ (1 − β)',
        'freq_label': 'Payment Frequency',
        'freq_annual': 'Annual', 'freq_semi': 'Semi-annual', 'freq_quarterly': 'Quarterly', 'freq_monthly': 'Monthly',
        'per_payment': 'Per Payment', 'gross_annual': 'Gross Annual',
        'net_premium': 'Net Premium', 'net_premium_help': 'Pure risk premium',
        'reserve_chart': 'Policy Reserve Curve', 'reserve_table': 'Reserve by Policy Year',
        'col_year': 'Policy Year', 'col_reserve': 'Reserve',
        'footer': '{age}y {gender} · Sum ¥{sum:,} · {term}yr · Rate {rate:.1%} · {risk} · {payment}',
    },
}


def t(key, **kw):
    text = T[st.session_state.lang][key]
    return text.format(**kw) if kw else text


# Language init
if 'lang' not in st.session_state:
    st.session_state.lang = 'zh'

st.set_page_config(page_title=t('title'), page_icon='🏠', layout='wide')
st.title(t('title'))
st.caption(t('caption'))

# Sidebar
age = st.sidebar.slider(t('age'), 0, 80, 30)
sum_insured = st.sidebar.number_input(t('sum'), 10000, 100000000, 1000000, 10000, format='%d')
term = st.sidebar.slider(t('term'), 1, 50, 20)
rate = st.sidebar.slider(t('rate'), 0.0, 10.0, 3.5, 0.5) / 100
gender = st.sidebar.radio(t('gender'), [t('gender_m'), t('gender_f')], horizontal=True)
gender_code = 'M' if gender == t('gender_m') else 'F'

risk_label = st.sidebar.radio(t('risk_label'), [t('risk_pref'), t('risk_std'), t('risk_sub')], horizontal=True)
risk_map = {t('risk_pref'): 0.7, t('risk_std'): 1.0, t('risk_sub'): 2.0}
st.sidebar.caption(t('risk_hint'))

pay_label = st.sidebar.radio(t('payment_label'), [t('pay_eoy'), t('pay_imm')], horizontal=True)
claim_accel = (pay_label == t('pay_imm'))
st.sidebar.caption(t('pay_hint'))

# Expense parameters
st.sidebar.divider()
alpha = st.sidebar.slider(t('expense_alpha'), 0.0, 15.0, 5.0, 0.5) / 100
beta  = st.sidebar.slider(t('expense_beta'), 0.0, 10.0, 2.0, 0.5) / 100
gamma = st.sidebar.slider(t('expense_gamma'), 0.0, 5.0, 0.5, 0.1) / 1000
st.sidebar.caption(t('expense_formula'))

# Payment frequency
freq_label = st.sidebar.radio(
    t('freq_label'),
    [t('freq_annual'), t('freq_semi'), t('freq_quarterly'), t('freq_monthly')],
    horizontal=True,
)
freq_map = {t('freq_annual'): 1, t('freq_semi'): 2, t('freq_quarterly'): 4, t('freq_monthly'): 12}
freq_m = freq_map[freq_label]

if age + term > 105:
    st.sidebar.error(f'Age + Term = {age + term} exceeds limit age 105')
    st.stop()

# Calculate
from premium import gross_annual_premium, periodic_premium, annual_premium as net_ap

@st.cache_data
def get_lt(g, rf):
    return build_life_table(load_table(DATA_PATH), g, risk_factor=rf)

lt = get_lt(gender_code, risk_map[risk_label])
gap = gross_annual_premium(lt, age, sum_insured, term, rate,
                           alpha=alpha, beta=beta, gamma=gamma, claim_accel=claim_accel)
payment = periodic_premium(gap, freq_m)
net = net_ap(lt, age, sum_insured, term, rate, claim_accel)
reserves = reserve_table(lt, age, sum_insured, term, rate)

# Display
c1, c2, c3 = st.columns(3)
c1.metric(f'{t("per_payment")} ({freq_label})', f'¥{payment:,.0f}',
          help=f'Per-payment amount · Gross annual ¥{gap:,.0f}')
c2.metric(t('gross_annual'), f'¥{gap:,.0f}', help='Annual premium with expenses')
c3.metric(t('net_premium'), f'¥{net:,.0f}',
          help=t('net_premium_help'), delta=f'¥{gap - net:,.0f}',
          delta_color='off')
st.divider()

st.subheader(t('reserve_chart'))
df_r = pd.DataFrame(reserves, columns=['Year', 'Reserve']).set_index('Year')
st.line_chart(df_r, height=300)

st.subheader(t('reserve_table'))
df_d = pd.DataFrame(reserves, columns=[t('col_year'), t('col_reserve')])
df_d[t('col_reserve')] = df_d[t('col_reserve')].apply(lambda x: f'¥{x:,.2f}')
st.dataframe(df_d, width='stretch', hide_index=True, height=400)

st.divider()
st.caption(t('footer', age=age, gender=gender, sum=sum_insured, term=term, rate=rate, risk=risk_label, payment=pay_label))
