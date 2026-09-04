"""AI 理赔欺诈检测 · Claims Fraud Detection"""
import streamlit as st
import pandas as pd
import numpy as np
from ml_fraud import (train_fraud_models, fraud_model_metrics, analyze_claim,
                      fraud_feature_importance)

st.set_page_config(page_title='Fraud Detection', layout='wide', initial_sidebar_state='expanded')

T = {
    'zh': {
        'title': 'AI 理赔欺诈检测',
        'caption': '双层检测：Isolation Forest 异常检测 + XGBoost 分类器',
        'metrics_title': '模型性能',
        'auc_label': 'AUC',
        'claim_form': '理赔信息',
        'claim_amount': '理赔金额 (¥)',
        'policy_age': '保单生效月数',
        'age': '被保险人年龄',
        'policy_type': '保单类型',
        'pt_term': '定期寿险',
        'pt_whole': '终身寿险',
        'pt_endowment': '两全保险',
        'claim_type': '理赔类型',
        'ct_death': '死亡',
        'ct_disability': '残疾',
        'ct_ci': '重疾',
        'ct_accident': '意外',
        'prev_claims': '历史理赔次数',
        'annual_premium': '年缴保费 (¥)',
        'report_days': '出险到报案天数',
        'has_witness': '有目击证人',
        'has_police': '有警方报告',
        'medical_ok': '医疗记录与理赔一致',
        'beneficiary_change': '近期变更过受益人',
        'analyze_btn': '分析理赔',
        'result_title': '检测结果',
        'fraud_prob': '欺诈概率',
        'risk_level': '风险等级',
        'recommendation': '建议处理',
        'xgb_prob': 'XGBoost 概率',
        'anomaly_score': '异常分数',
        'flags_title': '风险标记',
        'no_flags': '未发现明显风险标记',
        'rec_auto': '自动通过',
        'rec_review': '人工审核',
        'rec_investigate': '深入调查',
        'rec_reject': '拒绝理赔',
        'how_title': '工作原理',
        'how_text': '双层检测架构：1) Isolation Forest 无监督异常检测识别离群理赔；2) XGBoost 监督分类器学习历史欺诈模式。综合评分 = XGBoost×0.6 + Anomaly×0.4。训练数据 20000 条，含 8% 欺诈样本。',
        'feature_imp': '特征重要性',
        'batch_title': '批量检测',
        'batch_upload': '上传 CSV 批量检测',
        'batch_columns': '需要列: claim_amount, policy_age_months, age, policy_type, claim_type, previous_claims, annual_premium',
    },
    'en': {
        'title': 'AI Claims Fraud Detection',
        'caption': 'Dual-layer: Isolation Forest anomaly detection + XGBoost classifier',
        'metrics_title': 'Model Performance',
        'auc_label': 'AUC',
        'claim_form': 'Claim Information',
        'claim_amount': 'Claim Amount (¥)',
        'policy_age': 'Policy Age (months)',
        'age': 'Insured Age',
        'policy_type': 'Policy Type',
        'pt_term': 'Term Life',
        'pt_whole': 'Whole Life',
        'pt_endowment': 'Endowment',
        'claim_type': 'Claim Type',
        'ct_death': 'Death',
        'ct_disability': 'Disability',
        'ct_ci': 'Critical Illness',
        'ct_accident': 'Accidental',
        'prev_claims': 'Previous Claims',
        'annual_premium': 'Annual Premium (¥)',
        'report_days': 'Days to Report',
        'has_witness': 'Witness Present',
        'has_police': 'Police Report',
        'medical_ok': 'Medical Records Consistent',
        'beneficiary_change': 'Recent Beneficiary Change',
        'analyze_btn': 'Analyze Claim',
        'result_title': 'Detection Result',
        'fraud_prob': 'Fraud Probability',
        'risk_level': 'Risk Level',
        'recommendation': 'Recommendation',
        'xgb_prob': 'XGBoost Probability',
        'anomaly_score': 'Anomaly Score',
        'flags_title': 'Risk Flags',
        'no_flags': 'No significant risk flags detected',
        'rec_auto': 'Auto-Approve',
        'rec_review': 'Manual Review',
        'rec_investigate': 'Investigate',
        'rec_reject': 'Reject Claim',
        'how_title': 'How It Works',
        'how_text': 'Dual-layer detection: 1) Isolation Forest identifies outlier claims; 2) XGBoost learns fraud patterns from history. Combined score = XGBoost×0.6 + Anomaly×0.4. Trained on 20,000 records with 8% fraud samples.',
        'feature_imp': 'Feature Importance',
        'batch_title': 'Batch Detection',
        'batch_upload': 'Upload CSV for batch detection',
        'batch_columns': 'Required: claim_amount, policy_age_months, age, policy_type, claim_type, previous_claims, annual_premium',
    },
}


