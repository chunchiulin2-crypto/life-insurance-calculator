"""寿险精算计算器 · Web UI  /  Life Insurance Actuarial Calculator"""

import streamlit as st
import pandas as pd
import os
from mortality import load_table, build_life_table
from premium import (single_premium, annual_premium,
                     whole_life_single_premium, whole_life_annual_premium,
                     endowment_single_premium, endowment_annual_premium,
                     annuity_price)
from reserve import reserve_table, whole_life_reserve_table, endowment_reserve_table

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'clt_2010_2013.csv')

# ---- i18n ----
T = {
    'zh': {
        'page_title': '寿险保费计算器',
        'title': '寿险精算计算器',
        'caption': 'CLT 2010-2013 生命表 · 定期/终身/年金/两全',
        'lang_label': '语言 / Language',
        'product_label': '产品类型',
        'product_term': '定期寿险',
        'product_whole_life': '终身寿险',
        'product_annuity': '生存年金',
        'product_endowment': '两全保险',
        'params_header': '投保参数',
        'age': '投保年龄',
        'sum_insured': '保险金额（元）',
        'annual_payment': '年领金额（元）',
        'term': '保险期限（年）',
        'rate': '预定利率（%）',
        'gender': '性别',
        'gender_male': '男',
        'gender_female': '女',
        'risk_label': '核保等级',
        'risk_preferred': '优选体 (Preferred)',
        'risk_standard': '标准体 (Standard)',
        'risk_substandard': '次标准体 (Substandard)',
        'risk_hint': '健康、不吸烟 → 优选 | 吸烟/超重/慢性病 → 次标准',
        'payment_label': '赔付时点',
        'payment_eoy': '死亡年末付款',
        'payment_immediate': '死亡立即付款 (UDD)',
        'payment_hint': '立即付款 = (1+i)^0.5 × 年末付款 · 年金不受影响',
        'error_age_term': '年龄 + 期限 ({age}+{term}={total}) 超过极限年龄 105',
        'single_premium': '趸缴纯保费',
        'single_premium_help': '一次性缴清的纯保费',
        'annuity_price_label': '趸缴购买价格',
        'annuity_price_help': '一次性购买该年金的价格',
        'annual_premium': '年缴纯保费',
        'annual_premium_help': '每年初缴纳的均衡纯保费',
        'reserve_chart': '责任准备金曲线',
        'reserve_table': '各年末准备金明细',
        'col_year': '保单年度',
        'col_reserve': '准备金（元）',
        'annuity_note': '生存年金无责任准备金',
        'footer_term': '被保险人：{age} 岁 {gender} · 保额 ¥{sum:,} · 期限 {term} 年 · 利率 {rate:.1%} · {risk}',
        'footer_wl': '被保险人：{age} 岁 {gender} · 保额 ¥{sum:,} · 终身 · 利率 {rate:.1%} · {risk}',
        'footer_annuity': '被保险人：{age} 岁 {gender} · 年领 ¥{sum:,} · 期限 {term} 年 · 利率 {rate:.1%} · {risk}',
        'footer_endow': '被保险人：{age} 岁 {gender} · 保额 ¥{sum:,} · 期限 {term} 年 · 利率 {rate:.1%} · 到期返还 · {risk}',
    },
    'en': {
        'page_title': 'Life Insurance Calculator',
        'title': 'Life Insurance Actuarial Calculator',
        'caption': 'CLT 2010-2013 Table · Term / Whole Life / Annuity / Endowment',
        'lang_label': '语言 / Language',
        'product_label': 'Product Type',
        'product_term': 'Term Life',
        'product_whole_life': 'Whole Life',
        'product_annuity': 'Life Annuity',
        'product_endowment': 'Endowment',
        'params_header': 'Policy Parameters',
        'age': 'Issue Age',
        'sum_insured': 'Sum Insured (¥)',
        'annual_payment': 'Annual Payment (¥)',
        'term': 'Policy Term (years)',
        'rate': 'Interest Rate (%)',
        'gender': 'Gender',
        'gender_male': 'Male',
        'gender_female': 'Female',
        'risk_label': 'Underwriting Class',
        'risk_preferred': 'Preferred (Non-smoker, healthy)',
        'risk_standard': 'Standard',
        'risk_substandard': 'Substandard (Smoker, elevated risk)',
        'risk_hint': 'Healthy, non-smoker → Preferred | Smoker, chronic conditions → Substandard',
        'payment_label': 'Death Benefit Timing',
        'payment_eoy': 'End of Year of Death',
        'payment_immediate': 'Immediate on Death (UDD)',
        'payment_hint': 'Immediate = (1+i)^0.5 × End-of-Year · Annuity unaffected',
        'error_age_term': 'Age + Term ({age}+{term}={total}) exceeds limit age 105',
        'single_premium': 'Net Single Premium',
        'single_premium_help': 'One-time lump-sum premium',
        'annuity_price_label': 'Purchase Price',
        'annuity_price_help': 'Lump-sum price to buy this annuity',
        'annual_premium': 'Net Annual Premium',
        'annual_premium_help': 'Level premium paid at beginning of each year',
        'reserve_chart': 'Policy Reserve Curve',
        'reserve_table': 'Reserve by Policy Year',
        'col_year': 'Policy Year',
        'col_reserve': 'Reserve (¥)',
        'annuity_note': 'Life annuities have no policy reserves',
        'footer_term': 'Insured: Age {age} {gender} · Sum Insured ¥{sum:,} · Term {term} yrs · Rate {rate:.1%} · {risk}',
        'footer_wl': 'Insured: Age {age} {gender} · Sum Insured ¥{sum:,} · Whole Life · Rate {rate:.1%} · {risk}',
        'footer_annuity': 'Insured: Age {age} {gender} · Annual ¥{sum:,} · Term {term} yrs · Rate {rate:.1%} · {risk}',
        'footer_endow': 'Insured: Age {age} {gender} · Sum Insured ¥{sum:,} · Term {term} yrs · Rate {rate:.1%} · Endowment · {risk}',
    },
}


