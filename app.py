"""寿险精算计算器 · 首页"""

import os
import streamlit as st

st.set_page_config(page_title='精算计算器', layout='wide', initial_sidebar_state='expanded')

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

# Initialize session state defaults (must run before any page accesses them via st.navigation)
if 'lang' not in st.session_state:
    st.session_state.lang = 'zh'
if 'table_col' not in st.session_state:
    st.session_state.table_col = 'clt'
if 'table_path' not in st.session_state:
    st.session_state.table_path = os.path.join(DATA_DIR, 'clt_2010_2013.csv')

st.markdown('''
<style>
/* === Apple-Style Global CSS === */

/* System font stack */
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", "PingFang SC", sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    letter-spacing: -0.01em;
}

/* === Kill default Streamlit top padding === */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="stHeader"] { background: transparent !important; height: 2.5rem !important; }
[data-testid="stAppViewContainer"] > .block-container {
    padding-top: 0.5rem !important;
    padding-bottom: 0 !important;
}
.stMain { padding-top: 0; }

/* === Typography === */
h1 { font-weight: 700 !important; letter-spacing: -0.02em !important; font-size: 1.5rem !important; margin-top: 0 !important; }
h2 { font-weight: 600 !important; letter-spacing: -0.01em !important; font-size: 1.1rem !important; }
h3 { font-weight: 600 !important; font-size: 1rem !important; }

/* === Sidebar === */
[data-testid="stSidebar"] {
    background: #FAFAFA;
    border-right: 1px solid #E5E5EA !important;
    box-shadow: 2px 0 8px rgba(0, 0, 0, 0.06);
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stRadio label {
    font-size: 0.8rem;
    font-weight: 600;
    color: #6E6E73;
    text-transform: none;
    letter-spacing: 0;
    margin-bottom: 0;
}
[data-testid="stSidebar"] hr {
    margin: 0.5rem 0;
    border-color: #E5E5EA;
}

/* === Metric Cards === */
[data-testid="stMetric"] {
    background: #FFFFFF;
    border-radius: 14px;
    padding: 1rem 1.25rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 1px 8px rgba(0,0,0,0.02);
    border: 0.5px solid #F0F0F2;
    transition: box-shadow 0.2s ease;
}
[data-testid="stMetric"]:hover {
    box-shadow: 0 4px 16px rgba(0,0,0,0.06), 0 1px 4px rgba(0,0,0,0.04);
}
[data-testid="stMetricLabel"] {
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    color: #6E6E73 !important;
    letter-spacing: 0.02em;
    text-transform: none;
}
[data-testid="stMetricValue"] {
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    color: #1D1D1F !important;
}
[data-testid="stMetricDelta"] {
    font-size: 0.8rem !important;
}

/* === Apple-Style Cards === */
.apple-card {
    background: #FFFFFF;
    border-radius: 14px;
    padding: 1.25rem 1.5rem;
    border: 0.5px solid #F0F0F2;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 1px 8px rgba(0,0,0,0.02);
    transition: box-shadow 0.25s ease, transform 0.2s ease;
    cursor: default;
}
.apple-card:hover {
    box-shadow: 0 12px 32px rgba(0,0,0,0.08), 0 2px 8px rgba(0,0,0,0.04);
    transform: translateY(-3px);
}
.apple-card h3 {
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    margin-bottom: 0.25rem;
    color: #1D1D1F;
}
.apple-card p {
    font-size: 0.82rem;
    color: #86868B;
    margin: 0;
}

/* === Charts === */
[data-testid="stArrowVegaLiteChart"] {
    background: #FFFFFF;
    border-radius: 14px;
    padding: 0.75rem;
    border: 0.5px solid #F0F0F2;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}

/* === DataFrames === */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 0.5px solid #E5E5EA;
}

/* === Info / Note boxes === */
[data-testid="stNotification"] {
    border-radius: 12px;
    border: none;
    background: #F5F5F7;
    font-size: 0.85rem;
    color: #6E6E73;
}

/* === Dividers === */
hr {
    border-color: #E5E5EA !important;
    margin: 0.5rem 0 !important;
}

/* === Sidebar widgets === */
[data-testid="stSidebar"] .st-bx { gap: 0.25rem; }
[data-testid="stSidebar"] [data-testid="stExpander"] {
    border: none;
    border-radius: 12px;
    background: #F5F5F7;
    margin-top: 0.5rem;
}

/* === Sliders === */
div[data-testid="stSlider"] div[role="slider"] {
    background: #007AFF;
    border: 2px solid #FFFFFF;
    box-shadow: 0 1px 4px rgba(0,0,0,0.12);
}

/* === Radio buttons === */
div[data-testid="stRadio"] label[data-baseweb="radio"] {
    background: #F5F5F7;
    border-radius: 10px;
    padding: 0.15rem 0.6rem;
    margin-right: 0.25rem;
    font-size: 0.85rem;
    transition: background 0.15s ease;
}

/* === Scrollbar (macOS thin style) === */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #C7C7CC; border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: #AEAEB2; }

/* === Top header (keep minimal but visible for sidebar toggle) === */
/* Reduce toolbar visual weight without hiding it */
[data-testid="stToolbar"] {
    opacity: 0.3;
    transition: opacity 0.2s ease;
}
[data-testid="stToolbar"]:hover {
    opacity: 0.8;
}

/* Deploy button — keep it subtle */
[data-testid="stDeployButton"] {
    font-size: 0.7rem !important;
    opacity: 0.5;
    transition: opacity 0.2s;
}
[data-testid="stDeployButton"]:hover {
    opacity: 1;
}

/* === Captions / Footer text === */
.stCaption { color: #AEAEB2 !important; font-size: 0.75rem !important; }

/* === Subheader === */
.stSubheader { font-weight: 600; letter-spacing: -0.01em; font-size: 1rem !important; }

/* === Expander arrow fix === */
[data-testid="stExpander"] svg { color: #86868B; }

/* === Top bar widget labels — make them compact === */
.col_lang_label, .col_table_label {
    font-size: 0.7rem;
    font-weight: 600;
    color: #86868B;
    margin-bottom: 0;
    line-height: 1;
}

/* === Metric Color Accent Bars === */
[data-testid="stMetric"] {
    position: relative;
    overflow: hidden;
}
[data-testid="stMetric"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 3px 3px 0 0;
}
[data-testid="stColumn"]:nth-child(1) [data-testid="stMetric"]::before { background: #007AFF; }
[data-testid="stColumn"]:nth-child(2) [data-testid="stMetric"]::before { background: #34C759; }
[data-testid="stColumn"]:nth-child(3) [data-testid="stMetric"]::before { background: #FF9500; }
[data-testid="stColumn"]:nth-child(4) [data-testid="stMetric"]::before { background: #AF52DE; }

/* === Parameter Chips === */
.param-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 0.35rem;
    margin: 0.5rem 0 0 0;
}
.param-chip {
    display: inline-block;
    padding: 0.25rem 0.65rem;
    font-size: 0.78rem;
    font-weight: 500;
    color: #1D1D1F;
    background: #FFFFFF;
    border: 0.5px solid #E5E5EA;
    border-radius: 20px;
    white-space: nowrap;
    transition: border-color 0.15s ease;
}
.param-chip:hover { border-color: #AEAEB2; }

/* === Product Nav Strip === */
.nav-strip {
    display: flex;
    flex-wrap: wrap;
    gap: 0.3rem;
    margin: 0.25rem 0 0.25rem 0;
}
.nav-pill {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    font-size: 0.75rem;
    font-weight: 500;
    color: #6E6E73;
    background: #FFFFFF;
    border: 0.5px solid #E5E5EA;
    border-radius: 14px;
    text-decoration: none;
    transition: all 0.15s ease;
}
.nav-pill:hover {
    color: #1D1D1F;
    border-color: #AEAEB2;
    background: #F5F5F7;
}

</style>
''', unsafe_allow_html=True)

