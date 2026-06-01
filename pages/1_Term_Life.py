"""定期寿险 · Term Life Insurance"""

import streamlit as st
import pandas as pd
import os
from mortality import load_table, build_life_table, table_max_age
from ml_mortality import train_model, get_ml_life_table
from ml_underwriting import (train_uw_model, predict_risk_factor, classify_risk,
                             uw_model_metrics, feature_importance_df)

from reserve import reserve_table

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'clt_2010_2013.csv')
T = {
    'zh': {
        'title': '定期寿险 · Term Life',
        'caption': '约定期限内死亡赔付 · Net Single & Annual Premiums · Policy Reserves',
        'table_label': 'Life Table',
        'table_clt': 'CLT 2010-2013',
        'table_am92ult': 'AM92 Ultimate',
        'table_am92sel': 'AM92 Select',
        'table_am92sel_plusone': 'AM92 Select+1',
        'age': '投保年龄', 'sum': '保险金额（元）', 'term': '保险期限（年）',
        'rate': '预定利率（%）', 'gender': '性别', 'gender_m': '男', 'gender_f': '女',
        'risk_label': '核保等级',
        'risk_pref': '优选体 (×0.7)', 'risk_std': '标准体 (×1.0)', 'risk_sub': '次标准体 (×2.0)',
        'risk_hint': '健康不吸烟 → 优选 | 吸烟/超重 → 次标准',
        'payment_label': '赔付时点',
        'pay_eoy': '死亡年末付款', 'pay_imm': '死亡立即付款 (UDD)',
        'pay_hint': '立即付款 = (1+i)^0.5 × 年末付款',
        'advanced_options': '高级选项（核保 · 费用 · 缴费方式）',
        'uw_section': '核保与赔付',
        'expense_section': '费用参数',
        'freq_section': '缴费方式',
        'expense_alpha': 'α 获取费 (% × 保额)',
        'expense_beta': 'β 维持费 (% × 保费)',
        'expense_gamma': 'γ 收费费 (‰ × 保额)',
        'expense_formula': '毛保费 = (纯保费 + 费用现值) ÷ (1 − β)',
        'freq_label': '缴费频率',
        'freq_annual': '年缴', 'freq_semi': '半年缴', 'freq_quarterly': '季缴', 'freq_monthly': '月缴',
        'per_payment': '每期保费', 'gross_annual': '年毛保费',
        'net_premium': '纯保费 (净)', 'net_premium_help': '纯风险保费',
        'reserve_chart': '责任准备金曲线', 'reserve_table': '各年末准备金明细',
        'col_year': '保单年度', 'col_reserve': '准备金',
        'footer': '{age}岁 {gender} · 保额¥{sum:,} · {term}年 · 利率{rate:.1%} · {risk} · {payment}',
        'formula_title': '精算原理',
        'formula_1': r'''P = S \cdot \frac{A_{x:n}^{1}}{\ddot{a}_{x:n}}''',
        'formula_explain': '净保费 = 保额 × 死亡给付期望现值 ÷ 期初付年金现值',
        'formula_detail': '保险公司将未来可能的死亡赔付折现到今天，再平摊到每年缴费中。α/β/γ 费用加载后再得到毛保费。UDD 假设下，死亡立即付款 ≈ (1+i)^0.5 × 年末付款。',
        'nav_home': '首页', 'nav_term': '定期寿险', 'nav_whole_life': '终身寿险',
        'nav_annuity': '生存年金', 'nav_endowment': '两全保险', 'nav_def_annuity': '递延年金',
        'nav_def_assurance': '递延寿险', 'nav_pure_endow': '纯生存保险',
        'help_per_payment': '每期保费 · 年毛保费 {gap}',
        'help_gross_annual': '含费用的年保费',
        'caption_summary': '{freq}缴纳 · 费用附加 +{extra}（α/β/γ）· 纯保费 {net}',
        'ml_source_label': '死亡率来源',
        'ml_source_traditional': '传统生命表',
        'ml_source_ai': 'AI 预测',
        'ml_source_help': 'AI 模型基于年龄/性别/吸烟/BMI/运动/收入预测死亡率',
        'ml_smoker': '吸烟',
        'ml_bmi': 'BMI',
        'ml_exercise': '运动',
        'ml_exercise_low': '少',
        'ml_exercise_mid': '中',
        'ml_exercise_high': '多',
        'ml_income': '收入',
        'ml_income_low': '低',
        'ml_income_mid': '中',
        'ml_income_high': '高',
        'ml_ai_note': 'AI 预测基于 GradientBoosting，MAE<0.002，R²>0.99',
        'ml_vs_traditional': 'AI 预测 vs 传统生命表',
        'uw_ai_label': '核保方式',
        'uw_ai_manual': '人工分级',
        'uw_ai_auto': 'AI 智能核保',
        'uw_ai_help': 'AI 基于健康数据自动评估风险因子，替代人工选择',
        'uw_bmi_label': 'BMI',
        'uw_bp_label': '血压 (收缩/舒张)',
        'uw_cholesterol': '总胆固醇 (mg/dL)',
        'uw_family_history': '家族早逝史',
        'uw_exercise': '运动频率',
        'uw_alcohol': '饮酒',
        'uw_alcohol_none': '不喝',
        'uw_alcohol_moderate': '适量',
        'uw_alcohol_heavy': '大量',
        'uw_occupation': '职业风险',
        'uw_occ_desk': '办公室',
        'uw_occ_manual': '体力劳动',
        'uw_occ_hazard': '高危职业',
        'uw_chronic': '慢性病史',
        'uw_result_risk': '风险因子',
        'uw_result_class': '核保等级',
        'uw_result_mult': '费率乘数',
        'uw_class_pref_plus': '优选+',
        'uw_class_standard': '标准体',
        'uw_class_substandard': '次标准体',
        'uw_class_decline': '拒保',
    },
    'en': {
        'title': 'Term Life Insurance',
        'caption': 'Death benefit within a fixed term · Net Premiums · Reserves',
        'table_label': 'Life Table',
        'table_clt': 'CLT 2010-2013',
        'table_am92ult': 'AM92 Ultimate',
        'table_am92sel': 'AM92 Select',
        'table_am92sel_plusone': 'AM92 Select+1',
        'age': 'Issue Age', 'sum': 'Sum Insured (¥)', 'term': 'Policy Term (years)',
        'rate': 'Interest Rate (%)', 'gender': 'Gender', 'gender_m': 'Male', 'gender_f': 'Female',
        'risk_label': 'Underwriting Class',
        'risk_pref': 'Preferred (×0.7)', 'risk_std': 'Standard (×1.0)', 'risk_sub': 'Substandard (×2.0)',
        'risk_hint': 'Healthy non-smoker → Preferred | Smoker → Substandard',
        'payment_label': 'Death Benefit Timing',
        'pay_eoy': 'End of Year of Death', 'pay_imm': 'Immediate on Death (UDD)',
        'pay_hint': 'Immediate = (1+i)^0.5 × End-of-Year',
        'advanced_options': 'Advanced Options (UW · Expenses · Frequency)',
        'uw_section': 'Underwriting & Payment',
        'expense_section': 'Expense Parameters',
        'freq_section': 'Payment Method',
        'expense_alpha': 'α Acquisition (% × Sum Insured)',
        'expense_beta': 'β Maintenance (% × Premium)',
        'expense_gamma': 'γ Collection (‰ × Sum Insured)',
        'expense_formula': 'Gross = (Net + Expense PV) ÷ (1 − β)',
        'freq_label': 'Payment Frequency',
        'freq_annual': 'Annual', 'freq_semi': 'Semi-annual', 'freq_quarterly': 'Quarterly', 'freq_monthly': 'Monthly',
        'per_payment': 'Per Payment', 'gross_annual': 'Gross Annual',
        'net_premium': 'Net Premium', 'net_premium_help': 'Pure risk premium',
        'reserve_chart': 'Policy Reserve Curve', 'reserve_table': 'Reserve by Policy Year',
        'col_year': 'Policy Year', 'col_reserve': 'Reserve',
        'footer': '{age}y {gender} · Sum ¥{sum:,} · {term}yr · Rate {rate:.1%} · {risk} · {payment}',
        'formula_title': 'Actuarial Formula',
        'formula_1': r'''P = S \cdot \frac{A_{x:n}^{1}}{\ddot{a}_{x:n}}''',
        'formula_explain': 'Net premium = Sum Insured × EPV of death benefit ÷ Annuity-due',
        'formula_detail': 'The insurer discounts all possible future death benefits to today, then spreads them across annual premiums. α/β/γ expense loading yields the gross premium. Under UDD, immediate death benefit ≈ (1+i)^0.5 × end-of-year benefit.',
        'nav_home': 'Home', 'nav_term': 'Term Life', 'nav_whole_life': 'Whole Life',
        'nav_annuity': 'Life Annuity', 'nav_endowment': 'Endowment', 'nav_def_annuity': 'Deferred Annuity',
        'nav_def_assurance': 'Deferred Assurance', 'nav_pure_endow': 'Pure Endowment',
        'help_per_payment': 'Per-payment amount · Gross annual {gap}',
        'help_gross_annual': 'Annual premium with expenses',
        'caption_summary': '{freq} payment · Loading +{extra} (α/β/γ) · Net {net}',
        'ml_source_label': 'Mortality Source',
        'ml_source_traditional': 'Traditional Table',
        'ml_source_ai': 'AI Prediction',
        'ml_source_help': 'ML model predicts qx from age/gender/smoking/BMI/exercise/income',
        'ml_smoker': 'Smoker',
        'ml_bmi': 'BMI',
        'ml_exercise': 'Exercise',
        'ml_exercise_low': 'Low',
        'ml_exercise_mid': 'Medium',
        'ml_exercise_high': 'High',
        'ml_income': 'Income',
        'ml_income_low': 'Low',
        'ml_income_mid': 'Medium',
        'ml_income_high': 'High',
        'ml_ai_note': 'AI prediction via GradientBoosting, MAE<0.002, R²>0.99',
        'ml_vs_traditional': 'AI Prediction vs Traditional Table',
        'uw_ai_label': 'Underwriting',
        'uw_ai_manual': 'Manual',
        'uw_ai_auto': 'AI Smart UW',
        'uw_ai_help': 'AI predicts risk factor from health data',
        'uw_bmi_label': 'BMI',
        'uw_bp_label': 'BP (Sys/Dia)',
        'uw_cholesterol': 'Total Cholesterol (mg/dL)',
        'uw_family_history': 'Family Early Death',
        'uw_exercise': 'Exercise',
        'uw_alcohol': 'Alcohol',
        'uw_alcohol_none': 'None',
        'uw_alcohol_moderate': 'Moderate',
        'uw_alcohol_heavy': 'Heavy',
        'uw_occupation': 'Occupation Risk',
        'uw_occ_desk': 'Desk',
        'uw_occ_manual': 'Manual',
        'uw_occ_hazard': 'Hazardous',
        'uw_chronic': 'Chronic Condition',
        'uw_result_risk': 'Risk Factor',
        'uw_result_class': 'UW Class',
        'uw_result_mult': 'Rate Multiplier',
        'uw_class_pref_plus': 'Preferred+',
        'uw_class_standard': 'Standard',
        'uw_class_substandard': 'Substandard',
        'uw_class_decline': 'Decline',
    },
    'zh-Hant': {
        'title': '定期壽險 · Term Life',
        'caption': '約定期限內死亡給付 · Net Single & Annual Premiums · Policy Reserves',
        'table_label': 'Life Table', 'table_clt': 'CLT 2010-2013',
        'table_am92ult': 'AM92 Ultimate', 'table_am92sel': 'AM92 Select', 'table_am92sel_plusone': 'AM92 Select+1',
        'age': '投保年齡', 'sum': '保險金額（元）', 'term': '保險期限（年）',
        'rate': '預定利率（%）', 'gender': '性別', 'gender_m': '男', 'gender_f': '女',
        'risk_label': '核保等級', 'risk_pref': '優選體 (×0.7)', 'risk_std': '標準體 (×1.0)', 'risk_sub': '次標準體 (×2.0)',
        'risk_hint': '健康不吸菸 → 優選 | 吸菸/超重 → 次標準',
        'payment_label': '給付時點', 'pay_eoy': '死亡年末給付', 'pay_imm': '死亡立即給付 (UDD)',
        'pay_hint': '立即給付 = (1+i)^0.5 × 年末給付',
        'advanced_options': '進階選項（核保 · 費用 · 繳費方式）',
        'uw_section': '核保與給付', 'expense_section': '費用參數', 'freq_section': '繳費方式',
        'expense_alpha': 'α 獲取費 (% × 保額)', 'expense_beta': 'β 維持費 (% × 保費)', 'expense_gamma': 'γ 收費費 (‰ × 保額)',
        'expense_formula': '毛保費 = (純保費 + 費用現值) ÷ (1 − β)',
        'freq_label': '繳費頻率', 'freq_annual': '年繳', 'freq_semi': '半年繳', 'freq_quarterly': '季繳', 'freq_monthly': '月繳',
        'per_payment': '每期保費', 'gross_annual': '年毛保費',
        'net_premium': '純保費（淨）', 'net_premium_help': '純風險保費',
        'reserve_chart': '責任準備金曲線', 'reserve_table': '各年末準備金明細',
        'col_year': '保單年度', 'col_reserve': '準備金',
        'footer': '{age}歲 {gender} · 保額¥{sum:,} · {term}年 · 利率{rate:.1%} · {risk} · {payment}',
        'formula_title': '精算原理',
        'formula_1': r'''P = S \cdot \frac{A_{x:n}^{1}}{\ddot{a}_{x:n}}''',
        'formula_explain': '純保費 = 保額 × 死亡給付期望現值 ÷ 期初付年金現值',
        'formula_detail': '保險公司將未來可能的死亡給付折現到今天，再平攤到每年繳費中。α/β/γ 費用加載後再得到毛保費。UDD 假設下，死亡立即給付 ≈ (1+i)^0.5 × 年末給付。',
        'nav_home': '首頁', 'nav_term': '定期壽險', 'nav_whole_life': '終身壽險',
        'nav_annuity': '生存年金', 'nav_endowment': '兩全保險', 'nav_def_annuity': '遞延年金',
        'nav_def_assurance': '遞延壽險', 'nav_pure_endow': '純生存保險',
        'help_per_payment': '每期保費 · 年毛保費 {gap}',
        'help_gross_annual': '含費用的年保費',
        'caption_summary': '{freq}繳納 · 費用附加 +{extra}（α/β/γ）· 純保費 {net}',
        'ml_source_label': '死亡率來源',
        'ml_source_traditional': '傳統生命表',
        'ml_source_ai': 'AI 預測',
        'ml_source_help': 'AI 模型基於年齡/性別/吸菸/BMI/運動/收入預測死亡率',
        'ml_smoker': '吸菸',
        'ml_bmi': 'BMI',
        'ml_exercise': '運動',
        'ml_exercise_low': '少',
        'ml_exercise_mid': '中',
        'ml_exercise_high': '多',
        'ml_income': '收入',
        'ml_income_low': '低',
        'ml_income_mid': '中',
        'ml_income_high': '高',
        'ml_ai_note': 'AI 預測基於 GradientBoosting，MAE<0.002，R²>0.99',
        'ml_vs_traditional': 'AI 預測 vs 傳統生命表',
        'uw_ai_label': '核保方式',
        'uw_ai_manual': '人工分級',
        'uw_ai_auto': 'AI 智能核保',
        'uw_ai_help': 'AI 基於健康數據自動評估風險因子',
        'uw_bmi_label': 'BMI',
        'uw_bp_label': '血壓 (收縮/舒張)',
        'uw_cholesterol': '總膽固醇 (mg/dL)',
        'uw_family_history': '家族早逝史',
        'uw_exercise': '運動頻率',
        'uw_alcohol': '飲酒',
        'uw_alcohol_none': '不喝',
        'uw_alcohol_moderate': '適量',
        'uw_alcohol_heavy': '大量',
        'uw_occupation': '職業風險',
        'uw_occ_desk': '辦公室',
        'uw_occ_manual': '體力勞動',
        'uw_occ_hazard': '高危職業',
        'uw_chronic': '慢性病史',
        'uw_result_risk': '風險因子',
        'uw_result_class': '核保等級',
        'uw_result_mult': '費率乘數',
        'uw_class_pref_plus': '優選+',
        'uw_class_standard': '標準體',
        'uw_class_substandard': '次標準體',
        'uw_class_decline': '拒保',
    },
}


