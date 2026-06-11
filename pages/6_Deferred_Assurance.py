"""递延寿险 · Deferred Life Assurance"""

import streamlit as st
import pandas as pd
import os
from mortality import load_table, build_life_table, table_max_age

from ml_mortality import train_model, get_ml_life_table
from ml_underwriting import (train_uw_model, predict_risk_factor, classify_risk,
                             uw_model_metrics, feature_importance_df)

from premium import (deferred_whole_life_annual_premium, deferred_term_annual_premium,
                     deferred_whole_life_single_premium, deferred_term_single_premium,
                     periodic_premium)
from reserve import deferred_assurance_reserve_table

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
        'formula_title': '精算原理',
        'formula_1': r'''{}_{n|}A_x = v^n \cdot {}_np_x \cdot A_{x+n}''',
        'formula_explain': '递延寿险 = 生存到保障开始时的概率 × 折现 × 当时的寿险趸缴保费',
        'formula_detail': '递延期内死亡不赔付。只有活到保障开始年龄，保障才生效。准备金在递延期逐步积累，保障期后按对应寿险模式释放。',
        'nav_home': '首页', 'nav_term': '定期寿险', 'nav_whole_life': '终身寿险',
        'nav_annuity': '生存年金', 'nav_endowment': '两全保险', 'nav_def_annuity': '递延年金',
        'nav_def_assurance': '递延寿险', 'nav_pure_endow': '纯生存保险',
        'reserve_curve': 'Reserve Curve',
        'survival_curve': 'Survival Probability',
        'deferral_vs_coverage': 'Deferral vs Coverage',
        'survival_to_maturity': 'Survival to Maturity',
        'caption_summary': '{freq}缴费 {defer} 年 · 年缴 ¥{ap} · {start} 岁起保障生效',
        'advanced_options': '高级选项（核保 · 赔付 · 缴费）',
        'uw_section': '核保与赔付',
        'ml_source_label': '死亡率来源',
        'ml_source_traditional': '传统生命表',
        'ml_source_ai': 'AI 预测',
        'ml_source_help': 'AI 模型基于年龄/性别/吸烟/BMI/运动/收入预测死亡率',
        'ml_smoker': '吸烟', 'ml_bmi': 'BMI',
        'ml_exercise': '运动', 'ml_exercise_low': '少', 'ml_exercise_mid': '中', 'ml_exercise_high': '多',
        'ml_income': '收入', 'ml_income_low': '低', 'ml_income_mid': '中', 'ml_income_high': '高',
        'ml_ai_note': 'AI 基于 GradientBoosting 预测，MAE<0.002，R²>0.99',
        'ml_vs_traditional': 'AI 预测 vs 传统生命表',
        'uw_ai_label': '核保方式', 'uw_ai_manual': '人工分级', 'uw_ai_auto': 'AI 智能核保',
        'uw_ai_help': 'AI 基于健康数据自动评估风险因子',
        'uw_bmi_label': 'BMI', 'uw_bp_label': '血压 (收缩/舒张)',
        'uw_cholesterol': '总胆固醇 (mg/dL)', 'uw_family_history': '家族早逝史',
        'uw_exercise': '运动频率', 'uw_alcohol': '饮酒',
        'uw_alcohol_none': '不喝', 'uw_alcohol_moderate': '适量', 'uw_alcohol_heavy': '大量',
        'uw_occupation': '职业风险', 'uw_occ_desk': '办公室', 'uw_occ_manual': '体力劳动', 'uw_occ_hazard': '高危职业',
        'uw_chronic': '慢性病史',
        'uw_result_risk': '风险因子', 'uw_result_class': '核保等级', 'uw_result_mult': '费率乘数',
        'uw_class_pref_plus': '优选+', 'uw_class_standard': '标准体', 'uw_class_substandard': '次标准体', 'uw_class_decline': '拒保',
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
        'formula_title': 'Actuarial Formula',
        'formula_1': r'''{}_{n|}A_x = v^n \cdot {}_np_x \cdot A_{x+n}''',
        'formula_explain': 'Deferred assurance = Survival probability to coverage start × discount × net single premium at that age',
        'formula_detail': 'No benefit if death during deferral. Coverage only activates if the insured survives to the start age. Reserves accumulate during deferral and release during coverage.',
        'nav_home': 'Home', 'nav_term': 'Term Life', 'nav_whole_life': 'Whole Life',
        'nav_annuity': 'Life Annuity', 'nav_endowment': 'Endowment', 'nav_def_annuity': 'Deferred Annuity',
        'nav_def_assurance': 'Deferred Assurance', 'nav_pure_endow': 'Pure Endowment',
        'reserve_curve': 'Reserve Curve',
        'survival_curve': 'Survival Probability',
        'deferral_vs_coverage': 'Deferral vs Coverage',
        'survival_to_maturity': 'Survival to Maturity',
        'caption_summary': '{freq} × {defer}yr · ¥{ap}/yr · Cover starts at age {start}',
        'advanced_options': 'Advanced Options (UW · Payment · Frequency)',
        'uw_section': 'UW & Payment',
        'ml_source_label': 'Mortality Source', 'ml_source_traditional': 'Traditional Table', 'ml_source_ai': 'AI Prediction',
        'ml_source_help': 'ML model predicts qx from age/gender/smoking/BMI/exercise/income',
        'ml_smoker': 'Smoker', 'ml_bmi': 'BMI',
        'ml_exercise': 'Exercise', 'ml_exercise_low': 'Low', 'ml_exercise_mid': 'Medium', 'ml_exercise_high': 'High',
        'ml_income': 'Income', 'ml_income_low': 'Low', 'ml_income_mid': 'Medium', 'ml_income_high': 'High',
        'ml_ai_note': 'AI via GradientBoosting, MAE<0.002, R²>0.99',
        'ml_vs_traditional': 'AI Prediction vs Traditional Table',
        'uw_ai_label': 'Underwriting', 'uw_ai_manual': 'Manual', 'uw_ai_auto': 'AI Smart UW',
        'uw_ai_help': 'AI predicts risk factor from health data',
        'uw_bmi_label': 'BMI', 'uw_bp_label': 'BP (Sys/Dia)',
        'uw_cholesterol': 'Total Cholesterol (mg/dL)', 'uw_family_history': 'Family Early Death',
        'uw_exercise': 'Exercise', 'uw_alcohol': 'Alcohol',
        'uw_alcohol_none': 'None', 'uw_alcohol_moderate': 'Moderate', 'uw_alcohol_heavy': 'Heavy',
        'uw_occupation': 'Occupation Risk', 'uw_occ_desk': 'Desk', 'uw_occ_manual': 'Manual', 'uw_occ_hazard': 'Hazardous',
        'uw_chronic': 'Chronic Condition',
        'uw_result_risk': 'Risk Factor', 'uw_result_class': 'UW Class', 'uw_result_mult': 'Rate Multiplier',
        'uw_class_pref_plus': 'Preferred+', 'uw_class_standard': 'Standard', 'uw_class_substandard': 'Substandard', 'uw_class_decline': 'Decline',
    },
    'zh-Hant': {
        'title': '遞延壽險 · Deferred Assurance',
        'caption': '先繳費 · 後保障 · 遞延期內死亡不給付',
        'table_label': 'Life Table', 'table_clt': 'CLT 2010-2013',
        'table_am92ult': 'AM92 Ultimate', 'table_am92sel': 'AM92 Select', 'table_am92sel_plusone': 'AM92 Select+1',
        'age': '目前年齡', 'start_age': '保障開始年齡', 'sum': '保險金額（元）', 'coverage': '保障期限（年）',
        'rate': '預定利率（%）', 'gender': '性別', 'gender_m': '男', 'gender_f': '女',
        'risk_label': '核保等級', 'risk_pref': '優選體 (×0.7)', 'risk_std': '標準體 (×1.0)', 'risk_sub': '次標準體 (×2.0)',
        'payment_label': '給付時點', 'pay_eoy': '死亡年末給付', 'pay_imm': '死亡立即給付 (UDD)',
        'freq_label': '繳費頻率', 'freq_annual': '年繳', 'freq_semi': '半年繳', 'freq_quarterly': '季繳', 'freq_monthly': '月繳',
        'product_label': '保障類型', 'product_wl': '遞延終身壽險', 'product_term': '遞延定期壽險',
        'per_payment': '每期保費', 'annual_premium': '年繳保費', 'lump_sum': '躉繳純保費',
        'summary_wl': '{age}歲繳費至{start}歲 · {start}歲起保終身 · 保額¥{sum:,}',
        'summary_term': '{age}歲繳費至{start}歲 · {start}歲起保{cov}年 · 保額¥{sum:,}',
        'note': '遞延期內死亡：不給付（或退保費）· 保障從 {start} 歲開始',
        'footer': '{age}歲 {gender} · 繳費{defer}年至{start}歲 · 保障從{start}歲 · 保額¥{sum:,} · 利率{rate:.1%}',
        'formula_title': '精算原理',
        'formula_1': r'''{}_{n|}A_x = v^n \cdot {}_np_x \cdot A_{x+n}''',
        'formula_explain': '遞延壽險 = 存活到保障開始時的機率 × 折現 × 當時的壽險躉繳保費',
        'formula_detail': '遞延期內死亡不給付。只有活到保障開始年齡，保障才生效。準備金在遞延期逐步累積，保障期後按對應壽險模式釋放。',
        'nav_home': '首頁', 'nav_term': '定期壽險', 'nav_whole_life': '終身壽險',
        'nav_annuity': '生存年金', 'nav_endowment': '兩全保險', 'nav_def_annuity': '遞延年金',
        'nav_def_assurance': '遞延壽險', 'nav_pure_endow': '純生存保險',
        'reserve_curve': 'Reserve Curve',
        'survival_curve': 'Survival Probability',
        'deferral_vs_coverage': 'Deferral vs Coverage',
        'survival_to_maturity': 'Survival to Maturity',
        'caption_summary': '{freq}繳費 {defer} 年 · 年繳 ¥{ap} · {start} 歲起保障生效',
        'advanced_options': '進階選項（核保 · 給付 · 繳費）',
        'uw_section': '核保與給付',
        'ml_source_label': '死亡率來源', 'ml_source_traditional': '傳統生命表', 'ml_source_ai': 'AI 預測',
        'ml_source_help': 'AI 模型基於年齡/性別/吸菸/BMI/運動/收入預測死亡率',
        'ml_smoker': '吸菸', 'ml_bmi': 'BMI',
        'ml_exercise': '運動', 'ml_exercise_low': '少', 'ml_exercise_mid': '中', 'ml_exercise_high': '多',
        'ml_income': '收入', 'ml_income_low': '低', 'ml_income_mid': '中', 'ml_income_high': '高',
        'ml_ai_note': 'AI 基於 GradientBoosting 預測，MAE<0.002，R²>0.99',
        'ml_vs_traditional': 'AI 預測 vs 傳統生命表',
        'uw_ai_label': '核保方式', 'uw_ai_manual': '人工分級', 'uw_ai_auto': 'AI 智能核保',
        'uw_ai_help': 'AI 基於健康數據自動評估風險因子',
        'uw_bmi_label': 'BMI', 'uw_bp_label': '血壓 (收縮/舒張)',
        'uw_cholesterol': '總膽固醇 (mg/dL)', 'uw_family_history': '家族早逝史',
        'uw_exercise': '運動頻率', 'uw_alcohol': '飲酒',
        'uw_alcohol_none': '不喝', 'uw_alcohol_moderate': '適量', 'uw_alcohol_heavy': '大量',
        'uw_occupation': '職業風險', 'uw_occ_desk': '辦公室', 'uw_occ_manual': '體力勞動', 'uw_occ_hazard': '高危職業',
        'uw_chronic': '慢性病史',
        'uw_result_risk': '風險因子', 'uw_result_class': '核保等級', 'uw_result_mult': '費率乘數',
        'uw_class_pref_plus': '優選+', 'uw_class_standard': '標準體', 'uw_class_substandard': '次標準體', 'uw_class_decline': '拒保',
    },
}


