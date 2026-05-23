"""终身寿险 · Whole Life Insurance"""

import streamlit as st
import pandas as pd
import os
from mortality import load_table, build_life_table
from premium import whole_life_single_premium, whole_life_annual_premium
from reserve import whole_life_reserve_table

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'clt_2010_2013.csv')

T = {
    'zh': {
        'title': '终身寿险 · Whole Life',
        'caption': '保障终身 · 无论何时死亡都赔付 · 准备金单调递增至保额',
        'age': '投保年龄', 'sum': '保险金额（元）',
        'rate': '预定利率（%）', 'gender': '性别', 'gender_m': '男', 'gender_f': '女',
        'risk_label': '核保等级',
        'risk_pref': '优选体 (×0.7)', 'risk_std': '标准体 (×1.0)', 'risk_sub': '次标准体 (×2.0)',
        'risk_hint': '健康不吸烟 → 优选 | 吸烟/超重 → 次标准',
        'payment_label': '赔付时点',
        'pay_eoy': '死亡年末付款', 'pay_imm': '死亡立即付款 (UDD)',
        'pay_hint': '立即付款 = (1+i)^0.5 × 年末付款',
        'term_auto': '保险期限 = 105 − 年龄 = {term} 年（自动）',
        'sp': '趸缴纯保费', 'sp_help': '一次性缴清的纯保费',
        'ap': '年缴纯保费', 'ap_help': '每年初缴纳的均衡纯保费',
        'reserve_chart': '责任准备金曲线', 'reserve_table': '各年末准备金明细',
        'col_year': '保单年度', 'col_reserve': '准备金',
        'footer': '{age}岁 {gender} · 保额¥{sum:,} · 终身 · 利率{rate:.1%} · {risk} · {payment}',
    },
    'en': {
        'title': 'Whole Life Insurance',
        'caption': 'Lifetime coverage · Pays on death whenever it occurs · Reserve approaches sum insured',
        'age': 'Issue Age', 'sum': 'Sum Insured (¥)',
        'rate': 'Interest Rate (%)', 'gender': 'Gender', 'gender_m': 'Male', 'gender_f': 'Female',
        'risk_label': 'Underwriting Class',
        'risk_pref': 'Preferred (×0.7)', 'risk_std': 'Standard (×1.0)', 'risk_sub': 'Substandard (×2.0)',
        'risk_hint': 'Healthy non-smoker → Preferred | Smoker → Substandard',
        'payment_label': 'Death Benefit Timing',
        'pay_eoy': 'End of Year of Death', 'pay_imm': 'Immediate on Death (UDD)',
        'pay_hint': 'Immediate = (1+i)^0.5 × End-of-Year',
        'term_auto': 'Policy Term = 105 − Age = {term} years (auto)',
        'sp': 'Net Single Premium', 'sp_help': 'One-time lump-sum premium',
        'ap': 'Net Annual Premium', 'ap_help': 'Level premium paid each year-beginning',
        'reserve_chart': 'Policy Reserve Curve', 'reserve_table': 'Reserve by Policy Year',
        'col_year': 'Policy Year', 'col_reserve': 'Reserve',
        'footer': '{age}y {gender} · Sum ¥{sum:,} · Whole Life · Rate {rate:.1%} · {risk} · {payment}',
    },
}


def t(key, **kw):
    text = T[st.session_state.lang][key]
    return text.format(**kw) if kw else text


if 'lang' not in st.session_state:
    st.session_state.lang = 'zh'

st.set_page_config(page_title=t('title'), page_icon='🔒', layout='wide')
st.title(t('title'))
st.caption(t('caption'))

# Sidebar — no term slider for whole life
age = st.sidebar.slider(t('age'), 0, 80, 30)
sum_insured = st.sidebar.number_input(t('sum'), 10000, 100000000, 1000000, 10000, format='%d')
term = 105 - age
st.sidebar.caption(t('term_auto', term=term))
rate = st.sidebar.slider(t('rate'), 0.0, 10.0, 3.5, 0.5) / 100
gender = st.sidebar.radio(t('gender'), [t('gender_m'), t('gender_f')], horizontal=True)
gender_code = 'M' if gender == t('gender_m') else 'F'

risk_label = st.sidebar.radio(t('risk_label'), [t('risk_pref'), t('risk_std'), t('risk_sub')], horizontal=True)
risk_map = {t('risk_pref'): 0.7, t('risk_std'): 1.0, t('risk_sub'): 2.0}
st.sidebar.caption(t('risk_hint'))

pay_label = st.sidebar.radio(t('payment_label'), [t('pay_eoy'), t('pay_imm')], horizontal=True)
claim_accel = (pay_label == t('pay_imm'))
st.sidebar.caption(t('pay_hint'))

# Calculate
@st.cache_data
def get_lt(g, rf):
    return build_life_table(load_table(DATA_PATH), g, risk_factor=rf)

lt = get_lt(gender_code, risk_map[risk_label])
sp = whole_life_single_premium(lt, age, sum_insured, rate, claim_accel)
ap = whole_life_annual_premium(lt, age, sum_insured, rate, claim_accel)
reserves = whole_life_reserve_table(lt, age, sum_insured, rate)

# Display
c1, c2 = st.columns(2)
c1.metric(t('sp'), f'¥{sp:,.0f}', help=t('sp_help'))
c2.metric(t('ap'), f'¥{ap:,.0f}', help=t('ap_help'))
st.divider()

st.subheader(t('reserve_chart'))
df_r = pd.DataFrame(reserves, columns=['Year', 'Reserve']).set_index('Year')
st.line_chart(df_r, height=300)

st.subheader(t('reserve_table'))
df_d = pd.DataFrame(reserves, columns=[t('col_year'), t('col_reserve')])
df_d[t('col_reserve')] = df_d[t('col_reserve')].apply(lambda x: f'¥{x:,.2f}')
st.dataframe(df_d, width='stretch', hide_index=True, height=400)

st.divider()
st.caption(t('footer', age=age, gender=gender, sum=sum_insured, rate=rate, risk=risk_label, payment=pay_label))
