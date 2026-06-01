"""纯生存保险 · Pure Endowment"""

import streamlit as st
import os
from mortality import load_table, build_life_table, table_max_age
from ml_mortality import train_model, get_ml_life_table
from ml_underwriting import (train_uw_model, predict_risk_factor, classify_risk,
                             uw_model_metrics, feature_importance_df)

from premium import pure_endowment_single_premium, pure_endowment_annual_premium, periodic_premium

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'clt_2010_2013.csv')
T = {
    'zh': {
        'title': '纯生存保险 · Pure Endowment',
        'caption': '活到约定年龄 → 拿钱 · 中途死亡 → 不赔付',
        'table_label': 'Life Table',
        'table_clt': 'CLT 2010-2013',
        'table_am92ult': 'AM92 Ultimate',
        'table_am92sel': 'AM92 Select',
        'table_am92sel_plusone': 'AM92 Select+1',
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
        'formula_title': '精算原理',
        'formula_1': r'''{}_nE_x = v^n \cdot {}_np_x''',
        'formula_explain': '纯生存保险现值 = 折现因子 × 存活到满期的概率',
        'formula_detail': '只有活到约定年龄才给付。本质上是一个生存-contingent 的零息债券。准备金从 0 稳步增长到满期保额。',
        'nav_home': '首页', 'nav_term': '定期寿险', 'nav_whole_life': '终身寿险',
        'nav_annuity': '生存年金', 'nav_endowment': '两全保险', 'nav_def_annuity': '递延年金',
        'nav_def_assurance': '递延寿险', 'nav_pure_endow': '纯生存保险',
        'caption_summary': '{freq}缴费 {defer} 年 · 年缴 ¥{ap} · 活到 {maturity} 岁领 ¥{sum_insured}',
        'ml_source_label': '死亡率来源', 'ml_source_traditional': '传统生命表', 'ml_source_ai': 'AI 预测',
        'ml_source_help': 'AI 模型基于年龄/性别/吸烟/BMI/运动/收入预测死亡率',
        'ml_smoker': '吸烟', 'ml_bmi': 'BMI', 'ml_exercise': '运动', 'ml_exercise_low': '少', 'ml_exercise_mid': '中', 'ml_exercise_high': '多',
        'ml_income': '收入', 'ml_income_low': '低', 'ml_income_mid': '中', 'ml_income_high': '高',
        'ml_ai_note': 'AI 基于 GradientBoosting 预测，MAE<0.002，R²>0.99',
        'caption_prob': '活到 {maturity} 岁的概率 ≈ {prob}',
    },
    'en': {
        'title': 'Pure Endowment',
        'caption': 'Survive to maturity → receive lump sum · Die before → nothing',
        'table_label': 'Life Table',
        'table_clt': 'CLT 2010-2013',
        'table_am92ult': 'AM92 Ultimate',
        'table_am92sel': 'AM92 Select',
        'table_am92sel_plusone': 'AM92 Select+1',
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
        'formula_title': 'Actuarial Formula',
        'formula_1': r'''{}_nE_x = v^n \cdot {}_np_x''',
        'formula_explain': 'Pure endowment PV = Discount factor × probability of surviving to maturity',
        'formula_detail': 'Only pays if the insured survives to the maturity age. Essentially a survival-contingent zero-coupon bond. Reserve grows steadily from 0 to the sum insured.',
        'nav_home': 'Home', 'nav_term': 'Term Life', 'nav_whole_life': 'Whole Life',
        'nav_annuity': 'Life Annuity', 'nav_endowment': 'Endowment', 'nav_def_annuity': 'Deferred Annuity',
        'nav_def_assurance': 'Deferred Assurance', 'nav_pure_endow': 'Pure Endowment',
        'caption_summary': '{freq} × {defer}yr · ¥{ap}/yr · Survive to {maturity}, receive ¥{sum_insured}',
        'ml_source_label': 'Mortality Source', 'ml_source_traditional': 'Traditional Table', 'ml_source_ai': 'AI Prediction',
        'ml_source_help': 'ML model predicts qx from age/gender/smoking/BMI/exercise/income',
        'ml_smoker': 'Smoker', 'ml_bmi': 'BMI', 'ml_exercise': 'Exercise', 'ml_exercise_low': 'Low', 'ml_exercise_mid': 'Medium', 'ml_exercise_high': 'High',
        'ml_income': 'Income', 'ml_income_low': 'Low', 'ml_income_mid': 'Medium', 'ml_income_high': 'High',
        'ml_ai_note': 'AI via GradientBoosting, MAE<0.002, R²>0.99',
        'caption_prob': 'Probability of surviving to age {maturity} ≈ {prob}',
    },
    'zh-Hant': {
        'title': '純生存保險 · Pure Endowment',
        'caption': '活到約定年齡 → 領錢 · 中途死亡 → 不給付',
        'table_label': 'Life Table', 'table_clt': 'CLT 2010-2013',
        'table_am92ult': 'AM92 Ultimate', 'table_am92sel': 'AM92 Select', 'table_am92sel_plusone': 'AM92 Select+1',
        'age': '目前年齡', 'maturity_age': '約定領錢年齡', 'sum': '滿期保險金（元）',
        'rate': '預定利率（%）', 'gender': '性別', 'gender_m': '男', 'gender_f': '女',
        'freq_label': '繳費頻率', 'freq_annual': '年繳', 'freq_semi': '半年繳', 'freq_quarterly': '季繳', 'freq_monthly': '月繳',
        'per_payment': '每期保費', 'annual_premium': '年繳保費', 'lump_sum': '躉繳純保費',
        'summary': '{age}歲起繳{defer}年 · 活到{maturity}歲 → 領取¥{sum:,} · 中途死亡 → 不給付',
        'note': '純生存保險 = 只有生存給付，無死亡給付 · 類似定期儲蓄，活到約定年齡才兌現',
        'footer': '{age}歲 {gender} · 繳費{defer}年至{maturity}歲 · 滿期金¥{sum:,} · 利率{rate:.1%}',
        'formula_title': '精算原理',
        'formula_1': r'''{}_nE_x = v^n \cdot {}_np_x''',
        'formula_explain': '純生存保險現值 = 折現因子 × 存活到滿期的機率',
        'formula_detail': '只有活到約定年齡才給付。本質上是一個生存-contingent 的零息債券。準備金從 0 穩步增長到滿期保額。',
        'nav_home': '首頁', 'nav_term': '定期壽險', 'nav_whole_life': '終身壽險',
        'nav_annuity': '生存年金', 'nav_endowment': '兩全保險', 'nav_def_annuity': '遞延年金',
        'nav_def_assurance': '遞延壽險', 'nav_pure_endow': '純生存保險',
        'caption_summary': '{freq}繳費 {defer} 年 · 年繳 ¥{ap} · 活到 {maturity} 歲領 ¥{sum_insured}',
        'ml_source_label': '死亡率來源', 'ml_source_traditional': '傳統生命表', 'ml_source_ai': 'AI 預測',
        'ml_source_help': 'AI 模型基於年齡/性別/吸菸/BMI/運動/收入預測死亡率',
        'ml_smoker': '吸菸', 'ml_bmi': 'BMI', 'ml_exercise': '運動', 'ml_exercise_low': '少', 'ml_exercise_mid': '中', 'ml_exercise_high': '多',
        'ml_income': '收入', 'ml_income_low': '低', 'ml_income_mid': '中', 'ml_income_high': '高',
        'ml_ai_note': 'AI 基於 GradientBoosting 預測，MAE<0.002，R²>0.99',
        'caption_prob': '活到 {maturity} 歲的機率 ≈ {prob}',
    },
}


