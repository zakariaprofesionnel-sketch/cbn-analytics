"""
Page 2 : Analyse Historique — Ventes vs Cours du Brent
========================================================
Visualise la relation entre les ventes de gasoil et le cours du pétrole :
- Courbes superposées (double axe Y)
- Corrélation de Pearson
- Scatter plot avec ligne de tendance
- Analyse par trimestre
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from scipy import stats
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils import charger_ventes_mensuelles, formater_nombre

st.set_page_config(page_title="Analyse Historique", page_icon="📈", layout="wide")
st.title("📈 Analyse Historique — Ventes vs Cours du Brent")

# ─────────────────────────────────────────────
# CHARGER LES DONNÉES
# ─────────────────────────────────────────────
df = charger_ventes_mensuelles()
if df.empty:
    st.error("⚠️ Aucune donnée disponible depuis la base. Exécutez d'abord `python run_etl.py`.")
    st.stop()

# Filtres
st.sidebar.header("🔎 Filtres")
date_min = df['date_mois'].min().date()
date_max = df['date_mois'].max().date()
plage = st.sidebar.date_input(
    "Plage de dates",
    value=(date_min, date_max),
    min_value=date_min,
    max_value=date_max,
)
if len(plage) == 2:
    df = df[(df['date_mois'].dt.date >= plage[0]) & (df['date_mois'].dt.date <= plage[1])]

if df.empty:
    st.warning("Aucune donnée pour cette plage de dates.")
    st.stop()

# ─────────────────────────────────────────────
# COURBES SUPERPOSÉES (DOUBLE AXE Y)
# ─────────────────────────────────────────────
st.markdown("### Ventes de gasoil vs Cours du Brent")

fig_dual = go.Figure()

# Axe Y gauche : ventes
fig_dual.add_trace(go.Scatter(
    x=df['date_mois'],
    y=df['total_quantite_m3'],
    name='Ventes gasoil (m³)',
    line=dict(color='#2196F3', width=2.5),
    mode='lines+markers',
    yaxis='y1',
))

# Axe Y droit : cours Brent
fig_dual.add_trace(go.Scatter(
    x=df['date_mois'],
    y=df['cours_brent_moyen_usd'],
    name='Cours Brent (USD/baril)',
    line=dict(color='#FF9800', width=2.5, dash='dash'),
    mode='lines+markers',
    yaxis='y2',
))

fig_dual.update_layout(
    title="Évolution comparée : Ventes de gasoil et Cours du Brent",
    xaxis=dict(title=''),
    yaxis=dict(
        title=dict(
            text='Quantité vendue (m³)',
            font=dict(color='#2196F3'),
        ),
        tickfont=dict(color='#2196F3'),
    ),
    yaxis2=dict(
        title=dict(
            text='Cours Brent (USD/baril)',
            font=dict(color='#FF9800'),
        ),
        tickfont=dict(color='#FF9800'),
        overlaying='y',
        side='right',
    ),
    hovermode='x unified',
    legend=dict(orientation='h', yanchor='bottom', y=1.02),
    height=500,
)

st.plotly_chart(fig_dual, use_container_width=True)

# ─────────────────────────────────────────────
# CORRÉLATION DE PEARSON
# ─────────────────────────────────────────────
st.markdown("### Corrélation statistique")

# Supprimer les NaN pour le calcul
df_corr = df.dropna(subset=['total_quantite_m3', 'cours_brent_moyen_usd'])

if len(df_corr) > 2:
    pearson_r, p_value = stats.pearsonr(
        df_corr['total_quantite_m3'],
        df_corr['cours_brent_moyen_usd']
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Coefficient de Pearson (r)", f"{pearson_r:.4f}")
    with col2:
        st.metric("p-value", f"{p_value:.6f}")
    with col3:
        # Interpréter la corrélation
        if abs(pearson_r) < 0.3:
            interpretation = "Faible"
        elif abs(pearson_r) < 0.7:
            interpretation = "Modérée"
        else:
            interpretation = "Forte"
        direction = "positive" if pearson_r > 0 else "négative"
        st.metric("Interprétation", f"{interpretation} ({direction})")
    
    # ─────────────────────────────────────────
    # SCATTER PLOT
    # ─────────────────────────────────────────
    st.markdown("### Nuage de points — Ventes vs Cours")
    
    scatter_common = dict(
        data_frame=df_corr,
        x='cours_brent_moyen_usd',
        y='total_quantite_m3',
        color='annee',
        size='nb_livraisons',
        hover_data=['nom_mois', 'annee'],
        title="Relation entre le cours du Brent et les ventes de gasoil",
        labels={
            'cours_brent_moyen_usd': 'Cours Brent moyen (USD/baril)',
            'total_quantite_m3': 'Ventes mensuelles (m³)',
            'annee': 'Année',
        },
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    try:
        fig_scatter = px.scatter(**scatter_common, trendline='ols')
    except ModuleNotFoundError:
        st.info("`statsmodels` non installé : affichage du nuage sans droite de tendance.")
        fig_scatter = px.scatter(**scatter_common)
    fig_scatter.update_layout(height=500)
    st.plotly_chart(fig_scatter, use_container_width=True)

# ─────────────────────────────────────────────
# ANALYSE TRIMESTRIELLE
# ─────────────────────────────────────────────
st.markdown("### Analyse trimestrielle")

df_trim = df.copy()
df_trim['trimestre_label'] = df_trim['annee'].astype(str) + '-T' + df_trim['trimestre'].astype(str)
df_trim_agg = df_trim.groupby(['annee', 'trimestre', 'trimestre_label']).agg(
    ventes=('total_quantite_m3', 'sum'),
    cours_moyen=('cours_brent_moyen_usd', 'mean'),
).reset_index()

fig_trim = go.Figure()

fig_trim.add_trace(go.Bar(
    x=df_trim_agg['trimestre_label'],
    y=df_trim_agg['ventes'],
    name='Ventes (m³)',
    marker_color='#2196F3',
    yaxis='y1',
))

fig_trim.add_trace(go.Scatter(
    x=df_trim_agg['trimestre_label'],
    y=df_trim_agg['cours_moyen'],
    name='Cours Brent (USD)',
    line=dict(color='#FF9800', width=3),
    mode='lines+markers',
    yaxis='y2',
))

fig_trim.update_layout(
    title="Ventes et cours du Brent par trimestre",
    yaxis=dict(title='Ventes (m³)'),
    yaxis2=dict(title='Cours Brent (USD)', overlaying='y', side='right'),
    hovermode='x unified',
    legend=dict(orientation='h', yanchor='bottom', y=1.02),
    height=450,
)

st.plotly_chart(fig_trim, use_container_width=True)

# ─────────────────────────────────────────────
# TAUX DE VARIATION
# ─────────────────────────────────────────────
st.markdown("### Taux de variation mensuelle")

df_var = df.copy()
df_var['var_ventes'] = df_var['total_quantite_m3'].pct_change() * 100
df_var['var_cours'] = df_var['cours_brent_moyen_usd'].pct_change() * 100

fig_var = go.Figure()
fig_var.add_trace(go.Bar(
    x=df_var['date_mois'], y=df_var['var_ventes'],
    name='Variation ventes (%)', marker_color='#2196F3', opacity=0.7
))
fig_var.add_trace(go.Bar(
    x=df_var['date_mois'], y=df_var['var_cours'],
    name='Variation cours (%)', marker_color='#FF9800', opacity=0.7
))
fig_var.update_layout(
    title="Variations mensuelles comparées (%)",
    barmode='group', hovermode='x unified',
    yaxis_title='Variation (%)',
    legend=dict(orientation='h', yanchor='bottom', y=1.02),
    height=400,
)
st.plotly_chart(fig_var, use_container_width=True)
