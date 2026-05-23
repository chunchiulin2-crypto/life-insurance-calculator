"""纯生存保险 · Pure Endowment"""

import streamlit as st
import os
from mortality import load_table, build_life_table
from premium import pure_endowment_single_premium, pure_endowment_annual_premium, periodic_premium

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'clt_2010_2013.csv')

T = {
    'zh': {
        'title': '纯生存保险 · Pure Endowment',
        'caption': '活到约定年龄 → 拿钱 · 中途死亡 → 不赔付',
        'age': '当前年龄',
        'maturity_age': '约定领钱年龄',
        'sum': '满期保险金（元）',
        'rate': '预定利率（%）',
        'gender': '性别', 'gender_m': '男', 'gender_f': '女',
        'freq_label': '缴费频率',
        'freq_annual': '年缴', 'freq_semi': '半年缴', 'freq_quarterly': '季缴', 'freq_monthly': '月缴',
        'per_payment': '每期保费', 'annual_premium': '年缴保费',
        'lump_sum': '趸缴纯保费',
        'summary': '{age}岁起缴{defer}年 · 活到{maturity}岁 → 领取¥{sum:,} · 中途死亡 → 不赔付',
        'note': '纯生存保险 = 只有生存给付，无死亡给付 · 类似定期储蓄，活到约定年龄才兑现',
        'footer': '{age}岁 {gender} · 缴费{defer}年至{maturity}岁 · 满期金¥{sum:,} · 利率{rate:.1%}',
    },
    'en': {
        'title': 'Pure Endowment',
        'caption': 'Survive to maturity → receive lump sum · Die before → nothing',
        'age': 'Current Age',
        'maturity_age': 'Maturity Age',
        'sum': 'Maturity Benefit (¥)',
        'rate': 'Interest Rate (%)',
        'gender': 'Gender', 'gender_m': 'Male', 'gender_f': 'Female',
        'freq_label': 'Payment Frequency',
        'freq_annual': 'Annual', 'freq_semi': 'Semi-annual', 'freq_quarterly': 'Quarterly', 'freq_monthly': 'Monthly',
        'per_payment': 'Per Payment', 'annual_premium': 'Annual Premium',
        'lump_sum': 'Net Single Premium',
        'summary': 'Age {age} pay for {defer}yrs · Survive to {maturity} → receive ¥{sum:,} · Die before → nothing',
        'note': 'Pure endowment = survival benefit only, no death benefit · Like a savings plan that only pays if you survive',
        'footer': 'Age {age} {gender} · Pay {defer}yrs to {maturity} · Maturity ¥{sum:,} · Rate {rate:.1%}',
    },
}


def t(key, **kw):
    text = T[st.session_state.lang][key]
    return text.format(**kw) if kw else text


if 'lang' not in st.session_state:
    st.session_state.lang = 'zh'

st.set_page_config(page_title=t('title'), page_icon='🎓', layout='wide')
st.title(t('title'))
st.caption(t('caption'))

# Sidebar
age = st.sidebar.slider(t('age'), 0, 70, 20)
maturity_age = st.sidebar.slider(t('maturity_age'), age + 1, 90, 40)
gender = st.sidebar.radio(t('gender'), [t('gender_m'), t('gender_f')], horizontal=True)
gender_code = 'M' if gender == t('gender_m') else 'F'
sum_insured = st.sidebar.number_input(t('sum'), 10000, 100000000, 1000000, 10000, format='%d')
rate = st.sidebar.slider(t('rate'), 0.0, 10.0, 3.5, 0.5) / 100

defer = maturity_age - age

with st.sidebar.expander(t('freq_label'), expanded=False):
    freq_label = st.radio(
        t('freq_label'),
        [t('freq_annual'), t('freq_semi'), t('freq_quarterly'), t('freq_monthly')],
        horizontal=True,
    )
freq_map = {t('freq_annual'): 1, t('freq_semi'): 2, t('freq_quarterly'): 4, t('freq_monthly'): 12}
freq_m = freq_map[freq_label]

if age + defer > 105:
    st.sidebar.error('年龄超过极限年龄 105')
    st.stop()

# Calculate
@st.cache_data
def get_lt(g):
    return build_life_table(load_table(DATA_PATH), g)

lt = get_lt(gender_code)
sp = pure_endowment_single_premium(lt, age, sum_insured, defer, rate)
ap = pure_endowment_annual_premium(lt, age, sum_insured, defer, rate)
payment = periodic_premium(ap, freq_m)

# Display
st.info(t('note'))

c1, c2, c3 = st.columns(3)
c1.metric(f'{t("per_payment")} ({freq_label})', f'¥{payment:,.0f}')
c2.metric(t('annual_premium'), f'¥{ap:,.0f}')
c3.metric(t('lump_sum'), f'¥{sp:,.0f}')
st.caption(t('summary', age=age, defer=defer, maturity=maturity_age, sum=sum_insured))

st.divider()
st.caption(t('footer', age=age, gender=gender, defer=defer, maturity=maturity_age, sum=sum_insured, rate=rate))
