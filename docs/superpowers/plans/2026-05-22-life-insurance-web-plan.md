# Life Insurance Web UI — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Streamlit web UI to the existing CLI life insurance calculator, reusing all existing calculation modules.

**Architecture:** One `app.py` that imports `mortality`, `premium`, `reserve` modules. Streamlit sidebar for parameter input, main area for premium cards + reserve chart + data table.

**Tech Stack:** Streamlit, Python 3.14, existing mortality/premium/reserve modules

---

### Task 1: Update requirements.txt

**Files:**
- Modify: `/Users/linjiaye/Desktop/life-insurance/requirements.txt`

- [ ] **Step 1: Add streamlit to requirements.txt**

Read the current requirements.txt and append `streamlit`:

```bash
echo 'streamlit>=1.28.0' >> /Users/linjiaye/Desktop/life-insurance/requirements.txt
```

- [ ] **Step 2: Install streamlit**

```bash
pip install streamlit
```

- [ ] **Step 3: Commit**

```bash
cd /Users/linjiaye/Desktop/life-insurance && git add requirements.txt && git commit -m "chore: add streamlit dependency"
```

---

### Task 2: Create app.py — Streamlit Web UI

**Files:**
- Create: `/Users/linjiaye/Desktop/life-insurance/app.py`

- [ ] **Step 1: Create app.py**

```bash
cat > /Users/linjiaye/Desktop/life-insurance/app.py << 'PYEOF'
"""定期寿险保费计算器 · Web UI"""

import streamlit as st
import pandas as pd
import os
from mortality import load_table, build_life_table
from premium import single_premium, annual_premium
from reserve import reserve_table

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'clt_2010_2013.csv')

st.set_page_config(
    page_title='寿险保费计算器',
    page_icon='🛡️',
    layout='wide',
)

# ---- Header ----
st.title('定期寿险保费计算器')
st.caption('CLT 2010-2013 生命表（非养老类）· 趸缴/年缴纯保费 · 责任准备金')

# ---- Sidebar: Parameters ----
st.sidebar.header('投保参数')

age = st.sidebar.slider('投保年龄', min_value=0, max_value=80, value=30, step=1)
sum_insured = st.sidebar.number_input('保险金额（元）', min_value=10000, value=1000000, step=10000, format='%d')
term = st.sidebar.slider('保险期限（年）', min_value=1, max_value=50, value=20, step=1)
rate = st.sidebar.slider('预定利率', min_value=0.0, max_value=10.0, value=3.5, step=0.5) / 100
gender = st.sidebar.radio('性别', ['男', '女'], horizontal=True)
gender_code = 'M' if gender == '男' else 'F'

# Validate
if age + term > 105:
    st.sidebar.error(f'年龄 + 期限 ({age}+{term}={age+term}) 超过极限年龄 105')
    st.stop()

# ---- Calculate ----
@st.cache_data
def get_life_table(gender_code):
    df = load_table(DATA_PATH)
    return build_life_table(df, gender_code)

lt = get_life_table(gender_code)
sp = single_premium(lt, age, sum_insured, term, rate)
ap = annual_premium(lt, age, sum_insured, term, rate)
reserves = reserve_table(lt, age, sum_insured, term, rate)

# ---- Main Area ----
# Premium cards
col1, col2 = st.columns(2)
with col1:
    st.metric('趸缴纯保费', f'¥{sp:,.0f}', help='一次性缴清的纯保费')
with col2:
    st.metric('年缴纯保费', f'¥{ap:,.0f}', help='每年初缴纳的均衡纯保费')

st.divider()

# Reserve chart
st.subheader('责任准备金曲线')
df_reserve = pd.DataFrame(reserves, columns=['Year', 'Reserve']).set_index('Year')
st.line_chart(df_reserve, height=300)

# Reserve table
st.subheader('各年末准备金明细')
df_display = pd.DataFrame(reserves, columns=['保单年度', '准备金（元）'])
df_display['准备金（元）'] = df_display['准备金（元）'].apply(lambda x: f'¥{x:,.2f}')
st.dataframe(df_display, use_container_width=True, hide_index=True, height=400)

# ---- Footer ----
st.divider()
st.caption(f'被保险人：{age} 岁 {gender} · 保额 ¥{sum_insured:,} · 期限 {term} 年 · 利率 {rate:.1%} · 生命表 CLT 2010-2013')
PYEOF
```

- [ ] **Step 2: Verify app.py imports correctly**

```bash
cd /Users/linjiaye/Desktop/life-insurance && python3 -c "import app; print('Import OK')"
```
Expected: `Import OK` (Streamlit may show a warning about no running server — ignore)

- [ ] **Step 3: Verify existing tests still pass**

```bash
cd /Users/linjiaye/Desktop/life-insurance && python3 -m pytest -v 2>&1 | tail -3
```
Expected: `27 passed`

- [ ] **Step 4: Commit**

```bash
cd /Users/linjiaye/Desktop/life-insurance && git add app.py && git commit -m "feat: add Streamlit web UI for premium calculator"
```

---

### Task 3: End-to-End Verification

**不提交，仅验证**

- [ ] **Step 1: Launch Streamlit**

```bash
cd /Users/linjiaye/Desktop/life-insurance && streamlit run app.py --server.headless true &
sleep 3
echo "Streamlit should be running at http://localhost:8501"
```

- [ ] **Step 2: Verify page loads**

```bash
curl -s http://localhost:8501 | head -20
```
Expected: HTML content with "定期寿险保费计算器"

- [ ] **Step 3: Open in browser**

```bash
open http://localhost:8501
```

Verify visually:
- Sidebar shows all 5 parameter controls
- Premium cards display ¥ amounts
- Reserve line chart renders
- Reserve data table shows all years

- [ ] **Step 4: Change parameters and verify recalculation**

Change age slider to 45 — premiums should increase immediately.

- [ ] **Step 5: Stop Streamlit**

```bash
pkill -f "streamlit run app.py"
```
