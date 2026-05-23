"""首页内容"""

import streamlit as st

T = {
    'zh': {
        'title': '寿险精算计算器',
        'subtitle': 'CLT 2010-2013 生命表 · 7 种产品 · 双语 · 核保分级 · 赔付时点 · 费用加载',
        'intro': '选择一个产品开始计算',
        'cards': [
            ('定期寿险', '约定期限内死亡赔付。最基础的产品。'),
            ('终身寿险', '无论何时死亡都赔付。保障终身。'),
            ('生存年金', '活着每年领钱。养老规划工具。'),
            ('两全保险', '死亡赔 + 到期返还。保障+储蓄。'),
            ('递延年金', '先缴费后领钱。养老储蓄。'),
            ('递延寿险', '先缴费后保障。递延期无赔付。'),
            ('纯生存保险', '活到约定年龄拿钱。纯储蓄。'),
        ],
    },
    'en': {
        'title': 'Life Insurance Actuarial Calculator',
        'subtitle': 'CLT 2010-2013 Table · 7 Products · Bilingual · UW Classes · Expense Loading',
        'intro': 'Select a product to begin',
        'cards': [
            ('Term Life', 'Death benefit within a fixed term.'),
            ('Whole Life', 'Lifetime coverage.'),
            ('Life Annuity', 'Periodic payments while alive.'),
            ('Endowment', 'Death benefit + maturity return.'),
            ('Deferred Annuity', 'Pay now, receive later.'),
            ('Deferred Assurance', 'Pay now, covered later.'),
            ('Pure Endowment', 'Survive to maturity, get paid.'),
        ],
    },
}


def t(key):
    return T[st.session_state.lang][key]


if 'lang' not in st.session_state:
    st.session_state.lang = 'zh'

cards = t('cards')

col1, col2, col3, col4 = st.columns(4)
row1 = cards[:4]
for i, col in enumerate([col1, col2, col3, col4]):
    name, desc = row1[i]
    with col:
        st.markdown(f'### {name}')
        st.caption(desc)

st.markdown('<br>', unsafe_allow_html=True)

col5, col6, col7 = st.columns(3)
row2 = cards[4:]
for i, col in enumerate([col5, col6, col7]):
    name, desc = row2[i]
    with col:
        st.markdown(f'### {name}')
        st.caption(desc)

st.divider()
st.caption('Select a product from the sidebar · 从侧边栏选择产品页面')