def t(key, **kw):
    text = T[st.session_state.lang][key]
    return text.format(**kw) if kw else text

CURRENT_PAGE = 'term'
ACTIVE_STYLE = ' style="color:#1D1D1F;border-color:#AEAEB2;"'


# Language init
if 'lang' not in st.session_state:
    st.session_state.lang = 'zh'

st.set_page_config(page_title=t('title'), layout='wide', initial_sidebar_state='expanded')
st.title(t('title'))
st.caption(t('caption'))

# Product nav pills
st.markdown(f"""
<div class="nav-strip">
<a href="/" target="_self" class="nav-pill">{t('nav_home')}</a>
<a href="/Term_Life" target="_self" class="nav-pill" style="color:#1D1D1F;border-color:#AEAEB2;">{t('nav_term')}</a>
<a href="/Whole_Life" target="_self" class="nav-pill">{t('nav_whole_life')}</a>
<a href="/Annuity" target="_self" class="nav-pill">{t('nav_annuity')}</a>
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

# Sidebar — Basic Parameters
max_age = 120 if use_ml else table_max_age(st.session_state.table_col)
age = st.sidebar.slider(t('age'), 0, max_age - 1, 30)
gender = st.sidebar.radio(t('gender'), [t('gender_m'), t('gender_f')], horizontal=True)
gender_code = 'M' if gender == t('gender_m') else 'F'
sum_insured = st.sidebar.number_input(t('sum'), 10000, 100000000, 1000000, 10000, format='%d')
term = st.sidebar.slider(t('term'), 1, max_age - age, min(20, max_age - age))
rate = st.sidebar.slider(t('rate'), 0.0, 10.0, 3.5, 0.5) / 100

if age + term > max_age:
    st.sidebar.error(f'Age + Term = {age + term} exceeds limit age {max_age}')
    st.stop()

# Sidebar — Advanced Options (collapsed by default)
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

        # Show prediction result
        c1, c2, c3 = st.columns(3)
        cls_label = {
            'preferred': t('risk_pref'), 'preferred_plus': t('uw_class_pref_plus'),
            'standard': t('uw_class_standard'), 'substandard': t('uw_class_substandard'),
            'decline': t('uw_class_decline'),
        }
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

    st.divider()
    st.caption(t('expense_section'))
    alpha = st.slider(t('expense_alpha'), 0.0, 15.0, 5.0, 0.5) / 100
    beta  = st.slider(t('expense_beta'), 0.0, 10.0, 2.0, 0.5) / 100
    gamma = st.slider(t('expense_gamma'), 0.0, 5.0, 0.5, 0.1) / 1000

    st.divider()
    st.caption(t('freq_section'))
    freq_label = st.radio(
        t('freq_label'),
        [t('freq_annual'), t('freq_semi'), t('freq_quarterly'), t('freq_monthly')],
        horizontal=True,
    )

claim_accel = (pay_label == t('pay_imm'))
freq_map = {t('freq_annual'): 1, t('freq_semi'): 2, t('freq_quarterly'): 4, t('freq_monthly'): 12}
freq_m = freq_map[freq_label]

# Calculate
from premium import gross_annual_premium, periodic_premium, annual_premium as net_ap

@st.cache_data
def get_lt(g, rf, tp, tc):
    return build_life_table(load_table(tp), g if tc == 'clt' else tc, risk_factor=rf)

if use_ml:
    lt = get_ml_life_table(gender_code, ml_params)
    lt['qx'] = lt['qx'] * risk_factor  # apply UW risk factor on top
else:
    lt = get_lt(gender_code, risk_factor, st.session_state.table_path, st.session_state.table_col)
gap = gross_annual_premium(lt, age, sum_insured, term, rate,
                           alpha=alpha, beta=beta, gamma=gamma, claim_accel=claim_accel)
payment = periodic_premium(gap, freq_m)
net = net_ap(lt, age, sum_insured, term, rate, claim_accel)
reserves = reserve_table(lt, age, sum_insured, term, rate)

# Display
param_items = [
    (t('age'), f'{age}'), (t('gender'), gender), (t('sum'), f'¥{sum_insured:,}'),
    (t('term'), f'{term}yr'), (t('rate'), f'{rate*100:.1f}%'),
    (t('risk_label'), risk_label_display), (t('payment_label'), pay_label),
]
chips = ' '.join([f'<span class="param-chip">{k}: {v}</span>' for k, v in param_items])
st.markdown(f'<div class="param-chips">{chips}</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
c1.metric(f'{t("per_payment")} ({freq_label})', f'¥{payment:,.0f}',
          help=t('help_per_payment', gap=f'¥{gap:,.0f}'))
c2.metric(t('gross_annual'), f'¥{gap:,.0f}', help=t('help_gross_annual'))
c3.metric(t('net_premium'), f'¥{net:,.0f}',
          help=t('net_premium_help'), delta=f'¥{gap - net:,.0f}',
          delta_color='off')
st.caption(t('caption_summary', freq=freq_label, extra=f'¥{gap-net:,.0f}', net=f'¥{net:,.0f}'))

with st.expander(t('formula_title'), expanded=False):
    st.latex(t('formula_1'))
    st.caption(t('formula_explain'))
    st.caption(t('formula_detail'))

st.divider()

with st.container(border=True):
    st.subheader(t('reserve_chart'))
    df_r = pd.DataFrame(reserves, columns=['Year', 'Reserve']).set_index('Year')
    st.line_chart(df_r, height=300)

with st.container(border=True):
    st.subheader(t('reserve_table'))
    df_d = pd.DataFrame(reserves, columns=[t('col_year'), t('col_reserve')])
    df_d[t('col_reserve')] = df_d[t('col_reserve')].apply(lambda x: f'¥{x:,.2f}')
    st.dataframe(df_d, width='stretch', hide_index=True, height=400)

st.divider()
st.caption(t('footer', age=age, gender=gender, sum=sum_insured, term=term, rate=rate, risk=risk_label_display, payment=pay_label))
