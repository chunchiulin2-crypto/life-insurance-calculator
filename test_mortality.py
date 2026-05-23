import pytest
import pandas as pd
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'clt_2010_2013.csv')

from mortality import load_table, get_qx, build_life_table


class TestLoadTable:
    def test_load_returns_dataframe(self):
        df = load_table(DATA_PATH)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 106
        assert list(df.columns) == ['age', 'qx_male', 'qx_female']

    def test_load_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_table('nonexistent.csv')


class TestGetQx:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.df = load_table(DATA_PATH)

    def test_male_age_30(self):
        qx = get_qx(self.df, 30, 'M')
        assert qx == pytest.approx(0.000623, abs=1e-6)

    def test_female_age_30(self):
        qx = get_qx(self.df, 30, 'F')
        assert qx == pytest.approx(0.000486, abs=1e-6)

    def test_age_105_death_certain(self):
        qx_m = get_qx(self.df, 105, 'M')
        qx_f = get_qx(self.df, 105, 'F')
        assert qx_m == 1.0
        assert qx_f == 1.0

    def test_invalid_gender(self):
        with pytest.raises(ValueError, match='gender'):
            get_qx(self.df, 30, 'X')

    def test_age_out_of_range(self):
        with pytest.raises(ValueError, match='age'):
            get_qx(self.df, 106, 'M')


class TestBuildLifeTable:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.df = load_table(DATA_PATH)

    def test_build_male_table(self):
        lt = build_life_table(self.df, 'M')
        assert 'lx' in lt.columns
        assert 'dx' in lt.columns
        assert 'tpx' in lt.columns
        assert lt.loc[0, 'lx'] == pytest.approx(100000, abs=0.5)
        assert lt.loc[105, 'lx'] < lt.loc[0, 'lx']  # fewer survivors at oldest age

    def test_tpx_range(self):
        lt = build_life_table(self.df, 'M')
        assert 0 < lt.loc[0, 'tpx'] < 1  # high but not 1.0 for newborn
        assert lt['tpx'].between(0, 1).all()

    def test_dx_sums_to_lx0(self):
        lt = build_life_table(self.df, 'M')
        assert lt['dx'].sum() == pytest.approx(lt.loc[0, 'lx'], abs=0.5)
