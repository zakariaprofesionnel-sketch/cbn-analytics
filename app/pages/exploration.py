"""Page Exploration - Donnees brutes et decomposition."""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import pickle
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.ui import render_navbar, page_header, section_title, agil_chart_layout, styled_dataframe, CHART_COLORS
from utils import charger_ventes_mensuelles, charger_ventes_detail, formater_nombre
from config import BASE_DIR

render_navbar("Exploration")
page_header("Exploration des Donnees", "Statistiques descriptives, distribution et decomposition saisonniere")

# ── Filtres ──────────────────────────────────────────────────────────────────
df_detail = charger_ventes_detail()
if df_detail.empty:
    st.error("Aucune donnee detaillee disponible. Executez d'abord `python run_etl.py`.")
    st.stop()

section_title("Filtres")
c1, c2 = st.columns(2)
with c1:
    annees = sorted(df_detail["annee"].unique())
    annees_select = st.multiselect("Annees", annees, default=annees)
with c2:
    trimestres_select = st.multiselect(
        "Trimestres", [1, 2, 3, 4], default=[1, 2, 3, 4],
        format_func=lambda x: f"T{x}",
    )

df_f = df_detail[
    df_detail["annee"].isin(annees_select) &
    df_detail["trimestre"].isin(trimestres_select)
]

if df_f.empty:
    st.warning("Aucune donnee pour cette selection.")
    st.stop()

# ── Statistiques descriptives ────────────────────────────────────────────────
section_title("Statistiques descriptives")

c1, c2 = st.columns(2)

def build_stats_df(series: pd.Series, label: str) -> pd.DataFrame:
    desc = series.describe()
    return pd.DataFrame({
        "Statistique": ["Nombre", "Moyenne", "Ecart-type", "Min", "Q25", "Mediane", "Q75", "Max"],
        label: [
            formater_nombre(desc["count"]),
            f"{desc['mean']:.2f}",
            f"{desc['std']:.2f}",
            f"{desc['min']:.2f}",
            f"{desc['25%']:.2f}",
            f"{desc['50%']:.2f}",
            f"{desc['75%']:.2f}",
            f"{desc['max']:.2f}",
        ],
    })

with c1:
    st.markdown("**Quantite livree (m3)**")
    styled_dataframe(build_stats_df(df_f["quantite_m3"], "Valeur"), hide_index=True)
with c2:
    st.markdown("**Montant HT (TND)**")
    styled_dataframe(build_stats_df(df_f["montant_ht"], "Valeur"), hide_index=True)

st.markdown("---")

# ── Distribution ─────────────────────────────────────────────────────────────
section_title("Distribution des quantites livrees")

c1, c2 = st.columns(2)
with c1:
    fig_hist = go.Figure(go.Histogram(
        x=df_f["quantite_m3"],
        nbinsx=50,
        marker_color=CHART_COLORS[0],
        opacity=0.85,
    ))
    fig_hist.update_layout(**agil_chart_layout("Histogramme des quantites (m3)", 360))
    fig_hist.update_layout(xaxis_title="Quantite (m3)", yaxis_title="Frequence", showlegend=False)
    st.plotly_chart(fig_hist, use_container_width=True)

with c2:
    fig_box = px.box(
        df_f, x="annee", y="quantite_m3",
        color="annee",
        color_discrete_sequence=CHART_COLORS,
        labels={"annee": "Annee", "quantite_m3": "Quantite (m3)"},
    )
    layout_box = agil_chart_layout("Distribution par annee (box plot)", 360)
    layout_box["xaxis"]["type"] = "category"
    layout_box["showlegend"] = False
    fig_box.update_layout(**layout_box)
    st.plotly_chart(fig_box, use_container_width=True)

# ── Decomposition saisonniere ────────────────────────────────────────────────
section_title("Decomposition saisonniere (Prophet)")

MODEL_PATH = os.path.join(BASE_DIR, "ml", "prophet_model.pkl")

if os.path.exists(MODEL_PATH):
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)

    df_mensuel = charger_ventes_mensuelles()
    df_prophet = pd.DataFrame({
        "ds": df_mensuel["date_mois"],
        "y":  df_mensuel["total_quantite_m3"].astype(float),
        "cours_brent": df_mensuel["cours_brent_moyen_usd"].astype(float),
    })
    forecast_dec = model.predict(df_prophet)

    c1, c2 = st.columns(2)
    with c1:
        fig_trend = go.Figure(go.Scatter(
            x=forecast_dec["ds"], y=forecast_dec["trend"],
            mode="lines", line=dict(color="#00A651", width=3.5),
        ))
        fig_trend.update_layout(**agil_chart_layout("Composante : Tendance", 340))
        fig_trend.update_layout(showlegend=False, yaxis_title="Tendance (m3)")
        st.plotly_chart(fig_trend, use_container_width=True)

    with c2:
        if "yearly" in forecast_dec.columns:
            fig_yearly = go.Figure(go.Scatter(
                x=forecast_dec["ds"], y=forecast_dec["yearly"],
                mode="lines", line=dict(color=CHART_COLORS[0], width=3.5),
            ))
            fig_yearly.update_layout(**agil_chart_layout("Composante : Saisonnalite annuelle", 340))
            fig_yearly.update_layout(showlegend=False, yaxis_title="Effet saisonnier")
            st.plotly_chart(fig_yearly, use_container_width=True)
else:
    st.info("La decomposition sera disponible apres l'entrainement du modele (`python run_ml.py`).")

# ── Donnees brutes ───────────────────────────────────────────────────────────
section_title("Donnees brutes")

nb_lignes = st.slider("Nombre de lignes a afficher", 10, 500, 100)
df_affiche = df_f[[
    "date_complete", "annee", "nom_mois", "trimestre",
    "quantite_m3", "montant_ht", "prix_unitaire",
]].head(nb_lignes).rename(columns={
    "date_complete": "Date",
    "annee":         "Annee",
    "nom_mois":      "Mois",
    "trimestre":     "Trimestre",
    "quantite_m3":   "Quantite (m3)",
    "montant_ht":    "Montant HT (TND)",
    "prix_unitaire": "Prix unitaire (TND/m3)",
})
styled_dataframe(df_affiche, hide_index=True)
st.caption(
    f"Affichage de {min(nb_lignes, len(df_f))} lignes "
    f"sur {formater_nombre(len(df_f))} au total"
)
