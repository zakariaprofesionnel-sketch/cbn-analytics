"""Modele SARIMAX pour la prevision des ventes mensuelles de gasoil."""

import os
import pickle
import warnings

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from statsmodels.tsa.statespace.sarimax import SARIMAX

import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import BASE_DIR


warnings.filterwarnings("ignore")

MODEL_PATH = os.path.join(BASE_DIR, "ml", "sarima_model.pkl")


def preparer_donnees_sarimax(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare les donnees mensuelles pour SARIMAX."""
    data = pd.DataFrame(
        {
            "date_mois": pd.to_datetime(df["date_mois"]),
            "y": df["total_quantite_m3"].astype(float),
            "cours_brent": df["cours_brent_moyen_usd"].astype(float),
        }
    ).sort_values("date_mois")
    data = data.set_index("date_mois").asfreq("MS")
    data["cours_brent"] = data["cours_brent"].interpolate().ffill().bfill()
    data["y"] = data["y"].interpolate().ffill().bfill()
    return data


def _calculer_metriques(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    r2 = r2_score(y_true, y_pred)
    return {
        "MAE": round(float(mae), 2),
        "RMSE": round(float(rmse), 2),
        "MAPE": round(float(mape), 2),
        "R2": round(float(r2), 4),
    }


def _fit_best_sarimax(train: pd.DataFrame):
    """Teste une petite grille robuste et retourne le meilleur modele."""
    orders = [(0, 1, 1), (1, 1, 0), (1, 1, 1), (0, 1, 0), (2, 1, 1)]
    seasonal_orders = [(0, 0, 0, 12), (1, 0, 0, 12), (0, 1, 1, 12)]

    best_result = None
    best_cfg = None
    best_aic = np.inf

    for order in orders:
        for seasonal_order in seasonal_orders:
            try:
                model = SARIMAX(
                    train["y"],
                    exog=train[["cours_brent"]],
                    order=order,
                    seasonal_order=seasonal_order,
                    enforce_stationarity=False,
                    enforce_invertibility=False,
                )
                result = model.fit(disp=False, maxiter=300)
                if np.isfinite(result.aic) and result.aic < best_aic:
                    best_aic = result.aic
                    best_result = result
                    best_cfg = {"order": order, "seasonal_order": seasonal_order}
            except Exception:
                continue

    if best_result is None:
        model = SARIMAX(
            train["y"],
            exog=train[["cours_brent"]],
            order=(1, 1, 0),
            seasonal_order=(0, 0, 0, 12),
            enforce_stationarity=False,
            enforce_invertibility=False,
        )
        best_result = model.fit(disp=False, maxiter=300)
        best_cfg = {"order": (1, 1, 0), "seasonal_order": (0, 0, 0, 12)}

    return best_result, best_cfg


def entrainer_et_evaluer_sarimax(df: pd.DataFrame) -> dict:
    """Entraine sur 2015-2016 et evalue sur 2017."""
    data = preparer_donnees_sarimax(df)
    train = data[data.index.year <= 2016].copy()
    test = data[data.index.year == 2017].copy()

    print("[ML] Entrainement du modele SARIMAX...")
    print(f"[ML]   Train : {len(train)} mois (2015-2016)")
    print(f"[ML]   Test  : {len(test)} mois (2017)")

    result, cfg = _fit_best_sarimax(train)
    pred = result.get_forecast(steps=len(test), exog=test[["cours_brent"]])
    forecast_mean = pred.predicted_mean
    conf = pred.conf_int(alpha=0.05)

    forecast_test = pd.DataFrame(
        {
            "ds": test.index,
            "yhat": forecast_mean.values,
            "yhat_lower": conf.iloc[:, 0].values,
            "yhat_upper": conf.iloc[:, 1].values,
            "cours_brent": test["cours_brent"].values,
        }
    )

    metriques = _calculer_metriques(test["y"].values, forecast_test["yhat"].values)
    print("[ML] Metriques SARIMAX sur 2017 :")
    print(f"[ML]   MAE  = {metriques['MAE']:.2f} m3")
    print(f"[ML]   RMSE = {metriques['RMSE']:.2f} m3")
    print(f"[ML]   MAPE = {metriques['MAPE']:.2f}%")
    print(f"[ML]   R2   = {metriques['R2']:.4f}")
    print(f"[ML]   Config retenue : {cfg}")

    return {
        "model": result,
        "config": cfg,
        "metriques": metriques,
        "forecast_test": forecast_test,
        "train": train,
        "test": test,
    }


def entrainer_modele_final_sarimax(df: pd.DataFrame, end_year: int = 2017):
    """Entraine le modele final jusqu'a l'annee demandee."""
    data = preparer_donnees_sarimax(df)
    train = data[data.index.year <= end_year].copy()
    result, cfg = _fit_best_sarimax(train)

    payload = {
        "model": result,
        "config": cfg,
        "last_train_date": train.index.max().strftime("%Y-%m-%d"),
        "train_end_year": end_year,
    }
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(payload, f)

    print(f"[ML] Modele SARIMAX sauvegarde : {MODEL_PATH}")
    return payload


def prevoir_sarimax(
    model_payload: dict,
    df_historique: pd.DataFrame,
    horizon_mois: int,
    scenario_cours: str,
    dernier_cours: float,
) -> pd.DataFrame:
    """Prevoit les prochains mois avec pont exogene entre fin train et fin historique."""
    model = model_payload["model"]
    last_train_date = pd.Timestamp(model_payload["last_train_date"])
    derniere_date = pd.to_datetime(df_historique["date_mois"]).max()

    dates_bridge = pd.date_range(
        start=last_train_date + pd.offsets.MonthBegin(1),
        end=derniere_date,
        freq="MS",
    )
    brent_by_date = (
        df_historique.assign(date_mois=pd.to_datetime(df_historique["date_mois"]))
        .set_index("date_mois")["cours_brent_moyen_usd"]
        .astype(float)
    )
    bridge = brent_by_date.reindex(dates_bridge).interpolate().ffill().bfill()

    dates_futures = pd.date_range(
        start=derniere_date + pd.offsets.MonthBegin(1),
        periods=horizon_mois,
        freq="MS",
    )
    facteurs = {
        "stable": np.ones(horizon_mois),
        "hausse": np.linspace(1.0, 1.20, horizon_mois),
        "baisse": np.linspace(1.0, 0.80, horizon_mois),
    }
    cours_futurs = pd.Series(
        float(dernier_cours) * facteurs.get(scenario_cours, facteurs["stable"]),
        index=dates_futures,
    )

    exog_all = pd.concat([bridge, cours_futurs]).to_frame("cours_brent")
    pred = model.get_forecast(steps=len(exog_all), exog=exog_all)
    conf = pred.conf_int(alpha=0.05)

    forecast_all = pd.DataFrame(
        {
            "ds": exog_all.index,
            "yhat": pred.predicted_mean.values,
            "yhat_lower": conf.iloc[:, 0].values,
            "yhat_upper": conf.iloc[:, 1].values,
            "cours_brent": exog_all["cours_brent"].values,
        }
    )
    return forecast_all.tail(horizon_mois).reset_index(drop=True)


def charger_modele_sarimax() -> dict:
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)