def t(key, **kwargs):
    text = T[st.session_state.lang][key]
    if kwargs:
        text = text.format(**kwargs)
    return text


# ---- Init ----
if 'lang' not in st.session_state:
    st.session_state.lang = 'zh'

st.set_page_config(
    page_title=t('page_title'),
    page_icon='🛡️',
    layout='wide',
)

# ---- Sidebar ----
lang = st.sidebar.selectbox(
    t('lang_label'),
    ['中文', 'English'],
    index=0 if st.session_state.lang == 'zh' else 1,
    key='lang_selector',
)
new_lang = 'zh' if lang == '中文' else 'en'
if new_lang != st.session_state.lang:
    st.session_state.lang = new_lang
    st.rerun()

# Product selector
product = st.sidebar.selectbox(
    t('product_label'),
    [t('product_term'), t('product_whole_life'), t('product_annuity'), t('product_endowment')],
)

# ---- Header ----
st.title(t('title'))
st.caption(t('caption'))

# ---- Sidebar: Parameters ----
st.sidebar.header(t('params_header'))

age = st.sidebar.slider(t('age'), min_value=0, max_value=80, value=30, step=1)

# Adaptive: annuity shows "annual payment", others show "sum insured"
if product == t('product_annuity'):
    sum_insured = st.sidebar.number_input(t('annual_payment'), min_value=1000, value=50000, step=1000, format='%d')
else:
    sum_insured = st.sidebar.number_input(t('sum_insured'), min_value=10000, value=1000000, step=10000, format='%d')

# Adaptive: whole life hides term (auto = 105 - age)
if product != t('product_whole_life'):
    term = st.sidebar.slider(t('term'), min_value=1, max_value=50, value=20, step=1)
else:
    term = 105 - age  # implicit

