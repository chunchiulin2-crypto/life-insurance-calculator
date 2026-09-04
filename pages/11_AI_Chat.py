"""AI 智能问答 · NLP Insurance Chat"""
import streamlit as st
import os
from life_table_cache import cached_life_table
from nlp_parser import parse_query, format_response
from premium import (gross_annual_premium, periodic_premium,
                     annual_premium as net_ap,
                     annuity_price, endowment_annual_premium,
                     deferred_annuity_premium, pure_endowment_annual_premium,
                     deferred_term_annual_premium, deferred_whole_life_annual_premium)

st.set_page_config(page_title='AI Chat', layout='wide', initial_sidebar_state='expanded')

T = {
    'zh': {
        'title': 'AI 智能问答',
        'caption': '用自然语言描述需求 → AI 自动解析 → 精算引擎计算保费',
        'input_placeholder': '例如: 30岁男买100万定期寿险20年年缴利率3.5%',
        'send': '发送',
        'examples': '试试这些:',
        'ex1': '30岁男 100万定期寿险 20年 年缴',
        'ex2': '45岁女 200万终身寿险 月缴 利率3%',
        'ex3': '60岁买年金 50万趸缴 领15年',
        'ex4': '25岁递延年金 缴20年 60岁起年领10万',
        'result_title': '解析结果',
        'premium_title': '计算结果',
        'annual_premium': '年缴保费',
        'per_payment': '每期保费',
        'lump_sum': '趸缴保费',
        'not_understood': '没有完全理解你的需求，请尝试更具体的描述。例如: "30岁男买100万定期寿险20年"',
        'default_params': '未指定的参数使用默认值: 男/保额100万/20年/利率3.5%/年缴',
    },
    'en': {
        'title': 'AI Smart Chat',
        'caption': 'Describe your needs → AI parses → Actuarial engine calculates',
        'input_placeholder': 'e.g.: Male 30 buy 1M term life 20 years annual',
        'send': 'Send',
        'examples': 'Try these:',
        'ex1': 'Male 30, 1M term life, 20yr, annual',
        'ex2': 'Female 45, 2M whole life, monthly, rate 3%',
        'ex3': 'Age 60 annuity, 500K lump sum, 15yr payout',
        'ex4': 'Age 25 deferred annuity, pay 20yr, receive 100K/yr from 60',
        'result_title': 'Parsed Intent',
        'premium_title': 'Calculation Result',
        'annual_premium': 'Annual Premium',
        'per_payment': 'Per Payment',
        'lump_sum': 'Lump Sum',
        'not_understood': 'Could not fully understand. Try: "Male 30 buy 1M term life 20yr"',
        'default_params': 'Defaults for unspecified: Male/1M/20yr/3.5%/annual',
    },
}


def t(key, **kw):
    lang = st.session_state.get('lang', 'zh')
    text = T[lang][key]
    return text.format(**kw) if kw else text


st.title(t('title'))
st.caption(t('caption'))

# Init chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Load life table
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
default_path = os.path.join(DATA_DIR, 'clt_2010_2013.csv')
default_table_col = 'clt'


