"""Advisor-facing protection planning calculations and reports."""

from io import BytesIO
from dataclasses import dataclass
from html import escape
from typing import Iterable

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from mortality import build_life_table, load_table, table_max_age
from premium import (
    annual_premium,
    gross_annual_premium,
    periodic_premium,
    whole_life_annual_premium,
)
from validation import validate_issue_age, validate_term


CURRENCY_SYMBOLS = {
    "HKD": "HK$",
    "USD": "US$",
    "CNY": "¥",
}


PDF_FONT = "STSong-Light"


SAMPLE_CASES = {
    "hk_young_family": {
        "title": {
            "zh": "香港年轻家庭",
            "en": "Hong Kong Young Family",
            "zh-Hant": "香港年輕家庭",
        },
        "description": {
            "zh": "双职父母、有房贷和子女教育责任，适合演示最常见的保障缺口。",
            "en": "Dual-income parents with mortgage and education responsibilities.",
            "zh-Hant": "雙職父母、有房貸和子女教育責任，適合演示最常見的保障缺口。",
        },
        "case": {
            "age": 38,
            "gender": "M",
            "currency": "HKD",
            "annual_income": 600000,
            "replacement_years": 10,
            "debts": 2500000,
            "education_needs": 800000,
            "final_expenses": 150000,
            "existing_coverage": 500000,
            "planning_horizon": 20,
        },
    },
    "overseas_professional": {
        "title": {
            "zh": "海外华人专业人士",
            "en": "Overseas Chinese Professional",
            "zh-Hant": "海外華人專業人士",
        },
        "description": {
            "zh": "美元收入、跨境家庭责任较轻，适合展示双语和多币种沟通。",
            "en": "USD income with lighter family liabilities and cross-border context.",
            "zh-Hant": "美元收入、跨境家庭責任較輕，適合展示雙語和多幣種溝通。",
        },
        "case": {
            "age": 32,
            "gender": "F",
            "currency": "USD",
            "annual_income": 120000,
            "replacement_years": 8,
            "debts": 250000,
            "education_needs": 0,
            "final_expenses": 30000,
            "existing_coverage": 150000,
            "planning_horizon": 25,
        },
    },
    "business_owner": {
        "title": {
            "zh": "高收入企业主家庭",
            "en": "Business Owner Family",
            "zh-Hant": "高收入企業主家庭",
        },
        "description": {
            "zh": "收入高、负债和家庭责任大，适合展示高保额方案和终身寿险对比。",
            "en": "Higher income, larger liabilities, and stronger need for plan comparison.",
            "zh-Hant": "收入高、負債和家庭責任大，適合展示高保額方案和終身壽險對比。",
        },
        "case": {
            "age": 45,
            "gender": "M",
            "currency": "HKD",
            "annual_income": 1800000,
            "replacement_years": 12,
            "debts": 6000000,
            "education_needs": 1800000,
            "final_expenses": 300000,
            "existing_coverage": 2000000,
            "planning_horizon": 20,
        },
    },
}


@dataclass(frozen=True)
class ClientCase:
    age: int
    gender: str
    currency: str
    annual_income: float
    replacement_years: int
    debts: float
    education_needs: float
    final_expenses: float
    existing_coverage: float
    planning_horizon: int


@dataclass(frozen=True)
class Assumptions:
    rate: float
    alpha: float
    beta: float
    gamma: float
    frequency: int
    risk_factor: float
    table_path: str
    table_col: str


def sample_case_labels(lang="zh-Hant"):
    """Return localized sample case labels keyed by sample slug."""
    labels = {}
    for slug, sample in SAMPLE_CASES.items():
        titles = sample["title"]
        labels[slug] = titles.get(lang, titles["en"])
    return labels


def sample_case_description(slug, lang="zh-Hant"):
    """Return a localized sample case description."""
    sample = SAMPLE_CASES[slug]
    descriptions = sample["description"]
    return descriptions.get(lang, descriptions["en"])


def sample_client_case(slug):
    """Build a ClientCase from a named sample scenario."""
    return ClientCase(**SAMPLE_CASES[slug]["case"])


def money(value, currency="HKD", decimals=0):
    """Format a monetary value with the selected currency symbol."""
    symbol = CURRENCY_SYMBOLS.get(currency, currency)
    return f"{symbol}{value:,.{decimals}f}"


