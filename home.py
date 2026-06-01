"""首页内容"""

import streamlit as st

# Product index → category tag
CARD_TAGS = {
    'zh': ['保障', '保障', '養老', '保障+儲蓄', '養老', '保障', '儲蓄'],
    'en': ['Protection', 'Protection', 'Retirement', 'Protect+Save', 'Retirement', 'Protection', 'Savings'],
    'zh-Hant': ['保障', '保障', '養老', '保障+儲蓄', '養老', '保障', '儲蓄'],
}
CATEGORY_COLORS = ['#007AFF', '#007AFF', '#34C759', '#FF9500', '#34C759', '#007AFF', '#AF52DE']

T = {
    'zh': {
        'title': '寿险精算计算器',
        'hero': 'CLT 2010-2013 & AM92 双生命表 · 7 种精算产品 · 中英双语 · 保费 + 准备金一体化计算',
        'cards': [
            ('定期寿险', '约定期限内死亡赔付。最基础的产品。'),
            ('终身寿险', '无论何时死亡都赔付。保障终身。'),
            ('生存年金', '活着每年领钱。养老规划工具。'),
            ('两全保险', '死亡赔 + 到期返还。保障+储蓄。'),
            ('递延年金', '先缴费后领钱。养老储蓄。'),
            ('递延寿险', '先缴费后保障。递延期无赔付。'),
            ('纯生存保险', '活到约定年龄拿钱。纯储蓄。'),
        ],
        'guide_title': '不知道怎么选？',
        'guide_1': '需要**身故保障** → 定期寿险（预算有限）/ 终身寿险（终身保障）/ 递延寿险（未来再开始）',
        'guide_2': '需要**养老储蓄** → 生存年金（即将退休）/ 递延年金（还在工作积累期）',
        'guide_3': '**保障 + 储蓄**都要 → 两全保险（到期返还 + 身故赔付）',
        'guide_4': '只想存一笔钱，活到约定年龄才拿 → 纯生存保险',
        'footer': '保障型：1—4　　储蓄/年金型：5—7',
        'nav_home': '首页', 'nav_term': '定期寿险', 'nav_whole_life': '终身寿险',
        'nav_annuity': '生存年金', 'nav_endowment': '两全保险', 'nav_def_annuity': '递延年金',
        'nav_def_assurance': '递延寿险', 'nav_pure_endow': '纯生存保险',
    },
    'en': {
        'title': 'Life Insurance Actuarial Calculator',
        'hero': 'CLT 2010-2013 & AM92 Dual Life Tables · 7 Products · Bilingual · Premium & Reserve Calculator',
        'cards': [
            ('Term Life', 'Death benefit within a fixed term.'),
            ('Whole Life', 'Lifetime coverage.'),
            ('Life Annuity', 'Periodic payments while alive.'),
            ('Endowment', 'Death benefit + maturity return.'),
            ('Deferred Annuity', 'Pay now, receive later.'),
            ('Deferred Assurance', 'Pay now, covered later.'),
            ('Pure Endowment', 'Survive to maturity, get paid.'),
        ],
        'guide_title': 'Not sure which to pick?',
        'guide_1': 'Need **death protection** → Term Life (budget) / Whole Life (lifetime) / Deferred Assurance (future start)',
        'guide_2': 'Need **retirement income** → Life Annuity (near retirement) / Deferred Annuity (still saving)',
        'guide_3': 'Want **protection + savings** → Endowment (maturity return + death benefit)',
        'guide_4': 'Just a savings goal, paid only if you survive → Pure Endowment',
        'footer': 'Protection: 1–4　　Savings/Annuity: 5–7',
        'nav_home': 'Home', 'nav_term': 'Term Life', 'nav_whole_life': 'Whole Life',
        'nav_annuity': 'Life Annuity', 'nav_endowment': 'Endowment', 'nav_def_annuity': 'Deferred Annuity',
        'nav_def_assurance': 'Deferred Assurance', 'nav_pure_endow': 'Pure Endowment',
    },
    'zh-Hant': {
        'title': '壽險精算計算器',
        'hero': 'CLT 2010-2013 & AM92 雙生命表 · 7 種精算產品 · 中英雙語 · 保費 + 準備金一體化計算',
        'cards': [
            ('定期壽險', '約定期限內死亡給付。最基礎的產品。'),
            ('終身壽險', '不論何時死亡皆給付。保障終身。'),
            ('生存年金', '活著每年領錢。退休規劃工具。'),
            ('兩全保險', '死亡給付 + 到期返還。保障+儲蓄。'),
            ('遞延年金', '先繳費後領錢。退休儲蓄。'),
            ('遞延壽險', '先繳費後保障。遞延期無給付。'),
            ('純生存保險', '活到約定年齡領錢。純儲蓄。'),
        ],
        'guide_title': '不知道怎麼選？',
        'guide_1': '需要**身故保障** → 定期壽險（預算有限）/ 終身壽險（終身保障）/ 遞延壽險（未來再開始）',
        'guide_2': '需要**退休儲蓄** → 生存年金（即將退休）/ 遞延年金（仍在工作累積期）',
        'guide_3': '**保障 + 儲蓄**都要 → 兩全保險（到期返還 + 身故給付）',
        'guide_4': '只想存一筆錢，活到約定年齡才領 → 純生存保險',
        'footer': '保障型：1—4　　儲蓄/年金型：5—7',
        'nav_home': '首頁', 'nav_term': '定期壽險', 'nav_whole_life': '終身壽險',
        'nav_annuity': '生存年金', 'nav_endowment': '兩全保險', 'nav_def_annuity': '遞延年金',
        'nav_def_assurance': '遞延壽險', 'nav_pure_endow': '純生存保險',
    },
}