def t(key, **kw):
    lang = st.session_state.get('lang', 'zh')
    text = T[lang][key]
    return text.format(**kw) if kw else text


st.title(t('title'))
st.caption(t('caption'))

# Train model
@st.cache_resource(show_spinner=True)
def get_cached_fraud_model():
    return train_fraud_models()


model = get_cached_fraud_model()
auc = fraud_model_metrics()

c1, c2 = st.columns(2)
c1.metric(t('auc_label'), f'{auc:.4f}')
c2.metric('Model', 'IsoForest + XGBoost', delta='200 trees')

st.divider()

# ── Single Claim Form ──
st.subheader(t('claim_form'))
col1, col2, col3 = st.columns(3)

with col1:
    claim_amount = st.number_input(t('claim_amount'), 1000, 50000000, 100000, 10000, format='%d')
    policy_age = st.slider(t('policy_age'), 1, 240, 24)
    age = st.slider(t('age'), 18, 85, 40)
    pt_map = {t('pt_term'): 'term', t('pt_whole'): 'whole', t('pt_endowment'): 'endowment'}
    policy_type = st.selectbox(t('policy_type'), list(pt_map.keys()))

with col2:
    ct_map = {t('ct_death'): 'death', t('ct_disability'): 'disability',
              t('ct_ci'): 'critical_illness', t('ct_accident'): 'accidental'}
    claim_type = st.selectbox(t('claim_type'), list(ct_map.keys()))
    prev = st.number_input(t('prev_claims'), 0, 20, 0)
    annual_prem = st.number_input(t('annual_premium'), 100, 10000000, 5000, 1000, format='%d')

with col3:
    report_days = st.slider(t('report_days'), 0, 90, 7)
    witness = st.checkbox(t('has_witness'), value=True)
    police = st.checkbox(t('has_police'), value=True)
    medical = st.checkbox(t('medical_ok'), value=True)
    ben_change = st.checkbox(t('beneficiary_change'), value=False)

if st.button(t('analyze_btn'), type='primary'):
    ratio = claim_amount / max(annual_prem, 1)
    st.caption(f'理赔/保费比: {ratio:.0f}x')

    result = analyze_claim(
        claim_amount=claim_amount, policy_age_months=policy_age,
        age=age, policy_type=pt_map[policy_type],
        claim_type=ct_map[claim_type], previous_claims=prev,
        annual_premium=annual_prem, time_to_report_days=report_days,
        has_witness=witness, has_police_report=police,
        medical_consistent=medical, beneficiary_change_recent=ben_change,
    )

    color = {'low': 'green', 'medium': 'orange', 'high': 'red', 'critical': 'red'}
    rec_label = {
        'auto_approve': t('rec_auto'), 'review': t('rec_review'),
        'investigate': t('rec_investigate'), 'reject': t('rec_reject'),
    }

    st.divider()
    st.subheader(t('result_title'))

    m1, m2, m3, m4 = st.columns(4)
    m1.metric(t('fraud_prob'), f'{result["fraud_probability"]:.1%}',
              delta=f'risk: {result["risk_level"]}')
    m2.metric(t('xgb_prob'), f'{result["xgb_probability"]:.1%}')
    m3.metric(t('anomaly_score'), f'{result["anomaly_score"]:.1%}')
    m4.metric(t('recommendation'), rec_label.get(result['recommendation'], result['recommendation']))

    st.subheader(t('flags_title'))
    if result['flags']:
        for flag in result['flags']:
            st.warning(f'⚑ {flag}')
    else:
        st.success(t('no_flags'))

# ── Feature Importance ──
st.divider()
st.subheader(t('feature_imp'))
imp_df = fraud_feature_importance()
st.bar_chart(imp_df.set_index('feature'), height=250)

# ── How it works ──
with st.expander(t('how_title')):
    st.caption(t('how_text'))
