"""定期寿险保费计算器 · Web UI  /  Term Life Premium Calculator"""

import streamlit as st
import pandas as pd
import os
from mortality import load_table, build_life_table
from premium import single_premium, annual_premium
from reserve import reserve_table

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'clt_2010_2013.csv')

# ---- i18n ----
T = {
    'zh': {
        'page_title': '寿险保费计算器',
        'title': '定期寿险保费计算器',
        'caption': 'CLT 2010-2013 生命表（非养老类）· 趸缴/年缴纯保费 · 责任准备金',
        'lang_label': '语言 / Language',
        'params_header': '投保参数',
        'age': '投保年龄',
        'sum_insured': '保险金额（元）',
        'term': '保险期限（年）',
        'rate': '预定利率（%）',
        'gender': '性别',
        'gender_male': '男',
        'gender_female': '女',
        'error_age_term': '年龄 + 期限 ({age}+{term}={total}) 超过极限年龄 105',
        'single_premium': '趸缴纯保费',
        'single_premium_help': '一次性缴清的纯保费',
        'annual_premium': '年缴纯保费',
        'annual_premium_help': '每年初缴纳的均衡纯保费',
        'reserve_chart': '责任准备金曲线',
        'reserve_table': '各年末准备金明细',
        'col_year': '保单年度',
        'col_reserve': '准备金（元）',
        'footer': '被保险人：{age} 岁 {gender} · 保额 ¥{sum:,} · 期限 {term} 年 · 利率 {rate:.1%} · 生命表 CLT 2010-2013',
    },
    'en': {
        'page_title': 'Life Insurance Calculator',
        'title': 'Term Life Insurance Calculator',
        'caption': 'CLT 2010-2013 Mortality Table (Non-Pension) · Net Premiums · Policy Reserves',
        'lang_label': '语言 / Language',
        'params_header': 'Policy Parameters',
        'age': 'Issue Age',
        'sum_insured': 'Sum Insured (¥)',
        'term': 'Policy Term (years)',
        'rate': 'Interest Rate (%)',
        'gender': 'Gender',
        'gender_male': 'Male',
        'gender_female': 'Female',
        'error_age_term': 'Age + Term ({age}+{term}={total}) exceeds limit age 105',
        'single_premium': 'Net Single Premium',
        'single_premium_help': 'One-time lump-sum premium',
        'annual_premium': 'Net Annual Premium',
        'annual_premium_help': 'Level premium paid at beginning of each year',
        'reserve_chart': 'Policy Reserve Curve',
        'reserve_table': 'Reserve by Policy Year',
        'col_year': 'Policy Year',
        'col_reserve': 'Reserve (¥)',
        'footer': 'Insured: Age {age} {gender} · Sum Insured ¥{sum:,} · Term {term} yrs · Rate {rate:.1%} · CLT 2010-2013',
    },
}


def t(key, **kwargs):
    """Translate key to current language, with optional format kwargs."""
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

# ---- Language Switcher (top of sidebar) ----
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

# ---- Header ----
st.title(t('title'))
st.caption(t('caption'))

# ---- Sidebar: Parameters ----
st.sidebar.header(t('params_header'))

age = st.sidebar.slider(t('age'), min_value=0, max_value=80, value=30, step=1)
sum_insured = st.sidebar.number_input(t('sum_insured'), min_value=10000, value=1000000, step=10000, format='%d')
term = st.sidebar.slider(t('term'), min_value=1, max_value=50, value=20, step=1)
rate_pct = st.sidebar.slider(t('rate'), min_value=0.0, max_value=10.0, value=3.5, step=0.5)
rate = rate_pct / 100
gender_label = st.sidebar.radio(
    t('gender'),
    [t('gender_male'), t('gender_female')],
    horizontal=True,
)
gender_code = 'M' if gender_label == t('gender_male') else 'F'

# Validate
if age + term > 105:
    st.sidebar.error(t('error_age_term', age=age, term=term, total=age + term))
    st.stop()

# ---- Calculate ----
@st.cache_data
def get_life_table(gender_code):
    df = load_table(DATA_PATH)
    return build_life_table(df, gender_code)

lt = get_life_table(gender_code)
sp = single_premium(lt, age, sum_insured, term, rate)
ap = annual_premium(lt, age, sum_insured, term, rate)
reserves = reserve_table(lt, age, sum_insured, term, rate)

# ---- Main Area ----
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
st.caption(t('footer', age=age, gender=gender_label, sum=sum_insured, term=term, rate=rate))
