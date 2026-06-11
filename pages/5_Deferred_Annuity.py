"""递延终身年金 · Deferred Life Annuity"""

import streamlit as st
import pandas as pd
import os
from mortality import load_table, build_life_table, table_max_age
from ml_mortality import train_model, get_ml_life_table
from ml_underwriting import (train_uw_model, predict_risk_factor, classify_risk,
                             uw_model_metrics, feature_importance_df)

from premium import deferred_annuity_premium, deferred_annuity_lump_sum, periodic_premium

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'clt_2010_2013.csv')
T = {
    'zh': {
        'title': '递延终身年金 · Deferred Annuity',
        'caption': '先缴费 · 后领钱 · 活多久领多久',
        'table_label': 'Life Table',
        'table_clt': 'CLT 2010-2013',
        'table_am92ult': 'AM92 Ultimate',
        'table_am92sel': 'AM92 Select',
        'table_am92sel_plusone': 'AM92 Select+1',
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
        'formula_title': '精算原理',
        'formula_1': r'''P \cdot \ddot{a}_{x:\text{defer}}^{(m)} = R \cdot v^{\text{defer}} \cdot {}_{\text{defer}}p_x \cdot \ddot{a}_{x+\text{defer}}^{(p)}''',
        'formula_explain': '缴费期保费现值 = 递延后的终身年金期望现值',
        'formula_detail': '缴费期缴纳保费（m次/年），递延期后开始终身领取（p次/年）。核心是递延因子 v^defer × defer_p_x。',
        'phase_title': '缴费期 vs 领取期', 'phase_pay': '缴费期 (Pay)', 'phase_receive': '领取期 (Receive)',
        'nav_home': '首页', 'nav_term': '定期寿险', 'nav_whole_life': '终身寿险',
        'nav_annuity': '生存年金', 'nav_endowment': '两全保险', 'nav_def_annuity': '递延年金',
        'nav_def_assurance': '递延寿险', 'nav_pure_endow': '纯生存保险',
        'help_annual': '年领总额 ¥{annual} · 分{m}次',
        'caption_summary': '缴费 {defer} 年 · 年缴 ¥{ap} · {retire} 岁起年领 ¥{annual} 终身',
        'ml_source_label': '死亡率来源', 'ml_source_traditional': '传统生命表', 'ml_source_ai': 'AI 预测',
        'ml_source_help': 'AI 模型基于年龄/性别/吸烟/BMI/运动/收入预测死亡率',
        'ml_smoker': '吸烟', 'ml_bmi': 'BMI', 'ml_exercise': '运动', 'ml_exercise_low': '少', 'ml_exercise_mid': '中', 'ml_exercise_high': '多',
        'ml_income': '收入', 'ml_income_low': '低', 'ml_income_mid': '中', 'ml_income_high': '高',
        'ml_ai_note': 'AI 基于 GradientBoosting 预测，MAE<0.002，R²>0.99',
    },
    'en': {
        'title': 'Deferred Life Annuity',
        'caption': 'Pay now · Receive later · For life',
        'table_label': 'Life Table',
        'table_clt': 'CLT 2010-2013',
        'table_am92ult': 'AM92 Ultimate',
        'table_am92sel': 'AM92 Select',
        'table_am92sel_plusone': 'AM92 Select+1',
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
        'formula_title': 'Actuarial Formula',
        'formula_1': r'''P \cdot \ddot{a}_{x:\text{defer}}^{(m)} = R \cdot v^{\text{defer}} \cdot {}_{\text{defer}}p_x \cdot \ddot{a}_{x+\text{defer}}^{(p)}''',
        'formula_explain': 'PV of premiums during deferral = Deferred EPV of lifetime annuity',
        'formula_detail': 'Pay premiums (m-thly) during deferral, then receive (p-thly) for life after deferral. The key is the deferral factor v^defer × defer_p_x.',
        'phase_title': 'Pay-in vs Pay-out', 'phase_pay': 'Pay-in Phase', 'phase_receive': 'Pay-out Phase',
        'nav_home': 'Home', 'nav_term': 'Term Life', 'nav_whole_life': 'Whole Life',
        'nav_annuity': 'Life Annuity', 'nav_endowment': 'Endowment', 'nav_def_annuity': 'Deferred Annuity',
        'nav_def_assurance': 'Deferred Assurance', 'nav_pure_endow': 'Pure Endowment',
        'help_annual': 'Annual total ¥{annual} · {m} payments/year',
        'caption_summary': 'Pay {defer}yr · ¥{ap}/yr · Annuity from age {retire}: ¥{annual}/yr for life',
        'ml_source_label': 'Mortality Source', 'ml_source_traditional': 'Traditional Table', 'ml_source_ai': 'AI Prediction',
        'ml_source_help': 'ML model predicts qx from age/gender/smoking/BMI/exercise/income',
        'ml_smoker': 'Smoker', 'ml_bmi': 'BMI', 'ml_exercise': 'Exercise', 'ml_exercise_low': 'Low', 'ml_exercise_mid': 'Medium', 'ml_exercise_high': 'High',
        'ml_income': 'Income', 'ml_income_low': 'Low', 'ml_income_mid': 'Medium', 'ml_income_high': 'High',
        'ml_ai_note': 'AI via GradientBoosting, MAE<0.002, R²>0.99',
    },
    'zh-Hant': {
        'title': '遞延年金 · Deferred Annuity',
        'caption': '先繳費 · 後領錢 · 存活時每年領取',
        'table_label': 'Life Table', 'table_clt': 'CLT 2010-2013',
        'table_am92ult': 'AM92 Ultimate', 'table_am92sel': 'AM92 Select', 'table_am92sel_plusone': 'AM92 Select+1',
        'age': '目前年齡', 'retire_age': '開始領取年齡', 'payment': '年領金額（元）',
        'rate': '預定利率（%）', 'gender': '性別', 'gender_m': '男', 'gender_f': '女',
        'freq_label': '繳費頻率', 'freq_annual': '年繳', 'freq_semi': '半年繳', 'freq_quarterly': '季繳', 'freq_monthly': '月繳',
        'freq_payout_label': '領取頻率', 'freq_payout_annual': '年領', 'freq_payout_semi': '半年領', 'freq_payout_quarterly': '季領', 'freq_payout_monthly': '月領',
        'per_payment': '每期繳費', 'annual_premium': '年繳保費', 'lump_sum': '躉繳純保費', 'lump_sum_help': '一次性繳清的公平價格',
        'per_payout': '每次領取',
        'how_it_works': '繳費 {defer} 年（{age}→{retire}歲），然後每年領 ¥{pay:,} 直到身故。',
        'summary': '{age}歲開始繳費 · {defer}年繳費期 · {retire}歲開始領錢 · 年領 ¥{pay:,} · 終身',
        'footer': '{age}歲 {gender} · 繳費{defer}年至{retire}歲 · 年領¥{pay:,} · 終身 · 利率{rate:.1%}',
        'formula_title': '精算原理',
        'formula_1': r'''P \cdot \ddot{a}_{x:\text{defer}}^{(m)} = R \cdot v^{\text{defer}} \cdot {}_{\text{defer}}p_x \cdot \ddot{a}_{x+\text{defer}}^{(p)}''',
        'formula_explain': '繳費期保費現值 = 遞延後的終身年金期望現值',
        'formula_detail': '繳費期繳納保費（m次/年），遞延期後開始終身領取（p次/年）。核心是遞延因子 v^defer × defer_p_x。',
        'phase_title': '繳費期 vs 領取期', 'phase_pay': '繳費期 (Pay)', 'phase_receive': '領取期 (Receive)',
        'nav_home': '首頁', 'nav_term': '定期壽險', 'nav_whole_life': '終身壽險',
        'nav_annuity': '生存年金', 'nav_endowment': '兩全保險', 'nav_def_annuity': '遞延年金',
        'nav_def_assurance': '遞延壽險', 'nav_pure_endow': '純生存保險',
        'help_annual': '年領總額 ¥{annual} · 分{m}次',
        'caption_summary': '繳費 {defer} 年 · 年繳 ¥{ap} · {retire} 歲起年領 ¥{annual} 終身',
        'ml_source_label': '死亡率來源', 'ml_source_traditional': '傳統生命表', 'ml_source_ai': 'AI 預測',
        'ml_source_help': 'AI 模型基於年齡/性別/吸菸/BMI/運動/收入預測死亡率',
        'ml_smoker': '吸菸', 'ml_bmi': 'BMI', 'ml_exercise': '運動', 'ml_exercise_low': '少', 'ml_exercise_mid': '中', 'ml_exercise_high': '多',
        'ml_income': '收入', 'ml_income_low': '低', 'ml_income_mid': '中', 'ml_income_high': '高',
        'ml_ai_note': 'AI 基於 GradientBoosting 預測，MAE<0.002，R²>0.99',
    },
}


