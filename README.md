---
title: AI Actuarial Platform
emoji: 🧮
colorFrom: blue
colorTo: indigo
sdk: streamlit
sdk_version: "1.57.0"
app_file: app.py
pinned: false
---

# AI-Powered Actuarial Platform

ML mortality prediction, smart underwriting, fraud detection, pricing optimization & NLP chat assistant for life insurance products.

## Features

- **7 Life Insurance Products**: Term Life, Whole Life, Annuity, Endowment, Deferred Annuity, Deferred Assurance, Pure Endowment
- **Dual Life Tables**: CLT 2010-2013 (China) + AM92 (UK)
- **AI Mortality Prediction**: GradientBoostingRegressor replaces static table lookup (MAE 0.001, R² 0.99)
- **AI Smart Underwriting**: RandomForest predicts continuous risk factor from 11 health features (MAE 0.1, R² 0.89)
- **AI Fraud Detection**: Isolation Forest + XGBoost dual-layer detection (AUC 0.99)
- **Dynamic Pricing Optimizer**: Bayesian optimization for profit vs competitiveness balance
- **NLP Chat Assistant**: Natural language query → automatic premium calculation
- **i18n**: Chinese / English / Traditional Chinese

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Links

- GitHub: https://github.com/chunchiulin2-crypto/life-insurance-calculator