def t(key, **kw):
    text = T[st.session_state.lang][key]
    return text.format(**kw) if kw else text

CURRENT_PAGE = 'pure_endow'
ACTIVE_STYLE = ' style="color:#1D1D1F;border-color:#AEAEB2;"'


if 'lang' not in st.session_state:
    st.session_state.lang = 'zh'

st.set_page_config(page_title=t('title'), layout='wide', initial_sidebar_state='expanded')
st.title(t('title'))
st.caption(t('caption'))

st.markdown(f"""
<div class="nav-strip">
<a href="/" target="_self" class="nav-pill">{t('nav_home')}</a>
<a href="/Term_Life" target="_self" class="nav-pill">{t('nav_term')}</a>
<a href="/Whole_Life" target="_self" class="nav-pill">{t('nav_whole_life')}</a>
<a href="/Annuity" target="_self" class="nav-pill">{t('nav_annuity')}</a>
<a href="/Endowment" target="_self" class="nav-pill">{t('nav_endowment')}</a>
<a href="/Deferred_Annuity" target="_self" class="nav-pill">{t('nav_def_annuity')}</a>
<a href="/Deferred_Assurance" target="_self" class="nav-pill">{t('nav_def_assurance')}</a>
<a href="/Pure_Endowment" target="_self" class="nav-pill" style="color:#1D1D1F;border-color:#AEAEB2;">{t('nav_pure_endow')}</a>
""", unsafe_allow_html=True)

