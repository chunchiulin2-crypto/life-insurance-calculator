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
/* === Actuarial Pro · Apple-Style === */

:root {
    --bg: #f2f2f7;
    --card: #ffffff;
    --accent: #007AFF;
    --accent-dim: rgba(0,122,255,0.08);
    --text: #1d1d1f;
    --text-secondary: #515154;
    --muted: #86868b;
    --border: rgba(0,0,0,0.06);
    --border-strong: rgba(0,0,0,0.1);
    --shadow-sm: 0 0.5px 1px rgba(0,0,0,0.04);
    --shadow-md: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.02);
    --shadow-lg: 0 4px 16px rgba(0,0,0,0.06), 0 1px 4px rgba(0,0,0,0.04);
    --radius-sm: 10px;
    --radius: 14px;
    --radius-lg: 18px;
}

html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", "PingFang SC", sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    font-size: 15px;
    color: var(--text);
}

/* Background — subtle mesh */
.stApp {
    background:
        radial-gradient(ellipse 80% 50% at 50% -20%, rgba(0,122,255,0.03), transparent),
        radial-gradient(ellipse 60% 40% at 80% 80%, rgba(0,122,255,0.02), transparent),
        linear-gradient(180deg, #fafafc 0%, #f2f2f7 40%, #eeeef3 100%);
}

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="stHeader"] { background: transparent !important; height: 2rem !important; }
[data-testid="stAppViewContainer"] > .block-container { padding: 0 2rem 0 2rem !important; max-width: 1200px; }
.block-container { max-width: 1200px; padding-left: 1.5rem !important; padding-right: 1.5rem !important; }

/* ── Typography ── */
h1 {
    font-weight: 700 !important; font-size: 1.75rem !important;
    letter-spacing: -0.03em !important; line-height: 1.15 !important;
    color: var(--text) !important; margin-bottom: 0.25rem !important;
}
h2 { font-weight: 600 !important; font-size: 1.15rem !important; letter-spacing: -0.02em !important; color: var(--text) !important; }
h3 { font-weight: 600 !important; font-size: 1rem !important; color: var(--text-secondary) !important; }

/* Label style — uppercase tracking */
label, .stSelectbox label, .stSlider label {
    font-size: 0.7rem !important; font-weight: 600 !important;
    color: var(--muted) !important; letter-spacing: 0.05em;
    text-transform: uppercase !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: rgba(250,250,252,0.82);
    backdrop-filter: blur(24px) saturate(180%);
    -webkit-backdrop-filter: blur(24px) saturate(180%);
    border-right: 0.5px solid var(--border-strong) !important;
}
[data-testid="stSidebar"] .block-container { padding: 1.25rem 1rem !important; }
[data-testid="stSidebar"] hr { margin: 0.75rem 0; border-color: var(--border); }
[data-testid="stSidebar"] [data-testid="stExpander"] {
    border-radius: var(--radius-sm); border: 0.5px solid var(--border);
    background: rgba(255,255,255,0.6); margin-top: 0.5rem;
}
/* Sidebar section headings */
[data-testid="stSidebar"] .stMarkdown p { font-size: 0.7rem; font-weight: 600; color: var(--muted); letter-spacing: 0.06em; text-transform: uppercase; }

/* ── Metric Cards ── */
[data-testid="stMetric"] {
    background: var(--card);
    border-radius: var(--radius-lg); padding: 1.25rem 1.5rem;
    border: 0.5px solid var(--border);
    box-shadow: var(--shadow-sm);
    transition: all 0.3s cubic-bezier(0.25, 0.1, 0.25, 1);
    position: relative; overflow: hidden;
}
[data-testid="stMetric"]:hover {
    box-shadow: var(--shadow-lg); transform: translateY(-2px);
    border-color: rgba(0,122,255,0.15);
}
[data-testid="stMetricLabel"] {
    font-size: 0.65rem !important; font-weight: 600 !important;
    color: var(--muted) !important; letter-spacing: 0.08em;
    text-transform: uppercase !important; margin-bottom: 0.25rem !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.75rem !important; font-weight: 700 !important;
    color: var(--text) !important; letter-spacing: -0.02em;
    font-feature-settings: "tnum"; font-variant-numeric: tabular-nums;
}
[data-testid="stMetric"]::before {
    content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, var(--accent), rgba(0,122,255,0.2));
    opacity: 0; transition: opacity 0.3s;
}
[data-testid="stMetric"]:hover::before { opacity: 1; }