def t(key, **kw):
    lang = st.session_state.get('lang', 'zh')
    if lang not in T or key not in T.get(lang, {}):
        lang = 'zh'
    text = T[lang][key]
    return text.format(**kw) if kw else text

CURRENT_PAGE = 'def_annuity'
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
<a href="/Deferred_Annuity" target="_self" class="nav-pill" style="color:#1D1D1F;border-color:#AEAEB2;">{t('nav_def_annuity')}</a>
<a href="/Deferred_Assurance" target="_self" class="nav-pill">{t('nav_def_assurance')}</a>
<a href="/Pure_Endowment" target="_self" class="nav-pill">{t('nav_pure_endow')}</a>
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

# Sidebar — Basic
max_age = 120 if use_ml else table_max_age(st.session_state.table_col)
age = st.sidebar.slider(t('age'), 0, max_age - 1, 25)
retire_age = st.sidebar.slider(t('retire_age'), age + 1, max_age, min(60, max_age))
gender = st.sidebar.radio(t('gender'), [t('gender_m'), t('gender_f')], horizontal=True)
gender_code = 'M' if gender == t('gender_m') else 'F'
annual_payment = st.sidebar.number_input(t('payment'), 1000, 10000000, 50000, 1000, format='%d')
rate = st.sidebar.slider(t('rate'), 0.0, 10.0, 3.5, 0.5) / 100

