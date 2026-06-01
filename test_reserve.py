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


class TestWholeLifeReserve:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.df = load_table(DATA_PATH)
        self.lt_m = build_life_table(self.df, 'M')

    def test_wl_reserve_starts_at_zero(self):
        from reserve import whole_life_reserve_table
        tbl = whole_life_reserve_table(self.lt_m, 30, 1000000, 0.035)
        assert tbl[0][1] == pytest.approx(0.0, abs=1e-6)

    def test_wl_reserve_increases_over_time(self):
        from reserve import whole_life_reserve_table
        tbl = whole_life_reserve_table(self.lt_m, 30, 1000000, 0.035)
        r10 = [v for y, v in tbl if y == 10][0]
        r30 = [v for y, v in tbl if y == 30][0]
        assert r30 > r10


class TestEndowmentReserve:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.df = load_table(DATA_PATH)
        self.lt_m = build_life_table(self.df, 'M')

    def test_endow_reserve_ends_at_sum_insured(self):
        from reserve import endowment_reserve_table
        tbl = endowment_reserve_table(self.lt_m, 30, 1000000, 20, 0.035)
        assert tbl[0][1] == pytest.approx(0.0, abs=1e-6)
        assert tbl[-1][1] == pytest.approx(1000000, rel=1e-5)


class TestAnnuityReserve:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.df = load_table(DATA_PATH)
        self.lt_m = build_life_table(self.df, 'M')

    def test_annuity_reserve_starts_at_price(self):
        from reserve import annuity_reserve_table
        from premium import annuity_price
        price = annuity_price(self.lt_m, 30, 100000, 20, 0.035)
        tbl = annuity_reserve_table(self.lt_m, 30, 100000, 20, 0.035)
        assert tbl[0][1] == pytest.approx(price, rel=1e-5)

    def test_annuity_reserve_ends_at_zero(self):
        from reserve import annuity_reserve_table
        tbl = annuity_reserve_table(self.lt_m, 30, 100000, 20, 0.035)
        assert tbl[-1][1] == pytest.approx(0.0, abs=1e-6)

    def test_annuity_reserve_decreases(self):
        from reserve import annuity_reserve_table
        tbl = annuity_reserve_table(self.lt_m, 30, 100000, 20, 0.035)
        r5 = [v for y, v in tbl if y == 5][0]
        r10 = [v for y, v in tbl if y == 10][0]
        assert r10 < r5  # liability decreases as payments are made


class TestDeferredAssuranceReserve:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.df = load_table(DATA_PATH)
        self.lt_m = build_life_table(self.df, 'M')

    def test_def_assurance_starts_at_zero(self):
        from reserve import deferred_assurance_reserve_table
        tbl = deferred_assurance_reserve_table(self.lt_m, 30, 10, 1000000, 0.035, coverage=15)
        assert tbl[0][1] == pytest.approx(0.0, abs=1e-6)

    def test_def_assurance_reserve_positive_during_deferral(self):
        from reserve import deferred_assurance_reserve_table
        tbl = deferred_assurance_reserve_table(self.lt_m, 30, 10, 1000000, 0.035, coverage=15)
        r5 = [v for y, v in tbl if y == 5][0]
        assert r5 > 0  # reserve builds up from premiums

    def test_def_assurance_term_ends_at_zero(self):
        from reserve import deferred_assurance_reserve_table
        tbl = deferred_assurance_reserve_table(self.lt_m, 30, 5, 1000000, 0.035, coverage=10)
        assert tbl[-1][1] == pytest.approx(0.0, abs=1e-6)

    def test_def_assurance_whole_life_increasing(self):
        from reserve import deferred_assurance_reserve_table
        tbl = deferred_assurance_reserve_table(self.lt_m, 30, 10, 1000000, 0.035, coverage=None)
        r_at_def = [v for y, v in tbl if y == 10][0]
        r_later = [v for y, v in tbl if y == 30][0]
        assert r_later > r_at_def


class TestPureEndowmentReserve:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.df = load_table(DATA_PATH)
        self.lt_m = build_life_table(self.df, 'M')

    def test_pe_reserve_starts_at_zero(self):
        from reserve import pure_endowment_reserve_table
        tbl = pure_endowment_reserve_table(self.lt_m, 30, 1000000, 20, 0.035)
        assert tbl[0][1] == pytest.approx(0.0, abs=1e-6)

    def test_pe_reserve_ends_at_sum_insured(self):
        from reserve import pure_endowment_reserve_table
        tbl = pure_endowment_reserve_table(self.lt_m, 30, 1000000, 20, 0.035)
        assert tbl[-1][1] == pytest.approx(1000000, rel=1e-5)

    def test_pe_reserve_monotonically_increasing(self):
        from reserve import pure_endowment_reserve_table
        tbl = pure_endowment_reserve_table(self.lt_m, 30, 1000000, 20, 0.035)
        values = [v for y, v in tbl]
        for i in range(1, len(values)):
            assert values[i] >= values[i-1] - 1e-9
