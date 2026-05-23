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


class TestWholeLife:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.df = load_table(DATA_PATH)
        self.lt_m = build_life_table(self.df, 'M')

    def test_whole_life_sp_positive(self):
        from premium import whole_life_single_premium
        sp = whole_life_single_premium(self.lt_m, 30, 1000000, 0.035)
        assert sp > 0
        sp_term = single_premium(self.lt_m, 30, 1000000, 20, 0.035)
        assert sp > sp_term  # whole life > term-20

    def test_whole_life_sp_increases_with_age(self):
        from premium import whole_life_single_premium
        sp30 = whole_life_single_premium(self.lt_m, 30, 1000000, 0.035)
        sp50 = whole_life_single_premium(self.lt_m, 50, 1000000, 0.035)
        assert sp50 > sp30

    def test_whole_life_ap_consistency(self):
        from premium import whole_life_single_premium, whole_life_annual_premium, annuity_due_whole_life
        sp = whole_life_single_premium(self.lt_m, 30, 1000000, 0.035)
        ap = whole_life_annual_premium(self.lt_m, 30, 1000000, 0.035)
        a = annuity_due_whole_life(self.lt_m, 30, 0.035)
        assert sp == pytest.approx(ap * a, rel=1e-5)

    def test_whole_life_annuity_due_decreases_with_age(self):
        from premium import annuity_due_whole_life
        a30 = annuity_due_whole_life(self.lt_m, 30, 0.035)
        a60 = annuity_due_whole_life(self.lt_m, 60, 0.035)
        assert a60 < a30


class TestEndowment:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.df = load_table(DATA_PATH)
        self.lt_m = build_life_table(self.df, 'M')

    def test_endowment_sp_greater_than_term(self):
        from premium import endowment_single_premium
        sp_term = single_premium(self.lt_m, 30, 1000000, 20, 0.035)
        sp_endow = endowment_single_premium(self.lt_m, 30, 1000000, 20, 0.035)
        assert sp_endow > sp_term

    def test_pure_endowment_between_0_and_1(self):
        from premium import pure_endowment
        pe = pure_endowment(self.lt_m, 30, 20, 0.035)
        assert 0 < pe < 1

    def test_endowment_ap_consistency(self):
        from premium import endowment_single_premium, endowment_annual_premium
        sp = endowment_single_premium(self.lt_m, 30, 1000000, 20, 0.035)
        ap = endowment_annual_premium(self.lt_m, 30, 1000000, 20, 0.035)
        a = annuity_due(self.lt_m, 30, 20, 0.035)
        assert sp == pytest.approx(ap * a, rel=1e-5)


class TestAnnuity:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.df = load_table(DATA_PATH)
        self.lt_m = build_life_table(self.df, 'M')

    def test_annuity_price_positive(self):
        from premium import annuity_price
        price = annuity_price(self.lt_m, 30, 50000, 20, 0.035)
        assert price > 0

    def test_annuity_price_equals_annuity_due_times_payment(self):
        from premium import annuity_price
        payment = 50000
        price = annuity_price(self.lt_m, 30, payment, 20, 0.035)
        a = annuity_due(self.lt_m, 30, 20, 0.035)
        expected = payment * a
        assert price == pytest.approx(expected, rel=1e-5)

    def test_annuity_price_decreases_with_age(self):
        from premium import annuity_price
        p30 = annuity_price(self.lt_m, 30, 50000, 10, 0.035)
        p60 = annuity_price(self.lt_m, 60, 50000, 10, 0.035)
        assert p60 < p30  # older = fewer expected payments
