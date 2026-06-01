"""AI 动态保费优化 · Dynamic Premium Optimizer"""
import streamlit as st
import pandas as pd
import numpy as np
from ml_pricing import optimize_premium, compare_scenarios, optimal_vs_competitors

st.set_page_config(page_title='Pricing Optimizer', layout='wide', initial_sidebar_state='expanded')

T = {
    'zh': {
        'title': 'AI 动态保费优化',
        'caption': '贝叶斯优化 · 利润 vs 竞争力平衡 · 对标竞品定价',
        'net_premium': '纯保费 (¥)',
        'alpha': 'α 获取费 (%)',
        'beta': 'β 维持费 (%)',
        'gamma': 'γ 收费费 (‰)',
        'competitors': '竞品价格 (逗号分隔)',
        'comp_help': '例如: 12000,13500,11000,14000',
        'weight': '竞争力权重',
        'weight_help': '0=纯利润最大化, 1=纯市场份额最大化',
        'optimize_btn': '计算最优保费',
        'result_title': '最优定价方案',
        'optimal_premium': '最优保费',
        'profit_margin': '利润率',
        'cost_base': '成本基准',
        'profit_per': '每单利润',
        'vs_median': 'vs 竞品中位数',
        'scenarios_title': '三种策略对比',
        'col_strategy': '策略',
        'col_premium': '保费',
        'col_margin': '利润率',
        'col_profit': '每单利润',
        'col_vs_median': 'vs中位数',
        'position_title': '价格定位分析',
        'col_competitor': '竞品',
        'col_their_price': '竞品价格',
        'col_our_price': '我方价格',
        'col_diff': '价差%',
        'col_position': '定位',
        'how_title': '工作原理',
        'how_text': 'scipy.optimize 在给定利润率约束下最大化复合得分 = 利润分 × (1−权重) + 市场分 × 权重。市场分基于我方价格与竞品中位数的比值。保守策略权重=0.2，均衡=0.5，激进=0.8。',
    },
    'en': {
        'title': 'AI Dynamic Premium Optimizer',
        'caption': 'Bayesian optimization · Profit vs Competitiveness · Competitor benchmarking',
        'net_premium': 'Net Premium (¥)',
        'alpha': 'α Acquisition (%)',
        'beta': 'β Maintenance (%)',
        'gamma': 'γ Collection (‰)',
        'competitors': 'Competitor Prices (comma separated)',
        'comp_help': 'e.g.: 12000,13500,11000,14000',
        'weight': 'Competitiveness Weight',
        'weight_help': '0=pure profit max, 1=pure market share max',
        'optimize_btn': 'Calculate Optimal Premium',
        'result_title': 'Optimal Pricing',
        'optimal_premium': 'Optimal Premium',
        'profit_margin': 'Profit Margin',
        'cost_base': 'Cost Base',
        'profit_per': 'Profit/Policy',
        'vs_median': 'vs Competitor Median',
        'scenarios_title': 'Strategy Comparison',
        'col_strategy': 'Strategy',
        'col_premium': 'Premium',
        'col_margin': 'Margin',
        'col_profit': 'Profit/Policy',
        'col_vs_median': 'vs Median',
        'position_title': 'Price Positioning',
        'col_competitor': 'Competitor',
        'col_their_price': 'Their Price',
        'col_our_price': 'Our Price',
        'col_diff': 'Diff%',
        'col_position': 'Position',
        'how_title': 'How It Works',
        'how_text': 'scipy.optimize maximizes composite score = profit_score × (1−weight) + market_score × weight under margin constraints. Market score is based on our price vs competitor median. Conservative weight=0.2, Balanced=0.5, Aggressive=0.8.',
    },
}


def t(key, **kw):
    lang = st.session_state.get('lang', 'zh')
    text = T[lang][key]
    return text.format(**kw) if kw else text


st.title(t('title'))
st.caption(t('caption'))

col1, col2, col3 = st.columns(3)
with col1:
    net = st.number_input(t('net_premium'), 100, 10000000, 10000, 1000, format='%d')
    alpha = st.slider(t('alpha'), 0.0, 15.0, 5.0, 0.5)
with col2:
    beta = st.slider(t('beta'), 0.0, 10.0, 2.0, 0.5)
    gamma = st.slider(t('gamma'), 0.0, 5.0, 0.5, 0.1)
with col3:
    comp_text = st.text_input(t('competitors'), '12000, 13500, 11000, 14000', help=t('comp_help'))
    weight = st.slider(t('weight'), 0.0, 1.0, 0.5, 0.1, help=t('weight_help'))

competitors = [float(x.strip()) for x in comp_text.split(',') if x.strip()]

if st.button(t('optimize_btn'), type='primary'):
    result = optimize_premium(net, alpha / 100, beta / 100, gamma / 1000, competitors, competitiveness_weight=weight)

    st.divider()
    st.subheader(t('result_title'))
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric(t('optimal_premium'), f'¥{result["optimal_premium"]:,.0f}')
    m2.metric(t('profit_margin'), f'{result["optimal_margin"]:.1f}%')
    m3.metric(t('cost_base'), f'¥{result["cost_base"]:,.0f}')
    m4.metric(t('profit_per'), f'¥{result["profit_per_policy"]:,.0f}')
    m5.metric(t('vs_median'), f'{result["price_vs_median"]:.2f}x')

    # Scenarios
    st.divider()
    st.subheader(t('scenarios_title'))
    scenarios = compare_scenarios(net, competitors, alpha / 100, beta / 100, gamma / 1000)
    df = pd.DataFrame([{
        t('col_strategy'): s['label'],
        t('col_premium'): f'¥{s["optimal_premium"]:,.0f}',
        t('col_margin'): f'{s["optimal_margin"]:.1f}%',
        t('col_profit'): f'¥{s["profit_per_policy"]:,.0f}',
        t('col_vs_median'): f'{s["price_vs_median"]:.2f}x',
    } for s in scenarios])
    st.dataframe(df, width='stretch', hide_index=True)

    # Positioning
    if competitors:
        st.subheader(t('position_title'))
        pos = optimal_vs_competitors(net, competitors, alpha / 100, beta / 100, gamma / 1000)
        dfp = pd.DataFrame([{
            t('col_competitor'): p['competitor'],
            t('col_their_price'): f'¥{p["their_price"]:,.0f}',
            t('col_our_price'): f'¥{p["our_price"]:,.0f}',
            t('col_diff'): f'{p["diff_pct"]:+.1f}%',
            t('col_position'): p['position'],
        } for p in pos])
        st.dataframe(dfp, width='stretch', hide_index=True)

with st.expander(t('how_title')):
    st.caption(t('how_text'))
