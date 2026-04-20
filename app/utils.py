"""
Utilitaires partagés pour l'application Streamlit
===================================================
Fonctions de connexion DB, requêtes communes, formatage.
"""

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_URL


@st.cache_resource
def get_engine():
    """Crée une connexion SQLAlchemy (mise en cache par Streamlit)."""
    try:
        return create_engine(DB_URL)
    except Exception as exc:
        st.error(f"Erreur de configuration de la connexion DB : {exc}")
        raise


@st.cache_data(ttl=3600)
def charger_ventes_mensuelles() -> pd.DataFrame:
    """Charge les ventes mensuelles agrégées depuis la vue PostgreSQL."""
    try:
        engine = get_engine()
        query = """
        SELECT * FROM v_ventes_mensuelles_gasoil ORDER BY date_mois
        """
        df = pd.read_sql(query, engine)
        df['date_mois'] = pd.to_datetime(df['date_mois'])
        return df
    except (SQLAlchemyError, KeyError, ValueError) as exc:
        st.error(f"Impossible de charger les ventes mensuelles : {exc}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def charger_ventes_detail() -> pd.DataFrame:
    """Charge les ventes détaillées avec les infos de date."""
    try:
        engine = get_engine()
        query = """
        SELECT 
            d.date_complete, d.annee, d.mois, d.nom_mois, d.trimestre,
            f.quantite_m3, f.montant_ht, f.prix_unitaire,
            f.code_depot, f.num_compte
        FROM fact_ventes f
        JOIN dim_date d ON f.id_date = d.id_date
        JOIN dim_produit p ON f.id_produit = p.id_produit
        WHERE p.code_produit = 4
        ORDER BY d.date_complete
        """
        df = pd.read_sql(query, engine)
        df['date_complete'] = pd.to_datetime(df['date_complete'])
        return df
    except (SQLAlchemyError, KeyError, ValueError) as exc:
        st.error(f"Impossible de charger les ventes détaillées : {exc}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def charger_cours_brent() -> pd.DataFrame:
    """Charge les cours du Brent avec les dates."""
    try:
        engine = get_engine()
        query = """
        SELECT 
            d.date_complete, c.cours_brent_usd, c.variation_pct
        FROM dim_cours c
        JOIN dim_date d ON c.id_date = d.id_date
        ORDER BY d.date_complete
        """
        df = pd.read_sql(query, engine)
        df['date_complete'] = pd.to_datetime(df['date_complete'])
        return df
    except (SQLAlchemyError, KeyError, ValueError) as exc:
        st.error(f"Impossible de charger les cours Brent : {exc}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def charger_stats_globales() -> dict:
    """Calcule les KPIs globaux."""
    try:
        engine = get_engine()
        
        query = """
        SELECT
            COUNT(*) AS nb_livraisons,
            SUM(f.quantite_m3) AS total_quantite,
            SUM(f.montant_ht) AS total_montant,
            AVG(f.prix_unitaire) AS prix_moyen,
            MIN(d.date_complete) AS date_debut,
            MAX(d.date_complete) AS date_fin
        FROM fact_ventes f
        JOIN dim_date d ON f.id_date = d.id_date
        JOIN dim_produit p ON f.id_produit = p.id_produit
        WHERE p.code_produit = 4
        """
        
        row = pd.read_sql(query, engine).iloc[0]
        
        return {
            'nb_livraisons': int(row['nb_livraisons']),
            'total_quantite': float(row['total_quantite']),
            'total_montant': float(row['total_montant']),
            'prix_moyen': float(row['prix_moyen']),
            'date_debut': row['date_debut'],
            'date_fin': row['date_fin'],
        }
    except (SQLAlchemyError, KeyError, ValueError, IndexError) as exc:
        st.error(f"Impossible de calculer les statistiques globales : {exc}")
        return {
            'nb_livraisons': 0,
            'total_quantite': 0.0,
            'total_montant': 0.0,
            'prix_moyen': 0.0,
            'date_debut': None,
            'date_fin': None,
        }


def formater_nombre(n: float, decimales: int = 0) -> str:
    """Formate un nombre avec des espaces comme séparateur de milliers."""
    if decimales == 0:
        return f"{n:,.0f}".replace(",", " ")
    return f"{n:,.{decimales}f}".replace(",", " ")
