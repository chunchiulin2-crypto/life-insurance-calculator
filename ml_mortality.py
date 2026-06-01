"""ML-based mortality prediction — replaces static life table lookup.

Trains a GradientBoostingRegressor on synthetic mortality data with
richer features (age, gender, smoker, BMI, income_level, exercise).
Exposes the same build_life_table() interface as mortality.py so
existing premium/reserve code works without changes.
"""

import os
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

RADIX = 100000

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

# ── Synthetic training data generation ──────────────────────────────

def _generate_training_data(n_samples=20000, seed=42):
    """Generate synthetic mortality training data with multiple features.

    Uses CLT 2010-2013 as the base mortality curve, then adds variation
    from lifestyle factors (smoking, BMI, exercise, income).
    """
    rng = np.random.default_rng(seed)

    # Load base mortality from CLT
    clt = pd.read_csv(os.path.join(DATA_DIR, 'clt_2010_2013.csv'))
    base_qx_male = clt['qx_male'].values
    base_qx_female = clt['qx_female'].values

    samples = []
    for _ in range(n_samples):
        age = rng.integers(0, 105)
        gender = rng.choice(['M', 'F'])
        smoker = rng.choice([0, 1], p=[0.7, 0.3])
        bmi = rng.normal(24, 4)
        bmi = max(16, min(42, bmi))
        exercise = rng.choice([0, 1, 2], p=[0.3, 0.4, 0.3])
        income_level = rng.choice([0, 1, 2], p=[0.3, 0.4, 0.3])

        # Base qx from life table
        base_qx = base_qx_male[age] if gender == 'M' else base_qx_female[age]

        # Apply lifestyle modifiers
        smoker_mult = 2.0 if smoker else 1.0
        bmi_mult = 1.0 + 0.03 * abs(bmi - 23)
        exercise_mult = 1.0 - 0.12 * exercise
        income_mult = 1.0 - 0.06 * income_level

        qx = base_qx * smoker_mult * bmi_mult * exercise_mult * income_mult
        qx = min(qx, 1.0)
        qx = max(qx, 0.00001)

        # Add noise
        qx *= rng.lognormal(0, 0.08)

        samples.append({
            'age': age,
            'gender': 1 if gender == 'M' else 0,
            'smoker': smoker,
            'bmi': round(bmi, 1),
            'exercise': exercise,
            'income_level': income_level,
            'qx': qx,
        })

    return pd.DataFrame(samples)


# ── Model ───────────────────────────────────────────────────────────

_model = None
_model_mae = None
_model_r2 = None


def train_model(n_samples=20000, seed=42):
    """Train the mortality prediction model. Called once, result cached in memory."""
    global _model, _model_mae, _model_r2

    if _model is not None:
        return _model

    df = _generate_training_data(n_samples, seed)
    features = ['age', 'gender', 'smoker', 'bmi', 'exercise', 'income_level']
    X = df[features]
    y = df['qx']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=seed
    )

    _model = GradientBoostingRegressor(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.05,
        min_samples_leaf=20,
        random_state=seed,
    )
    _model.fit(X_train, y_train)

    y_pred = _model.predict(X_test)
    _model_mae = mean_absolute_error(y_test, y_pred)
    _model_r2 = r2_score(y_test, y_pred)

    return _model


def model_metrics():
    """Return MAE and R² of the trained model, or None if not trained."""
    if _model is None:
        return None, None
    return _model_mae, _model_r2


# ── Public API ──────────────────────────────────────────────────────

def predict_qx(age, gender='M', smoker=0, bmi=23.0, exercise=1, income_level=1):
    """Predict qx for a single individual using the ML model."""
    model = train_model()
    X = pd.DataFrame([{
        'age': age,
        'gender': 1 if gender == 'M' else 0,
        'smoker': smoker,
        'bmi': bmi,
        'exercise': exercise,
        'income_level': income_level,
    }])
    return float(model.predict(X)[0])


def build_ml_life_table(age_start, gender='M', smoker=0, bmi=23.0,
                        exercise=1, income_level=1):
    """Build full life table using ML-predicted qx for each age.

    Same interface as mortality.build_life_table() — returns DataFrame
    with columns: age, qx, lx, dx, tpx. Ages from age_start to 120.
    """
    ages = np.arange(age_start, 121)
    qx_values = np.array([
        predict_qx(a, gender, smoker, bmi, exercise, income_level)
        for a in ages
    ])
    qx_values = np.clip(qx_values, 0.0, 1.0)

    lx = np.zeros(len(ages))
    lx[0] = RADIX
    for i in range(len(ages) - 1):
        dx_i = lx[i] * qx_values[i]
        lx[i + 1] = lx[i] - dx_i
    dx = lx * qx_values
    dx[-1] = lx[-1]

    tpx = np.zeros(len(ages))
    for i in range(len(ages) - 1):
        tpx[i] = lx[i + 1] / lx[i] if lx[i] > 0 else 0
    tpx[-1] = 0.0

    return pd.DataFrame({
        'age': ages,
        'qx': qx_values,
        'lx': lx,
        'dx': dx,
        'tpx': tpx,
    })


def compare_tables(age_start=0, gender='M'):
    """Return a comparison DataFrame: traditional (CLT) vs ML-predicted qx."""
    train_model()

    clt = pd.read_csv(os.path.join(DATA_DIR, 'clt_2010_2013.csv'))
    col = 'qx_male' if gender == 'M' else 'qx_female'

    ages = np.arange(age_start, min(105, len(clt)))
    traditional = clt[col].values[age_start:age_start + len(ages)]
    ml_pred = np.array([predict_qx(a, gender) for a in ages])

    return pd.DataFrame({
        'age': ages,
        'qx_traditional': traditional,
        'qx_ml': ml_pred,
        'diff': ml_pred - traditional,
        'diff_pct': (ml_pred - traditional) / traditional * 100,
    })


# ── Streamlit sidebar integration ───────────────────────────────────

def st_mortality_selector(t):
    """Render a sidebar mortality source selector + return the life table.

    Usage in product pages:
        lt, is_ml = st_mortality_selector(t)

    t() is the i18n function from the calling page.
    """
    import streamlit as st
    from mortality import load_table, build_life_table

    source = st.sidebar.radio(
        t('ml_source_label'),
        [t('ml_source_traditional'), t('ml_source_ai')],
        horizontal=True,
        help=t('ml_source_help'),
    )

    if source == t('ml_source_ai'):
        train_model()

        col1, col2 = st.sidebar.columns(2)
        with col1:
            smoker = 1 if st.checkbox(t('ml_smoker'), value=False) else 0
            bmi = st.slider(t('ml_bmi'), 16.0, 42.0, 23.0, 0.5)
        with col2:
            exercise_map = {t('ml_exercise_low'): 0, t('ml_exercise_mid'): 1, t('ml_exercise_high'): 2}
            exercise = st.selectbox(t('ml_exercise'), list(exercise_map.keys()))
            income_map = {t('ml_income_low'): 0, t('ml_income_mid'): 1, t('ml_income_high'): 2}
            income = st.selectbox(t('ml_income'), list(income_map.keys()))

        st.sidebar.caption(t('ml_ai_note'))

        return None, {
            'smoker': smoker,
            'bmi': bmi,
            'exercise': exercise_map[exercise],
            'income': income_map[income],
        }

    return None, None


def get_ml_life_table(gender_code, ml_params):
    """Build ML life table from sidebar params."""
    return build_ml_life_table(
        0, gender_code,
        smoker=ml_params['smoker'],
        bmi=ml_params['bmi'],
        exercise=ml_params['exercise'],
        income_level=ml_params['income'],
    )