def t(key, **kw):
    lang = st.session_state.get('lang', 'zh')
    if lang not in T or key not in T.get(lang, {}):
        lang = 'zh'
    text = T[lang][key]
    return text.format(**kw) if kw else text

CURRENT_PAGE = 'def_assurance'
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
<a href="/Deferred_Assurance" target="_self" class="nav-pill" style="color:#1D1D1F;border-color:#AEAEB2;">{t('nav_def_assurance')}</a>
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
start_age = st.sidebar.slider(t('start_age'), age + 1, max_age, min(45, max_age))
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
    max_cov = max_age - start_age
    coverage = st.sidebar.slider(t('coverage'), 1, max_cov, min(20, max_cov))

if start_age + (coverage if is_term else 0) > max_age:
    st.sidebar.error(f'保障期限超过极限年龄 {max_age}')
    st.stop()

# Sidebar — Advanced
with st.sidebar.expander(t('advanced_options'), expanded=False):
    st.caption(t('uw_section'))
    # -- AI Underwriting Toggle --
    uw_mode = st.radio(t('uw_ai_label'), [t('uw_ai_manual'), t('uw_ai_auto')],
                       horizontal=True, help=t('uw_ai_help'))
    use_ai_uw = (uw_mode == t('uw_ai_auto'))

    if use_ai_uw:
        train_uw_model()
        col_u1, col_u2 = st.columns(2)
        with col_u1:
            uw_bmi = st.slider(t('uw_bmi_label'), 16.0, 45.0, 23.0, 0.5)
            uw_sys = st.slider(t('uw_bp_label'), 90, 200, (110, 130))
            uw_chol = st.slider(t('uw_cholesterol'), 120, 320, 190)
            uw_ex = st.selectbox(t('uw_exercise'), [t('ml_exercise_low'), t('ml_exercise_mid'), t('ml_exercise_high')])
        with col_u2:
            uw_smoker = 1 if st.checkbox(t('ml_smoker'), value=False) else 0
            uw_family = 1 if st.checkbox(t('uw_family_history'), value=False) else 0
            uw_chronic = 1 if st.checkbox(t('uw_chronic'), value=False) else 0
            alc_map = {t('uw_alcohol_none'): 0, t('uw_alcohol_moderate'): 1, t('uw_alcohol_heavy'): 2}
            uw_alc = st.selectbox(t('uw_alcohol'), list(alc_map.keys()))
            occ_map = {t('uw_occ_desk'): 0, t('uw_occ_manual'): 1, t('uw_occ_hazard'): 2}
            uw_occ = st.selectbox(t('uw_occupation'), list(occ_map.keys()))

        ex_map = {t('ml_exercise_low'): 0, t('ml_exercise_mid'): 1, t('ml_exercise_high'): 2}
        uw_risk_factor = predict_risk_factor(
            age=age, bmi=uw_bmi, smoker=uw_smoker,
            systolic_bp=uw_sys[0], diastolic_bp=uw_sys[1],
            cholesterol=uw_chol, family_history=uw_family,
            exercise=ex_map[uw_ex], alcohol=alc_map[uw_alc],
            occupation_risk=occ_map[uw_occ], chronic_condition=uw_chronic,
        )
        uw_class, uw_mult = classify_risk(uw_risk_factor)
        risk_factor = uw_mult
        cls_label = {
            'preferred': t('risk_pref'), 'preferred_plus': t('uw_class_pref_plus'),
            'standard': t('uw_class_standard'), 'substandard': t('uw_class_substandard'),
            'decline': t('uw_class_decline'),
        }
        c1, c2, c3 = st.columns(3)
        c1.metric(t('uw_result_risk'), f'{uw_risk_factor:.3f}')
        c2.metric(t('uw_result_class'), cls_label.get(uw_class, uw_class))
        c3.metric(t('uw_result_mult'), f'×{uw_mult}')
        risk_label_display = f'{cls_label.get(uw_class, uw_class)} (×{uw_mult})'
    else:
        risk_label = st.radio(t('risk_label'), [t('risk_pref'), t('risk_std'), t('risk_sub')], horizontal=True)
        risk_label_display = risk_label
        risk_map_manual = {t('risk_pref'): 0.7, t('risk_std'): 1.0, t('risk_sub'): 2.0}
        risk_factor = risk_map_manual[risk_label]

    pay_label = st.radio(t('payment_label'), [t('pay_eoy'), t('pay_imm')], horizontal=True)
    freq_label = st.radio(
        t('freq_label'),
        [t('freq_annual'), t('freq_semi'), t('freq_quarterly'), t('freq_monthly')],
        horizontal=True,
    )

