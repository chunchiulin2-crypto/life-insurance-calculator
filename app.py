"""寿险精算计算器 · 首页"""

import streamlit as st

st.set_page_config(page_title='精算计算器', page_icon='🛡️', layout='wide')

T = {
    'zh': {
        'title': '寿险精算计算器',
        'subtitle': 'CLT 2010-2013 生命表 · 7 种产品 · 双语 · 核保分级 · 赔付时点 · 费用加载',
        'lang_label': '语言 / Language',
        'intro': '选择一个产品开始计算',
        'cards': [
            ('定期寿险', '🏠', '约定期限内死亡赔付。最基础的产品。'),
            ('终身寿险', '🔒', '无论何时死亡都赔付。保障终身。'),
            ('生存年金', '💰', '活着每年领钱。养老规划工具。'),
            ('两全保险', '🎯', '死亡赔 + 到期返还。保障+储蓄。'),
            ('递延年金', '⏳', '先缴费后领钱。养老储蓄。'),
            ('递延寿险', '⏰', '先缴费后保障。递延期无赔付。'),
            ('纯生存保险', '🎓', '活到约定年龄拿钱。纯储蓄。'),
        ],
    },
    'en': {
        'title': 'Life Insurance Actuarial Calculator',
        'subtitle': 'CLT 2010-2013 Table · 7 Products · Bilingual · UW Classes · Expense Loading',
        'lang_label': '语言 / Language',
        'intro': 'Select a product to begin',
        'cards': [
            ('Term Life', '🏠', 'Death benefit within a fixed term.'),
            ('Whole Life', '🔒', 'Lifetime coverage.'),
            ('Life Annuity', '💰', 'Periodic payments while alive.'),
            ('Endowment', '🎯', 'Death benefit + maturity return.'),
            ('Deferred Annuity', '⏳', 'Pay now, receive later.'),
            ('Deferred Assurance', '⏰', 'Pay now, covered later.'),
            ('Pure Endowment', '🎓', 'Survive to maturity, get paid.'),
        ],
    },
}


def t(key):
    return T[st.session_state.lang][key]


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

st.title(t('title'))
st.caption(t('subtitle'))
st.divider()
st.subheader(t('intro'))

cards = t('cards')
rows = [cards[i:i+4] for i in range(0, len(cards), 4)]
for row in rows:
    cols = st.columns(len(row))
    for i, col in enumerate(cols):
        name, icon, desc = row[i]
        with col:
            st.markdown(f'### {icon} {name}')
            st.caption(desc)

st.divider()
st.caption('👈 Select a product from the sidebar · 从侧边栏选择产品页面')
