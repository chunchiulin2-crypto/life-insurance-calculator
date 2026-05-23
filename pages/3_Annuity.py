"""生存年金 · Life Annuity"""

import streamlit as st
import os
from mortality import load_table, build_life_table
from premium import annuity_price

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'clt_2010_2013.csv')
AM92_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'am92.csv')

T = {
    'zh': {
        'title': '生存年金 · Life Annuity',
        'caption': '活着每年领钱 · 趸缴购买价格 = 年领金额 × äx:n⌉',,
        'table_label': '生命表',
        'table_clt': 'CLT 2010-2013',
        'table_am92ult': 'AM92 Ultimate',
        'table_am92sel': 'AM92 Select',
        'table_am92sel_plusone': 'AM92 Select+1',
        'age': '投保年龄', 'payment': '年领金额（元）', 'term': '领取年限',
        'rate': '预定利率（%）', 'gender': '性别', 'gender_m': '男', 'gender_f': '女',
        'freq_payout': '领取频率',
        'freq_annual': '年领', 'freq_semi': '半年领', 'freq_quarterly': '季领', 'freq_monthly': '月领',
        'price': '趸缴购买价格', 'price_help': '一次性购买该年金的保费',
        'formula': '购买价格 = 年领金额 × ä(m){age}:{term}⌉',
        'note': '年金无责任准备金（签发后即开始支付）',
        'footer': '{age}岁 {gender} · 年领¥{sum:,} · {term}年 · 利率{rate:.1%}',
    },
    'en': {
        'title': 'Life Annuity',
        'caption': 'Periodic payments while alive · Purchase Price = Annual Payment × äx:n⌉',,
        'table_label': '生命表',
        'table_clt': 'CLT 2010-2013',
        'table_am92ult': 'AM92 Ultimate',
        'table_am92sel': 'AM92 Select',
        'table_am92sel_plusone': 'AM92 Select+1',,
        'table_label': 'Life Table',
        'table_clt': 'CLT 2010-2013',
        'table_am92ult': 'AM92 Ultimate',
        'table_am92sel': 'AM92 Select',
        'table_am92sel_plusone': 'AM92 Select+1',
        'age': 'Issue Age', 'payment': 'Annual Payment (¥)', 'term': 'Payment Period (years)',
        'rate': 'Interest Rate (%)', 'gender': 'Gender', 'gender_m': 'Male', 'gender_f': 'Female',
        'freq_payout': 'Payout Frequency',
        'freq_annual': 'Annual', 'freq_semi': 'Semi-annual', 'freq_quarterly': 'Quarterly', 'freq_monthly': 'Monthly',
        'price': 'Lump-Sum Purchase Price', 'price_help': 'One-time premium to purchase this annuity',
        'formula': 'Purchase Price = Annual Payment × a(m)_{age}:{term}',
        'note': 'Annuities have no policy reserves (payments begin immediately)',
        'footer': '{age}y {gender} · Yearly ¥{sum:,} · {term}yr · Rate {rate:.1%}',
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

# Sidebar — annuity uses different qx assumption (no risk class needed for liability)
age = st.sidebar.slider(t('age'), 0, 80, 60)
annual_payment = st.sidebar.number_input(t('payment'), 1000, 10000000, 50000, 1000, format='%d')
term = st.sidebar.slider(t('term'), 1, 50, 20)
rate = st.sidebar.slider(t('rate'), 0.0, 10.0, 3.5, 0.5) / 100
gender = st.sidebar.radio(t('gender'), [t('gender_m'), t('gender_f')], horizontal=True)
gender_code = 'M' if gender == t('gender_m') else 'F'

payout_label = st.sidebar.radio(
    t('freq_payout'),
    [t('freq_annual'), t('freq_semi'), t('freq_quarterly'), t('freq_monthly')],
    horizontal=True,
)
payout_map = {t('freq_annual'): 1, t('freq_semi'): 2, t('freq_quarterly'): 4, t('freq_monthly'): 12}
payout_m = payout_map[payout_label]

if age + term > 105:
    st.sidebar.error(f'Age + Term = {age + term} exceeds 105')
    st.stop()

# Calculate
@st.cache_data
def get_lt(g):
    return build_life_table(load_table(table_path), g if table_col == 'clt' else table_col)

lt = get_lt(gender_code)
price = annuity_price(lt, age, annual_payment, term, rate, payout_m=payout_m)
per_payment = annual_payment / payout_m

# Display
c1, c2 = st.columns(2)
c1.metric(t('price'), f'¥{price:,.0f}', help=t('price_help'))
c2.metric(f'每次领取 ({payout_label})', f'¥{per_payment:,.0f}',
          help=f'年领总额 ¥{annual_payment:,} · 分{payout_m}次')
st.caption(t('formula', age=age, term=term))
st.info(t('note'))

st.divider()
st.caption(t('footer', age=age, gender=gender, sum=annual_payment, term=term, rate=rate))
