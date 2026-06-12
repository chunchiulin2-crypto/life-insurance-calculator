"""Product Comparison — side-by-side premium comparison."""
import streamlit as st
import pandas as pd
import os
from mortality import build_life_table, load_table
from premium import (annual_premium, whole_life_annual_premium, endowment_annual_premium,
                     annuity_price, deferred_annuity_premium, deferred_whole_life_single_premium,
                     pure_endowment_annual_premium, gross_annual_premium)

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

T = {
    'zh': {
        'title': '产品对比 · Product Comparison',
        'caption': '并排比较不同产品的保费与特性',
        'params': '通用参数',
        'age': '投保年龄', 'sum': '保险金额（元）', 'rate': '预定利率（%）',
        'term': '保险期限（年）', 'gender': '性别', 'gender_m': '男', 'gender_f': '女',
        'defer': '递延期（年）',
        'select_products': '选择要对比的产品（选 2–7 个）',
        'compare': '开始对比',
        'premium_col': '年毛保费', 'net_col': '年纯保费', 'per_payment': '每期保费（月缴）',
        'type_col': '产品类型', 'feature_col': '核心特点',
        'chart_title': '保费对比',
        'nav_home': '首页',
        'products': {
            'term': '定期寿险', 'whole_life': '终身寿险', 'annuity': '生存年金',
            'endowment': '两全保险', 'def_annuity': '递延年金', 'def_assurance': '递延寿险',
            'pure_endow': '纯生存保险',
        },
        'features': {
            'term': '约定期限内死亡赔付', 'whole_life': '终身保障、随时赔付',
            'annuity': '活着每年领钱', 'endowment': '死亡赔+到期返',
            'def_annuity': '先缴费后领钱', 'def_assurance': '先缴费后保障',
            'pure_endow': '活到约定年龄拿钱',
        },
    },
    'en': {
        'title': 'Product Comparison',
        'caption': 'Compare premiums and features side by side',
        'params': 'Parameters',
        'age': 'Entry Age', 'sum': 'Sum Assured (¥)', 'rate': 'Interest Rate (%)',
        'term': 'Term (years)', 'gender': 'Gender', 'gender_m': 'Male', 'gender_f': 'Female',
        'defer': 'Deferral (years)',
        'select_products': 'Select products to compare (2–7)',
        'compare': 'Compare',
        'premium_col': 'Gross Annual', 'net_col': 'Net Annual', 'per_payment': 'Monthly Payment',
        'type_col': 'Type', 'feature_col': 'Key Feature',
        'chart_title': 'Premium Comparison',
        'nav_home': 'Home',
        'products': {
            'term': 'Term Life', 'whole_life': 'Whole Life', 'annuity': 'Life Annuity',
            'endowment': 'Endowment', 'def_annuity': 'Deferred Annuity', 'def_assurance': 'Deferred Assurance',
            'pure_endow': 'Pure Endowment',
        },
        'features': {
            'term': 'Death benefit within term', 'whole_life': 'Lifetime coverage',
            'annuity': 'Periodic lifetime payments', 'endowment': 'Death + maturity return',
            'def_annuity': 'Pay now, receive later', 'def_assurance': 'Pay now, covered later',
            'pure_endow': 'Survive to maturity, get paid',
        },
    },
    'zh-Hant': {
        'title': '產品對比 · Product Comparison',
        'caption': '並排比較不同產品的保費與特性',
        'params': '通用參數',
        'age': '投保年齡', 'sum': '保險金額（元）', 'rate': '預定利率（%）',
        'term': '保險期限（年）', 'gender': '性別', 'gender_m': '男', 'gender_f': '女',
        'defer': '遞延期（年）',
        'select_products': '選擇要對比的產品（選 2–7 個）',
        'compare': '開始對比',
        'premium_col': '年毛保費', 'net_col': '年純保費', 'per_payment': '每期保費（月繳）',
        'type_col': '產品類型', 'feature_col': '核心特點',
        'chart_title': '保費對比',
        'nav_home': '首頁',
        'products': {
            'term': '定期壽險', 'whole_life': '終身壽險', 'annuity': '生存年金',
            'endowment': '兩全保險', 'def_annuity': '遞延年金', 'def_assurance': '遞延壽險',
            'pure_endow': '純生存保險',
        },
        'features': {
            'term': '约定期限内死亡赔付', 'whole_life': '終身保障、隨時賠付',
            'annuity': '活著每年領錢', 'endowment': '死亡賠+到期返',
            'def_annuity': '先繳費後領錢', 'def_assurance': '先繳費後保障',
            'pure_endow': '活到約定年齡拿錢',
        },
    },
}

