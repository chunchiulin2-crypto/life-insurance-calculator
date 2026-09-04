from ui_components import normalize_metric_specs, param_chips_html


def test_param_chips_html_escapes_values():
    html = param_chips_html([("Age", 30), ("Risk", "<script>bad()</script>")])

    assert "Age: 30" in html
    assert "&lt;script&gt;bad()&lt;/script&gt;" in html
    assert "<script>" not in html


def test_param_chips_html_skips_none_values():
    html = param_chips_html([("Age", 30), ("Optional", None)])

    assert "Age: 30" in html
    assert "Optional" not in html


def test_normalize_metric_specs_defaults_optional_fields():
    metrics = normalize_metric_specs([{"label": "Premium", "value": "¥1,000"}])

    assert metrics == [{
        "label": "Premium",
        "value": "¥1,000",
        "help": None,
        "delta": None,
        "delta_color": "normal",
    }]
