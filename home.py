"""LifePlan Advisor workspace."""

import os

import pandas as pd
import streamlit as st

from advisor_planner import (
    Assumptions,
    ClientCase,
    branded_report_pdf_bytes,
    bilingual_report_html,
    calculate_needs,
    compare_plans,
    money,
    plan_dataframe,
    recommendation_text,
    sample_case_description,
    sample_case_labels,
    sample_client_case,
)
from ui_components import render_metric_row, section_panel


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


T = {
    "zh": {
        "title": "LifePlan Advisor",
        "subtitle": "香港与海外华人保险顾问的寿险保障规划工作台",
        "case": "客户案例",
        "needs": "保障缺口",
        "compare": "方案对比",
        "report": "报告输出",
        "client_inputs": "客户与家庭责任",
        "sample_case": "样例案例",
        "advisor_inputs": "顾问假设",
        "profile": "客户资料",
        "planning": "保障规划",
        "annual_income": "年收入",
        "replacement_years": "收入替代年数",
        "debts": "房贷/负债",
        "education": "教育金需求",
        "final_expenses": "最终费用",
        "existing": "已有寿险保障",
        "horizon": "保障年期",
        "currency": "币种",
        "gender": "性别",
        "age": "年龄",
        "male": "男",
        "female": "女",
        "advisor_name": "顾问姓名",
        "advisor_company": "公司/团队",
        "advisor_phone": "联系电话",
        "advisor_email": "联系邮箱",
        "rate": "定价利率",
        "risk": "风险因子",
        "frequency": "缴费频率",
        "monthly": "月缴",
        "annual": "年缴",
        "quarterly": "季缴",
        "semi": "半年缴",
        "alpha": "初始费用",
        "beta": "保费比例费用",
        "gamma": "保额维持费用",
        "gross_need": "总保障需求",
        "coverage_gap": "保障缺口",
        "standard_band": "标准建议保额",
        "per_payment": "每期保费",
        "band_title": "推荐保额区间",
        "need_components": "需求构成",
        "plan_table": "保障型方案对比",
        "report_preview": "客户报告预览",
        "download": "下载双语报告 HTML",
        "download_pdf": "下载品牌化 PDF 报告",
        "disclaimer": "仅供初步规划与客户沟通参考，不替代保险公司正式建议书或持牌意见。",
        "expert_tools": "专家工具",
        "term": "定期寿险",
        "whole": "终身寿险",
        "compare_tool": "产品对比",
        "stress": "压力测试",
        "sensitivity": "敏感性分析",
        "reinsurance": "再保险",
    },
    "en": {
        "title": "LifePlan Advisor",
        "subtitle": "Bilingual protection planning workspace for Chinese-speaking advisors",
        "case": "Client Case",
        "needs": "Coverage Gap",
        "compare": "Plan Compare",
        "report": "Report",
        "client_inputs": "Client and Family Responsibilities",
        "sample_case": "Sample Case",
        "advisor_inputs": "Advisor Assumptions",
        "profile": "Client Profile",
        "planning": "Protection Planning",
        "annual_income": "Annual Income",
        "replacement_years": "Income Replacement Years",
        "debts": "Mortgage / Debt",
        "education": "Education Need",
        "final_expenses": "Final Expenses",
        "existing": "Existing Life Coverage",
        "horizon": "Coverage Term",
        "currency": "Currency",
        "gender": "Gender",
        "age": "Age",
        "male": "Male",
        "female": "Female",
        "advisor_name": "Advisor Name",
        "advisor_company": "Firm / Team",
        "advisor_phone": "Phone",
        "advisor_email": "Email",
        "rate": "Pricing Rate",
        "risk": "Risk Factor",
        "frequency": "Payment Frequency",
        "monthly": "Monthly",
        "annual": "Annual",
        "quarterly": "Quarterly",
        "semi": "Semiannual",
        "alpha": "Initial Expense",
        "beta": "Premium Expense",
        "gamma": "Maintenance Expense",
        "gross_need": "Gross Need",
        "coverage_gap": "Coverage Gap",
        "standard_band": "Standard Coverage",
        "per_payment": "Per Payment",
        "band_title": "Recommended Coverage Bands",
        "need_components": "Need Components",
        "plan_table": "Protection Plan Comparison",
        "report_preview": "Client Report Preview",
        "download": "Download Bilingual HTML Report",
        "download_pdf": "Download Branded PDF Report",
        "disclaimer": "For preliminary planning and client discussion only. Not an official insurer illustration or licensed advice.",
        "expert_tools": "Expert Tools",
        "term": "Term Life",
        "whole": "Whole Life",
        "compare_tool": "Product Compare",
        "stress": "Stress Testing",
        "sensitivity": "Sensitivity",
        "reinsurance": "Reinsurance",
    },
    "zh-Hant": {
        "title": "LifePlan Advisor",
        "subtitle": "香港與海外華人保險顧問的壽險保障規劃工作台",
        "case": "客戶案例",
        "needs": "保障缺口",
        "compare": "方案對比",
        "report": "報告輸出",
        "client_inputs": "客戶與家庭責任",
        "sample_case": "樣例案例",
        "advisor_inputs": "顧問假設",
        "profile": "客戶資料",
        "planning": "保障規劃",
        "annual_income": "年收入",
        "replacement_years": "收入替代年數",
        "debts": "房貸/負債",
        "education": "教育金需求",
        "final_expenses": "最終費用",
        "existing": "已有壽險保障",
        "horizon": "保障年期",
        "currency": "幣種",
        "gender": "性別",
        "age": "年齡",
        "male": "男",
        "female": "女",
        "advisor_name": "顧問姓名",
        "advisor_company": "公司/團隊",
        "advisor_phone": "聯絡電話",
        "advisor_email": "聯絡電郵",
        "rate": "定價利率",
        "risk": "風險因子",
        "frequency": "繳費頻率",
        "monthly": "月繳",
        "annual": "年繳",
        "quarterly": "季繳",
        "semi": "半年繳",
        "alpha": "初始費用",
        "beta": "保費比例費用",
        "gamma": "保額維持費用",
        "gross_need": "總保障需求",
        "coverage_gap": "保障缺口",
        "standard_band": "標準建議保額",
        "per_payment": "每期保費",
        "band_title": "建議保額區間",
        "need_components": "需求構成",
        "plan_table": "保障型方案對比",
        "report_preview": "客戶報告預覽",
        "download": "下載雙語報告 HTML",
        "download_pdf": "下載品牌化 PDF 報告",
        "disclaimer": "僅供初步規劃與客戶溝通參考，不替代保險公司正式建議書或持牌意見。",
        "expert_tools": "專家工具",
        "term": "定期壽險",
        "whole": "終身壽險",
        "compare_tool": "產品對比",
        "stress": "壓力測試",
        "sensitivity": "敏感性分析",
        "reinsurance": "再保險",
    },
}


