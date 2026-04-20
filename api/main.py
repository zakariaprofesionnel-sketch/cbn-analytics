"""
CBN Analytics — FastAPI Backend
=================================
Pont entre le frontend React et la logique Python existante.

Endpoints :
  GET /api/ventes         → ventes mensuelles (PostgreSQL)
  GET /api/kpis           → KPIs globaux
  GET /api/forecast       → prévisions Prophet (?scenario=stable|hausse|baisse&horizon=6)
  GET /api/agent/context  → signaux de l'agent IA
  GET /api/agent/recs     → recommandations de l'agent IA

Démarrage :
  cd api
  uvicorn main:app --reload --port 8000
"""

import os
import sys
import pickle

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

# ─── Chemins ─────────────────────────────────────────────────────────────────
# api/ est un cran sous la racine du projet
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "app"))

from config import BASE_DIR                             # noqa: E402
from ml.forecast import (                               # noqa: E402
    charger_donnees_mensuelles,
    preparer_donnees_prophet,
    prevoir,
)
from app.agent.context import build_agent_context       # noqa: E402
from app.agent.rules import generate_recommendations    # noqa: E402

# ─── App ─────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="CBN Analytics API",
    description="API pour le dashboard React — SNDP Tunisie",
    version="1.0.0",
)

# Autoriser le serveur de développement React (ports 5173 et 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Chemins vers les artefacts ML
MODEL_PATH   = os.path.join(BASE_DIR, "ml", "prophet_model.pkl")
METRICS_PATH = os.path.join(BASE_DIR, "ml", "metriques.pkl")
PREDS_PATH   = os.path.join(BASE_DIR, "ml", "predictions_test.csv")


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _load_model():
    """Charge le modèle Prophet depuis le fichier .pkl."""
    if not os.path.exists(MODEL_PATH):
        raise HTTPException(
            status_code=503,
            detail="Modèle non entraîné. Lancez d'abord : python run_ml.py",
        )
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)


def _load_metrics() -> dict:
    """Charge les métriques ML depuis metriques.pkl."""
    if not os.path.exists(METRICS_PATH):
        return {}
    with open(METRICS_PATH, "rb") as f:
        return pickle.load(f)


# ─── Endpoints ───────────────────────────────────────────────────────────────

@app.get("/api/ventes")
def get_ventes():
    """
    Retourne les ventes mensuelles agrégées depuis la vue PostgreSQL.
    Colonnes : date_mois, total_quantite_m3, total_montant_ht,
               prix_unitaire_moyen, cours_brent_moyen_usd, nb_livraisons
    """
    df = charger_donnees_mensuelles()
    if df.empty:
        raise HTTPException(status_code=404, detail="Aucune donnée disponible.")
    df["date_mois"] = df["date_mois"].dt.strftime("%Y-%m-%d")
    return df.to_dict(orient="records")


@app.get("/api/kpis")
def get_kpis():
    """
    KPIs globaux : livraisons, volume total, montant HT, Brent moyen.
    """
    df = charger_donnees_mensuelles()
    if df.empty:
        raise HTTPException(status_code=404, detail="Aucune donnée disponible.")

    return {
        "nb_livraisons":    97_238,  # filtré sur gasoil (code_produit = 4)
        "total_quantite_m3": round(float(df["total_quantite_m3"].sum()), 0),
        "total_montant_tnd": round(float(df["total_montant_ht"].sum()), 0),
        "brent_moyen_usd":   round(float(df["cours_brent_moyen_usd"].mean()), 2),
        "date_debut": str(df["date_mois"].min().date()),
        "date_fin":   str(df["date_mois"].max().date()),
    }


@app.get("/api/forecast")
def get_forecast(
    scenario: str = Query(default="stable", description="stable | hausse | baisse"),
    horizon:  int  = Query(default=6,        description="Nombre de mois à prévoir"),
):
    """
    Prévisions Prophet pour un scénario de cours Brent donné.

    Retourne :
      - previsions    : liste de {date, prevision_m3, borne_basse, borne_haute, cours_brent}
      - historique    : prédictions sur la période de test 2018 (fichier CSV)
      - metriques     : MAE, RMSE, MAPE, R² sur le test 2018
    """
    if scenario not in ("stable", "hausse", "baisse"):
        raise HTTPException(
            status_code=400,
            detail="scenario doit être : stable, hausse ou baisse",
        )

    model = _load_model()
    df    = charger_donnees_mensuelles()
    dernier_cours = float(df["cours_brent_moyen_usd"].iloc[-1])

    # Générer les prévisions futures
    forecast = prevoir(
        model,
        horizon_mois=horizon,
        scenario_cours=scenario,
        dernier_cours=dernier_cours,
    )

    previsions = [
        {
            "date":         row["ds"].strftime("%Y-%m-%d"),
            "prevision_m3": round(float(row["yhat"]),       0),
            "borne_basse":  round(float(row["yhat_lower"]), 0),
            "borne_haute":  round(float(row["yhat_upper"]), 0),
            "cours_brent":  round(float(row["cours_brent"]), 2),
        }
        for _, row in forecast.iterrows()
    ]

    # Historique test (période 2018 — pour le graphique)
    historique = []
    if os.path.exists(PREDS_PATH):
        df_test = pd.read_csv(PREDS_PATH)
        historique = df_test.to_dict(orient="records")

    return {
        "scenario":   scenario,
        "previsions": previsions,
        "historique": historique,
        "metriques":  _load_metrics(),
    }


@app.get("/api/agent/context")
def get_agent_context():
    """
    Signaux détectés par l'agent : volume, Brent, tendance, erreur modèle.
    """
    ctx = build_agent_context()
    return ctx


@app.get("/api/agent/recs")
def get_agent_recs():
    """
    Recommandations générées par le moteur de règles (8 règles métier).
    """
    ctx  = build_agent_context()
    recs = generate_recommendations(ctx)
    return {
        "context":         ctx,
        "recommendations": recs,
    }


# ─── Health check ─────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "ok", "app": "CBN Analytics API v1.0"}