claim_accel = (pay_label == t('pay_imm'))
freq_map = {t('freq_annual'): 1, t('freq_semi'): 2, t('freq_quarterly'): 4, t('freq_monthly'): 12}
freq_m = freq_map[freq_label]

# Calculate
@st.cache_data
def get_lt(g, rf, tp, tc):
    return build_life_table(load_table(tp), g if tc == 'clt' else tc, risk_factor=rf)

if use_ml:
    lt = get_ml_life_table(gender_code, ml_params)
    lt['qx'] = lt['qx'] * risk_factor
else:
    lt = get_lt(gender_code, risk_factor, st.session_state.table_path, st.session_state.table_col)

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
param_items = [
    (t('age'), f'{age}'), (t('gender'), gender), (t('start_age'), f'{start_age}'),
    (t('sum'), f'¥{sum_insured:,}'), (t('rate'), f'{rate*100:.1f}%'),
    (t('product_label'), product.split(' ')[-1] if ' ' in product else product),
    (t('risk_label'), risk_label_display), (t('payment_label'), pay_label),
]
chips = ' '.join([f'<span class="param-chip">{k}: {v}</span>' for k, v in param_items])
st.markdown(f'<div class="param-chips">{chips}</div>', unsafe_allow_html=True)

st.info(t('note', start=start_age))