# Sidebar — Mortality Source Selector
use_ml = False
ml_params = None
ml_source = st.sidebar.radio(
    t('ml_source_label'),
    [t('ml_source_traditional'), t('ml_source_ai')],
    horizontal=True,
    help=t('ml_source_help'),
)
if ml_source == t('ml_source_ai'):
    use_ml = True
    train_model()
    col_a, col_b = st.sidebar.columns(2)
    with col_a:
        ml_smoker = 1 if st.checkbox(t('ml_smoker'), value=False) else 0
        ml_bmi = st.slider(t('ml_bmi'), 16.0, 42.0, 23.0, 0.5)
    with col_b:
        ex_map = {t('ml_exercise_low'): 0, t('ml_exercise_mid'): 1, t('ml_exercise_high'): 2}
        ml_exercise = st.selectbox(t('ml_exercise'), list(ex_map.keys()))
        in_map = {t('ml_income_low'): 0, t('ml_income_mid'): 1, t('ml_income_high'): 2}
        ml_income = st.selectbox(t('ml_income'), list(in_map.keys()))
    ml_params = {'smoker': ml_smoker, 'bmi': ml_bmi,
                 'exercise': ex_map[ml_exercise], 'income': in_map[ml_income]}
    st.sidebar.caption(t('ml_ai_note'))

st.sidebar.divider()

# Sidebar
max_age = 120 if use_ml else table_max_age(st.session_state.table_col)
age = st.sidebar.slider(t('age'), 0, max_age - 1, 20)
maturity_age = st.sidebar.slider(t('maturity_age'), age + 1, max_age, min(40, max_age))
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

if age + defer > max_age:
    st.sidebar.error(f'年龄超过极限年龄 {max_age}')
    st.stop()

# Calculate
import pandas as pd
from reserve import pure_endowment_reserve_table

@st.cache_data
def get_lt(g, tp, tc):
    return build_life_table(load_table(tp), g if tc == 'clt' else tc)

if use_ml:
    lt = get_ml_life_table(gender_code, ml_params)
else:
    lt = get_lt(gender_code, st.session_state.table_path, st.session_state.table_col)
sp = pure_endowment_single_premium(lt, age, sum_insured, defer, rate)
ap = pure_endowment_annual_premium(lt, age, sum_insured, defer, rate)
payment = periodic_premium(ap, freq_m)

# Display
param_items = [
    (t('age'), f'{age}'), (t('gender'), gender), (t('maturity_age'), f'{maturity_age}'),
    (t('sum'), f'¥{sum_insured:,}'), (t('rate'), f'{rate*100:.1f}%'), (t('freq_label'), freq_label),
]
chips = ' '.join([f'<span class="param-chip">{k}: {v}</span>' for k, v in param_items])
st.markdown(f'<div class="param-chips">{chips}</div>', unsafe_allow_html=True)

st.info(t('note'))

c1, c2, c3 = st.columns(3)
c1.metric(f'{t("per_payment")} ({freq_label})', f'¥{payment:,.0f}')
c2.metric(t('annual_premium'), f'¥{ap:,.0f}')
c3.metric(t('lump_sum'), f'¥{sp:,.0f}')
st.caption(t('caption_summary', freq=freq_label, defer=defer, ap=f'{ap:,.0f}', maturity=maturity_age, sum_insured=f'{sum_insured:,}'))

with st.expander(t('formula_title'), expanded=False):
    st.latex(t('formula_1'))
    st.caption(t('formula_explain'))
    st.caption(t('formula_detail'))

st.divider()

with st.container(border=True):
    st.subheader('准备金曲线 · Reserve Curve')
    reserves = pure_endowment_reserve_table(lt, age, sum_insured, defer, rate)
    df_r = pd.DataFrame(reserves, columns=['Year', 'Reserve']).set_index('Year')
    st.line_chart(df_r, height=300)

with st.container(border=True):
    st.subheader('满期生存概率 · Survival to Maturity')
    x_idx = lt[lt['age'] == age].index[0]
    lx = lt.loc[x_idx, 'lx']
    surv_data = []
    for t_val in range(defer + 1):
        if x_idx + t_val < len(lt):
            lxt = lt.loc[x_idx + t_val, 'lx']
            tpx = lxt / lx if lx > 0 else 0
            surv_data.append({'Year': t_val, 't_p_x': tpx})
    df_s = pd.DataFrame(surv_data).set_index('Year')
    st.line_chart(df_s, height=250)
    if surv_data:
        maturity_prob = surv_data[-1]['t_p_x']
        st.caption(t('caption_prob', maturity=maturity_age, prob=f'{maturity_prob:.1%}'))

st.divider()
st.caption(t('footer', age=age, gender=gender, defer=defer, maturity=maturity_age, sum=sum_insured, rate=rate))
