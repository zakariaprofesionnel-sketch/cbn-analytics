"""
Pipeline ML — CBN Analytics
=============================
Script qui entraîne le modèle Prophet et sauvegarde les résultats.

Usage :
  python run_ml.py

Pré-requis :
  - PostgreSQL démarré avec les données chargées (run_etl.py exécuté)
  - Prophet installé (pip install prophet)
"""

import sys
import os
import pickle
import time
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ml.forecast import (
    charger_donnees_mensuelles,
    preparer_donnees_prophet,
    entrainer_et_evaluer,
    entrainer_modele_final,
    prevoir,
)
from config import BASE_DIR


def run():
    debut = time.time()
    print("=" * 60)
    print("  PIPELINE ML — Prévision Gasoil (Prophet)")
    print("=" * 60)

    # 1. Charger les données mensuelles depuis PostgreSQL
    print("\n[1/5] Chargement des données mensuelles...")
    df = charger_donnees_mensuelles()
    print(f"       → {len(df)} mois chargés")

    # 2. Préparer pour Prophet
    print("\n[2/5] Préparation des données Prophet...")
    df_prophet = preparer_donnees_prophet(df)
    print(f"       → Colonnes : {list(df_prophet.columns)}")

    # 3. Entraîner et évaluer (train 2015-2017 / test 2018)
    print("\n[3/5] Entraînement et évaluation...")
    resultats = entrainer_et_evaluer(df_prophet)

    # Sauvegarder les métriques
    metrics_path = os.path.join(BASE_DIR, "ml", "metriques.pkl")
    with open(metrics_path, 'wb') as f:
        pickle.dump(resultats['metriques'], f)
    print(f"       Métriques sauvegardées : {metrics_path}")

    # Sauvegarder le comparatif réel vs prédit (période test)
    comparison_path = os.path.join(BASE_DIR, "ml", "predictions_test.csv")
    df_comparison = pd.DataFrame({
        "date_mois": pd.to_datetime(resultats["test"]["ds"]).dt.strftime("%Y-%m-%d"),
        "reel_m3": resultats["test"]["y"].values,
        "prediction_m3": resultats["forecast_test"]["yhat"].values,
        "borne_basse_m3": resultats["forecast_test"]["yhat_lower"].values,
        "borne_haute_m3": resultats["forecast_test"]["yhat_upper"].values,
    })
    df_comparison["erreur_m3"] = df_comparison["reel_m3"] - df_comparison["prediction_m3"]
    df_comparison["erreur_abs_m3"] = df_comparison["erreur_m3"].abs()
    df_comparison.to_csv(comparison_path, index=False)
    print(f"       Comparatif réel/prédit sauvegardé : {comparison_path}")

    # 4. Entraîner le modèle final sur toutes les données
    print("\n[4/5] Entraînement du modèle final (2015-2018)...")
    model_final = entrainer_modele_final(df_prophet)

    # 5. Test de prévision
    print("\n[5/5] Test de prévision (6 mois, 3 scénarios)...")
    dernier_cours = float(df['cours_brent_moyen_usd'].iloc[-1])
    print(f"       Dernier cours Brent : {dernier_cours:.2f} USD/baril")

    for scenario in ['stable', 'hausse', 'baisse']:
        forecast = prevoir(
            model_final,
            horizon_mois=6,
            scenario_cours=scenario,
            dernier_cours=dernier_cours,
        )
        total = forecast['yhat'].sum()
        borne_basse = forecast['yhat_lower'].sum()
        borne_haute = forecast['yhat_upper'].sum()
        print(f"       Scénario {scenario:>7s} : {total:>10,.0f} m³  "
              f"[{borne_basse:>10,.0f} — {borne_haute:>10,.0f}]")

    duree = time.time() - debut
    print(f"\n{'=' * 60}")
    print(f"  PIPELINE ML TERMINÉ EN {duree:.1f} SECONDES")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    run()
