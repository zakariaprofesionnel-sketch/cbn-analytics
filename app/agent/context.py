from __future__ import annotations

import os
import sys
from typing import Dict, Any

import pandas as pd
import pickle

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import BASE_DIR  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import charger_ventes_mensuelles  # noqa: E402


PREDICTIONS_TEST_PATH = os.path.join(BASE_DIR, "ml", "predictions_test.csv")


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def load_ml_results() -> dict:
    """Charge les résultats ML (prévisions, métriques)."""
    ml_results = {}
    base_path = os.path.join(os.path.dirname(__file__), "../../ml")

    # Charger les prévisions
    predictions_path = os.path.join(base_path, "predictions_test.csv")
    if os.path.exists(predictions_path):
        ml_results["predictions"] = pd.read_csv(predictions_path)

    # Charger les métriques
    metrics_path = os.path.join(base_path, "metriques.pkl")
    if os.path.exists(metrics_path):
        with open(metrics_path, "rb") as f:
            metrics_payload = pickle.load(f)
            if isinstance(metrics_payload, dict) and "best_model" in metrics_payload:
                best_model = metrics_payload.get("best_model", "Prophet")
                ml_results["metrics_all"] = metrics_payload
                ml_results["best_model"] = best_model
                ml_results["metrics"] = metrics_payload.get(best_model, {})
            else:
                ml_results["metrics"] = metrics_payload

    if "predictions" in ml_results and "best_model" in ml_results:
        best = str(ml_results["best_model"]).lower()
        pred_col = f"{best}_prediction_m3"
        err_col = f"{best}_erreur_abs_m3"
        predictions = ml_results["predictions"]
        if pred_col in predictions.columns and "prediction_m3" not in predictions.columns:
            predictions["prediction_m3"] = predictions[pred_col]
        if err_col in predictions.columns and "erreur_abs_m3" not in predictions.columns:
            predictions["erreur_abs_m3"] = predictions[err_col]

    return ml_results


def build_agent_context() -> Dict[str, Any]:
    """Builds a compact context from warehouse + ML artifacts."""
    df = charger_ventes_mensuelles()
    if df.empty:
        return {
            "status": "no_data",
            "message": "Aucune donnée mensuelle disponible.",
            "signals": {},
            "raw": {},
        }


    df = df.sort_values("date_mois").copy()
    df["date_mois"] = pd.to_datetime(df["date_mois"])

    latest = df.iloc[-1]
    last_12 = df.tail(min(12, len(df)))

    mean_last_12 = _safe_float(last_12["total_quantite_m3"].mean())
    std_last_12 = _safe_float(last_12["total_quantite_m3"].std())
    latest_qty = _safe_float(latest["total_quantite_m3"])
    latest_brent = _safe_float(latest.get("cours_brent_moyen_usd"))

    trend_3m = 0.0
    if len(df) >= 4:
        prev_3 = _safe_float(df.iloc[-4]["total_quantite_m3"])
        trend_3m = ((latest_qty - prev_3) / prev_3 * 100.0) if prev_3 else 0.0

    error_mae = 0.0
    error_rmse = 0.0
    if os.path.exists(PREDICTIONS_TEST_PATH):
        df_pred = pd.read_csv(PREDICTIONS_TEST_PATH)
        if not df_pred.empty and "erreur_abs_m3" in df_pred.columns:
            error_mae = _safe_float(df_pred["erreur_abs_m3"].mean())
            if "erreur_m3" in df_pred.columns:
                error_rmse = _safe_float((df_pred["erreur_m3"] ** 2).mean() ** 0.5)
        elif not df_pred.empty and "sarimax_erreur_abs_m3" in df_pred.columns:
            error_mae = _safe_float(df_pred["sarimax_erreur_abs_m3"].mean())
            if "sarimax_prediction_m3" in df_pred.columns and "reel_m3" in df_pred.columns:
                err = df_pred["reel_m3"] - df_pred["sarimax_prediction_m3"]
                error_rmse = _safe_float((err ** 2).mean() ** 0.5)
        elif not df_pred.empty and "prophet_erreur_abs_m3" in df_pred.columns:
            error_mae = _safe_float(df_pred["prophet_erreur_abs_m3"].mean())
            if "prophet_prediction_m3" in df_pred.columns and "reel_m3" in df_pred.columns:
                err = df_pred["reel_m3"] - df_pred["prophet_prediction_m3"]
                error_rmse = _safe_float((err ** 2).mean() ** 0.5)

    signals = {
        "latest_date": str(pd.to_datetime(latest["date_mois"]).date()),
        "latest_qty_m3": latest_qty,
        "latest_brent_usd": latest_brent,
        "mean_qty_last_12_m3": mean_last_12,
        "std_qty_last_12_m3": std_last_12,
        "qty_trend_3m_pct": trend_3m,
        "mae_test_m3": error_mae,
        "rmse_test_m3": error_rmse,
    }

    context = {
        "status": "ok",
        "message": "Contexte construit avec succès.",
        "signals": signals,
        "raw": {
            "nb_rows": int(len(df)),
            "start_date": str(df["date_mois"].min().date()),
            "end_date": str(df["date_mois"].max().date()),
        },
    }

    # Ajouter les résultats ML au contexte
    ml_results = load_ml_results()
    context["ml_results"] = ml_results

    return context
