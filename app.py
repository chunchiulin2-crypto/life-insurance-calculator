"""寿险精算计算器 · 首页"""

import streamlit as st

st.set_page_config(
    page_title='精算计算器',
    page_icon='🛡️',
    layout='wide',
)

# ---- i18n ----
T = {
    'zh': {
        'title': '寿险精算计算器',
        'subtitle': 'CLT 2010-2013 生命表 · 四种产品 · 双语 · 核保分级 · 赔付时点',
        'lang_label': '语言 / Language',
        'intro': '选择一个产品开始计算',
        'cards': [
            ('定期寿险', '🏠', '约定期限内死亡赔付。最基础、最常用的寿险产品。'),
            ('终身寿险', '🔒', '无论何时死亡都赔付。保障终身，保费较高。'),
            ('生存年金', '💰', '活着每年领钱。养老规划的经典工具。'),
            ('两全保险', '🎯', '死亡赔钱、到期生存也返还。保障+储蓄。'),
        ],
    },
    'en': {
        'title': 'Life Insurance Actuarial Calculator',
        'subtitle': 'CLT 2010-2013 Table · 4 Products · Bilingual · UW Classes · Payment Timing',
        'lang_label': '语言 / Language',
        'intro': 'Select a product to begin',
        'cards': [
            ('Term Life', '🏠', 'Death benefit within a fixed term. The most basic and common product.'),
            ('Whole Life', '🔒', 'Lifetime coverage. Pays on death whenever it occurs.'),
            ('Life Annuity', '💰', 'Periodic payments while alive. Classic retirement tool.'),
            ('Endowment', '🎯', 'Pays on death or at maturity. Protection + savings.'),
        ],
    },
}


def t(key):
    return T[st.session_state.lang][key]


# ---- Init ----
if 'lang' not in st.session_state:
    st.session_state.lang = 'zh'

lang = st.sidebar.selectbox(
    t('lang_label'), ['中文', 'English'],
    index=0 if st.session_state.lang == 'zh' else 1,
)
new_lang = 'zh' if lang == '中文' else 'en'
if new_lang != st.session_state.lang:
    st.session_state.lang = new_lang
    st.rerun()

# ---- Home Page ----
st.title(t('title'))
st.caption(t('subtitle'))
st.divider()
st.subheader(t('intro'))

cards = t('cards')
cols = st.columns(4)
for i, col in enumerate(cols):
    name, icon, desc = cards[i]
    with col:
        st.markdown(f'### {icon} {name}')
        st.caption(desc)

st.divider()
st.caption('👈 从侧边栏选择产品页面 · Select a product page from the sidebar')
