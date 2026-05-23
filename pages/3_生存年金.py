"""生存年金 · Life Annuity"""

import streamlit as st
import os
from mortality import load_table, build_life_table
from premium import annuity_price

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'clt_2010_2013.csv')

T = {
    'zh': {
        'title': '生存年金 · Life Annuity',
        'caption': '活着每年领钱 · 趸缴购买价格 = 年领金额 × äx:n⌉',
        'age': '投保年龄', 'payment': '年领金额（元）', 'term': '领取年限',
        'rate': '预定利率（%）', 'gender': '性别', 'gender_m': '男', 'gender_f': '女',
        'price': '趸缴购买价格', 'price_help': '一次性购买该年金的保费',
        'formula': '购买价格 = 年领金额 × ä{age}:{term}⌉',
        'note': '年金无责任准备金（签发后即开始支付）',
        'footer': '{age}岁 {gender} · 年领¥{sum:,} · {term}年 · 利率{rate:.1%}',
    },
    'en': {
        'title': 'Life Annuity',
        'caption': 'Periodic payments while alive · Purchase Price = Annual Payment × äx:n⌉',
        'age': 'Issue Age', 'payment': 'Annual Payment (¥)', 'term': 'Payment Period (years)',
        'rate': 'Interest Rate (%)', 'gender': 'Gender', 'gender_m': 'Male', 'gender_f': 'Female',
        'price': 'Lump-Sum Purchase Price', 'price_help': 'One-time premium to purchase this annuity',
        'formula': 'Purchase Price = Annual Payment × a_{age}:{term}',
        'note': 'Annuities have no policy reserves (payments begin immediately)',
        'footer': '{age}y {gender} · Yearly ¥{sum:,} · {term}yr · Rate {rate:.1%}',
    },
}


def t(key, **kw):
    text = T[st.session_state.lang][key]
    return text.format(**kw) if kw else text


if 'lang' not in st.session_state:
    st.session_state.lang = 'zh'

st.set_page_config(page_title=t('title'), page_icon='💰', layout='wide')
st.title(t('title'))
st.caption(t('caption'))

# Sidebar — annuity uses different qx assumption (no risk class needed for liability)
age = st.sidebar.slider(t('age'), 0, 80, 60)
annual_payment = st.sidebar.number_input(t('payment'), 1000, 10000000, 50000, 1000, format='%d')
term = st.sidebar.slider(t('term'), 1, 50, 20)
rate = st.sidebar.slider(t('rate'), 0.0, 10.0, 3.5, 0.5) / 100
gender = st.sidebar.radio(t('gender'), [t('gender_m'), t('gender_f')], horizontal=True)
gender_code = 'M' if gender == t('gender_m') else 'F'

if age + term > 105:
    st.sidebar.error(f'Age + Term = {age + term} exceeds 105')
    st.stop()

# Calculate
@st.cache_data
def get_lt(g):
    return build_life_table(load_table(DATA_PATH), g)

lt = get_lt(gender_code)
price = annuity_price(lt, age, annual_payment, term, rate)

# Display
st.metric(t('price'), f'¥{price:,.0f}', help=t('price_help'))
st.caption(t('formula', age=age, term=term))
st.info(t('note'))

st.divider()
st.caption(t('footer', age=age, gender=gender, sum=annual_payment, term=term, rate=rate))