rate_pct = st.sidebar.slider(t('rate'), min_value=0.0, max_value=10.0, value=3.5, step=0.5)
rate = rate_pct / 100

gender_label = st.sidebar.radio(
    t('gender'),
    [t('gender_male'), t('gender_female')],
    horizontal=True,
)
gender_code = 'M' if gender_label == t('gender_male') else 'F'

risk_label = st.sidebar.radio(
    t('risk_label'),
    [t('risk_preferred'), t('risk_standard'), t('risk_substandard')],
    horizontal=True,
)
risk_map = {
    t('risk_preferred'): 0.7,
    t('risk_standard'): 1.0,
    t('risk_substandard'): 2.0,
}
risk_factor = risk_map[risk_label]
st.sidebar.caption(t('risk_hint'))

# Payment timing
payment_label = st.sidebar.radio(
    t('payment_label'),
    [t('payment_eoy'), t('payment_immediate')],
    horizontal=True,
)
claim_accel = (payment_label == t('payment_immediate'))
st.sidebar.caption(t('payment_hint'))

# Validate
if product != t('product_whole_life') and age + term > 105:
    st.sidebar.error(t('error_age_term', age=age, term=term, total=age + term))
    st.stop()

# ---- Calculate ----
@st.cache_data
def get_life_table(gender_code, risk_factor):
    df = load_table(DATA_PATH)
    return build_life_table(df, gender_code, risk_factor=risk_factor)

lt = get_life_table(gender_code, risk_factor)

# Dispatch by product
if product == t('product_whole_life'):
    sp = whole_life_single_premium(lt, age, sum_insured, rate, claim_accel=claim_accel)
    ap = whole_life_annual_premium(lt, age, sum_insured, rate, claim_accel=claim_accel)
    reserves = whole_life_reserve_table(lt, age, sum_insured, rate)
    footer_key = 'footer_wl'
elif product == t('product_annuity'):
    sp = annuity_price(lt, age, sum_insured, term, rate)
    ap = None
    reserves = []
    footer_key = 'footer_annuity'
elif product == t('product_endowment'):
    sp = endowment_single_premium(lt, age, sum_insured, term, rate, claim_accel=claim_accel)
    ap = endowment_annual_premium(lt, age, sum_insured, term, rate, claim_accel=claim_accel)
    reserves = endowment_reserve_table(lt, age, sum_insured, term, rate)
    footer_key = 'footer_endow'
else:  # term
    sp = single_premium(lt, age, sum_insured, term, rate, claim_accel=claim_accel)
    ap = annual_premium(lt, age, sum_insured, term, rate, claim_accel=claim_accel)
    reserves = reserve_table(lt, age, sum_insured, term, rate)
    footer_key = 'footer_term'

# ---- Main Area ----
if product == t('product_annuity'):
    st.metric(t('annuity_price_label'), f'¥{sp:,.0f}', help=t('annuity_price_help'))
    st.caption(t('annuity_note'))
else:
    col1, col2 = st.columns(2)
    with col1:
        st.metric(t('single_premium'), f'¥{sp:,.0f}', help=t('single_premium_help'))
    with col2:
        st.metric(t('annual_premium'), f'¥{ap:,.0f}', help=t('annual_premium_help'))

    st.divider()

    # Reserve chart
    st.subheader(t('reserve_chart'))
    df_reserve = pd.DataFrame(reserves, columns=['Year', 'Reserve']).set_index('Year')
    st.line_chart(df_reserve, height=300)

    # Reserve table
    st.subheader(t('reserve_table'))
    df_display = pd.DataFrame(reserves, columns=[t('col_year'), t('col_reserve')])
    df_display[t('col_reserve')] = df_display[t('col_reserve')].apply(lambda x: f'¥{x:,.2f}')
    st.dataframe(df_display, width='stretch', hide_index=True, height=400)

# ---- Footer ----
st.divider()
st.caption(t(footer_key, age=age, gender=gender_label, sum=sum_insured, term=term, rate=rate, risk=risk_label))