/* ── Cards ── */
.apple-card {
    background: var(--card);
    border-radius: var(--radius-lg); padding: 1.5rem 1.75rem;
    border: 0.5px solid var(--border);
    box-shadow: var(--shadow-sm);
    transition: all 0.3s cubic-bezier(0.25, 0.1, 0.25, 1);
}
.apple-card:hover {
    box-shadow: var(--shadow-lg); transform: translateY(-2px);
    border-color: rgba(0,122,255,0.12);
}
.apple-card h3 { color: var(--text) !important; font-weight: 700 !important; font-size: 1.05rem !important; margin-bottom: 0.35rem; }
.apple-card p { color: var(--text-secondary); font-size: 0.85rem; line-height: 1.5; margin: 0; }

/* ── Container borders ── */
[data-testid="stExpander"] {
    border: 0.5px solid var(--border) !important;
    border-radius: var(--radius) !important;
    background: rgba(255,255,255,0.6);
}
[data-testid="stExpander"] svg { color: var(--muted); }

/* ── Charts ── */
[data-testid="stArrowVegaLiteChart"] {
    background: var(--card);
    border-radius: var(--radius-lg); padding: 0.75rem;
    border: 0.5px solid var(--border);
    box-shadow: var(--shadow-sm);
}

/* ── Tables ── */
[data-testid="stDataFrame"] {
    border-radius: var(--radius-sm); overflow: hidden;
    border: 0.5px solid var(--border-strong);
}
[data-testid="stDataFrame"] th {
    background: #f9f9fb !important; padding: 0.5rem 0.75rem !important;
    font-size: 0.68rem !important; font-weight: 600 !important;
    text-transform: uppercase; letter-spacing: 0.06em;
    color: var(--muted) !important; border-bottom: 1px solid var(--border) !important;
}
[data-testid="stDataFrame"] td {
    padding: 0.4rem 0.75rem !important; font-size: 0.82rem !important;
    color: var(--text) !important; border-bottom: 0.5px solid var(--border) !important;
    font-feature-settings: "tnum"; font-variant-numeric: tabular-nums;
}
[data-testid="stDataFrame"] tr:hover td { background: rgba(0,122,255,0.03); }

/* ── Widgets ── */
.stSelectbox > div { border-radius: var(--radius-sm) !important; border-color: var(--border-strong) !important; box-shadow: var(--shadow-sm) !important; }
.stSelectbox > div:focus-within { border-color: var(--accent) !important; box-shadow: 0 0 0 3px var(--accent-dim) !important; }

.stSlider > div { padding-top: 0.25rem; }
div[data-testid="stSlider"] div[role="slider"] {
    background: var(--accent); border: 2px solid #fff;
    box-shadow: 0 1px 4px rgba(0,122,255,0.3); width: 16px; height: 16px;
}

div[data-testid="stRadio"] label[data-baseweb="radio"] {
    background: rgba(0,0,0,0.03); border-radius: 8px;
    padding: 0.25rem 0.75rem; font-size: 0.8rem;
    transition: background 0.15s;
}
div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) {
    background: var(--accent-dim); color: var(--accent);
}

/* ── Buttons ── */
.stButton button {
    background: var(--accent); color: #fff; border: none;
    border-radius: 100px; font-weight: 600; font-size: 0.85rem;
    padding: 0.55rem 1.75rem;
    box-shadow: 0 2px 8px rgba(0,122,255,0.2);
    transition: all 0.2s ease;
    letter-spacing: -0.01em;
}
.stButton button:hover {
    box-shadow: 0 4px 16px rgba(0,122,255,0.3);
    transform: translateY(-1px); background: #0070e9;
}

