"""Page Tableau de Bord — KPIs et evolution des ventes"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.ui import render_navbar, page_header, section_title, agil_chart_layout, CHART_COLORS
from utils import charger_ventes_mensuelles, formater_nombre

render_navbar("Tableau de Bord")
page_header("Tableau de Bord", "Indicateurs cles des ventes de gasoil — 2015 a 2018")

# ── Chargement des données ───────────────────────────────────────────────────
df_mensuel = charger_ventes_mensuelles()
if df_mensuel.empty:
    st.error("Aucune donnee disponible. Executez d'abord `python run_etl.py`.")
    st.stop()

# ── Filtre années ────────────────────────────────────────────────────────────
section_title("Filtres")
annees_dispo = sorted(df_mensuel["annee"].unique())
annees_select = st.multiselect(
    "Annees",
    options=annees_dispo,
    default=annees_dispo,
    label_visibility="collapsed",
)

df = df_mensuel[df_mensuel["annee"].isin(annees_select)]

if df.empty:
    st.warning("Aucune donnee pour la selection. Modifiez les filtres.")
    st.stop()

# ── KPIs ─────────────────────────────────────────────────────────────────────
section_title("Indicateurs cles")

total_qte  = df["total_quantite_m3"].sum()
total_mnt  = df["total_montant_ht"].sum()
prix_moyen = df["prix_unitaire_moyen"].mean()
nb_livr    = df["nb_livraisons"].sum()

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Volume total (m3)", formater_nombre(total_qte))
with c2:
    st.metric("Chiffre d'affaires HT (TND)", formater_nombre(total_mnt))
with c3:
    st.metric("Prix moyen (TND/m3)", formater_nombre(prix_moyen, 2))
with c4:
    st.metric("Nombre de livraisons", formater_nombre(nb_livr))

st.markdown("---")

# ── Evolution mensuelle ──────────────────────────────────────────────────────
section_title("Evolution mensuelle des ventes")

fig_line = go.Figure()
fig_line.add_trace(go.Scatter(
    x=df["date_mois"],
    y=df["total_quantite_m3"],
    mode="lines+markers",
    name="Volume (m3)",
    line=dict(color=CHART_COLORS[0], width=3.5),
    marker=dict(size=7, color=CHART_COLORS[0]),
    fill="tozeroy",
    fillcolor="rgba(255,209,0,0.08)",
))
fig_line.update_layout(**agil_chart_layout("Volume de gasoil vendu par mois (m3)", 400))
st.plotly_chart(fig_line, use_container_width=True)

# ── Comparaison annuelle ─────────────────────────────────────────────────────
section_title("Comparaison annuelle")

df_annuel = df.groupby("annee").agg(
    total_quantite=("total_quantite_m3", "sum"),
    total_montant=("total_montant_ht", "sum"),
).reset_index()

c1, c2 = st.columns(2)

with c1:
    fig_bar = go.Figure(go.Bar(
        x=df_annuel["annee"].astype(str),
        y=df_annuel["total_quantite"],
        marker_color=CHART_COLORS[0],
        text=[formater_nombre(v) for v in df_annuel["total_quantite"]],
        textposition="outside",
        textfont=dict(size=11, color="#1C1C1C"),
    ))
    layout = agil_chart_layout("Volume annuel (m3)", 360)
    layout["xaxis"]["type"] = "category"
    layout["showlegend"] = False
    fig_bar.update_layout(**layout)
    st.plotly_chart(fig_bar, use_container_width=True)

with c2:
    fig_ca = go.Figure(go.Bar(
        x=df_annuel["annee"].astype(str),
        y=df_annuel["total_montant"],
        marker_color=CHART_COLORS[1],
        text=[formater_nombre(v) for v in df_annuel["total_montant"]],
        textposition="outside",
        textfont=dict(size=13, color="#2C2C2C"),
    ))
    layout = agil_chart_layout("Chiffre d'affaires annuel HT (TND)", 360)
    layout["xaxis"]["type"] = "category"
    layout["showlegend"] = False
    fig_ca.update_layout(**layout)
    st.plotly_chart(fig_ca, use_container_width=True)

# ── Saisonnalité ─────────────────────────────────────────────────────────────
section_title("Saisonnalite mensuelle")

noms_mois = ["Jan","Fev","Mar","Avr","Mai","Juin","Jul","Aout","Sep","Oct","Nov","Dec"]
df_saison = df.groupby("mois")["total_quantite_m3"].mean().reset_index()
df_saison["nom_mois"] = [noms_mois[m - 1] for m in df_saison["mois"]]

fig_saison = go.Figure(go.Bar(
    x=df_saison["nom_mois"],
    y=df_saison["total_quantite_m3"],
    marker=dict(
        color=df_saison["total_quantite_m3"],
        colorscale=[[0, "#1C1C1C"], [0.5, "#E5BA00"], [1, "#FFD100"]],
        showscale=False,
    ),
    text=[formater_nombre(v) for v in df_saison["total_quantite_m3"]],
    textposition="outside",
    textfont=dict(size=10, color="#1C1C1C"),
))
layout = agil_chart_layout("Volume moyen par mois — toutes annees confondues (m3)", 380)
layout["xaxis"]["type"] = "category"
layout["showlegend"] = False
fig_saison.update_layout(**layout)
st.plotly_chart(fig_saison, use_container_width=True)