def t(key):
    return T[st.session_state.get("lang", "zh-Hant")][key]


def workflow_strip():
    steps = [t("case"), t("needs"), t("compare"), t("report")]
    st.markdown(
        '<div class="advisor-steps">'
        + "".join(f'<span class="advisor-step">{step}</span>' for step in steps)
        + "</div>",
        unsafe_allow_html=True,
    )


def render_expert_tools():
    links = [
        (t("term"), "Term_Life"),
        (t("whole"), "Whole_Life"),
        (t("compare_tool"), "Product_Compare"),
        (t("stress"), "Stress_Testing"),
        (t("sensitivity"), "Sensitivity"),
        (t("reinsurance"), "Reinsurance"),
    ]
    st.markdown(
        '<div class="nav-strip">'
        + "".join(
            f'<a href="/{url}" target="_self" class="nav-pill">{label}</a>'
            for label, url in links
        )
        + "</div>",
        unsafe_allow_html=True,
    )


lang = st.session_state.get("lang", "zh-Hant")
st.title(t("title"))
st.caption(t("subtitle"))
workflow_strip()

left, center, right = st.columns([1.05, 1.45, 0.95], gap="large")

with left:
    with section_panel(t("client_inputs")):
        labels = sample_case_labels(lang)
        selected_sample = st.selectbox(
            t("sample_case"),
            list(labels.keys()),
            format_func=lambda slug: labels[slug],
            key="case_sample_slug",
        )
        sample_case = sample_client_case(selected_sample)
        st.caption(sample_case_description(selected_sample, lang))

        st.markdown(f"**{t('profile')}**")
        profile_cols = st.columns(2)
        with profile_cols[0]:
            age = st.number_input(
                t("age"),
                min_value=18,
                max_value=80,
                value=sample_case.age,
                step=1,
                key=f"{selected_sample}_age",
            )
        with profile_cols[1]:
            gender_code = st.selectbox(
                t("gender"),
                ["M", "F"],
                format_func=lambda code: t("male") if code == "M" else t("female"),
                index=0 if sample_case.gender == "M" else 1,
                key=f"{selected_sample}_gender",
            )
        currency_options = ["HKD", "USD", "CNY"]
        currency = st.selectbox(
            t("currency"),
            currency_options,
            index=currency_options.index(sample_case.currency),
            key=f"{selected_sample}_currency",
        )

        st.markdown(f"**{t('planning')}**")
        annual_income = st.number_input(
            t("annual_income"),
            min_value=0,
            value=int(sample_case.annual_income),
            step=50000,
            key=f"{selected_sample}_annual_income",
        )
        replacement_years = st.slider(
            t("replacement_years"),
            3,
            25,
            sample_case.replacement_years,
            key=f"{selected_sample}_replacement_years",
        )
        debts = st.number_input(
            t("debts"),
            min_value=0,
            value=int(sample_case.debts),
            step=100000,
            key=f"{selected_sample}_debts",
        )
        education_needs = st.number_input(
            t("education"),
            min_value=0,
            value=int(sample_case.education_needs),
            step=50000,
            key=f"{selected_sample}_education_needs",
        )
        final_expenses = st.number_input(
            t("final_expenses"),
            min_value=0,
            value=int(sample_case.final_expenses),
            step=10000,
            key=f"{selected_sample}_final_expenses",
        )
        existing_coverage = st.number_input(
            t("existing"),
            min_value=0,
            value=int(sample_case.existing_coverage),
            step=50000,
            key=f"{selected_sample}_existing_coverage",
        )
        planning_horizon = st.slider(
            t("horizon"),
            5,
            35,
            sample_case.planning_horizon,
            key=f"{selected_sample}_planning_horizon",
        )

    with section_panel(t("advisor_inputs")):
        advisor_name = st.text_input(t("advisor_name"), "Advisor")
        advisor_company = st.text_input(t("advisor_company"), "LifePlan Advisory")
        advisor_phone = st.text_input(t("advisor_phone"), "+852 0000 0000")
        advisor_email = st.text_input(t("advisor_email"), "advisor@example.com")
        frequency_label = st.selectbox(
            t("frequency"),
            [t("monthly"), t("quarterly"), t("semi"), t("annual")],
        )
        frequency_map = {
            t("monthly"): 12,
            t("quarterly"): 4,
            t("semi"): 2,
            t("annual"): 1,
        }
        frequency = frequency_map[frequency_label]
        rate = st.slider(t("rate"), 0.01, 0.08, 0.035, 0.005)
        risk_factor = st.slider(t("risk"), 0.70, 2.00, 1.00, 0.05)
        alpha = st.slider(t("alpha"), 0.00, 0.12, 0.05, 0.005)
        beta = st.slider(t("beta"), 0.00, 0.12, 0.02, 0.005)
        gamma = st.slider(t("gamma"), 0.000, 0.010, 0.001, 0.001)

