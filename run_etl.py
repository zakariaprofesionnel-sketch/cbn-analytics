"""
Pipeline ETL Complet - CBN Analytics
=====================================
Script principal qui orchestre les 3 phases ETL :
  1. EXTRACT  : Charger les données brutes (Excel + Yahoo Finance)
  2. TRANSFORM : Nettoyer, filtrer, enrichir
  3. LOAD      : Créer la base et charger dans PostgreSQL

Usage :
  python run_etl.py

Pré-requis :
  - PostgreSQL démarré en local (port 5432)
  - Fichier Excel dans data/raw/
  - Connexion internet pour Yahoo Finance (ou CSV de secours)
"""

import sys
import os
import time

# Ajouter les répertoires au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'etl'))

from config import *
from etl.extract import extract_ventes, extract_cours_brent
from etl.transform import (
    transform_ventes, transform_cours_brent,
    generer_dim_date, generer_dim_produit
)
from etl.load import (
    creer_base_si_inexistante, executer_schema,
    charger_dim_date, charger_dim_produit,
    charger_dim_cours, charger_fact_ventes,
    verifier_chargement
)


def run_pipeline():
    """Exécute le pipeline ETL complet."""
    
    debut = time.time()
    print("=" * 60)
    print("  PIPELINE ETL - CBN Analytics (SNDP)")
    print("=" * 60)
    
    # ────────────────────────────────────────
    # PHASE 1 : EXTRACT
    # ────────────────────────────────────────
    print("\n" + "─" * 40)
    print("  PHASE 1 : EXTRACT")
    print("─" * 40)
    
    df_ventes_brut = extract_ventes()
    df_brent_brut = extract_cours_brent()
    
    # ────────────────────────────────────────
    # PHASE 2 : TRANSFORM
    # ────────────────────────────────────────
    print("\n" + "─" * 40)
    print("  PHASE 2 : TRANSFORM")
    print("─" * 40)
    
    # Transformer les ventes (filtrer gasoil, nettoyer)
    df_gasoil = transform_ventes(df_ventes_brut)
    
    # Sauvegarder le CSV nettoyé (utile pour debug)
    os.makedirs(DATA_PROCESSED, exist_ok=True)
    df_gasoil.to_csv(FICHIER_GASOIL_CSV, index=False)
    print(f"[TRANSFORM] CSV nettoyé sauvegardé : {FICHIER_GASOIL_CSV}")
    
    # Transformer les cours Brent (forward-fill)
    df_brent = transform_cours_brent(df_brent_brut)
    
    # Générer les dimensions
    df_dim_date = generer_dim_date()
    df_dim_produit = generer_dim_produit(df_ventes_brut)
    
    # ────────────────────────────────────────
    # PHASE 3 : LOAD
    # ────────────────────────────────────────
    print("\n" + "─" * 40)
    print("  PHASE 3 : LOAD (PostgreSQL)")
    print("─" * 40)
    
    creer_base_si_inexistante()
    executer_schema()
    charger_dim_date(df_dim_date)
    charger_dim_produit(df_dim_produit)
    charger_dim_cours(df_brent)
    charger_fact_ventes(df_gasoil)
    
    # Vérification finale
    verifier_chargement()
    
    duree = time.time() - debut
    print(f"\n{'=' * 60}")
    print(f"  PIPELINE TERMINÉ EN {duree:.1f} SECONDES")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    run_pipeline()
