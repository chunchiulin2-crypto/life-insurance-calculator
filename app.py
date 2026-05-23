"""寿险精算计算器 · 首页"""

import streamlit as st

st.set_page_config(page_title='精算计算器', page_icon='🛡️', layout='wide')

# ---- i18n Navigation Labels ----
NAV = {
    'zh': {
        'home': '🏠 首页',
        'term': '🏠 定期寿险',
        'whole_life': '🔒 终身寿险',
        'annuity': '💰 生存年金',
        'endowment': '🎯 两全保险',
        'def_annuity': '⏳ 递延年金',
        'def_assurance': '⏰ 递延寿险',
        'pure_endow': '🎓 纯生存保险',
        'lang_label': '语言 / Language',
    },
    'en': {
        'home': '🏠 Home',
        'term': '🏠 Term Life',
        'whole_life': '🔒 Whole Life',
        'annuity': '💰 Life Annuity',
        'endowment': '🎯 Endowment',
        'def_annuity': '⏳ Deferred Annuity',
        'def_assurance': '⏰ Deferred Assurance',
        'pure_endow': '🎓 Pure Endowment',
        'lang_label': '语言 / Language',
    },
}

# ---- Init ----
if 'lang' not in st.session_state:
    st.session_state.lang = 'zh'

# ---- Language Switcher ----
with st.sidebar:
    lang = st.selectbox(
        NAV[st.session_state.lang]['lang_label'],
        ['中文', 'English'],
        index=0 if st.session_state.lang == 'zh' else 1,
    )
new_lang = 'zh' if lang == '中文' else 'en'
if new_lang != st.session_state.lang:
    st.session_state.lang = new_lang
    st.rerun()

# ---- Build Navigation with Bilingual Labels ----
L = NAV[st.session_state.lang]

pages = [
    st.Page('home.py', title=L['home'], default=True),
    st.Page('pages/1_Term_Life.py', title=L['term']),
    st.Page('pages/2_Whole_Life.py', title=L['whole_life']),
    st.Page('pages/3_Annuity.py', title=L['annuity']),
    st.Page('pages/4_Endowment.py', title=L['endowment']),
    st.Page('pages/5_Deferred_Annuity.py', title=L['def_annuity']),
    st.Page('pages/6_Deferred_Assurance.py', title=L['def_assurance']),
    st.Page('pages/7_Pure_Endowment.py', title=L['pure_endow']),
]

pg = st.navigation(pages)
pg.run()
