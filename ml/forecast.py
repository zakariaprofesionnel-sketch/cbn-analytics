"""
Module ML - Prévision des ventes de gasoil
=============================================
Utilise Facebook Prophet pour prévoir les ventes mensuelles de gasoil.

Pourquoi Prophet ?
- Conçu pour les séries temporelles métier (tendance + saisonnalité)
- API simple : fit() → predict()
- Gère les données manquantes et les jours fériés
- Produit automatiquement des intervalles de confiance
- Permet d'ajouter des régresseurs externes (cours du pétrole)

Architecture du modèle :
  y(t) = tendance(t) + saisonnalité(t) + régresseurs(t) + erreur(t)

Pipeline :
  1. Charger les ventes mensuelles depuis PostgreSQL
  2. Entraîner sur 2015-2016, tester sur 2017
  3. Évaluer (MAE, RMSE, MAPE, R²)
  4. Ré-entraîner sur 2015-2017 pour prévoir 2018
  5. Prévoir N mois avec scénarios de cours pétrole
"""

import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sqlalchemy import create_engine
import warnings
import sys
import os
import pickle

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import *

warnings.filterwarnings('ignore')

# Chemin pour sauvegarder le modèle entraîné
MODEL_PATH = os.path.join(BASE_DIR, "ml", "prophet_model.pkl")


def charger_donnees_mensuelles() -> pd.DataFrame:
    """
    Charge les ventes mensuelles agrégées depuis la vue PostgreSQL.
    Retourne un DataFrame avec colonnes : date_mois, total_quantite_m3, cours_brent_moyen_usd
    """
    engine = create_engine(DB_URL)
    
    query = """
    SELECT 
        date_mois,
        total_quantite_m3,
        total_montant_ht,
        prix_unitaire_moyen,
        cours_brent_moyen_usd,
        nb_livraisons
    FROM v_ventes_mensuelles_gasoil
    ORDER BY date_mois
    """
    
    df = pd.read_sql(query, engine)
    df['date_mois'] = pd.to_datetime(df['date_mois'])
    engine.dispose()
    
    return df


def preparer_donnees_prophet(df: pd.DataFrame) -> pd.DataFrame:
    """
    Formate les données pour Prophet.
    Prophet exige : 'ds' (date) et 'y' (valeur à prédire).
    On ajoute 'cours_brent' comme régresseur externe.
    """
    df_prophet = pd.DataFrame({
        'ds': df['date_mois'],
        'y': df['total_quantite_m3'].astype(float),
        'cours_brent': df['cours_brent_moyen_usd'].astype(float),
    })
    
    return df_prophet


def entrainer_et_evaluer(df_prophet: pd.DataFrame) -> dict:
    """
    Entraîne Prophet sur 2015-2016 et évalue sur 2017.
    
    Returns:
        dict avec : modèle, métriques, prévisions test, composantes
    """
    print("[ML] Entraînement du modèle Prophet...")
    
    # Split train/test
    train = df_prophet[df_prophet['ds'].dt.year <= TRAIN_END_YEAR].copy()
    test = df_prophet[df_prophet['ds'].dt.year == TEST_YEAR].copy()
    
    print(f"[ML]   Train : {len(train)} mois (2015-{TRAIN_END_YEAR})")
    print(f"[ML]   Test  : {len(test)} mois ({TEST_YEAR})")
    
    # Configurer Prophet
    model = Prophet(
        yearly_seasonality=True,    # Saisonnalité annuelle (été vs hiver)
        weekly_seasonality=False,   # Pas pertinent en mensuel
        daily_seasonality=False,    # Pas pertinent en mensuel
        seasonality_mode='multiplicative',  # La saisonnalité est proportionnelle
        changepoint_prior_scale=0.05,       # Flexibilité de la tendance
        interval_width=0.95,                # Intervalle de confiance à 95%
    )
    
    # Ajouter le cours du Brent comme régresseur
    model.add_regressor('cours_brent', mode='multiplicative')
    
    # Entraîner
    model.fit(train)
    
    # Prédire sur la période test
    future_test = test[['ds', 'cours_brent']].copy()
    forecast_test = model.predict(future_test)
    
    # Calculer les métriques
    y_true = test['y'].values
    y_pred = forecast_test['yhat'].values
    
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    r2 = r2_score(y_true, y_pred)
    
    metriques = {
        'MAE': round(mae, 2),
        'RMSE': round(rmse, 2),
        'MAPE': round(mape, 2),
        'R2': round(r2, 4),
    }
    
    print(f"[ML] Metriques Prophet sur {TEST_YEAR} :")
    print(f"[ML]   MAE  = {metriques['MAE']:.2f} m3 (erreur absolue moyenne)")
    print(f"[ML]   RMSE = {metriques['RMSE']:.2f} m3 (erreur quadratique)")
    print(f"[ML]   MAPE = {metriques['MAPE']:.2f}% (erreur % moyenne)")
    print(f"[ML]   R2   = {metriques['R2']:.4f} (qualite d'ajustement)")
    
    return {
        'model': model,
        'metriques': metriques,
        'forecast_test': forecast_test,
        'train': train,
        'test': test,
    }


