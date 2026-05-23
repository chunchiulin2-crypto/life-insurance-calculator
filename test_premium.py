import pytest
from mortality import load_table, build_life_table
from premium import annuity_due, single_premium, annual_premium
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'clt_2010_2013.csv')


class TestAnnuityDue:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.df = load_table(DATA_PATH)
        self.lt_m = build_life_table(self.df, 'M')

    def test_one_year_annuity(self):
        # ax:1 = 1 (single payment at beginning, discount factor near 1 when rate=0)
        # Actually a_x:1 = 1 always for annuity-due (payment at time 0, no survival needed)
        result = annuity_due(self.lt_m, 30, 1, 0.035)
        assert result == pytest.approx(1.0, abs=1e-6)

    def test_annuity_decreases_with_age(self):
        a30 = annuity_due(self.lt_m, 30, 10, 0.035)
        a50 = annuity_due(self.lt_m, 50, 10, 0.035)
        assert a50 < a30

    def test_annuity_positive(self):
        a = annuity_due(self.lt_m, 30, 20, 0.035)
        assert a > 0
        assert a < 20  # less than term (discounting + mortality)


class TestSinglePremium:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.df = load_table(DATA_PATH)
        self.lt_m = build_life_table(self.df, 'M')

    def test_premium_positive(self):
        sp = single_premium(self.lt_m, 30, 1000000, 20, 0.035)
        assert sp > 0

    def test_premium_increases_with_age(self):
        sp30 = single_premium(self.lt_m, 30, 1000000, 10, 0.035)
        sp50 = single_premium(self.lt_m, 50, 1000000, 10, 0.035)
        assert sp50 > sp30

    def test_term_matters(self):
        sp10 = single_premium(self.lt_m, 30, 1000000, 10, 0.035)
        sp20 = single_premium(self.lt_m, 30, 1000000, 20, 0.035)
        assert sp20 > sp10

    def test_zero_interest_rate(self):
        sp = single_premium(self.lt_m, 30, 1000000, 20, 0.0)
        assert 0 < sp < 1000000

    def test_very_high_rate(self):
        sp = single_premium(self.lt_m, 30, 1000000, 20, 0.20)
        assert sp < 100000


class TestAnnualPremium:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.df = load_table(DATA_PATH)
        self.lt_m = build_life_table(self.df, 'M')

    def test_consistency_with_single_premium(self):
        # P * a_x:n = A_x:n * S  ->  P = SP / a
        sp = single_premium(self.lt_m, 30, 1000000, 20, 0.035)
        ap = annual_premium(self.lt_m, 30, 1000000, 20, 0.035)
        a = annuity_due(self.lt_m, 30, 20, 0.035)
        assert sp == pytest.approx(ap * a, rel=1e-5)

    def test_annual_less_than_single(self):
        sp = single_premium(self.lt_m, 30, 1000000, 20, 0.035)
        ap = annual_premium(self.lt_m, 30, 1000000, 20, 0.035)
        assert ap < sp
