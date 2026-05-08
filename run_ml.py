"""Pipeline ML - comparaison Prophet vs SARIMAX.

Usage:
  python run_ml.py
"""

import json
import os
import pickle
import sys
import time

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import BASE_DIR, TEST_YEAR, TRAIN_END_YEAR
from ml.arima_forecast import entrainer_et_evaluer_sarimax, entrainer_modele_final_sarimax
from ml.forecast import (
    charger_donnees_mensuelles,
    entrainer_et_evaluer,
    entrainer_modele_final,
    preparer_donnees_prophet,
    prevoir,
)


def _comparison_row(model_name: str, metrics: dict) -> dict:
    return {
        "modele": model_name,
        "MAE": metrics["MAE"],
        "RMSE": metrics["RMSE"],
        "MAPE": metrics["MAPE"],
        "R2": metrics["R2"],
    }


def _choose_best(comparison: pd.DataFrame) -> str:
    ranked = comparison.sort_values(["MAPE", "RMSE", "MAE"], ascending=True)
    return str(ranked.iloc[0]["modele"])


def run():
    debut = time.time()
    ml_dir = os.path.join(BASE_DIR, "ml")

    print("=" * 72)
    print("  PIPELINE ML - Comparaison Prophet vs SARIMAX")
    print("=" * 72)
    print(f"  Train : 2015-{TRAIN_END_YEAR}")
    print(f"  Test  : {TEST_YEAR}")

    print("\n[1/6] Chargement des donnees mensuelles...")
    df = charger_donnees_mensuelles()
    print(f"       {len(df)} mois charges")

    print("\n[2/6] Evaluation Prophet...")
    df_prophet = preparer_donnees_prophet(df)
    resultats_prophet = entrainer_et_evaluer(df_prophet)

    print("\n[3/6] Evaluation SARIMAX...")
    resultats_sarimax = entrainer_et_evaluer_sarimax(df)

    print("\n[4/6] Comparaison des modeles...")
    comparison = pd.DataFrame(
        [
            _comparison_row("Prophet", resultats_prophet["metriques"]),
            _comparison_row("SARIMAX", resultats_sarimax["metriques"]),
        ]
    )
    best_model = _choose_best(comparison)
    print(comparison.to_string(index=False))
    print(f"       Modele retenu : {best_model}")

    comparison_path = os.path.join(ml_dir, "model_comparison.csv")
    comparison.to_csv(comparison_path, index=False)
    print(f"       Comparaison sauvegardee : {comparison_path}")

    best_model_path = os.path.join(ml_dir, "best_model.json")
    with open(best_model_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "best_model": best_model,
                "train_period": f"2015-{TRAIN_END_YEAR}",
                "test_year": TEST_YEAR,
                "final_train_period": "2015-2017",
                "forecast_start_year": 2018,
                "selection_rule": "MAPE puis RMSE puis MAE les plus faibles",
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    print(f"       Choix du modele sauvegarde : {best_model_path}")

    metrics_path = os.path.join(ml_dir, "metriques.pkl")
    metrics_payload = {
        "best_model": best_model,
        "Prophet": resultats_prophet["metriques"],
        "SARIMAX": resultats_sarimax["metriques"],
    }
    with open(metrics_path, "wb") as f:
        pickle.dump(metrics_payload, f)
    print(f"       Metriques sauvegardees : {metrics_path}")

    predictions_path = os.path.join(ml_dir, "predictions_test.csv")
    df_predictions = pd.DataFrame(
        {
            "date_mois": pd.to_datetime(resultats_prophet["test"]["ds"]).dt.strftime("%Y-%m-%d"),
            "reel_m3": resultats_prophet["test"]["y"].values,
            "prophet_prediction_m3": resultats_prophet["forecast_test"]["yhat"].values,
            "sarimax_prediction_m3": resultats_sarimax["forecast_test"]["yhat"].values,
        }
    )
    df_predictions["prophet_erreur_abs_m3"] = (
        df_predictions["reel_m3"] - df_predictions["prophet_prediction_m3"]
    ).abs()
    df_predictions["sarimax_erreur_abs_m3"] = (
        df_predictions["reel_m3"] - df_predictions["sarimax_prediction_m3"]
    ).abs()
    df_predictions.to_csv(predictions_path, index=False)
    print(f"       Predictions test sauvegardees : {predictions_path}")

    print("\n[5/6] Entrainement des modeles finaux sur 2015-2017...")
    prophet_final = entrainer_modele_final(df_prophet, end_year=TEST_YEAR)
    entrainer_modele_final_sarimax(df, end_year=TEST_YEAR)

    print("\n[6/6] Test prevision Prophet (6 mois, scenarios Brent)...")
    df_cours_final = df[pd.to_datetime(df["date_mois"]).dt.year <= TEST_YEAR]
    dernier_cours = float(df_cours_final["cours_brent_moyen_usd"].iloc[-1])
    for scenario in ["stable", "hausse", "baisse"]:
        forecast = prevoir(
            prophet_final,
            horizon_mois=6,
            scenario_cours=scenario,
            dernier_cours=dernier_cours,
        )
        print(f"       {scenario:>7s} : {forecast['yhat'].sum():>10,.0f} m3")

    duree = time.time() - debut
    print(f"\n{'=' * 72}")
    print(f"  PIPELINE ML TERMINE EN {duree:.1f} SECONDES")
    print(f"{'=' * 72}")


if __name__ == "__main__":
    run()
