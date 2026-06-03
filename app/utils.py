"""
Utilitaires partagés pour l'application Streamlit
===================================================
Fonctions de connexion DB, requêtes communes, formatage.
"""

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.pool import NullPool
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_URL


@st.cache_resource
def get_engine():
    """Crée une connexion SQLAlchemy avec gestion de pool désactivée pour Streamlit.
    
    NullPool évite les problèmes de transaction restante avec Streamlit.
    """
    try:
        # NullPool : chaque connexion est fermée immédiatement après utilisation
        return create_engine(
            DB_URL,
            poolclass=NullPool,
            echo=False,
        )
    except Exception as exc:
        st.error(f"Erreur de configuration de la connexion DB : {exc}")
        raise


def execute_query(query: str, engine=None):
    """Exécute une requête SQL de manière sûre avec gestion d'erreur.
    
    Args:
        query: Requête SQL à exécuter
        engine: Engine SQLAlchemy (obtient le default si None)
    
    Returns:
        DataFrame avec les résultats ou DataFrame vide en cas d'erreur
    """
    try:
        if engine is None:
            engine = get_engine()
        
        # Utiliser le context manager pour garantir la fermeture
        with engine.connect() as connection:
            # Forcer l'autocommit pour les requêtes SELECT
            if query.strip().upper().startswith('SELECT'):
                result = pd.read_sql(text(query), connection)
            else:
                result = pd.read_sql(text(query), connection)
        
        return result
    
    except OperationalError as e:
        if "invalid transaction" in str(e).lower():
            st.error(
                "⚠️ **Erreur de connexion BD** : Transaction invalide. "
                "Vérifiez que PostgreSQL est actif et la BD initialisée."
            )
        else:
            st.error(f"Erreur opérationnelle BD : {e}")
        return pd.DataFrame()
    
    except Exception as exc:
        st.error(f"Erreur lors de l'exécution de la requête : {exc}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def charger_ventes_mensuelles() -> pd.DataFrame:
    """Charge les ventes mensuelles agrégées depuis la vue PostgreSQL."""
    query = """
    SELECT * FROM v_ventes_mensuelles_gasoil ORDER BY date_mois
    """
    
    df = execute_query(query)
    
    if not df.empty:
        try:
            df['date_mois'] = pd.to_datetime(df['date_mois'])
        except (KeyError, ValueError) as e:
            st.error(f"Erreur lors du traitement des dates : {e}")
            return pd.DataFrame()
    
    return df


@st.cache_data(ttl=3600)
def charger_ventes_detail() -> pd.DataFrame:
    """Charge les ventes détaillées avec les infos de date."""
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
    
    df = execute_query(query)
    
    if not df.empty:
        try:
            df['date_complete'] = pd.to_datetime(df['date_complete'])
        except (KeyError, ValueError) as e:
            st.error(f"Erreur lors du traitement des dates : {e}")
            return pd.DataFrame()
    
    return df


@st.cache_data(ttl=3600)
def charger_cours_brent() -> pd.DataFrame:
    """Charge les cours du Brent avec les dates."""
    query = """
    SELECT 
        d.date_complete, c.cours_brent_usd, c.variation_pct
    FROM dim_cours c
    JOIN dim_date d ON c.id_date = d.id_date
    ORDER BY d.date_complete
    """
    
    df = execute_query(query)
    
    if not df.empty:
        try:
            df['date_complete'] = pd.to_datetime(df['date_complete'])
        except (KeyError, ValueError) as e:
            st.error(f"Erreur lors du traitement des dates : {e}")
            return pd.DataFrame()
    
    return df


@st.cache_data(ttl=3600)
def charger_stats_globales() -> dict:
    """Calcule les KPIs globaux."""
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
    
    try:
        df = execute_query(query)
        
        if df.empty or df.iloc[0]['nb_livraisons'] is None:
            return {
                'nb_livraisons': 0,
                'total_quantite': 0.0,
                'total_montant': 0.0,
                'prix_moyen': 0.0,
                'date_debut': None,
                'date_fin': None,
            }
        
        row = df.iloc[0]
        
        return {
            'nb_livraisons': int(row['nb_livraisons']) if row['nb_livraisons'] else 0,
            'total_quantite': float(row['total_quantite']) if row['total_quantite'] else 0.0,
            'total_montant': float(row['total_montant']) if row['total_montant'] else 0.0,
            'prix_moyen': float(row['prix_moyen']) if row['prix_moyen'] else 0.0,
            'date_debut': row['date_debut'],
            'date_fin': row['date_fin'],
        }
    except (KeyError, ValueError, IndexError) as exc:
        st.error(f"Erreur lors du calcul des statistiques : {exc}")
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