# Force sidebar to stay open (clear all possible persisted collapsed states)
st.markdown("""
<script>
(function() {
    // Clear all known Streamlit sidebar state keys
    var keys = Object.keys(localStorage);
    for (var i = 0; i < keys.length; i++) {
        if (keys[i].toLowerCase().indexOf('sidebar') !== -1 ||
            keys[i].indexOf('stSidebar') !== -1 ||
            keys[i].indexOf('collapsed') !== -1) {
            localStorage.removeItem(keys[i]);
        }
    }
    // Also clear all sessionStorage sidebar keys
    keys = Object.keys(sessionStorage);
    for (var i = 0; i < keys.length; i++) {
        if (keys[i].toLowerCase().indexOf('sidebar') !== -1 ||
            keys[i].indexOf('stSidebar') !== -1 ||
            keys[i].indexOf('collapsed') !== -1) {
            sessionStorage.removeItem(keys[i]);
        }
    }
})();
</script>
""", unsafe_allow_html=True)

# ---- i18n Navigation Labels ----
NAV = {
    'zh': {
        'home': '首页',
        'term': '定期寿险',
        'whole_life': '终身寿险',
        'annuity': '生存年金',
        'endowment': '两全保险',
        'def_annuity': '递延年金',
        'def_assurance': '递延寿险',
        'pure_endow': '纯生存保险',
        'ai_mortality': 'AI 死亡率',
        'fraud': 'AI 反欺诈',
        'pricing': 'AI 定价优化',
        'chat': 'AI 智能问答',
        'lang_label': '语言 / Language',
        'table_label': '生命表',
        'table_clt': 'CLT 2010-2013',
        'table_am92ult': 'AM92 Ultimate',
        'table_am92sel': 'AM92 Select',
        'table_am92sel_plusone': 'AM92 Select+1',
        'sidebar_brand': '精算计算器',
    },
    'en': {
        'home': 'Home',
        'term': 'Term Life',
        'whole_life': 'Whole Life',
        'annuity': 'Life Annuity',
        'endowment': 'Endowment',
        'def_annuity': 'Deferred Annuity',
        'def_assurance': 'Deferred Assurance',
        'pure_endow': 'Pure Endowment',
        'ai_mortality': 'AI Mortality',
        'fraud': 'Fraud Detection',
        'pricing': 'AI Pricing',
        'chat': 'AI Chat',
        'lang_label': '语言 / Language',
        'table_label': 'Life Table',
        'table_clt': 'CLT 2010-2013',
        'table_am92ult': 'AM92 Ultimate',
        'table_am92sel': 'AM92 Select',
        'table_am92sel_plusone': 'AM92 Select+1',
        'sidebar_brand': 'Actuarial Calc',
    },
    'zh-Hant': {
        'home': '首頁',
        'term': '定期壽險',
        'whole_life': '終身壽險',
        'annuity': '生存年金',
        'endowment': '兩全保險',
        'def_annuity': '遞延年金',
        'def_assurance': '遞延壽險',
        'pure_endow': '純生存保險',
        'ai_mortality': 'AI 死亡率',
        'fraud': 'AI 反欺詐',
        'pricing': 'AI 定價優化',
        'chat': 'AI 智能問答',
        'lang_label': '語言 / Language',
        'table_label': '生命表',
        'table_clt': 'CLT 2010-2013',
        'table_am92ult': 'AM92 Ultimate',
        'table_am92sel': 'AM92 Select',
        'table_am92sel_plusone': 'AM92 Select+1',
        'sidebar_brand': '精算計算器',
    },
}

