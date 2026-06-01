"""AI Claims Fraud Detection — anomaly detection + ensemble classification.

Detects potentially fraudulent insurance claims using a two-layer approach:
1. Isolation Forest (unsupervised anomaly detection)
2. XGBoost classifier (supervised, trained on synthetic fraud patterns)

Returns: fraud probability (0-1) + risk flags + recommendation.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, classification_report

FEATURES = [
    'claim_amount', 'policy_age_months', 'age', 'policy_type_code',
    'claim_type_code', 'previous_claims', 'amount_to_premium_ratio',
    'time_to_report_days', 'has_witness', 'has_police_report',
    'medical_consistent', 'beneficiary_change_recent',
]


def _generate_fraud_data(n_samples=20000, fraud_rate=0.08, seed=42):
    """Generate synthetic claims data with realistic fraud patterns.

    Fraud red flags (increase fraud probability):
    - Claim filed shortly after policy inception
    - Claim amount >> annual premium
    - Many previous claims
    - No witness / no police report
    - Recent beneficiary change
    - Inconsistent medical records
    - Delayed reporting then large claim
    """
    rng = np.random.default_rng(seed)

    records = []
    for _ in range(n_samples):
        age = rng.integers(18, 85)
        policy_age = rng.integers(1, 240)
        policy_type = rng.choice([0, 1, 2])  # term, whole, endowment
        claim_type = rng.choice([0, 1, 2, 3])  # death, disability, critical_illness, accidental
        claim_amount = int(rng.lognormal(11, 1.2))  # median ~60k
        annual_premium = int(claim_amount / rng.uniform(5, 200))
        previous_claims = rng.poisson(0.8)
        time_to_report = rng.integers(0, 90)
        has_witness = rng.choice([0, 1], p=[0.3, 0.7])
        has_police = rng.choice([0, 1], p=[0.4, 0.6])
        medical_ok = rng.choice([0, 1], p=[0.2, 0.8])
        beneficiary_change = rng.choice([0, 1], p=[0.9, 0.1])

        ratio = claim_amount / max(annual_premium, 1)

        # Fraud scoring logic
        fraud_score = 0.0

        # Policy age < 12 months + high ratio
        if policy_age < 12 and ratio > 30:
            fraud_score += 0.35
        elif policy_age < 24 and ratio > 50:
            fraud_score += 0.25

        # Many previous claims
        if previous_claims >= 3:
            fraud_score += 0.2
        elif previous_claims >= 2:
            fraud_score += 0.1

        # No witness + no police report
        if not has_witness and not has_police:
            fraud_score += 0.15

        # Recent beneficiary change
        if beneficiary_change and policy_age < 12:
            fraud_score += 0.25

        # Inconsistent medical
        if not medical_ok:
            fraud_score += 0.15

        # Delayed report on large claim
        if time_to_report > 30 and claim_amount > 500000:
            fraud_score += 0.15

        # High ratio alone
        if ratio > 100:
            fraud_score += 0.15

        # Add noise
        fraud_score += rng.normal(0, 0.05)
        fraud_score = max(0, min(1, fraud_score))

        is_fraud = 1 if fraud_score > 0.55 else 0

        records.append({
            'claim_amount': claim_amount,
            'policy_age_months': policy_age,
            'age': age,
            'policy_type_code': policy_type,
            'claim_type_code': claim_type,
            'previous_claims': previous_claims,
            'amount_to_premium_ratio': round(ratio, 1),
            'time_to_report_days': time_to_report,
            'has_witness': has_witness,
            'has_police_report': has_police,
            'medical_consistent': medical_ok,
            'beneficiary_change_recent': beneficiary_change,
            'is_fraud': is_fraud,
        })

    df = pd.DataFrame(records)
    fraud_count = df['is_fraud'].sum()
    print(f'[ml_fraud] Generated {n_samples} records, {fraud_count} fraud ({fraud_count/n_samples*100:.1f}%)')
    return df


# ── Models ──────────────────────────────────────────────────────────

_iso_model = None
_xgb_model = None
_auc = None


def train_fraud_models(n_samples=20000, seed=42):
    """Train both anomaly detection and classification models."""
    global _iso_model, _xgb_model, _auc

    if _xgb_model is not None:
        return _xgb_model

    df = _generate_fraud_data(n_samples, seed)
    X = df[FEATURES]
    y = df['is_fraud']

    # Unsupervised: Isolation Forest
    _iso_model = IsolationForest(
        n_estimators=150, contamination=0.08, random_state=seed, n_jobs=-1,
    )
    _iso_model.fit(X)

    # Supervised: XGBoost
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=seed, stratify=y,
    )
    scale_pos_weight = (len(y_train) - y_train.sum()) / max(y_train.sum(), 1)

    _xgb_model = XGBClassifier(
        n_estimators=200, max_depth=6, learning_rate=0.05,
        scale_pos_weight=scale_pos_weight,
        random_state=seed, verbosity=0,
    )
    _xgb_model.fit(X_train, y_train)

    y_prob = _xgb_model.predict_proba(X_test)[:, 1]
    _auc = roc_auc_score(y_test, y_prob)

    return _xgb_model


def fraud_model_metrics():
    """Return AUC of the fraud detection model."""
    if _xgb_model is None:
        return None
    return _auc


def fraud_feature_importance():
    """Return feature importance from XGBoost model."""
    model = train_fraud_models()
    imp = model.feature_importances_
    return pd.DataFrame({'feature': FEATURES, 'importance': imp}).sort_values(
        'importance', ascending=False
    )


# ── Public API ──────────────────────────────────────────────────────


def analyze_claim(claim_amount, policy_age_months, age, policy_type='term',
                  claim_type='death', previous_claims=0, annual_premium=None,
                  time_to_report_days=7, has_witness=True, has_police_report=True,
                  medical_consistent=True, beneficiary_change_recent=False):
    """Analyze a claim and return fraud probability + risk flags.

    Returns:
        dict with fraud_probability, anomaly_score, risk_level, flags, recommendation
    """
    train_fraud_models()

    if annual_premium is None:
        annual_premium = max(1000, claim_amount / 50)

    policy_map = {'term': 0, 'whole': 1, 'endowment': 2}
    claim_map = {'death': 0, 'disability': 1, 'critical_illness': 2, 'accidental': 3}

    X = pd.DataFrame([{
        'claim_amount': claim_amount,
        'policy_age_months': policy_age_months,
        'age': age,
        'policy_type_code': policy_map.get(policy_type, 0),
        'claim_type_code': claim_map.get(claim_type, 0),
        'previous_claims': previous_claims,
        'amount_to_premium_ratio': round(claim_amount / max(annual_premium, 1), 1),
        'time_to_report_days': time_to_report_days,
        'has_witness': int(has_witness),
        'has_police_report': int(has_police_report),
        'medical_consistent': int(medical_consistent),
        'beneficiary_change_recent': int(beneficiary_change_recent),
    }])

    # XGBoost probability
    xgb_prob = float(_xgb_model.predict_proba(X)[:, 1][0])

    # Isolation Forest anomaly score (-1 = anomaly)
    iso_pred = int(_iso_model.predict(X)[0])
    iso_score = float(_iso_model.score_samples(X)[0])
    # Normalize to 0-1 where 1 = most anomalous
    anomaly_score = round(1.0 / (1.0 + np.exp(iso_score)), 3)

    # Combined score (weighted average)
    combined = round(xgb_prob * 0.6 + anomaly_score * 0.4, 3)

    # Risk level
    if combined < 0.15:
        risk_level = 'low'
        recommendation = 'auto_approve'
    elif combined < 0.35:
        risk_level = 'medium'
        recommendation = 'review'
    elif combined < 0.6:
        risk_level = 'high'
        recommendation = 'investigate'
    else:
        risk_level = 'critical'
        recommendation = 'reject'

    # Risk flags
    flags = []
    if iso_pred == -1:
        flags.append('Isolation Forest flagged as anomaly')
    if xgb_prob > 0.5:
        flags.append('XGBoost high fraud probability')
    if claim_amount / max(annual_premium, 1) > 50:
        flags.append(f'Claim/premium ratio extremely high ({claim_amount/annual_premium:.0f}x)')
    if policy_age_months < 12:
        flags.append('Claim within first policy year')
    if not has_witness and not has_police_report:
        flags.append('No witness or police report')
    if beneficiary_change_recent and policy_age_months < 12:
        flags.append('Recent beneficiary change + new policy')
    if not medical_consistent:
        flags.append('Medical records inconsistent with claim')
    if previous_claims >= 3:
        flags.append(f'High previous claims ({previous_claims})')

    return {
        'fraud_probability': combined,
        'xgb_probability': round(xgb_prob, 3),
        'anomaly_score': anomaly_score,
        'risk_level': risk_level,
        'recommendation': recommendation,
        'flags': flags,
    }