def t(key):
    return T[st.session_state.lang][key]


if 'lang' not in st.session_state:
    st.session_state.lang = 'zh'

lang = st.session_state.lang

st.title(t('title'))
st.caption(t('hero'))

CURRENT_PAGE = 'home'
ACTIVE_STYLE = ' style="color:#1D1D1F;border-color:#AEAEB2;"'

st.markdown(f"""
<div class="nav-strip">
<a href="/" target="_self" class="nav-pill"{ACTIVE_STYLE if CURRENT_PAGE == 'home' else ''}>{t('nav_home')}</a>
<a href="/Term_Life" target="_self" class="nav-pill"{ACTIVE_STYLE if CURRENT_PAGE == 'term' else ''}>{t('nav_term')}</a>
<a href="/Whole_Life" target="_self" class="nav-pill"{ACTIVE_STYLE if CURRENT_PAGE == 'whole_life' else ''}>{t('nav_whole_life')}</a>
<a href="/Annuity" target="_self" class="nav-pill"{ACTIVE_STYLE if CURRENT_PAGE == 'annuity' else ''}>{t('nav_annuity')}</a>
<a href="/Endowment" target="_self" class="nav-pill"{ACTIVE_STYLE if CURRENT_PAGE == 'endowment' else ''}>{t('nav_endowment')}</a>
<a href="/Deferred_Annuity" target="_self" class="nav-pill"{ACTIVE_STYLE if CURRENT_PAGE == 'def_annuity' else ''}>{t('nav_def_annuity')}</a>
<a href="/Deferred_Assurance" target="_self" class="nav-pill"{ACTIVE_STYLE if CURRENT_PAGE == 'def_assurance' else ''}>{t('nav_def_assurance')}</a>
<a href="/Pure_Endowment" target="_self" class="nav-pill"{ACTIVE_STYLE if CURRENT_PAGE == 'pure_endow' else ''}>{t('nav_pure_endow')}</a>
</div>
""", unsafe_allow_html=True)
st.divider()

PAGE_URLS = [
    'Term_Life', 'Whole_Life', 'Annuity', 'Endowment',
    'Deferred_Annuity', 'Deferred_Assurance', 'Pure_Endowment',
]

cards = t('cards')
tags = CARD_TAGS[lang]
cols = st.columns(4)
cols2 = st.columns(4)

for i, (name, desc) in enumerate(cards):
    col = cols[i] if i < 4 else cols2[i - 4]
    color = CATEGORY_COLORS[i]
    tag = tags[i]
    url = PAGE_URLS[i]
    with col:
        st.markdown(f"""
        <a href="/{url}" target="_self" style="text-decoration:none;color:inherit;">
        <div class="apple-card">
            <h3>{name}</h3>
            <p>{desc}</p>
            <span style="display:inline-block;margin-top:0.5rem;padding:0.15rem 0.6rem;
            font-size:0.72rem;font-weight:600;color:{color};background:{color}15;
            border-radius:6px;border-left:3px solid {color};">{tag}</span>
        </div>
        </a>
        """, unsafe_allow_html=True)

st.divider()

with st.expander(t('guide_title'), expanded=False):
    st.markdown(t('guide_1'))
    st.markdown(t('guide_2'))
    st.markdown(t('guide_3'))
    st.markdown(t('guide_4'))

st.caption(t('footer'))