TABLE_OPTIONS = {
    'CLT 2010-2013': ('clt_2010_2013.csv', 'clt'),
    'AM92 Ultimate': ('am92.csv', 'am92ult'),
    'AM92 Select': ('am92.csv', 'am92sel'),
    'AM92 Select+1': ('am92.csv', 'am92sel_plusone'),
}

# ---- Init ----
L = NAV[st.session_state.lang]

LANG_OPTIONS = ['中文', 'English', '繁體中文']
LANG_KEYS = {'中文': 'zh', 'English': 'en', '繁體中文': 'zh-Hant'}
lang_idx = list(LANG_KEYS.values()).index(st.session_state.lang) if st.session_state.lang in LANG_KEYS.values() else 0

# ---- Top Bar: Brand + Language + Table ----
col_brand, col_lang, col_table = st.columns([5, 1, 1.2])
with col_brand:
    st.markdown(f"<p style='font-size:0.75rem;font-weight:700;color:#86868B;"
                f"letter-spacing:0.04em;text-transform:uppercase;"
                f"margin:0;line-height:1;'>{L['sidebar_brand']}</p>",
                unsafe_allow_html=True)
with col_lang:
    lang = st.selectbox(L['lang_label'], LANG_OPTIONS, index=lang_idx, label_visibility='visible')
    new_lang = LANG_KEYS[lang]
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()
with col_table:
    table_choice = st.selectbox(L['table_label'], list(TABLE_OPTIONS.keys()), index=0, label_visibility='visible')
    st.session_state.table_path = os.path.join(DATA_DIR, TABLE_OPTIONS[table_choice][0])
    st.session_state.table_col = TABLE_OPTIONS[table_choice][1]

st.divider()

pages = [
    st.Page('home.py', title=L['home'], url_path='', default=True),
    st.Page('pages/1_Term_Life.py', title=L['term'], url_path='Term_Life'),
    st.Page('pages/2_Whole_Life.py', title=L['whole_life'], url_path='Whole_Life'),
    st.Page('pages/3_Annuity.py', title=L['annuity'], url_path='Annuity'),
    st.Page('pages/4_Endowment.py', title=L['endowment'], url_path='Endowment'),
    st.Page('pages/5_Deferred_Annuity.py', title=L['def_annuity'], url_path='Deferred_Annuity'),
    st.Page('pages/6_Deferred_Assurance.py', title=L['def_assurance'], url_path='Deferred_Assurance'),
    st.Page('pages/7_Pure_Endowment.py', title=L['pure_endow'], url_path='Pure_Endowment'),
    st.Page('pages/8_AI_Mortality.py', title=L['ai_mortality'], url_path='AI_Mortality'),
    st.Page('pages/9_Fraud_Detection.py', title=L['fraud'], url_path='Fraud_Detection'),
    st.Page('pages/10_Pricing_Optimizer.py', title=L['pricing'], url_path='Pricing_Optimizer'),
    st.Page('pages/11_AI_Chat.py', title=L['chat'], url_path='AI_Chat'),
]

pg = st.navigation(pages)
pg.run()
