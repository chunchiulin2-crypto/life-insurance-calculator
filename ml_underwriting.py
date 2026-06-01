"""AI Smart Underwriting — predict risk factor from health/lifestyle data.

Replaces the manual 3-class underwriting (Preferred/Standard/Substandard)
with an ML model that outputs a continuous risk factor (0.5–3.0).

The model uses a RandomForestRegressor trained on synthetic data that
simulates real actuarial underwriting guidelines.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

# ── Synthetic training data ─────────────────────────────────────────


def _generate_uw_data(n_samples=15000, seed=42):
    """Generate synthetic underwriting data with realistic risk rules.

    Based on standard actuarial underwriting guidelines:
    - Smoking is the largest risk factor (~+0.5)
    - High BMI, high BP, high cholesterol each add ~0.2-0.4
    - Family history of early death adds ~0.2
    - Exercise provides a discount (~-0.2)
    - Occupation risk (desk vs manual vs hazardous) adds up to 0.4
    """
    rng = np.random.default_rng(seed)

    records = []
    for _ in range(n_samples):
        age = rng.integers(18, 80)
        bmi = round(rng.normal(25, 5), 1)
        bmi = max(16, min(45, bmi))
        smoker = rng.choice([0, 1], p=[0.75, 0.25])
        systolic_bp = int(rng.normal(120, 15))
        diastolic_bp = int(rng.normal(80, 10))
        cholesterol = int(rng.normal(190, 40))
        family_history = rng.choice([0, 1], p=[0.8, 0.2])
        exercise = rng.choice([0, 1, 2], p=[0.3, 0.4, 0.3])
        alcohol = rng.choice([0, 1, 2], p=[0.4, 0.4, 0.2])
        occupation_risk = rng.choice([0, 1, 2], p=[0.5, 0.35, 0.15])
        chronic_condition = rng.choice([0, 1], p=[0.85, 0.15])

        # Base risk factor
        risk = 1.0

        # Smoking: strong effect
        risk += 0.5 * smoker

        # BMI: U-shaped risk
        if bmi < 18.5:
            risk += 0.15
        elif bmi > 30:
            risk += 0.25
        elif bmi > 27:
            risk += 0.1

        # Blood pressure
        if systolic_bp > 140 or diastolic_bp > 90:
            risk += 0.35
        elif systolic_bp > 130 or diastolic_bp > 85:
            risk += 0.15

        # Cholesterol
        if cholesterol > 240:
            risk += 0.25
        elif cholesterol > 200:
            risk += 0.1

        # Family history
        risk += 0.2 * family_history

        # Exercise discount
        risk -= 0.15 * exercise

        # Alcohol
        risk += 0.1 * (alcohol == 2)

        # Occupation
        risk += 0.2 * occupation_risk

        # Chronic condition
        risk += 0.4 * chronic_condition

        # Age modifier (older = slightly higher risk)
        risk += 0.003 * max(0, age - 50)

        # Add noise
        risk *= rng.normal(1.0, 0.06)
        risk = round(max(0.4, min(3.5, risk)), 3)

        records.append({
            'age': age, 'bmi': bmi, 'smoker': smoker,
            'systolic_bp': systolic_bp, 'diastolic_bp': diastolic_bp,
            'cholesterol': cholesterol, 'family_history': family_history,
            'exercise': exercise, 'alcohol': alcohol,
            'occupation_risk': occupation_risk,
            'chronic_condition': chronic_condition,
            'risk_factor': risk,
        })

    return pd.DataFrame(records)


# ── Model ───────────────────────────────────────────────────────────

_model = None
_model_mae = None
_model_r2 = None
FEATURES = ['age', 'bmi', 'smoker', 'systolic_bp', 'diastolic_bp',
            'cholesterol', 'family_history', 'exercise', 'alcohol',
            'occupation_risk', 'chronic_condition']


def train_uw_model(n_samples=15000, seed=42):
    """Train the underwriting risk model."""
    global _model, _model_mae, _model_r2

    if _model is not None:
        return _model

    df = _generate_uw_data(n_samples, seed)
    X = df[FEATURES]
    y = df['risk_factor']
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=seed
    )

    _model = RandomForestRegressor(
        n_estimators=150, max_depth=12, min_samples_leaf=10,
        random_state=seed, n_jobs=-1,
    )
    _model.fit(X_train, y_train)

    y_pred = _model.predict(X_test)
    _model_mae = mean_absolute_error(y_test, y_pred)
    _model_r2 = r2_score(y_test, y_pred)

    return _model


def uw_model_metrics():
    """Return MAE and R² of the trained underwriting model."""
    if _model is None:
        return None, None
    return _model_mae, _model_r2


# ── Public API ──────────────────────────────────────────────────────


def predict_risk_factor(age=30, bmi=23.0, smoker=0, systolic_bp=120, diastolic_bp=80,
                        cholesterol=190, family_history=0, exercise=1,
                        alcohol=1, occupation_risk=0, chronic_condition=0):
    """Predict the continuous risk factor for a given health profile."""
    model = train_uw_model()
    X = pd.DataFrame([{
        'age': age, 'bmi': bmi, 'smoker': smoker,
        'systolic_bp': systolic_bp, 'diastolic_bp': diastolic_bp,
        'cholesterol': cholesterol, 'family_history': family_history,
        'exercise': exercise, 'alcohol': alcohol,
        'occupation_risk': occupation_risk,
        'chronic_condition': chronic_condition,
    }])
    return round(float(model.predict(X)[0]), 3)


def classify_risk(risk_factor):
    """Map continuous risk factor to underwriting class."""
    if risk_factor <= 0.75:
        return 'preferred', 0.7
    elif risk_factor <= 0.9:
        return 'preferred_plus', 0.85
    elif risk_factor <= 1.15:
        return 'standard', 1.0
    elif risk_factor <= 1.5:
        return 'substandard', 1.5
    else:
        return 'decline', 2.0


def feature_importance_df():
    """Return feature importance as a sorted DataFrame."""
    model = train_uw_model()
    return pd.DataFrame({
        'feature': FEATURES,
        'importance': model.feature_importances_,
    }).sort_values('importance', ascending=False)