def gender_or_table_column(table_col, gender):
    """Return the mortality column selector expected by build_life_table."""
    if str(table_col).startswith("am92"):
        return table_col
    return gender


def calculate_needs(case: ClientCase):
    """Calculate coverage need components and recommendation bands."""
    income_replacement = case.annual_income * case.replacement_years
    gross_need = (
        income_replacement
        + case.debts
        + case.education_needs
        + case.final_expenses
    )
    gap = max(0.0, gross_need - case.existing_coverage)

    return {
        "income_replacement": income_replacement,
        "debts": case.debts,
        "education_needs": case.education_needs,
        "final_expenses": case.final_expenses,
        "existing_coverage": case.existing_coverage,
        "gross_need": gross_need,
        "gap": gap,
        "bands": {
            "Basic": round(gap * 0.75, 2),
            "Standard": round(gap, 2),
            "Comprehensive": round(gap * 1.25, 2),
        },
    }


def build_case_life_table(case: ClientCase, assumptions: Assumptions):
    """Build the life table for the active case and selected assumptions."""
    df = load_table(assumptions.table_path)
    selector = gender_or_table_column(assumptions.table_col, case.gender)
    return build_life_table(df, selector, assumptions.risk_factor)


def compare_plans(case: ClientCase, assumptions: Assumptions, sum_assured):
    """Return term and whole-life comparison rows for the advisor workspace."""
    max_age = table_max_age(assumptions.table_col)
    validate_issue_age(case.age, max_age)
    term = max(1, min(case.planning_horizon, max_age - case.age))
    validate_term(case.age, term, max_age)

    life_table = build_case_life_table(case, assumptions)

    term_net = annual_premium(
        life_table,
        case.age,
        sum_assured,
        term,
        assumptions.rate,
    )
    term_gross = gross_annual_premium(
        life_table,
        case.age,
        sum_assured,
        term,
        assumptions.rate,
        assumptions.alpha,
        assumptions.beta,
        assumptions.gamma,
    )
    whole_net = whole_life_annual_premium(
        life_table,
        case.age,
        sum_assured,
        assumptions.rate,
    )
    whole_term = max_age - case.age
    whole_gross = gross_annual_premium(
        life_table,
        case.age,
        sum_assured,
        whole_term,
        assumptions.rate,
        assumptions.alpha,
        assumptions.beta,
        assumptions.gamma,
    )

    rows = [
        {
            "Plan": "Term Life",
            "Coverage": sum_assured,
            "Term": term,
            "Net Annual": term_net,
            "Gross Annual": term_gross,
            "Per Payment": periodic_premium(term_gross, assumptions.frequency),
            "Tradeoff": "Lower cost for fixed-period protection.",
        },
        {
            "Plan": "Whole Life",
            "Coverage": sum_assured,
            "Term": whole_term,
            "Net Annual": whole_net,
            "Gross Annual": whole_gross,
            "Per Payment": periodic_premium(whole_gross, assumptions.frequency),
            "Tradeoff": "Lifetime protection with higher long-term cost.",
        },
    ]
    return rows


def plan_dataframe(rows: Iterable[dict], currency="HKD"):
    """Return a display-ready comparison table."""
    display_rows = []
    for row in rows:
        display_rows.append({
            "Plan": row["Plan"],
            "Coverage": money(row["Coverage"], currency),
            "Term": f"{row['Term']} years",
            "Net Annual": money(row["Net Annual"], currency),
            "Gross Annual": money(row["Gross Annual"], currency),
            "Per Payment": money(row["Per Payment"], currency),
            "Tradeoff": row["Tradeoff"],
        })
    return pd.DataFrame(display_rows)


def recommendation_text(gap, currency="HKD"):
    """Return a concise customer-facing recommendation sentence."""
    if gap <= 0:
        return (
            "Existing coverage appears to meet the selected protection needs. "
            "The advisor may still review term length, liquidity, and beneficiary structure."
        )
    return (
        f"The selected needs indicate an estimated protection gap of "
        f"{money(gap, currency)}. A standard recommendation can start from this "
        "level, with basic and comprehensive bands used for budget discussion."
    )


