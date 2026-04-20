"""
Page 4 : Exploration des Données
==================================
Accès détaillé aux données du warehouse :
- Tableau interactif filtrable
- Distribution des quantités
- Décomposition saisonnière (composantes Prophet)
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import pickle
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils import charger_ventes_mensuelles, charger_ventes_detail, formater_nombre
from config import BASE_DIR

st.set_page_config(page_title="Exploration", page_icon="🔍", layout="wide")
st.title("🔍 Exploration des Données")

# ─────────────────────────────────────────────
# FILTRES
# ─────────────────────────────────────────────
st.sidebar.header("🔎 Filtres")
df_detail = charger_ventes_detail()
if df_detail.empty:
    st.error("⚠️ Aucune donnée détaillée disponible depuis la base. Exécutez d'abord `python run_etl.py`.")
    st.stop()

annees = sorted(df_detail['annee'].unique())
annees_select = st.sidebar.multiselect("Années", annees, default=annees)

trimestres = st.sidebar.multiselect(
    "Trimestres", [1, 2, 3, 4], default=[1, 2, 3, 4],
    format_func=lambda x: f"T{x}"
)

df_filtre = df_detail[
    (df_detail['annee'].isin(annees_select)) &
    (df_detail['trimestre'].isin(trimestres))
]

if df_filtre.empty:
    st.warning("Aucune donnée pour cette sélection.")
    st.stop()

# ─────────────────────────────────────────────
# STATISTIQUES DESCRIPTIVES
# ─────────────────────────────────────────────
st.markdown("### Statistiques descriptives")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Quantité livrée (m³)**")
    stats_qte = df_filtre['quantite_m3'].describe()
    st.dataframe(pd.DataFrame({
        'Statistique': ['Nombre', 'Moyenne', 'Écart-type', 'Min', '25%', 'Médiane', '75%', 'Max'],
        'Valeur': [
            formater_nombre(stats_qte['count']),
            f"{stats_qte['mean']:.2f}",
            f"{stats_qte['std']:.2f}",
            f"{stats_qte['min']:.2f}",
            f"{stats_qte['25%']:.2f}",
            f"{stats_qte['50%']:.2f}",
            f"{stats_qte['75%']:.2f}",
            f"{stats_qte['max']:.2f}",
        ]
    }), hide_index=True)

with col2:
    st.markdown("**Montant HT (TND)**")
    stats_mnt = df_filtre['montant_ht'].describe()
    st.dataframe(pd.DataFrame({
        'Statistique': ['Nombre', 'Moyenne', 'Écart-type', 'Min', '25%', 'Médiane', '75%', 'Max'],
        'Valeur': [
            formater_nombre(stats_mnt['count']),
            formater_nombre(stats_mnt['mean'], 2),
            formater_nombre(stats_mnt['std'], 2),
            formater_nombre(stats_mnt['min'], 2),
            formater_nombre(stats_mnt['25%'], 2),
            formater_nombre(stats_mnt['50%'], 2),
            formater_nombre(stats_mnt['75%'], 2),
            formater_nombre(stats_mnt['max'], 2),
        ]
    }), hide_index=True)

st.markdown("---")

# ─────────────────────────────────────────────
# DISTRIBUTION DES QUANTITÉS
# ─────────────────────────────────────────────
st.markdown("### Distribution des quantités livrées")

col1, col2 = st.columns(2)

with col1:
    fig_hist = px.histogram(
        df_filtre,
        x='quantite_m3',
        nbins=50,
        title="Histogramme des quantités (m³)",
        labels={'quantite_m3': 'Quantité (m³)', 'count': 'Fréquence'},
        color_discrete_sequence=['#2196F3'],
    )
    st.plotly_chart(fig_hist, use_container_width=True)

with col2:
    fig_box = px.box(
        df_filtre,
        x='annee',
        y='quantite_m3',
        title="Box plot des quantités par année",
        labels={'annee': 'Année', 'quantite_m3': 'Quantité (m³)'},
        color='annee',
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_box.update_layout(showlegend=False, xaxis_type='category')
    st.plotly_chart(fig_box, use_container_width=True)

# ─────────────────────────────────────────────
# DÉCOMPOSITION SAISONNIÈRE
# ─────────────────────────────────────────────
st.markdown("### Décomposition saisonnière (Prophet)")

MODEL_PATH = os.path.join(BASE_DIR, "ml", "prophet_model.pkl")

if os.path.exists(MODEL_PATH):
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    
    df_mensuel = charger_ventes_mensuelles()
    df_prophet = pd.DataFrame({
        'ds': df_mensuel['date_mois'],
        'y': df_mensuel['total_quantite_m3'].astype(float),
        'cours_brent': df_mensuel['cours_brent_moyen_usd'].astype(float),
    })
    
    forecast = model.predict(df_prophet)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Tendance
        fig_trend = px.line(
            forecast, x='ds', y='trend',
            title="Composante : Tendance",
            labels={'ds': '', 'trend': 'Tendance (m³)'},
        )
        fig_trend.update_traces(line_color='#4CAF50')
        st.plotly_chart(fig_trend, use_container_width=True)
    
    with col2:
        # Saisonnalité annuelle
        if 'yearly' in forecast.columns:
            fig_yearly = px.line(
                forecast, x='ds', y='yearly',
                title="Composante : Saisonnalité annuelle",
                labels={'ds': '', 'yearly': 'Effet saisonnier'},
            )
            fig_yearly.update_traces(line_color='#FF9800')
            st.plotly_chart(fig_yearly, use_container_width=True)
else:
    st.info("La décomposition sera disponible après l'entraînement du modèle (`python run_ml.py`).")

# ─────────────────────────────────────────────
# TABLEAU INTERACTIF
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("### Données brutes (échantillon)")

nb_lignes = st.slider("Nombre de lignes à afficher", 10, 500, 100)

df_affiche = df_filtre[[
    'date_complete', 'annee', 'nom_mois', 'trimestre',
    'quantite_m3', 'montant_ht', 'prix_unitaire'
]].head(nb_lignes).rename(columns={
    'date_complete': 'Date',
    'annee': 'Année',
    'nom_mois': 'Mois',
    'trimestre': 'Trimestre',
    'quantite_m3': 'Quantité (m³)',
    'montant_ht': 'Montant HT (TND)',
    'prix_unitaire': 'Prix unitaire (TND/m³)',
})

st.dataframe(df_affiche, use_container_width=True, hide_index=True)
st.caption(f"Affichage de {min(nb_lignes, len(df_filtre))} lignes sur {formater_nombre(len(df_filtre))} au total")
