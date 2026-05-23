import pytest
from mortality import load_table, build_life_table
from premium import single_premium, annual_premium
from reserve import prospective_reserve, reserve_table
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'clt_2010_2013.csv')


class TestProspectiveReserve:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.df = load_table(DATA_PATH)
        self.lt_m = build_life_table(self.df, 'M')

    def test_reserve_at_time_zero_equals_zero(self):
        r = prospective_reserve(self.lt_m, 30, 1000000, 20, 0.035, 0)
        assert r == pytest.approx(0.0, abs=1e-6)

    def test_reserve_at_maturity_equals_zero(self):
        r = prospective_reserve(self.lt_m, 30, 1000000, 20, 0.035, 20)
        assert r == pytest.approx(0.0, abs=1e-6)

    def test_reserve_positive_mid_term(self):
        r = prospective_reserve(self.lt_m, 30, 1000000, 20, 0.035, 10)
        assert r > 0

    def test_reserve_increases_then_decreases(self):
        r5 = prospective_reserve(self.lt_m, 30, 1000000, 20, 0.035, 5)
        r10 = prospective_reserve(self.lt_m, 30, 1000000, 20, 0.035, 10)
        r15 = prospective_reserve(self.lt_m, 30, 1000000, 20, 0.035, 15)
        assert r15 < r10  # term insurance: reserve peaks then drops

    def test_reserve_equals_future_benefit_minus_future_premium(self):
        from premium import annuity_due
        age, S, n, i = 30, 1000000, 20, 0.035
        k = 7
        P = annual_premium(self.lt_m, age, S, n, i)
        future_benefit = single_premium(self.lt_m, age + k, S, n - k, i)
        future_premium_pv = P * annuity_due(self.lt_m, age + k, n - k, i)
        expected = future_benefit - future_premium_pv
        actual = prospective_reserve(self.lt_m, age, S, n, i, k)
        assert actual == pytest.approx(expected, rel=1e-5)


class TestReserveTable:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.df = load_table(DATA_PATH)
        self.lt_m = build_life_table(self.df, 'M')

    def test_table_length(self):
        tbl = reserve_table(self.lt_m, 30, 1000000, 20, 0.035)
        assert len(tbl) == 21  # years 0..20 inclusive

    def test_table_first_and_last_zero(self):
        tbl = reserve_table(self.lt_m, 30, 1000000, 20, 0.035)
        assert tbl[0][1] == pytest.approx(0.0, abs=1e-6)
        assert tbl[-1][1] == pytest.approx(0.0, abs=1e-6)