c1, c2, c3 = st.columns(3)
c1.metric(f'{t("per_payment")} ({freq_label})', f'¥{payment:,.0f}', help=summary)
c2.metric(t('annual_premium'), f'¥{ap:,.0f}')
c3.metric(t('lump_sum'), f'¥{sp:,.0f}')
st.caption(t('caption_summary', freq=freq_label, defer=defer, ap=f'{ap:,.0f}', start=start_age))

with st.expander(t('formula_title'), expanded=False):
    st.latex(t('formula_1'))
    st.caption(t('formula_explain'))
    st.caption(t('formula_detail'))

st.divider()

with st.container(border=True):
    st.subheader(t('deferral_vs_coverage'))
    total_years = defer + (coverage if is_term else 30)
    timeline_data = pd.DataFrame({
        'Year': list(range(total_years)),
        'Phase': ['递延期 (Deferral)'] * defer + ['保障期 (Coverage)'] * (total_years - defer),
        'Cash Flow': [-ap] * defer + [sum_insured / (coverage if is_term else 30)] * (total_years - defer),
    })
    st.bar_chart(timeline_data.set_index('Year')['Cash Flow'], height=200)

with st.container(border=True):
    st.subheader(t('reserve_curve'))
    reserves = deferred_assurance_reserve_table(
        lt, age, defer, sum_insured, rate,
        coverage=coverage if is_term else None,
        claim_accel=claim_accel,
    )
    df_r = pd.DataFrame(reserves, columns=['Year', 'Reserve']).set_index('Year')
    st.line_chart(df_r, height=300)

st.divider()
st.caption(t('footer', age=age, gender=gender, defer=defer, start=start_age, sum=sum_insured, rate=rate))
