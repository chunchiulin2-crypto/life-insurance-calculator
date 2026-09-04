# Life Insurance Calculator — Web UI Design

## Summary

为现有的 CLI 寿险计算器添加 Streamlit Web 界面。一个 `app.py`，侧边栏输入参数，主区域展示保费卡片、准备金折线图和数据表。

## Scope

**MVP: 单页 Streamlit 应用**

- 侧边栏：年龄（slider）、保额（number_input）、期限（number_input）、利率（slider）、性别（radio）
- 保费卡片：st.metric 展示趸缴和年缴纯保费
- 准备金图：st.line_chart 折线图
- 准备金明细：st.dataframe 数据表

**不做：**
- 多险种切换（定期/终身/两全）
- PDF 报告导出
- 用户登录/历史记录

## Tech Stack

- Streamlit（新增依赖）
- 复用现有 mortality.py / premium.py / reserve.py
- Python 3.14

## Files

| File | Action |
|------|--------|
| `app.py` | Create — Streamlit entry point |
| `requirements.txt` | Modify — add `streamlit` |

## UI Layout

```
┌──────────────────────────────┐
│      标题 + 生命表说明        │
├────────┬─────────────────────┤
│侧边栏   │  趸缴保费  │ 年缴保费│
│        │  ¥16,309  │ ¥1,117 │
│年龄 ───│                     │
│保额    │  📊 准备金曲线      │
│期限    │  [折线图]           │
│利率    │                     │
│性别 ○  │  📋 准备金明细      │
│        │  [数据表]          │
│[计算]  │                     │
└────────┴─────────────────────┘
```

## Startup

```bash
pip install streamlit
streamlit run app.py
```

## Testing

Since Streamlit apps are interactive, testing focuses on:
- Import test: `from app import run_calculation` — verify calculation function produces correct results
- Smoke test: `streamlit run app.py` — page loads without errors