/* ── Navigation pills ── */
.nav-strip {
    display: flex; flex-wrap: wrap; gap: 0.35rem;
    padding: 0.5rem 0; margin-bottom: 0.5rem;
}
.nav-pill {
    display: inline-flex; align-items: center;
    padding: 0.35rem 0.85rem; font-size: 0.75rem; font-weight: 520;
    color: var(--text-secondary); background: rgba(255,255,255,0.75);
    backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
    border: 0.5px solid var(--border); border-radius: 100px;
    text-decoration: none; transition: all 0.2s ease;
    letter-spacing: -0.01em;
}
.nav-pill:hover {
    color: var(--accent); border-color: rgba(0,122,255,0.3);
    background: rgba(255,255,255,0.95); box-shadow: var(--shadow-md);
}

/* ── Parameter chips ── */
.param-chips {
    display: flex; flex-wrap: wrap; gap: 0.4rem;
    margin: 0.5rem 0 0 0;
}
.param-chip {
    display: inline-flex; align-items: center;
    padding: 0.35rem 0.8rem; font-size: 0.75rem; font-weight: 520;
    color: var(--text); background: rgba(255,255,255,0.7);
    backdrop-filter: blur(5px); -webkit-backdrop-filter: blur(5px);
    border: 0.5px solid var(--border-strong); border-radius: 100px;
    letter-spacing: -0.01em;
}

/* ── Dividers ── */
hr { border: none; border-top: 0.5px solid var(--border); margin: 1.25rem 0; }

/* ── Captions ── */
.stCaption { color: var(--muted) !important; font-size: 0.75rem !important; font-weight: 450 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.12); border-radius: 100px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0,0,0,0.2); }

/* ── Toolbar ── */
[data-testid="stToolbar"] { opacity: 0.25; transition: opacity 0.2s; }
[data-testid="stToolbar"]:hover { opacity: 0.7; }
[data-testid="stDeployButton"] { opacity: 0.35; transition: opacity 0.2s; }
[data-testid="stDeployButton"]:hover { opacity: 0.9; }

/* ── Info/Notifications ── */
[data-testid="stNotification"] {
    border-radius: var(--radius-sm); font-size: 0.82rem; line-height: 1.5;
    border: 0.5px solid var(--border); background: rgba(255,255,255,0.75);
}

/* ── Spacing refinements ── */
.stAlert { margin: 0.5rem 0; border-radius: var(--radius-sm) !important; }
.row-widget { gap: 0.75rem; }

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
        'stress_testing': '压力测试', 'reinsurance': '再保险', 'product_compare': '产品对比', 'sensitivity': '敏感性分析',
        'sec_products': '精算产品', 'sec_ai': 'AI 模块', 'sec_tools': '风险工具', 'sec_analysis': '分析工具',
        'reinsurance': '再保险',
        'stress_testing': '压力测试',
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
        'stress_testing': 'Stress Test', 'reinsurance': 'Reinsurance', 'product_compare': 'Compare', 'sensitivity': 'Sensitivity',
        'sec_products': 'Products', 'sec_ai': 'AI Modules', 'sec_tools': 'Risk Tools', 'sec_analysis': 'Analysis',
        'reinsurance': 'Reinsurance',
        'stress_testing': 'Stress Test',
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
        'stress_testing': '壓力測試', 'reinsurance': '再保險', 'product_compare': '產品對比', 'sensitivity': '敏感性分析',
        'sec_products': '精算產品', 'sec_ai': 'AI 模組', 'sec_tools': '風險工具', 'sec_analysis': '分析工具',
        'reinsurance': '再保險',
        'stress_testing': '壓力測試',
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
    st.Page('pages/12_Stress_Testing.py', title=L['stress_testing'], url_path='Stress_Testing'),
    st.Page('pages/13_Reinsurance.py', title=L['reinsurance'], url_path='Reinsurance'),
]

pg = st.navigation(pages)
pg.run()
