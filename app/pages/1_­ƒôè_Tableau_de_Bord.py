"""
Page 1 : Tableau de Bord — KPIs Synthétiques
==============================================
Affiche les indicateurs clés des ventes de gasoil :
- Volume total vendu
- Montant HT total
- Prix unitaire moyen
- Nombre de livraisons
- Évolution annuelle comparative
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils import (
    charger_ventes_mensuelles, charger_stats_globales,
    charger_ventes_detail, formater_nombre
)

st.set_page_config(page_title="Tableau de Bord", page_icon="📊", layout="wide")
st.title("📊 Tableau de Bord — Ventes Gasoil")

# ─────────────────────────────────────────────
# FILTRES (sidebar)
# ─────────────────────────────────────────────
st.sidebar.header("🔎 Filtres")
df_mensuel = charger_ventes_mensuelles()
if df_mensuel.empty:
    st.error("⚠️ Aucune donnée disponible depuis la base. Exécutez d'abord `python run_etl.py`.")
    st.stop()
annees_dispo = sorted(df_mensuel['annee'].unique())
annees_select = st.sidebar.multiselect(
    "Années",
    options=annees_dispo,
    default=annees_dispo
)

# Filtrer les données
df_filtre = df_mensuel[df_mensuel['annee'].isin(annees_select)]

if df_filtre.empty:
    st.warning("Aucune donnée pour la sélection. Modifiez les filtres.")
    st.stop()

# ─────────────────────────────────────────────
# KPIs PRINCIPAUX
# ─────────────────────────────────────────────
st.markdown("### Indicateurs clés")

total_qte = df_filtre['total_quantite_m3'].sum()
total_mnt = df_filtre['total_montant_ht'].sum()
prix_moyen = df_filtre['prix_unitaire_moyen'].mean()
nb_livraisons = df_filtre['nb_livraisons'].sum()
nb_mois = len(df_filtre)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Volume total (m³)",
        value=formater_nombre(total_qte),
    )
with col2:
    st.metric(
        label="Chiffre d'affaires HT (TND)",
        value=formater_nombre(total_mnt),
    )
with col3:
    st.metric(
        label="Prix moyen (TND/m³)",
        value=formater_nombre(prix_moyen, 2),
    )
with col4:
    st.metric(
        label="Nb livraisons",
        value=formater_nombre(nb_livraisons),
    )

st.markdown("---")

# ─────────────────────────────────────────────
# ÉVOLUTION MENSUELLE DES VENTES
# ─────────────────────────────────────────────
st.markdown("### Évolution mensuelle des ventes")

fig_ventes = px.line(
    df_filtre,
    x='date_mois',
    y='total_quantite_m3',
    title="Volume de gasoil vendu par mois (m³)",
    labels={'date_mois': 'Date', 'total_quantite_m3': 'Quantité (m³)'},
    markers=True,
)
fig_ventes.update_layout(
    hovermode='x unified',
    xaxis_title="",
    yaxis_title="Quantité (m³)",
)
st.plotly_chart(fig_ventes, use_container_width=True)

# ─────────────────────────────────────────────
# COMPARAISON ANNUELLE
# ─────────────────────────────────────────────
st.markdown("### Comparaison annuelle")

col1, col2 = st.columns(2)

with col1:
    # Volume par année
    df_annuel = df_filtre.groupby('annee').agg(
        total_quantite=('total_quantite_m3', 'sum'),
        total_montant=('total_montant_ht', 'sum'),
    ).reset_index()
    
    fig_bar = px.bar(
        df_annuel,
        x='annee',
        y='total_quantite',
        title="Volume annuel (m³)",
        labels={'annee': 'Année', 'total_quantite': 'Quantité (m³)'},
        text_auto='.3s',
        color='annee',
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_bar.update_layout(showlegend=False, xaxis_type='category')
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    # CA par année
    fig_ca = px.bar(
        df_annuel,
        x='annee',
        y='total_montant',
        title="Chiffre d'affaires annuel HT (TND)",
        labels={'annee': 'Année', 'total_montant': 'Montant HT (TND)'},
        text_auto='.3s',
        color='annee',
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    fig_ca.update_layout(showlegend=False, xaxis_type='category')
    st.plotly_chart(fig_ca, use_container_width=True)

# ─────────────────────────────────────────────
# SAISONNALITÉ
# ─────────────────────────────────────────────
st.markdown("### Saisonnalité mensuelle")

df_saison = df_filtre.groupby('mois')['total_quantite_m3'].mean().reset_index()
noms_mois = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin',
             'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
df_saison['nom_mois'] = [noms_mois[m-1] for m in df_saison['mois']]

fig_saison = px.bar(
    df_saison,
    x='nom_mois',
    y='total_quantite_m3',
    title="Volume moyen par mois (toutes années confondues)",
    labels={'nom_mois': 'Mois', 'total_quantite_m3': 'Quantité moyenne (m³)'},
    color='total_quantite_m3',
    color_continuous_scale='YlOrRd',
)
fig_saison.update_layout(xaxis_type='category')
st.plotly_chart(fig_saison, use_container_width=True)
