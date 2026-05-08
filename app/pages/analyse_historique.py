"""Page Analyse Historique - Ventes vs Cours du Brent."""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from scipy import stats
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.ui import render_navbar, page_header, section_title, agil_chart_layout, CHART_COLORS
from utils import charger_ventes_mensuelles, formater_nombre

render_navbar("Analyse")
page_header("Analyse Historique", "Relation entre les ventes de gasoil et le cours du Brent - 2015 a 2018")

# ── Chargement + filtre ──────────────────────────────────────────────────────
df = charger_ventes_mensuelles()
if df.empty:
    st.error("Aucune donnee disponible. Executez d'abord `python run_etl.py`.")
    st.stop()

section_title("Plage de dates")
date_min = df["date_mois"].min().date()
date_max = df["date_mois"].max().date()
plage = st.date_input(
    "Plage",
    value=(date_min, date_max),
    min_value=date_min,
    max_value=date_max,
    label_visibility="collapsed",
)
if len(plage) == 2:
    df = df[(df["date_mois"].dt.date >= plage[0]) & (df["date_mois"].dt.date <= plage[1])]

if df.empty:
    st.warning("Aucune donnee pour cette plage de dates.")
    st.stop()

# ── Double axe Y : ventes + Brent ────────────────────────────────────────────
section_title("Ventes de gasoil vs Cours du Brent")

fig_dual = go.Figure()
fig_dual.add_trace(go.Scatter(
    x=df["date_mois"],
    y=df["total_quantite_m3"],
    name="Ventes gasoil (m3)",
    line=dict(color=CHART_COLORS[0], width=3.5),
    mode="lines+markers",
    marker=dict(size=7),
    yaxis="y1",
))
fig_dual.add_trace(go.Scatter(
    x=df["date_mois"],
    y=df["cours_brent_moyen_usd"],
    name="Cours Brent (USD/baril)",
    line=dict(color=CHART_COLORS[1], width=3.5, dash="dash"),
    mode="lines+markers",
    marker=dict(size=7),
    yaxis="y2",
))

layout = agil_chart_layout("Evolution comparee : Ventes de gasoil et Cours du Brent", 480)
layout["yaxis"]  = dict(
    title=dict(text="Quantite vendue (m3)", font=dict(color=CHART_COLORS[0], size=11)),
    tickfont=dict(color=CHART_COLORS[0], size=11),
    gridcolor="#F5F5F5",
    linecolor="#E8E8E8",
)
layout["yaxis2"] = dict(
    title=dict(text="Cours Brent (USD/baril)", font=dict(color=CHART_COLORS[1], size=11)),
    tickfont=dict(color=CHART_COLORS[1], size=11),
    overlaying="y",
    side="right",
    showgrid=False,
)
fig_dual.update_layout(**layout)
st.plotly_chart(fig_dual, use_container_width=True)

# ── Corrélation de Pearson ───────────────────────────────────────────────────
section_title("Correlation statistique")

df_corr = df.dropna(subset=["total_quantite_m3", "cours_brent_moyen_usd"])

if len(df_corr) > 2:
    pearson_r, p_value = stats.pearsonr(
        df_corr["total_quantite_m3"],
        df_corr["cours_brent_moyen_usd"],
    )

    if abs(pearson_r) < 0.3:
        interpretation = "Faible"
    elif abs(pearson_r) < 0.7:
        interpretation = "Moderee"
    else:
        interpretation = "Forte"
    direction = "positive" if pearson_r > 0 else "negative"

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Coefficient de Pearson (r)", f"{pearson_r:.4f}")
    with c2:
        st.metric("p-value", f"{p_value:.6f}")
    with c3:
        st.metric("Interpretation", f"{interpretation} ({direction})")

    # ── Nuage de points ───────────────────────────────────────────────────────
    section_title("Nuage de points - Ventes vs Cours")

    scatter_kw = dict(
        data_frame=df_corr,
        x="cours_brent_moyen_usd",
        y="total_quantite_m3",
        color="annee",
        size="nb_livraisons",
        hover_data=["nom_mois", "annee"],
        labels={
            "cours_brent_moyen_usd": "Cours Brent moyen (USD/baril)",
            "total_quantite_m3": "Ventes mensuelles (m3)",
            "annee": "Annee",
        },
        color_discrete_sequence=CHART_COLORS,
    )
    try:
        fig_scatter = px.scatter(**scatter_kw, trendline="ols")
    except ModuleNotFoundError:
        fig_scatter = px.scatter(**scatter_kw)

    fig_scatter.update_layout(**agil_chart_layout(
        "Relation entre le cours du Brent et les ventes de gasoil", 460
    ))
    st.plotly_chart(fig_scatter, use_container_width=True)

# ── Analyse trimestrielle ────────────────────────────────────────────────────
section_title("Analyse trimestrielle")

df_trim = df.copy()
df_trim["trimestre"] = df_trim["date_mois"].dt.quarter
df_trim["trimestre_label"] = (
    df_trim["annee"].astype(str) + "-T" + df_trim["trimestre"].astype(str)
)
df_trim_agg = df_trim.groupby(
    ["annee", "trimestre", "trimestre_label"]
).agg(
    ventes=("total_quantite_m3", "sum"),
    cours_moyen=("cours_brent_moyen_usd", "mean"),
).reset_index()

fig_trim = go.Figure()
fig_trim.add_trace(go.Bar(
    x=df_trim_agg["trimestre_label"],
    y=df_trim_agg["ventes"],
    name="Ventes (m3)",
    marker_color=CHART_COLORS[0],
    yaxis="y1",
))
fig_trim.add_trace(go.Scatter(
    x=df_trim_agg["trimestre_label"],
    y=df_trim_agg["cours_moyen"],
    name="Cours Brent (USD)",
    line=dict(color=CHART_COLORS[1], width=4),
    mode="lines+markers",
    marker=dict(size=6),
    yaxis="y2",
))
layout_trim = agil_chart_layout("Ventes et cours du Brent par trimestre", 430)
layout_trim["yaxis2"] = dict(
    title="Cours Brent (USD)",
    overlaying="y",
    side="right",
    showgrid=False,
    tickfont=dict(size=11, color="#6B6B6B"),
)
fig_trim.update_layout(**layout_trim)
st.plotly_chart(fig_trim, use_container_width=True)

# ── Taux de variation ────────────────────────────────────────────────────────
section_title("Taux de variation mensuelle")

df_var = df.copy()
df_var["var_ventes"] = df_var["total_quantite_m3"].pct_change() * 100
df_var["var_cours"]  = df_var["cours_brent_moyen_usd"].pct_change() * 100

fig_var = go.Figure()
fig_var.add_trace(go.Bar(
    x=df_var["date_mois"], y=df_var["var_ventes"],
    name="Variation ventes (%)", marker_color=CHART_COLORS[0], opacity=0.85,
))
fig_var.add_trace(go.Bar(
    x=df_var["date_mois"], y=df_var["var_cours"],
    name="Variation cours (%)", marker_color=CHART_COLORS[1], opacity=0.85,
))
layout_var = agil_chart_layout("Variations mensuelles comparees (%)", 380)
layout_var["barmode"] = "group"
layout_var["yaxis"]["title"] = "Variation (%)"
fig_var.update_layout(**layout_var)
st.plotly_chart(fig_var, use_container_width=True)
