"""递延终身年金 · Deferred Life Annuity"""

import streamlit as st
import pandas as pd
import os
from mortality import load_table, build_life_table
from premium import deferred_annuity_premium, deferred_annuity_lump_sum, periodic_premium

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'clt_2010_2013.csv')

T = {
    'zh': {
        'title': '递延终身年金 · Deferred Annuity',
        'caption': '先缴费 · 后领钱 · 活多久领多久',
        'age': '当前年龄',
        'retire_age': '开始领取年龄',
        'payment': '年领金额（元）',
        'rate': '预定利率（%）',
        'gender': '性别', 'gender_m': '男', 'gender_f': '女',
        'freq_label': '缴费频率',
        'freq_annual': '年缴', 'freq_semi': '半年缴', 'freq_quarterly': '季缴', 'freq_monthly': '月缴',
        'freq_payout': '领取频率',
        'freq_payout_annual': '年领', 'freq_payout_semi': '半年领', 'freq_payout_quarterly': '季领', 'freq_payout_monthly': '月领',
        'per_payout': '每次领取金额',
        'annual_premium': '年缴保费',
        'per_payment': '每期保费',
        'lump_sum': '趸缴价格',
        'lump_sum_help': '一次性缴清的价格',
        'summary': '{age}岁开始缴费 · {defer}年缴费期 · {retire}岁开始领钱 · 年领 ¥{pay:,} · 终身',
        'how_it_works': '缴费 {defer} 年（{age}→{retire}岁），然后每年领 ¥{pay:,} 直到身故。',
        'footer': '{age}岁 {gender} · 缴费{defer}年至{retire}岁 · 年领¥{pay:,} · 终身 · 利率{rate:.1%}',
    },
    'en': {
        'title': 'Deferred Life Annuity',
        'caption': 'Pay now · Receive later · For life',
        'age': 'Current Age',
        'retire_age': 'Age to Start Receiving',
        'payment': 'Annual Payout (¥)',
        'rate': 'Interest Rate (%)',
        'gender': 'Gender', 'gender_m': 'Male', 'gender_f': 'Female',
        'freq_label': 'Payment Frequency',
        'freq_annual': 'Annual', 'freq_semi': 'Semi-annual', 'freq_quarterly': 'Quarterly', 'freq_monthly': 'Monthly',
        'freq_payout': 'Payout Frequency',
        'freq_payout_annual': 'Annual', 'freq_payout_semi': 'Semi-annual', 'freq_payout_quarterly': 'Quarterly', 'freq_payout_monthly': 'Monthly',
        'per_payout': 'Per Payout',
        'annual_premium': 'Annual Premium',
        'per_payment': 'Per Payment',
        'lump_sum': 'Lump Sum Price',
        'lump_sum_help': 'One-time purchase price',
        'summary': 'Start at age {age} · Pay for {defer} years · Receive from age {retire} · ¥{pay:,}/yr for life',
        'how_it_works': 'Pay for {defer} years (age {age}→{retire}), then receive ¥{pay:,} per year for life.',
        'footer': 'Age {age} {gender} · Pay {defer}yrs to {retire} · Receive ¥{pay:,}/yr for life · Rate {rate:.1%}',
    },
}


def t(key, **kw):
    text = T[st.session_state.lang][key]
    return text.format(**kw) if kw else text


if 'lang' not in st.session_state:
    st.session_state.lang = 'zh'

st.set_page_config(page_title=t('title'), page_icon='⏳', layout='wide')
st.title(t('title'))
st.caption(t('caption'))

# Sidebar — Basic
age = st.sidebar.slider(t('age'), 0, 70, 25)
retire_age = st.sidebar.slider(t('retire_age'), age + 1, 90, 60)
gender = st.sidebar.radio(t('gender'), [t('gender_m'), t('gender_f')], horizontal=True)
gender_code = 'M' if gender == t('gender_m') else 'F'
annual_payment = st.sidebar.number_input(t('payment'), 1000, 10000000, 50000, 1000, format='%d')
rate = st.sidebar.slider(t('rate'), 0.0, 10.0, 3.5, 0.5) / 100

defer = retire_age - age

if age + defer > 105:
    st.sidebar.error(f'开始领取年龄超过极限年龄 105')
    st.stop()

# Sidebar — Advanced
with st.sidebar.expander(t('freq_label'), expanded=False):
    freq_label = st.radio(
        t('freq_label'),
        [t('freq_annual'), t('freq_semi'), t('freq_quarterly'), t('freq_monthly')],
        horizontal=True,
    )
freq_map = {t('freq_annual'): 1, t('freq_semi'): 2, t('freq_quarterly'): 4, t('freq_monthly'): 12}
freq_m = freq_map[freq_label]

# Payout frequency
payout_label = st.sidebar.radio(
    t('freq_payout'),
    [t('freq_payout_annual'), t('freq_payout_semi'), t('freq_payout_quarterly'), t('freq_payout_monthly')],
    horizontal=True,
)
payout_map = {t('freq_payout_annual'): 1, t('freq_payout_semi'): 2, t('freq_payout_quarterly'): 4, t('freq_payout_monthly'): 12}
payout_m = payout_map[payout_label]

# Calculate
@st.cache_data
def get_lt(g):
    return build_life_table(load_table(DATA_PATH), g)

lt = get_lt(gender_code)
ap = deferred_annuity_premium(lt, age, defer, annual_payment, rate, m=freq_m, payout_m=payout_m)
payment = periodic_premium(ap, freq_m)
lump = deferred_annuity_lump_sum(lt, age, defer, annual_payment, rate, payout_m=payout_m)
per_payout = annual_payment / payout_m

# Display
st.info(t('how_it_works', defer=defer, age=age, retire=retire_age, pay=annual_payment))

c1, c2, c3, c4 = st.columns(4)
c1.metric(f'{t("per_payment")} ({freq_label})', f'¥{payment:,.0f}')
c2.metric(t('annual_premium'), f'¥{ap:,.0f}')
c3.metric(t('lump_sum'), f'¥{lump:,.0f}', help=t('lump_sum_help'))
c4.metric(f'{t("per_payout")} ({payout_label})', f'¥{per_payout:,.0f}',
          help=f'年领总额 ¥{annual_payment:,} · 分{payout_m}次')

# Visual: accumulation vs payout timeline
st.divider()
st.subheader('缴费期 vs 领取期')
timeline_data = pd.DataFrame({
    'Year': list(range(defer + 30)),  # defer + 30 years of payout shown
    'Phase': ['缴费期 (Pay)'] * defer + ['领取期 (Receive)'] * 30,
    'Cash Flow': [-ap] * defer + [annual_payment] * 30,
})
st.bar_chart(timeline_data.set_index('Year')['Cash Flow'], height=250)

st.divider()
st.caption(t('footer', age=age, gender=gender, defer=defer, retire=retire_age, pay=annual_payment, rate=rate))