defer = retire_age - age

if age + defer > max_age:
    st.sidebar.error(f'开始领取年龄超过极限年龄 {max_age}')
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
def get_lt(g, tp, tc):
    return build_life_table(load_table(tp), g if tc == 'clt' else tc)

if use_ml:
    lt = get_ml_life_table(gender_code, ml_params)
else:
    lt = get_lt(gender_code, st.session_state.table_path, st.session_state.table_col)
ap = deferred_annuity_premium(lt, age, defer, annual_payment, rate, m=freq_m, payout_m=payout_m)
payment = periodic_premium(ap, freq_m)
lump = deferred_annuity_lump_sum(lt, age, defer, annual_payment, rate, payout_m=payout_m)
per_payout = annual_payment / payout_m

# Display
param_items = [
    (t('age'), f'{age}'), (t('gender'), gender), (t('retire_age'), f'{retire_age}'),
    (t('payment'), f'¥{annual_payment:,}'), (t('rate'), f'{rate*100:.1f}%'),
    ('缴费', freq_label), ('领取', payout_label),
]
chips = ' '.join([f'<span class="param-chip">{k}: {v}</span>' for k, v in param_items])
st.markdown(f'<div class="param-chips">{chips}</div>', unsafe_allow_html=True)

st.info(t('how_it_works', defer=defer, age=age, retire=retire_age, pay=annual_payment))

c1, c2, c3, c4 = st.columns(4)
c1.metric(f'{t("per_payment")} ({freq_label})', f'¥{payment:,.0f}')
c2.metric(t('annual_premium'), f'¥{ap:,.0f}')
c3.metric(t('lump_sum'), f'¥{lump:,.0f}', help=t('lump_sum_help'))
c4.metric(f'{t("per_payout")} ({payout_label})', f'¥{per_payout:,.0f}',
          help=t('help_annual', annual=f'{annual_payment:,}', m=payout_m))
st.caption(t('caption_summary', defer=defer, ap=f'{ap:,.0f}', retire=retire_age, annual=f'{annual_payment:,}'))

with st.expander(t('formula_title'), expanded=False):
    st.latex(t('formula_1'))
    st.caption(t('formula_explain'))
    st.caption(t('formula_detail'))

st.divider()

with st.container(border=True):
    st.subheader(t('phase_title'))
    timeline_data = pd.DataFrame({
        'Year': list(range(defer + 30)),
        'Phase': [t('phase_pay')] * defer + [t('phase_receive')] * 30,
        'Cash Flow': [-ap] * defer + [annual_payment] * 30,
    })
    st.bar_chart(timeline_data.set_index('Year')['Cash Flow'], height=250)

st.divider()
st.caption(t('footer', age=age, gender=gender, defer=defer, retire=retire_age, pay=annual_payment, rate=rate))
