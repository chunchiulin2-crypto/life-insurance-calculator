"""递延寿险 · Deferred Life Assurance"""

import streamlit as st
import pandas as pd
import os
from mortality import load_table, build_life_table

AM92_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'am92.csv')
from premium import (deferred_whole_life_annual_premium, deferred_term_annual_premium,
                     deferred_whole_life_single_premium, deferred_term_single_premium,
                     periodic_premium)
from reserve import reserve_table

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'clt_2010_2013.csv')

T = {
    'zh': {
        'title': '递延寿险 · Deferred Assurance',
        'caption': '先缴费 · 后保障 · 递延期内死亡不赔付',
        'table_label': 'Life Table',
        'table_clt': 'CLT 2010-2013',
        'table_am92ult': 'AM92 Ultimate',
        'table_am92sel': 'AM92 Select',
        'table_am92sel_plusone': 'AM92 Select+1',
        'age': '当前年龄',
        'start_age': '保障开始年龄',
        'sum': '保险金额（元）',
        'coverage': '保障期限（年）',
        'rate': '预定利率（%）',
        'gender': '性别', 'gender_m': '男', 'gender_f': '女',
        'risk_label': '核保等级',
        'risk_pref': '优选体 (×0.7)', 'risk_std': '标准体 (×1.0)', 'risk_sub': '次标准体 (×2.0)',
        'payment_label': '赔付时点',
        'pay_eoy': '死亡年末付款', 'pay_imm': '死亡立即付款 (UDD)',
        'freq_label': '缴费频率',
        'freq_annual': '年缴', 'freq_semi': '半年缴', 'freq_quarterly': '季缴', 'freq_monthly': '月缴',
        'product_label': '保障类型',
        'product_wl': '递延终身寿险',
        'product_term': '递延定期寿险',
        'per_payment': '每期保费', 'annual_premium': '年缴保费',
        'lump_sum': '趸缴纯保费',
        'summary_wl': '{age}岁缴费至{start}岁 · {start}岁起保终身 · 保额¥{sum:,}',
        'summary_term': '{age}岁缴费至{start}岁 · {start}岁起保{cov}年 · 保额¥{sum:,}',
        'note': '递延期内死亡：不赔付（或退保费）· 保障从 {start} 岁开始',
        'footer': '{age}岁 {gender} · 缴费{defer}年至{start}岁 · 保障从{start}岁 · 保额¥{sum:,} · 利率{rate:.1%}',
    },
    'en': {
        'title': 'Deferred Life Assurance',
        'caption': 'Pay now · Covered later · No benefit if death during deferment',
        'table_label': 'Life Table',
        'table_clt': 'CLT 2010-2013',
        'table_am92ult': 'AM92 Ultimate',
        'table_am92sel': 'AM92 Select',
        'table_am92sel_plusone': 'AM92 Select+1',
        'age': 'Current Age',
        'start_age': 'Coverage Start Age',
        'sum': 'Sum Insured (¥)',
        'coverage': 'Coverage Period (years)',
        'rate': 'Interest Rate (%)',
        'gender': 'Gender', 'gender_m': 'Male', 'gender_f': 'Female',
        'risk_label': 'Underwriting Class',
        'risk_pref': 'Preferred (×0.7)', 'risk_std': 'Standard (×1.0)', 'risk_sub': 'Substandard (×2.0)',
        'payment_label': 'Death Benefit Timing',
        'pay_eoy': 'End of Year of Death', 'pay_imm': 'Immediate on Death (UDD)',
        'freq_label': 'Payment Frequency',
        'freq_annual': 'Annual', 'freq_semi': 'Semi-annual', 'freq_quarterly': 'Quarterly', 'freq_monthly': 'Monthly',
        'product_label': 'Coverage Type',
        'product_wl': 'Deferred Whole Life',
        'product_term': 'Deferred Term',
        'per_payment': 'Per Payment', 'annual_premium': 'Annual Premium',
        'lump_sum': 'Net Single Premium',
        'summary_wl': 'Age {age}→{start}: pay · Age {start}+: covered for life · Sum ¥{sum:,}',
        'summary_term': 'Age {age}→{start}: pay · Age {start}→{start_cov}: covered · Sum ¥{sum:,}',
        'note': 'No benefit if death during deferment · Coverage starts at age {start}',
        'footer': 'Age {age} {gender} · Pay {defer}yrs to {start} · Cover from {start} · Sum ¥{sum:,} · Rate {rate:.1%}',
    },
}