if 'lang' not in st.session_state:
    st.session_state.lang = 'zh'

def t(key):
    lang = st.session_state.get('lang', 'zh')
    if lang not in T or key not in T[lang]:
        lang = 'zh'
    return T[lang][key]

st.set_page_config(page_title=t('title'), layout='wide', initial_sidebar_state='expanded')
st.title(t('title'))
st.caption(t('caption'))

st.markdown(f"""<div class="nav-strip"><a href="/" target="_self" class="nav-pill">{t('nav_home')}</a></div>""", unsafe_allow_html=True)

# ── Parameters ──
c1, c2, c3, c4 = st.columns(4)
with c1:
    age = st.slider(t('age'), 20, 60, 30)
with c2:
    sum_assured = st.number_input(t('sum'), 100000, 10000000, 1000000, 100000)
with c3:
    rate = st.slider(t('rate'), 0.5, 6.0, 3.5, 0.5) / 100.0
with c4:
    term = st.slider(t('term'), 1, 50, 20)

c1, c2 = st.columns(2)
with c1:
    gender = st.radio(t('gender'), [t('gender_m'), t('gender_f')], horizontal=True)
    g = 'M' if gender == t('gender_m') else 'F'
with c2:
    defer = st.slider(t('defer'), 5, 30, 10)

# ── Product Selection ──
products = list(T['zh']['products'].keys())
labels = [t('products')[p] for p in products]
selected_labels = st.multiselect(t('select_products'), labels, default=labels[:3])

if len(selected_labels) < 2:
    st.info('请至少选择 2 个产品进行对比')
    st.stop()

selected_keys = [products[labels.index(l)] for l in selected_labels]

# ── Calculate ──
if st.button(t('compare'), type='primary', use_container_width=True):
    table_path = st.session_state.get('table_path', os.path.join(DATA_DIR, 'clt_2010_2013.csv'))
    table_col = st.session_state.get('table_col', 'clt')
    col = g if table_col == 'clt' else table_col
    lt = build_life_table(load_table(table_path), col)

    rows = []
    premiums = []
    for key in selected_keys:
        try:
            if key == 'term':
                net = annual_premium(lt, age, sum_assured, term, rate)
            elif key == 'whole_life':
                net = whole_life_annual_premium(lt, age, sum_assured, rate)
            elif key == 'annuity':
                payment = sum_assured * 0.05
                net = annuity_price(lt, age, payment, term, rate)
            elif key == 'endowment':
                net = endowment_annual_premium(lt, age, sum_assured, term, rate)
            elif key == 'def_annuity':
                annual_pay = sum_assured * 0.05
                net = deferred_annuity_premium(lt, age, defer, annual_pay, rate)
            elif key == 'def_assurance':
                net = deferred_whole_life_single_premium(lt, age, defer, sum_assured, rate) / max(1, defer)
            elif key == 'pure_endow':
                net = pure_endowment_annual_premium(lt, age, sum_assured, term, rate)
            else:
                net = 0

            gross = net * 1.05  # simplified gross with 5% loading
            monthly = gross / 12

            premiums.append((t('products')[key], gross))
            rows.append({
                t('type_col'): t('products')[key],
                t('feature_col'): t('features')[key],
                t('net_col'): f"¥{net:,.0f}",
                t('premium_col'): f"¥{gross:,.0f}",
                t('per_payment'): f"¥{monthly:,.0f}",
            })
        except Exception as e:
            rows.append({
                t('type_col'): t('products')[key],
                t('feature_col'): t('features')[key],
                t('net_col'): 'N/A', t('premium_col'): 'N/A', t('per_payment'): str(e)[:50],
            })

    # ── Table ──
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # ── Chart ──
    if premiums:
        chart_df = pd.DataFrame(premiums, columns=['Product', 'Premium'])
        st.subheader(t('chart_title'))
        st.bar_chart(chart_df.set_index('Product'), height=350)
