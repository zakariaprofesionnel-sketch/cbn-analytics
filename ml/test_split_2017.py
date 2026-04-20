"""
Test ML — Train 2015-2016 / Test 2017
=======================================
Script indépendant pour valider le modèle Prophet sur une coupure différente.
Ne modifie aucun fichier existant (modèle principal, métriques, CSV).

Usage :
  python ml/test_split_2017.py
"""

import sys
import os
import numpy as np
import pandas as pd
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import warnings

warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ml.forecast import charger_donnees_mensuelles, preparer_donnees_prophet


def entrainer_et_evaluer_2017():
    """Entraîne sur 2015-2016, teste sur 2017."""

    # Charger les données
    df = charger_donnees_mensuelles()
    df_prophet = preparer_donnees_prophet(df)

    # Split
    train = df_prophet[df_prophet['ds'].dt.year < 2017].copy()
    test  = df_prophet[df_prophet['ds'].dt.year == 2017].copy()

    print(f"Train : {len(train)} mois (2015-2016)")
    print(f"Test  : {len(test)} mois (2017)")

    # Modèle (mêmes paramètres que le modèle principal)
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        seasonality_mode='multiplicative',
        changepoint_prior_scale=0.05,
        interval_width=0.95,
    )
    model.add_regressor('cours_brent', mode='multiplicative')
    model.fit(train)

    # Prédire sur 2017
    future_test = test[['ds', 'cours_brent']].copy()
    forecast    = model.predict(future_test)

    # Métriques
    y_true = test['y'].values
    y_pred = forecast['yhat'].values

    mae  = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    r2   = r2_score(y_true, y_pred)

    print()
    print("=== MÉTRIQUES SUR 2017 ===")
    print(f"  MAE  = {mae:.2f} m³")
    print(f"  RMSE = {rmse:.2f} m³")
    print(f"  MAPE = {mape:.2f}%")
    print(f"  R²   = {r2:.4f}")

    # Détail mois par mois
    df_result = pd.DataFrame({
        'date_mois':      test['ds'].dt.strftime('%Y-%m'),
        'reel_m3':        y_true,
        'prediction_m3':  y_pred,
        'erreur_abs_m3':  np.abs(y_true - y_pred),
        'erreur_pct':     np.abs(y_true - y_pred) / y_true * 100,
    })

    print()
    print("=== RÉEL vs PRÉDIT (2017) ===")
    print(df_result.to_string(index=False))


if __name__ == "__main__":
    entrainer_et_evaluer_2017()