def bilingual_report_html(case: ClientCase, needs: dict, plan_rows: list[dict],
                         assumptions: Assumptions, advisor_name: str,
                         advisor_company: str, advisor_phone: str = "",
                         advisor_email: str = ""):
    """Generate a polished bilingual HTML report for client sharing."""
    advisor = escape(advisor_name or "Advisor")
    company = escape(advisor_company or "LifePlan Advisory")
    contact = " · ".join(
        escape(item) for item in [advisor_phone, advisor_email] if item
    )
    currency = case.currency

    bands = needs["bands"]
    band_rows = "".join(
        f"<tr><td>{escape(name)}</td><td>{money(value, currency)}</td></tr>"
        for name, value in bands.items()
    )
    plan_html = "".join(
        "<tr>"
        f"<td>{escape(row['Plan'])}</td>"
        f"<td>{money(row['Coverage'], currency)}</td>"
        f"<td>{row['Term']} years</td>"
        f"<td>{money(row['Gross Annual'], currency)}</td>"
        f"<td>{money(row['Per Payment'], currency)}</td>"
        f"<td>{escape(row['Tradeoff'])}</td>"
        "</tr>"
        for row in plan_rows
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Life Protection Planning Report</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", "PingFang SC", sans-serif; max-width: 860px; margin: 40px auto; color: #1d1d1f; line-height: 1.55; }}
.meta {{ color: #6e6e73; font-size: 13px; }}
.hero {{ border-bottom: 1px solid #e5e5ea; padding-bottom: 18px; margin-bottom: 24px; }}
h1 {{ font-size: 28px; margin: 0 0 8px 0; }}
h2 {{ font-size: 18px; margin-top: 30px; }}
table {{ width: 100%; border-collapse: collapse; margin: 12px 0 18px 0; }}
th, td {{ border-bottom: 1px solid #e5e5ea; padding: 9px 10px; text-align: left; font-size: 13px; vertical-align: top; }}
th {{ background: #f5f5f7; color: #6e6e73; font-size: 11px; text-transform: uppercase; letter-spacing: .04em; }}
.kpis {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin: 18px 0; }}
.kpi {{ border: 1px solid #e5e5ea; border-radius: 8px; padding: 14px; background: #fbfbfd; }}
.label {{ color: #6e6e73; font-size: 11px; text-transform: uppercase; letter-spacing: .04em; }}
.value {{ font-size: 20px; font-weight: 700; margin-top: 6px; }}
.disclaimer {{ color: #6e6e73; font-size: 12px; border-top: 1px solid #e5e5ea; padding-top: 16px; margin-top: 28px; }}
</style>
</head>
<body>
<section class="hero">
  <p class="meta">{company} · Prepared by {advisor}</p>
  <h1>Life Protection Planning Report<br>寿险保障规划报告</h1>
  <p class="meta">{contact}</p>
  <p class="meta">For preliminary client discussion only · 仅供初步客户沟通参考</p>
</section>

<section>
  <h2>Client Profile / 客户概况</h2>
  <table>
    <tr><td>Age / 年龄</td><td>{case.age}</td></tr>
    <tr><td>Currency / 币种</td><td>{escape(currency)}</td></tr>
    <tr><td>Planning Horizon / 规划年期</td><td>{case.planning_horizon} years</td></tr>
    <tr><td>Existing Coverage / 已有保障</td><td>{money(case.existing_coverage, currency)}</td></tr>
  </table>
</section>

<section>
  <h2>Protection Need / 保障需求</h2>
  <div class="kpis">
    <div class="kpi"><div class="label">Gross Need</div><div class="value">{money(needs['gross_need'], currency)}</div></div>
    <div class="kpi"><div class="label">Existing Coverage</div><div class="value">{money(needs['existing_coverage'], currency)}</div></div>
    <div class="kpi"><div class="label">Coverage Gap</div><div class="value">{money(needs['gap'], currency)}</div></div>
  </div>
  <p>{escape(recommendation_text(needs['gap'], currency))}</p>
  <table><thead><tr><th>Band</th><th>Recommended Coverage</th></tr></thead><tbody>{band_rows}</tbody></table>
</section>

<section>
  <h2>Plan Comparison / 方案对比</h2>
  <table>
    <thead><tr><th>Plan</th><th>Coverage</th><th>Term</th><th>Annual</th><th>Per Payment</th><th>Tradeoff</th></tr></thead>
    <tbody>{plan_html}</tbody>
  </table>
</section>

<section>
  <h2>Selected Assumptions / 主要假设</h2>
  <table>
    <tr><td>Interest Rate / 利率</td><td>{assumptions.rate:.2%}</td></tr>
    <tr><td>Risk Factor / 风险因子</td><td>{assumptions.risk_factor:.2f}x</td></tr>
    <tr><td>Expense Load / 费用假设</td><td>alpha {assumptions.alpha:.2%}, beta {assumptions.beta:.2%}, gamma {assumptions.gamma:.2%}</td></tr>
  </table>
</section>

<p class="disclaimer">
This report is an educational planning aid based on selected assumptions. It is not an insurer quotation, policy illustration, legal advice, tax advice, or regulated financial advice. Final recommendations should be checked against official insurer materials and local licensing requirements.
<br><br>
本报告仅为基于所选假设的教育性规划辅助，不构成保险公司正式报价、产品建议书、法律意见、税务意见或受监管财务建议。最终方案应以保险公司正式资料及当地持牌要求为准。
</p>
</body>
</html>"""


def _register_pdf_fonts():
    """Register built-in CID fonts that can render Chinese text."""
    try:
        pdfmetrics.getFont(PDF_FONT)
    except KeyError:
        pdfmetrics.registerFont(UnicodeCIDFont(PDF_FONT))


def _pdf_styles():
    _register_pdf_fonts()
    styles = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "AdvisorTitle",
            parent=styles["Title"],
            fontName=PDF_FONT,
            fontSize=21,
            leading=28,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#1d1d1f"),
            spaceAfter=10,
        ),
        "subtitle": ParagraphStyle(
            "AdvisorSubtitle",
            parent=styles["Normal"],
            fontName=PDF_FONT,
            fontSize=9,
            leading=13,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#6e6e73"),
        ),
        "heading": ParagraphStyle(
            "AdvisorHeading",
            parent=styles["Heading2"],
            fontName=PDF_FONT,
            fontSize=13,
            leading=18,
            textColor=colors.HexColor("#1d1d1f"),
            spaceBefore=12,
            spaceAfter=8,
        ),
        "body": ParagraphStyle(
            "AdvisorBody",
            parent=styles["Normal"],
            fontName=PDF_FONT,
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#2c2c2e"),
        ),
        "small": ParagraphStyle(
            "AdvisorSmall",
            parent=styles["Normal"],
            fontName=PDF_FONT,
            fontSize=7.5,
            leading=10,
            textColor=colors.HexColor("#6e6e73"),
        ),
        "label": ParagraphStyle(
            "AdvisorLabel",
            parent=styles["Normal"],
            fontName=PDF_FONT,
            fontSize=7.5,
            leading=10,
            textColor=colors.HexColor("#6e6e73"),
            alignment=TA_LEFT,
        ),
    }


def _p(text, style):
    return Paragraph(escape(str(text)), style)


def _table(rows, col_widths=None, header=True):
    style = TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), PDF_FONT),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("LEADING", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d1d1d6")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#c7c7cc")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ])
    if header:
        style.add("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f5f5f7"))
        style.add("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1d1d1f"))
        style.add("FONTNAME", (0, 0), (-1, 0), PDF_FONT)
    table = Table(rows, colWidths=col_widths, repeatRows=1 if header else 0)
    table.setStyle(style)
    return table


def branded_report_pdf_bytes(case: ClientCase, needs: dict, plan_rows: list[dict],
                             assumptions: Assumptions, advisor_name: str,
                             advisor_company: str, advisor_phone: str = "",
                             advisor_email: str = ""):
    """Generate an A4 bilingual PDF report as bytes."""
    styles = _pdf_styles()
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="Life Protection Planning Report",
    )
    currency = case.currency
    advisor = advisor_name or "Advisor"
    company = advisor_company or "LifePlan Advisory"
    contact_items = [item for item in [advisor_phone, advisor_email] if item]
    contact = " | ".join(contact_items) if contact_items else "Prepared for client discussion"

    story = [
        _p("Life Protection Planning Report", styles["title"]),
        _p("寿险保障规划报告", styles["title"]),
        _p(f"{company} | Prepared by {advisor}", styles["subtitle"]),
        _p(contact, styles["subtitle"]),
        Spacer(1, 8 * mm),
        _p("Executive Summary / 摘要", styles["heading"]),
        _table(
            [
                ["Gross Need / 总需求", "Existing Coverage / 已有保障", "Coverage Gap / 保障缺口"],
                [
                    money(needs["gross_need"], currency),
                    money(needs["existing_coverage"], currency),
                    money(needs["gap"], currency),
                ],
            ],
            col_widths=[55 * mm, 55 * mm, 55 * mm],
        ),
        Spacer(1, 4 * mm),
        _p(recommendation_text(needs["gap"], currency), styles["body"]),
        _p(
            "以上结果用于帮助顾问与客户讨论保障缺口、保额区间和不同寿险结构的取舍。",
            styles["body"],
        ),
        _p("Client Profile / 客户概况", styles["heading"]),
        _table(
            [
                ["Item", "Value"],
                ["Age / 年龄", case.age],
                ["Currency / 币种", currency],
                ["Planning Horizon / 规划年期", f"{case.planning_horizon} years"],
                ["Annual Income / 年收入", money(case.annual_income, currency)],
                ["Existing Coverage / 已有保障", money(case.existing_coverage, currency)],
            ],
            col_widths=[70 * mm, 95 * mm],
        ),
        _p("Coverage Need Components / 保障需求构成", styles["heading"]),
        _table(
            [
                ["Component", "Amount"],
                ["Income Replacement / 收入替代", money(needs["income_replacement"], currency)],
                ["Mortgage or Debt / 房贷或负债", money(needs["debts"], currency)],
                ["Education Need / 教育金", money(needs["education_needs"], currency)],
                ["Final Expenses / 最终费用", money(needs["final_expenses"], currency)],
                ["Less Existing Coverage / 扣除已有保障", f"-{money(needs['existing_coverage'], currency)}"],
                ["Estimated Coverage Gap / 估算保障缺口", money(needs["gap"], currency)],
            ],
            col_widths=[95 * mm, 70 * mm],
        ),
        _p("Recommended Coverage Bands / 建议保额区间", styles["heading"]),
        _table(
            [["Band", "Recommended Coverage"]]
            + [[name, money(value, currency)] for name, value in needs["bands"].items()],
            col_widths=[80 * mm, 85 * mm],
        ),
        _p("Plan Comparison / 方案对比", styles["heading"]),
        _table(
            [["Plan", "Coverage", "Term", "Annual", "Per Payment"]]
            + [
                [
                    row["Plan"],
                    money(row["Coverage"], currency),
                    f"{row['Term']} years",
                    money(row["Gross Annual"], currency),
                    money(row["Per Payment"], currency),
                ]
                for row in plan_rows
            ],
            col_widths=[35 * mm, 38 * mm, 28 * mm, 34 * mm, 34 * mm],
        ),
        _p("Selected Assumptions / 主要假设", styles["heading"]),
        _table(
            [
                ["Assumption", "Value"],
                ["Interest Rate / 利率", f"{assumptions.rate:.2%}"],
                ["Risk Factor / 风险因子", f"{assumptions.risk_factor:.2f}x"],
                [
                    "Expense Load / 费用假设",
                    f"alpha {assumptions.alpha:.2%}, beta {assumptions.beta:.2%}, gamma {assumptions.gamma:.2%}",
                ],
            ],
            col_widths=[70 * mm, 95 * mm],
        ),
        Spacer(1, 5 * mm),
        _p(
            "Disclaimer / 免责声明: This report is an educational planning aid based on selected assumptions. "
            "It is not an insurer quotation, policy illustration, legal advice, tax advice, or regulated financial advice. "
            "Final recommendations should be checked against official insurer materials and local licensing requirements.",
            styles["small"],
        ),
        _p(
            "本报告仅为基于所选假设的教育性规划辅助，不构成保险公司正式报价、产品建议书、法律意见、税务意见或受监管财务建议。"
            "最终方案应以保险公司正式资料及当地持牌要求为准。",
            styles["small"],
        ),
    ]

    def add_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont(PDF_FONT, 7)
        canvas.setFillColor(colors.HexColor("#8e8e93"))
        canvas.drawString(16 * mm, 10 * mm, f"{company} | LifePlan Advisor")
        canvas.drawRightString(194 * mm, 10 * mm, f"Page {doc.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)
    return buffer.getvalue()
