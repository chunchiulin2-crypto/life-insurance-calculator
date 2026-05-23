"""定期寿险保费计算器 · Web UI"""

import streamlit as st
import pandas as pd
import os
from mortality import load_table, build_life_table
from premium import single_premium, annual_premium
from reserve import reserve_table

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'clt_2010_2013.csv')

st.set_page_config(
    page_title='寿险保费计算器',
    page_icon='🛡️',
    layout='wide',
)

# ---- Header ----
st.title('定期寿险保费计算器')
st.caption('CLT 2010-2013 生命表（非养老类）· 趸缴/年缴纯保费 · 责任准备金')

# ---- Sidebar: Parameters ----
st.sidebar.header('投保参数')

age = st.sidebar.slider('投保年龄', min_value=0, max_value=80, value=30, step=1)
sum_insured = st.sidebar.number_input('保险金额（元）', min_value=10000, value=1000000, step=10000, format='%d')
term = st.sidebar.slider('保险期限（年）', min_value=1, max_value=50, value=20, step=1)
rate_pct = st.sidebar.slider('预定利率（%）', min_value=0.0, max_value=10.0, value=3.5, step=0.5)
rate = rate_pct / 100
gender = st.sidebar.radio('性别', ['男', '女'], horizontal=True)
gender_code = 'M' if gender == '男' else 'F'

# Validate
if age + term > 105:
    st.sidebar.error(f'年龄 + 期限 ({age}+{term}={age+term}) 超过极限年龄 105')
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
    st.metric('趸缴纯保费', f'¥{sp:,.0f}', help='一次性缴清的纯保费')
with col2:
    st.metric('年缴纯保费', f'¥{ap:,.0f}', help='每年初缴纳的均衡纯保费')

st.divider()

# Reserve chart
st.subheader('责任准备金曲线')
df_reserve = pd.DataFrame(reserves, columns=['Year', 'Reserve']).set_index('Year')
st.line_chart(df_reserve, height=300)

# Reserve table
st.subheader('各年末准备金明细')
df_display = pd.DataFrame(reserves, columns=['保单年度', '准备金（元）'])
df_display['准备金（元）'] = df_display['准备金（元）'].apply(lambda x: f'¥{x:,.2f}')
st.dataframe(df_display, width='stretch', hide_index=True, height=400)

# ---- Footer ----
st.divider()
st.caption(f'被保险人：{age} 岁 {gender} · 保额 ¥{sum_insured:,} · 期限 {term} 年 · 利率 {rate:.1%} · 生命表 CLT 2010-2013')