def entrainer_modele_final(df_prophet: pd.DataFrame, end_year: int = 2017) -> Prophet:
    """
    Re-entraine le modele sur les donnees disponibles jusqu'a end_year.
    """
    print(f"[ML] Entrainement du modele final Prophet (2015-{end_year})...")
    
    df_train = df_prophet[df_prophet["ds"].dt.year <= end_year].copy()

    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        seasonality_mode='multiplicative',
        changepoint_prior_scale=0.05,
        interval_width=0.95,
    )
    model.add_regressor('cours_brent', mode='multiplicative')
    model.fit(df_train)
    
    # Sauvegarder le modèle
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)
    print(f"[ML] Modele Prophet sauvegarde : {MODEL_PATH}")
    
    return model


def prevoir(
    model: Prophet,
    horizon_mois: int = HORIZON_DEFAUT,
    scenario_cours: str = 'stable',
    dernier_cours: float = None,
) -> pd.DataFrame:
    """
    Génère les prévisions futures.
    
    Scénarios de cours du pétrole :
    - 'stable'  : le dernier cours connu est maintenu
    - 'hausse'  : +20% progressif sur l'horizon
    - 'baisse'  : -20% progressif sur l'horizon
    
    Args:
        model: modèle Prophet entraîné
        horizon_mois: nombre de mois à prévoir
        scenario_cours: 'stable', 'hausse', ou 'baisse'
        dernier_cours: dernier cours Brent connu (USD/baril)
    
    Returns:
        DataFrame avec colonnes : ds, yhat, yhat_lower, yhat_upper, cours_brent
    """
    if dernier_cours is None:
        # Charger le dernier cours depuis la DB
        engine = create_engine(DB_URL)
        dernier_cours = pd.read_sql(
            "SELECT cours_brent_usd FROM dim_cours ORDER BY id_date DESC LIMIT 1",
            engine
        ).iloc[0, 0]
        engine.dispose()
    
    # Generer les dates futures juste apres la derniere date vue par le modele.
    try:
        derniere_date = pd.to_datetime(model.history["ds"]).max()
    except (AttributeError, KeyError):
        derniere_date = pd.Timestamp(DATE_FIN)
    dates_futures = pd.date_range(
        start=derniere_date + pd.offsets.MonthBegin(1),
        periods=horizon_mois,
        freq='MS'
    )
    
    # Appliquer le scénario de cours
    facteurs = {
        'stable': np.ones(horizon_mois),
        'hausse': np.linspace(1.0, 1.20, horizon_mois),
        'baisse': np.linspace(1.0, 0.80, horizon_mois),
    }
    
    cours_scenario = float(dernier_cours) * facteurs.get(scenario_cours, facteurs['stable'])
    
    future = pd.DataFrame({
        'ds': dates_futures,
        'cours_brent': cours_scenario,
    })
    
    forecast = model.predict(future)
    forecast['cours_brent'] = cours_scenario
    forecast['scenario'] = scenario_cours
    
    return forecast


def charger_modele() -> Prophet:
    """Charge le modèle Prophet sauvegardé."""
    with open(MODEL_PATH, 'rb') as f:
        return pickle.load(f)


def run_ml_pipeline():
    """Exécute le pipeline ML complet."""
    print("=" * 60)
    print("  PIPELINE ML - Prévision Gasoil")
    print("=" * 60)
    
    # 1. Charger les données
    df = charger_donnees_mensuelles()
    print(f"\n[ML] Données chargées : {len(df)} mois")
    
    # 2. Préparer pour Prophet
    df_prophet = preparer_donnees_prophet(df)
    
    # 3. Entraîner et évaluer (train/test split)
    resultats = entrainer_et_evaluer(df_prophet)
    
    # 4. Entraîner le modèle final
    model_final = entrainer_modele_final(df_prophet)
    
    # 5. Test de prévision (3 scénarios)
    print("\n[ML] === PRÉVISIONS TEST (6 mois, 3 scénarios) ===")
    for scenario in ['stable', 'hausse', 'baisse']:
        forecast = prevoir(model_final, horizon_mois=6, scenario_cours=scenario)
        total = forecast['yhat'].sum()
        print(f"[ML]   Scénario {scenario:>7s} : {total:,.0f} m³ sur 6 mois")
    
    print("\n[ML] ✓ Pipeline ML terminé")
    return resultats, model_final


if __name__ == "__main__":
    run_ml_pipeline()