def calculate_premium(product, params):
    """Run the actuarial calculation for the parsed intent."""
    age = params.get('age', 30)
    gender = params.get('gender', 'M')
    sa = params.get('sum_insured', 1000000)
    term = params.get('term', 20)
    rate = params.get('rate', 0.035)
    freq = params.get('freq', 'annual')

    freq_map = {'annual': 1, 'semi': 2, 'quarterly': 4, 'monthly': 12}
    freq_m = freq_map.get(freq, 1)

    lt = cached_life_table(default_path, default_table_col, gender)

    # Default expense params
    alpha, beta, gamma = 0.05, 0.02, 0.0005

    result = {}

    if product == 'term_life':
        gap = gross_annual_premium(lt, age, sa, term, rate, alpha=alpha, beta=beta, gamma=gamma)
        result['annual'] = gap
        result['per_payment'] = periodic_premium(gap, freq_m)
        result['lump_sum'] = net_ap(lt, age, sa, term, rate)

    elif product == 'whole_life':
        max_age = 105
        wl_term = max_age - age
        gap = gross_annual_premium(lt, age, sa, wl_term, rate, alpha=alpha, beta=beta, gamma=gamma)
        result['annual'] = gap
        result['per_payment'] = periodic_premium(gap, freq_m)
        result['lump_sum'] = net_ap(lt, age, sa, wl_term, rate)

    elif product == 'annuity':
        price = annuity_price(lt, age, sa, term, rate)
        result['lump_sum'] = price
        result['annual'] = sa
        result['per_payment'] = sa / freq_m

    elif product == 'endowment':
        gap = endowment_annual_premium(lt, age, sa, term, rate, alpha=alpha, beta=beta, gamma=gamma)
        result['annual'] = gap
        result['per_payment'] = periodic_premium(gap, freq_m)
        result['lump_sum'] = net_ap(lt, age, sa, term, rate)

    elif product == 'deferred_annuity':
        retire_age = params.get('maturity_age', 60)
        defer = retire_age - age
        if defer <= 0:
            defer = 30
        annual_payout = params.get('sum_insured', 100000)
        ap = deferred_annuity_premium(lt, age, defer, annual_payout, rate, freq_m)
        result['annual'] = ap
        result['per_payment'] = ap / freq_m
        result['lump_sum'] = ap * defer

    elif product == 'deferred_assurance':
        start_age = params.get('maturity_age', 45)
        defer = start_age - age
        if defer <= 0:
            defer = 15
        ap = deferred_term_annual_premium(lt, age, defer, term, sa, rate)
        result['annual'] = ap
        result['per_payment'] = periodic_premium(ap, freq_m)

    elif product == 'pure_endowment':
        mat_age = params.get('maturity_age', 60)
        defer = mat_age - age
        if defer <= 0:
            defer = 30
        ap = pure_endowment_annual_premium(lt, age, mat_age, sa, rate)
        result['annual'] = ap
        result['per_payment'] = periodic_premium(ap, freq_m)
        result['lump_sum'] = ap * defer

    else:
        # Generic term life fallback
        gap = gross_annual_premium(lt, age, sa, term, rate, alpha=alpha, beta=beta, gamma=gamma)
        result['annual'] = gap
        result['per_payment'] = periodic_premium(gap, freq_m)

    return result


# ── Chat UI ──
st.caption(t('examples'))
cols = st.columns(2)
with cols[0]:
    if st.button(t('ex1'), use_container_width=True):
        st.session_state.chat_history.append(('user', t('ex1')))
        st.rerun()
    if st.button(t('ex3'), use_container_width=True):
        st.session_state.chat_history.append(('user', t('ex3')))
        st.rerun()
with cols[1]:
    if st.button(t('ex2'), use_container_width=True):
        st.session_state.chat_history.append(('user', t('ex2')))
        st.rerun()
    if st.button(t('ex4'), use_container_width=True):
        st.session_state.chat_history.append(('user', t('ex4')))
        st.rerun()

# Input
user_input = st.chat_input(t('input_placeholder'))
if user_input:
    st.session_state.chat_history.append(('user', user_input))

# Process last user message
last_user_msg = None
for role, msg in reversed(st.session_state.chat_history):
    if role == 'user':
        last_user_msg = msg
        break

if last_user_msg:
    product, params = parse_query(last_user_msg)
    parsed_text = format_response(product, params, st.session_state.get('lang', 'zh'))

    # Calculate
    try:
        premium_result = calculate_premium(product, params)
        has_result = True
    except Exception:
        has_result = False

# Display history
for role, msg in st.session_state.chat_history:
    if role == 'user':
        with st.chat_message('user'):
            st.write(msg)
    else:
        with st.chat_message('assistant'):
            st.markdown(msg)

# Show result for last message
if last_user_msg and ('_last_displayed' not in st.session_state or
                      st.session_state._last_displayed != last_user_msg):
    st.session_state._last_displayed = last_user_msg

    with st.chat_message('assistant'):
        st.subheader(t('result_title'))
        st.text(parsed_text)

        if has_result:
            st.subheader(t('premium_title'))
            c1, c2, c3 = st.columns(3)
            if 'annual' in premium_result:
                c1.metric(t('annual_premium'), f'¥{premium_result["annual"]:,.0f}')
            if 'per_payment' in premium_result:
                c2.metric(t('per_payment'), f'¥{premium_result["per_payment"]:,.0f}')
            if 'lump_sum' in premium_result:
                c3.metric(t('lump_sum'), f'¥{premium_result["lump_sum"]:,.0f}')
        else:
            st.warning(t('not_understood'))
        st.caption(t('default_params'))
