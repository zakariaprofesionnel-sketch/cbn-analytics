"""
Test ML - Train 2015-2016 / Test 2017.

Script independant pour valider Prophet sur le meme decoupage que le pipeline
principal. Ne modifie aucun fichier existant.

Usage :
  python ml/test_split_2017.py
"""

import os
import sys
import warnings

import numpy as np
import pandas as pd
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ml.forecast import charger_donnees_mensuelles, preparer_donnees_prophet  # noqa: E402


def entrainer_et_evaluer_2017():
    """Entraine sur 2015-2016, teste sur 2017."""
    df = charger_donnees_mensuelles()
    df_prophet = preparer_donnees_prophet(df)

    train = df_prophet[df_prophet["ds"].dt.year <= 2016].copy()
    test = df_prophet[df_prophet["ds"].dt.year == 2017].copy()

    print(f"Train : {len(train)} mois (2015-2016)")
    print(f"Test  : {len(test)} mois (2017)")

    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        seasonality_mode="multiplicative",
        changepoint_prior_scale=0.05,
        interval_width=0.95,
    )
    model.add_regressor("cours_brent", mode="multiplicative")
    model.fit(train)

    future_test = test[["ds", "cours_brent"]].copy()
    forecast = model.predict(future_test)

    y_true = test["y"].values
    y_pred = forecast["yhat"].values

    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    r2 = r2_score(y_true, y_pred)

    print()
    print("=== METRIQUES SUR 2017 ===")
    print(f"  MAE  = {mae:.2f} m3")
    print(f"  RMSE = {rmse:.2f} m3")
    print(f"  MAPE = {mape:.2f}%")
    print(f"  R2   = {r2:.4f}")

    df_result = pd.DataFrame(
        {
            "date_mois": test["ds"].dt.strftime("%Y-%m"),
            "reel_m3": y_true,
            "prediction_m3": y_pred,
            "erreur_abs_m3": np.abs(y_true - y_pred),
            "erreur_pct": np.abs(y_true - y_pred) / y_true * 100,
        }
    )

    print()
    print("=== REEL vs PREDIT (2017) ===")
    print(df_result.to_string(index=False))


if __name__ == "__main__":
    entrainer_et_evaluer_2017()
