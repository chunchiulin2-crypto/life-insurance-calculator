import os

import pytest

from app_utils import table_column_for_gender
from life_table_cache import cached_life_table, cached_load_table
from premium import annual_premium
from validation import (
    validate_coverage_window,
    validate_deferment,
    validate_issue_age,
    validate_term,
)


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CLT_PATH = os.path.join(DATA_DIR, "clt_2010_2013.csv")
AM92_PATH = os.path.join(DATA_DIR, "am92.csv")


class TestTableHelpers:
    def test_table_column_for_clt_uses_gender(self):
        assert table_column_for_gender("clt", "M") == "M"
        assert table_column_for_gender("clt", "F") == "F"

    def test_table_column_for_am92_uses_selected_column(self):
        assert table_column_for_gender("am92ult", "M") == "am92ult"
        assert table_column_for_gender("am92sel", "F") == "am92sel"

    def test_cached_load_table_returns_copy(self):
        first = cached_load_table(CLT_PATH)
        first.loc[0, "qx_male"] = 0.99

        second = cached_load_table(CLT_PATH)
        assert second.loc[0, "qx_male"] != 0.99

    def test_cached_life_table_matches_existing_premium_path(self):
        lt = cached_life_table(CLT_PATH, "clt", "M", 1.0)
        premium = annual_premium(lt, 30, 1000000, 20, 0.035)

        assert premium > 0
        assert "lx" in lt.columns

    def test_cached_life_table_supports_am92_columns(self):
        lt = cached_life_table(AM92_PATH, "am92ult", "M", 1.0)

        assert "qx" in lt.columns
        assert lt.loc[0, "lx"] == pytest.approx(100000)


class TestValidationHelpers:
    def test_valid_issue_age_and_term(self):
        assert validate_issue_age(30, 105)
        assert validate_term(30, 20, 105)

    def test_issue_age_must_be_below_limit_age(self):
        with pytest.raises(ValueError, match="below limit age"):
            validate_issue_age(105, 105)

    def test_term_must_fit_limit_age(self):
        with pytest.raises(ValueError, match="exceeds limit age"):
            validate_term(90, 20, 105)

    def test_deferment_must_end_before_limit_age(self):
        with pytest.raises(ValueError, match="below limit age"):
            validate_deferment(90, 15, 105)

    def test_deferred_coverage_window_must_fit_limit_age(self):
        with pytest.raises(ValueError, match="exceeds limit age"):
            validate_coverage_window(60, 20, 30, 105)
