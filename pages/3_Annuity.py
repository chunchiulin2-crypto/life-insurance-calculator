"""生存年金 · Life Annuity"""

import streamlit as st
import os
from life_table_cache import cached_life_table
from mortality import table_max_age
from ml_mortality import train_model, get_ml_life_table
from ml_underwriting import (train_uw_model, predict_risk_factor, classify_risk,
                             uw_model_metrics, feature_importance_df)

from premium import annuity_price
from ui_components import render_metric_row, render_param_chips, section_panel
from validation import validate_term

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'clt_2010_2013.csv')
T = {
    'zh': {
        'title': '生存年金 · Life Annuity',
        'caption': '活着每年领钱 · 趸缴购买价格 = 年领金额 × äx:n⌉',
        'table_label': 'Life Table',
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
        'formula_title': '精算原理',
        'formula_1': r'''\text{Price} = R \cdot \ddot{a}_{x:n}^{(m)}''',
        'formula_explain': '趸缴购买价格 = 年领取金额 × m次付期初付年金现值',
        'formula_detail': 'ä(m)x:n 考虑了生存概率和利率折现。m次付意味着每年分 m 次领取（如月领 m=12），每次领取金额 = 年金额/m。',
        'nav_home': '首页', 'nav_term': '定期寿险', 'nav_whole_life': '终身寿险',
        'nav_annuity': '生存年金', 'nav_endowment': '两全保险', 'nav_def_annuity': '递延年金',
        'nav_def_assurance': '递延寿险', 'nav_pure_endow': '纯生存保险',
        'help_annual': '年领总额 ¥{annual} · 分{m}次',
        'reserve_curve': 'Reserve Curve',
        'survival_curve': 'Survival Probability',
        'deferral_vs_coverage': 'Deferral vs Coverage',
        'survival_to_maturity': 'Survival to Maturity',
        'caption_summary': '趸缴 ≈ 年领金额 × {ratio} 倍 · 共领 {term} 年 · 每次 ¥{per}',
        'ml_source_label': '死亡率来源', 'ml_source_traditional': '传统生命表', 'ml_source_ai': 'AI 预测',
        'ml_source_help': 'AI 模型基于年龄/性别/吸烟/BMI/运动/收入预测死亡率',
        'ml_smoker': '吸烟', 'ml_bmi': 'BMI', 'ml_exercise': '运动', 'ml_exercise_low': '少', 'ml_exercise_mid': '中', 'ml_exercise_high': '多',
        'ml_income': '收入', 'ml_income_low': '低', 'ml_income_mid': '中', 'ml_income_high': '高',
        'ml_ai_note': 'AI 基于 GradientBoosting 预测，MAE<0.002，R²>0.99',
    },
    'en': {
        'title': 'Life Annuity',
        'caption': 'Periodic payments while alive · Purchase Price = Annual Payment × äx:n⌉',
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
        'formula_title': 'Actuarial Formula',
        'formula_1': r'''\text{Price} = R \cdot \ddot{a}_{x:n}^{(m)}''',
        'formula_explain': 'Lump-sum price = Annual payment × m-thly annuity-due',
        'formula_detail': 'ä(m)x:n accounts for survival probability and interest discount. m-thly means payments are split m times per year (e.g. monthly m=12), each payment = annual/m.',
        'nav_home': 'Home', 'nav_term': 'Term Life', 'nav_whole_life': 'Whole Life',
        'nav_annuity': 'Life Annuity', 'nav_endowment': 'Endowment', 'nav_def_annuity': 'Deferred Annuity',
        'nav_def_assurance': 'Deferred Assurance', 'nav_pure_endow': 'Pure Endowment',
        'help_annual': 'Annual total ¥{annual} · {m} payments/year',
        'reserve_curve': 'Reserve Curve',
        'survival_curve': 'Survival Probability',
        'deferral_vs_coverage': 'Deferral vs Coverage',
        'survival_to_maturity': 'Survival to Maturity',
        'caption_summary': 'Lump sum ≈ Annual × {ratio}× · {term}yr · ¥{per}/payment',
        'ml_source_label': 'Mortality Source', 'ml_source_traditional': 'Traditional Table', 'ml_source_ai': 'AI Prediction',
        'ml_source_help': 'ML model predicts qx from age/gender/smoking/BMI/exercise/income',
        'ml_smoker': 'Smoker', 'ml_bmi': 'BMI', 'ml_exercise': 'Exercise', 'ml_exercise_low': 'Low', 'ml_exercise_mid': 'Medium', 'ml_exercise_high': 'High',
        'ml_income': 'Income', 'ml_income_low': 'Low', 'ml_income_mid': 'Medium', 'ml_income_high': 'High',
        'ml_ai_note': 'AI via GradientBoosting, MAE<0.002, R²>0.99',
    },
    'zh-Hant': {
        'title': '生存年金 · Life Annuity',
        'caption': '活著每年領錢 · 躉繳購買價格 = 年領金額 × äx:n⌉',
        'table_label': 'Life Table', 'table_clt': 'CLT 2010-2013',
        'table_am92ult': 'AM92 Ultimate', 'table_am92sel': 'AM92 Select', 'table_am92sel_plusone': 'AM92 Select+1',
        'age': '投保年齡', 'payment': '年領金額（元）', 'term': '領取年限',
        'rate': '預定利率（%）', 'gender': '性別', 'gender_m': '男', 'gender_f': '女',
        'freq_payout': '領取頻率', 'freq_annual': '年領', 'freq_semi': '半年領', 'freq_quarterly': '季領', 'freq_monthly': '月領',
        'price': '躉繳購買價格', 'price_help': '一次性購買該年金的保費',
        'formula': '購買價格 = 年領金額 × ä(m){age}:{term}⌉',
        'footer': '{age}歲 {gender} · 年領¥{sum:,} · {term}年 · 利率{rate:.1%}',
        'formula_title': '精算原理',
        'formula_1': r'''\text{Price} = R \cdot \ddot{a}_{x:n}^{(m)}''',
        'formula_explain': '躉繳購買價格 = 年領取金額 × m次付期初付年金現值',
        'formula_detail': 'ä(m)x:n 考慮了生存機率和利率折現。m次付意味著每年分 m 次領取（如月領 m=12），每次領取金額 = 年金額/m。',
        'nav_home': '首頁', 'nav_term': '定期壽險', 'nav_whole_life': '終身壽險',
        'nav_annuity': '生存年金', 'nav_endowment': '兩全保險', 'nav_def_annuity': '遞延年金',
        'nav_def_assurance': '遞延壽險', 'nav_pure_endow': '純生存保險',
        'help_annual': '年領總額 ¥{annual} · 分{m}次',
        'reserve_curve': 'Reserve Curve',
        'survival_curve': 'Survival Probability',
        'deferral_vs_coverage': 'Deferral vs Coverage',
        'survival_to_maturity': 'Survival to Maturity',
        'caption_summary': '躉繳 ≈ 年領金額 × {ratio} 倍 · 共領 {term} 年 · 每次 ¥{per}',
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

CURRENT_PAGE = 'annuity'
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
<a href="/Annuity" target="_self" class="nav-pill" style="color:#1D1D1F;border-color:#AEAEB2;">{t('nav_annuity')}</a>
<a href="/Endowment" target="_self" class="nav-pill">{t('nav_endowment')}</a>
<a href="/Deferred_Annuity" target="_self" class="nav-pill">{t('nav_def_annuity')}</a>
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

# Sidebar — annuity uses different qx assumption (no risk class needed for liability)
max_age = 120 if use_ml else table_max_age(st.session_state.table_col)
age = st.sidebar.slider(t('age'), 0, max_age - 1, min(60, max_age - 1))
annual_payment = st.sidebar.number_input(t('payment'), 1000, 10000000, 50000, 1000, format='%d')
term = st.sidebar.slider(t('term'), 1, max_age - age, min(20, max_age - age))
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

try:
    validate_term(age, term, max_age)
except ValueError as exc:
    st.sidebar.error(str(exc))
    st.stop()

# Calculate
import pandas as pd
from reserve import annuity_reserve_table

if use_ml:
    lt = get_ml_life_table(gender_code, ml_params)
else:
    lt = cached_life_table(st.session_state.table_path, st.session_state.table_col, gender_code)
price = annuity_price(lt, age, annual_payment, term, rate, payout_m=payout_m)
per_payment = annual_payment / payout_m

# Display
param_items = [
    (t('age'), f'{age}'), (t('gender'), gender), (t('payment'), f'¥{annual_payment:,}'),
    (t('term'), f'{term}yr'), (t('rate'), f'{rate*100:.1f}%'), ('领取', payout_label),
]
render_param_chips(param_items)

render_metric_row([
    {'label': t('price'), 'value': f'¥{price:,.0f}', 'help': t('price_help')},
    {
        'label': f'每次领取 ({payout_label})',
        'value': f'¥{per_payment:,.0f}',
        'help': t('help_annual', annual=f'{annual_payment:,}', m=payout_m),
    },
])
st.caption(t('caption_summary', ratio=f'{price/annual_payment:.1f}', term=term, per=f'{per_payment:,.0f}'))

with st.expander(t('formula_title'), expanded=False):
    st.latex(t('formula_1'))
    st.caption(t('formula_explain'))
    st.caption(t('formula_detail'))

# Reserve curve
st.divider()
with section_panel(t('reserve_curve')):
    reserves = annuity_reserve_table(lt, age, annual_payment, term, rate, payout_m)
    df_r = pd.DataFrame(reserves, columns=['Year', 'Reserve']).set_index('Year')
    st.line_chart(df_r, height=300)

# Survival probability curve
with section_panel(t('survival_curve')):
    x_idx = lt[lt['age'] == age].index[0]
    lx = lt.loc[x_idx, 'lx']
    surv_data = []
    for t_val in range(term + 1):
        if x_idx + t_val < len(lt):
            lxt = lt.loc[x_idx + t_val, 'lx']
            tpx = lxt / lx if lx > 0 else 0
            surv_data.append({'Year': t_val, 't_p_x': tpx})
    df_s = pd.DataFrame(surv_data).set_index('Year')
    st.line_chart(df_s, height=250)

st.divider()

st.caption(t('footer', age=age, gender=gender, sum=annual_payment, term=term, rate=rate))