case = ClientCase(
    age=int(age),
    gender=gender_code,
    currency=currency,
    annual_income=float(annual_income),
    replacement_years=int(replacement_years),
    debts=float(debts),
    education_needs=float(education_needs),
    final_expenses=float(final_expenses),
    existing_coverage=float(existing_coverage),
    planning_horizon=int(planning_horizon),
)
assumptions = Assumptions(
    rate=float(rate),
    alpha=float(alpha),
    beta=float(beta),
    gamma=float(gamma),
    frequency=int(frequency),
    risk_factor=float(risk_factor),
    table_path=st.session_state.get(
        "table_path", os.path.join(DATA_DIR, "clt_2010_2013.csv")
    ),
    table_col=st.session_state.get("table_col", "clt"),
)

needs = calculate_needs(case)
standard_coverage = max(needs["bands"]["Standard"], 1.0)
plan_rows = compare_plans(case, assumptions, standard_coverage)
report_html = bilingual_report_html(
    case,
    needs,
    plan_rows,
    assumptions,
    advisor_name,
    advisor_company,
    advisor_phone,
    advisor_email,
)
report_pdf = branded_report_pdf_bytes(
    case,
    needs,
    plan_rows,
    assumptions,
    advisor_name,
    advisor_company,
    advisor_phone,
    advisor_email,
)

with center:
    render_metric_row([
        {"label": t("gross_need"), "value": money(needs["gross_need"], currency)},
        {"label": t("coverage_gap"), "value": money(needs["gap"], currency)},
        {"label": t("standard_band"), "value": money(standard_coverage, currency)},
    ], columns=3)

    st.markdown("")
    chart_data = pd.DataFrame([
        {"Component": t("annual_income"), "Amount": needs["income_replacement"]},
        {"Component": t("debts"), "Amount": needs["debts"]},
        {"Component": t("education"), "Amount": needs["education_needs"]},
        {"Component": t("final_expenses"), "Amount": needs["final_expenses"]},
        {"Component": t("existing"), "Amount": -needs["existing_coverage"]},
    ])

    with section_panel(t("need_components")):
        st.bar_chart(chart_data, x="Component", y="Amount", width="stretch")

    band_df = pd.DataFrame([
        {"Band": name, "Coverage": money(value, currency)}
        for name, value in needs["bands"].items()
    ])
    with section_panel(t("band_title")):
        st.dataframe(band_df, width="stretch", hide_index=True)
        st.caption(recommendation_text(needs["gap"], currency))

    with section_panel(t("plan_table")):
        st.dataframe(plan_dataframe(plan_rows, currency), width="stretch", hide_index=True)

with right:
    with section_panel(t("report_preview")):
        st.metric(t("coverage_gap"), money(needs["gap"], currency))
        st.metric(t("per_payment"), money(plan_rows[0]["Per Payment"], currency))
        st.markdown(
            f"""
            <div class="report-preview">
                <p><strong>{advisor_company}</strong></p>
                <p>{t('title')}</p>
                <hr>
                <p>{recommendation_text(needs['gap'], currency)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.download_button(
            t("download"),
            data=report_html,
            file_name="life-protection-planning-report.html",
            mime="text/html",
            width="stretch",
        )
        st.download_button(
            t("download_pdf"),
            data=report_pdf,
            file_name="life-protection-planning-report.pdf",
            mime="application/pdf",
            width="stretch",
        )
        st.caption(t("disclaimer"))

    with section_panel(t("expert_tools")):
        render_expert_tools()
