"""AI 死亡率预测 · ML Mortality Prediction"""
import streamlit as st
import pandas as pd
import numpy as np
from ml_mortality import train_model, model_metrics, compare_tables, predict_qx

st.set_page_config(page_title='AI Mortality', layout='wide', initial_sidebar_state='expanded')

T = {
    'zh': {
        'title': 'AI 死亡率预测',
        'caption': '机器学习替代静态生命表 · Gradient Boosting · 多因子建模',
        'train_btn': '训练模型',
        'metrics_title': '模型性能',
        'compare_title': '传统生命表 vs ML 预测',
        'compare_chart': '死亡率曲线对比 (对数刻度)',
        'single_title': '单点预测',
        'age': '年龄',
        'gender': '性别',
        'gender_m': '男',
        'gender_f': '女',
        'smoker': '吸烟',
        'smoker_yes': '是',
        'smoker_no': '否',
        'bmi': 'BMI',
        'exercise': '运动频率',
        'exercise_low': '少',
        'exercise_mid': '中',
        'exercise_high': '多',
        'income': '收入水平',
        'income_low': '低',
        'income_mid': '中',
        'income_high': '高',
        'predict_btn': '预测',
        'result_qx': '预测死亡率 qx',
        'result_compare': '对比传统表',
        'traditional_qx': '传统表 qx',
        'diff': '差值',
        'mae_label': 'MAE (平均绝对误差)',
        'r2_label': 'R² (拟合度)',
        'feature_importance': '特征重要性',
        'col_feature': '特征',
        'col_importance': '重要性',
        'how_it_works': '工作原理',
        'how_text': 'GradientBoostingRegressor 在 20000 条合成数据上训练。输入年龄、性别、吸烟、BMI、运动、收入 6 个特征，输出预测死亡率 qx。模型 MAE < 0.002，R² > 0.99。',
        'data_note': '训练数据基于 CLT 2010-2013 生命表，叠加生活方式因子（吸烟 ×2.0、BMI 偏离 ×3%/单位、运动 −12%/级、收入 −6%/级）并加入随机噪声生成。',
    },
    'en': {
        'title': 'AI Mortality Prediction',
        'caption': 'ML replaces static life tables · Gradient Boosting · Multi-factor',
        'train_btn': 'Train Model',
        'metrics_title': 'Model Performance',
        'compare_title': 'Traditional vs ML Life Table',
        'compare_chart': 'Mortality Curve Comparison (log scale)',
        'single_title': 'Single Prediction',
        'age': 'Age',
        'gender': 'Gender',
        'gender_m': 'Male',
        'gender_f': 'Female',
        'smoker': 'Smoker',
        'smoker_yes': 'Yes',
        'smoker_no': 'No',
        'bmi': 'BMI',
        'exercise': 'Exercise',
        'exercise_low': 'Low',
        'exercise_mid': 'Medium',
        'exercise_high': 'High',
        'income': 'Income Level',
        'income_low': 'Low',
        'income_mid': 'Medium',
        'income_high': 'High',
        'predict_btn': 'Predict',
        'result_qx': 'Predicted qx',
        'result_compare': 'vs Traditional',
        'traditional_qx': 'Traditional qx',
        'diff': 'Difference',
        'mae_label': 'MAE',
        'r2_label': 'R²',
        'feature_importance': 'Feature Importance',
        'col_feature': 'Feature',
        'col_importance': 'Importance',
        'how_it_works': 'How It Works',
        'how_text': 'GradientBoostingRegressor trained on 20,000 synthetic records. Inputs: age, gender, smoking, BMI, exercise, income. Output: predicted mortality rate qx. MAE < 0.002, R² > 0.99.',
        'data_note': 'Training data synthesized from CLT 2010-2013 base table with lifestyle modifiers (smoking ×2.0, BMI deviation ±3%/unit, exercise −12%/level, income −6%/level) plus random noise.',
    },
}


def t(key, **kw):
    lang = st.session_state.get('lang', 'zh')
    text = T[lang][key]
    return text.format(**kw) if kw else text


st.title(t('title'))
st.caption(t('caption'))


# Cache model across Streamlit reruns
@st.cache_resource(show_spinner=True)
def get_cached_model():
    return train_model()


model = get_cached_model()
mae, r2 = model_metrics()

# ── Metrics ──
c1, c2, c3 = st.columns(3)
c1.metric(t('mae_label'), f'{mae:.6f}')
c2.metric(t('r2_label'), f'{r2:.4f}')
c3.metric('Model', 'GradientBoosting', delta='200 trees')

# ── Comparison Chart ──
st.subheader(t('compare_title'))
df_comp = compare_tables(0, 'M')
chart_data = df_comp.set_index('age')[['qx_traditional', 'qx_ml']]
chart_data.columns = ['Traditional (CLT)', 'ML Prediction']
st.line_chart(chart_data, height=350)
st.caption(t('compare_chart'))

# ── Single Prediction ──
st.subheader(t('single_title'))
col1, col2, col3 = st.columns(3)
with col1:
    age = st.slider(t('age'), 0, 100, 30)
    gender = st.radio(t('gender'), [t('gender_m'), t('gender_f')], horizontal=True)
    smoker = 1 if st.checkbox(t('smoker_yes')) else 0
with col2:
    bmi = st.slider(t('bmi'), 16.0, 42.0, 23.0, 0.5)
    exercise = st.selectbox(t('exercise'),
                            [t('exercise_low'), t('exercise_mid'), t('exercise_high')])
    exercise_map = {t('exercise_low'): 0, t('exercise_mid'): 1, t('exercise_high'): 2}
with col3:
    income = st.selectbox(t('income'),
                          [t('income_low'), t('income_mid'), t('income_high')])
    income_map = {t('income_low'): 0, t('income_mid'): 1, t('income_high'): 2}

if st.button(t('predict_btn')):
    gender_code = 'M' if gender == t('gender_m') else 'F'
    qx_pred = predict_qx(age, gender_code, smoker, bmi,
                         exercise_map[exercise], income_map[income])

    clt = pd.read_csv('data/clt_2010_2013.csv')
    col = 'qx_male' if gender_code == 'M' else 'qx_female'
    traditional = float(clt[col].values[min(age, 104)])

    c1, c2, c3 = st.columns(3)
    c1.metric(t('result_qx'), f'{qx_pred:.6f}')
    c2.metric(t('traditional_qx'), f'{traditional:.6f}')
    diff = qx_pred - traditional
    c3.metric(t('diff'), f'{diff:+.6f}', delta=f'{diff/traditional*100:+.1f}%')

# ── Feature Importance ──
st.subheader(t('feature_importance'))
model = train_model()
importance = pd.DataFrame({
    t('col_feature'): ['age', 'gender', 'smoker', 'bmi', 'exercise', 'income_level'],
    t('col_importance'): model.feature_importances_,
}).sort_values(t('col_importance'), ascending=False)
st.bar_chart(importance.set_index(t('col_feature')), height=250)

# ── How it works ──
with st.expander(t('how_it_works')):
    st.caption(t('how_text'))
    st.caption(t('data_note'))
