"""
ETL - Phase EXTRACT
====================
Responsabilités :
1. Lire le fichier Excel des ventes brutes
2. Télécharger les cours du Brent via Yahoo Finance
3. Sauvegarder les données brutes extraites en CSV

Entrées  : fichier Excel ventes + API Yahoo Finance
Sorties  : DataFrames pandas prêts pour la transformation
"""

import pandas as pd
import sys
import os

# Ajouter le répertoire parent au path pour importer config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import *


def extract_ventes(chemin_fichier: str = FICHIER_VENTES_BRUT) -> pd.DataFrame:
    """
    Lit le fichier Excel des ventes de carburant.
    
    Étapes :
    - Chargement du fichier Excel
    - Renommage des colonnes pour clarté
    - Typage des dates
    
    Returns:
        DataFrame avec toutes les ventes (tous produits confondus)
    """
    print("[EXTRACT] Chargement du fichier ventes...")
    
    df = pd.read_excel(chemin_fichier)
    
    # Supprimer la colonne sans nom (index du fichier source)
    col_sans_nom = df.columns[0]  # Première colonne = '   '
    df = df.drop(columns=[col_sans_nom])
    
    # S'assurer que les dates sont bien au format datetime
    df['DATLIV'] = pd.to_datetime(df['DATLIV'])
    df['DATRET'] = pd.to_datetime(df['DATRET'])
    
    print(f"[EXTRACT] ✓ {len(df)} lignes chargées")
    print(f"[EXTRACT]   Produits : {df['LIBPRD1'].value_counts().to_dict()}")
    print(f"[EXTRACT]   Période : {df['DATLIV'].min().date()} → {df['DATLIV'].max().date()}")
    
    return df


def extract_cours_brent(
    date_debut: str = DATE_DEBUT,
    date_fin: str = DATE_FIN,
    ticker: str = BRENT_TICKER,
    chemin_fallback: str = FICHIER_BRENT_CSV
) -> pd.DataFrame:
    """
    Télécharge les cours du Brent depuis Yahoo Finance.
    En cas d'échec, tente de charger un CSV de secours.
    
    Le Brent (BZ=F) est la référence pour l'Afrique du Nord.
    Les données sont journalières (jours ouvrés boursiers uniquement).
    
    Returns:
        DataFrame avec colonnes : date, cours_brent_usd
    """
    print(f"[EXTRACT] Téléchargement cours Brent ({ticker})...")
    
    try:
        import yfinance as yf
        
        brent = yf.download(ticker, start=date_debut, end=date_fin, progress=False)
        
        if brent.empty:
            raise ValueError("Aucune donnée retournée par yfinance")
        
        # yfinance retourne un DataFrame avec MultiIndex si un seul ticker
        # On prend le cours de clôture (Close)
        if isinstance(brent.columns, pd.MultiIndex):
            brent = brent.droplevel('Ticker', axis=1)
        
        df_brent = pd.DataFrame({
            'date': brent.index,
            'cours_brent_usd': brent['Close'].values
        })
        df_brent['date'] = pd.to_datetime(df_brent['date']).dt.tz_localize(None)
        df_brent = df_brent.dropna(subset=['cours_brent_usd'])
        
        print(f"[EXTRACT] ✓ {len(df_brent)} jours de cours Brent téléchargés")
        print(f"[EXTRACT]   Cours moyen : {df_brent['cours_brent_usd'].mean():.2f} USD/baril")
        
        # Sauvegarder en CSV de secours pour les prochaines exécutions
        os.makedirs(os.path.dirname(chemin_fallback), exist_ok=True)
        df_brent.to_csv(chemin_fallback, index=False)
        print(f"[EXTRACT]   Sauvegardé en CSV de secours : {chemin_fallback}")
        
        return df_brent
        
    except Exception as e:
        print(f"[EXTRACT] ⚠ Échec yfinance : {e}")
        
        # Tentative de chargement du CSV de secours
        if os.path.exists(chemin_fallback):
            print(f"[EXTRACT] Chargement du CSV de secours...")
            df_brent = pd.read_csv(chemin_fallback, parse_dates=['date'])
            print(f"[EXTRACT] ✓ {len(df_brent)} jours chargés depuis le CSV")
            return df_brent
        else:
            print("[EXTRACT] ✗ Aucun CSV de secours disponible.")
            print("[EXTRACT]   → Télécharger manuellement depuis investing.com")
            raise


if __name__ == "__main__":
    # Test standalone
    df_ventes = extract_ventes()
    print()
    df_brent = extract_cours_brent()
