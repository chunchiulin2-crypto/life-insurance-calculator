import os

from advisor_planner import (
    Assumptions,
    ClientCase,
    SAMPLE_CASES,
    branded_report_pdf_bytes,
    bilingual_report_html,
    calculate_needs,
    compare_plans,
    money,
    plan_dataframe,
    sample_case_description,
    sample_case_labels,
    sample_client_case,
)


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def sample_case():
    return ClientCase(
        age=38,
        gender="M",
        currency="HKD",
        annual_income=600000,
        replacement_years=10,
        debts=2500000,
        education_needs=800000,
        final_expenses=150000,
        existing_coverage=500000,
        planning_horizon=20,
    )


def sample_assumptions():
    return Assumptions(
        rate=0.035,
        alpha=0.05,
        beta=0.02,
        gamma=0.001,
        frequency=12,
        risk_factor=1.0,
        table_path=os.path.join(DATA_DIR, "clt_2010_2013.csv"),
        table_col="clt",
    )


def test_calculate_needs_bands():
    needs = calculate_needs(sample_case())

    assert needs["income_replacement"] == 6000000
    assert needs["gross_need"] == 9450000
    assert needs["gap"] == 8950000
    assert needs["bands"]["Basic"] == 6712500
    assert needs["bands"]["Standard"] == 8950000
    assert needs["bands"]["Comprehensive"] == 11187500


def test_compare_plans_returns_displayable_rows():
    case = sample_case()
    needs = calculate_needs(case)
    rows = compare_plans(case, sample_assumptions(), needs["bands"]["Standard"])

    assert [row["Plan"] for row in rows] == ["Term Life", "Whole Life"]
    assert all(row["Gross Annual"] > 0 for row in rows)
    assert all(row["Per Payment"] > 0 for row in rows)

    df = plan_dataframe(rows, case.currency)
    assert list(df.columns) == [
        "Plan",
        "Coverage",
        "Term",
        "Net Annual",
        "Gross Annual",
        "Per Payment",
        "Tradeoff",
    ]
    assert df.loc[0, "Coverage"].startswith("HK$")


def test_bilingual_report_contains_core_sections():
    case = sample_case()
    needs = calculate_needs(case)
    rows = compare_plans(case, sample_assumptions(), needs["bands"]["Standard"])
    html = bilingual_report_html(
        case,
        needs,
        rows,
        sample_assumptions(),
        "Iris Chan",
        "Harbour Life Advisory",
    )

    assert "Life Protection Planning Report" in html
    assert "寿险保障规划报告" in html
    assert "Harbour Life Advisory" in html
    assert "Iris Chan" in html
    assert "advisor@example.com" not in html
    assert money(needs["gap"], "HKD") in html


def test_bilingual_report_includes_brand_contact_when_provided():
    case = sample_case()
    needs = calculate_needs(case)
    rows = compare_plans(case, sample_assumptions(), needs["bands"]["Standard"])
    html = bilingual_report_html(
        case,
        needs,
        rows,
        sample_assumptions(),
        "Iris Chan",
        "Harbour Life Advisory",
        "+852 1234 5678",
        "iris@example.com",
    )

    assert "+852 1234 5678" in html
    assert "iris@example.com" in html


def test_branded_pdf_report_returns_pdf_bytes():
    case = sample_case()
    needs = calculate_needs(case)
    rows = compare_plans(case, sample_assumptions(), needs["bands"]["Standard"])

    pdf_bytes = branded_report_pdf_bytes(
        case,
        needs,
        rows,
        sample_assumptions(),
        "Iris Chan",
        "Harbour Life Advisory",
        "+852 1234 5678",
        "iris@example.com",
    )

    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 3000
    assert b"%%EOF" in pdf_bytes[-1024:]


def test_sample_cases_are_complete_and_calculable():
    labels = sample_case_labels("zh-Hant")

    assert len(SAMPLE_CASES) == 3
    assert set(labels) == set(SAMPLE_CASES)

    for slug in SAMPLE_CASES:
        case = sample_client_case(slug)
        needs = calculate_needs(case)
        rows = compare_plans(case, sample_assumptions(), max(needs["gap"], 1))

        assert labels[slug]
        assert sample_case_description(slug, "en")
        assert needs["gross_need"] > 0
        assert len(rows) == 2
        assert all(row["Gross Annual"] > 0 for row in rows)