def t(key, **kw):
    text = T[st.session_state.lang][key]
    return text.format(**kw) if kw else text


if 'lang' not in st.session_state:
    st.session_state.lang = 'zh'

st.set_page_config(page_title=t('title'), layout='wide')
st.title(t('title'))
st.caption(t('caption'))

# Sidebar — Basic
age = st.sidebar.slider(t('age'), 0, 70, 25)
start_age = st.sidebar.slider(t('start_age'), age + 1, 90, 45)
gender = st.sidebar.radio(t('gender'), [t('gender_m'), t('gender_f')], horizontal=True)
gender_code = 'M' if gender == t('gender_m') else 'F'
sum_insured = st.sidebar.number_input(t('sum'), 10000, 100000000, 1000000, 10000, format='%d')
rate = st.sidebar.slider(t('rate'), 0.0, 10.0, 3.5, 0.5) / 100

defer = start_age - age

# Product type — whole life or term
product = st.sidebar.radio(
    t('product_label'),
    [t('product_wl'), t('product_term')],
    horizontal=True,
)
is_term = (product == t('product_term'))
coverage = 20
if is_term:
    max_cov = 105 - start_age
    coverage = st.sidebar.slider(t('coverage'), 1, max_cov, 20)

if start_age + (coverage if is_term else 0) > 105:
    st.sidebar.error('保障期限超过极限年龄 105')
    st.stop()

# Sidebar — Advanced
with st.sidebar.expander(t('risk_label'), expanded=False):
    risk_label = st.radio(t('risk_label'), [t('risk_pref'), t('risk_std'), t('risk_sub')], horizontal=True)
    pay_label = st.radio(t('payment_label'), [t('pay_eoy'), t('pay_imm')], horizontal=True)
    freq_label = st.radio(
        t('freq_label'),
        [t('freq_annual'), t('freq_semi'), t('freq_quarterly'), t('freq_monthly')],
        horizontal=True,
    )

risk_map = {t('risk_pref'): 0.7, t('risk_std'): 1.0, t('risk_sub'): 2.0}
claim_accel = (pay_label == t('pay_imm'))
freq_map = {t('freq_annual'): 1, t('freq_semi'): 2, t('freq_quarterly'): 4, t('freq_monthly'): 12}
freq_m = freq_map[freq_label]

# Calculate
@st.cache_data
def get_lt(g, rf):
    return build_life_table(load_table(table_path), g if table_col == 'clt' else table_col, risk_factor=rf)

lt = get_lt(gender_code, risk_map[risk_label])

if is_term:
    sp = deferred_term_single_premium(lt, age, defer, coverage, sum_insured, rate, claim_accel)
    ap = deferred_term_annual_premium(lt, age, defer, coverage, sum_insured, rate, claim_accel)
    summary = t('summary_term', age=age, start=start_age, start_cov=start_age + coverage, cov=coverage, sum=sum_insured)
else:
    sp = deferred_whole_life_single_premium(lt, age, defer, sum_insured, rate, claim_accel)
    ap = deferred_whole_life_annual_premium(lt, age, defer, sum_insured, rate, claim_accel)
    summary = t('summary_wl', age=age, start=start_age, sum=sum_insured)

payment = periodic_premium(ap, freq_m)

# Display
st.info(t('note', start=start_age))

c1, c2, c3 = st.columns(3)
c1.metric(f'{t("per_payment")} ({freq_label})', f'¥{payment:,.0f}', help=summary)
c2.metric(t('annual_premium'), f'¥{ap:,.0f}')
c3.metric(t('lump_sum'), f'¥{sp:,.0f}')

st.divider()
st.caption(t('footer', age=age, gender=gender, defer=defer, start=start_age, sum=sum_insured, rate=rate))
