"""Page Previsions IA - meilleur modele Prophet/SARIMAX."""

import json
import os
import pickle
import sys

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.ui import CHART_COLORS, agil_chart_layout, page_header, render_navbar, section_title, styled_dataframe
from config import BASE_DIR
from ml.arima_forecast import prevoir_sarimax
from utils import charger_ventes_mensuelles, formater_nombre


render_navbar("Previsions")
page_header("Previsions IA", "Comparaison Prophet vs SARIMAX - previsions avec le modele retenu")

PROPHET_MODEL_PATH = os.path.join(BASE_DIR, "ml", "prophet_model.pkl")
SARIMA_MODEL_PATH = os.path.join(BASE_DIR, "ml", "sarima_model.pkl")
BEST_MODEL_PATH = os.path.join(BASE_DIR, "ml", "best_model.json")
COMPARISON_PATH = os.path.join(BASE_DIR, "ml", "model_comparison.csv")


@st.cache_resource
def charger_modeles(best_model_mtime: float, prophet_mtime: float, sarimax_mtime: float | None):
    with open(BEST_MODEL_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    with open(PROPHET_MODEL_PATH, "rb") as f:
        prophet_model = pickle.load(f)
    sarimax_payload = None
    if os.path.exists(SARIMA_MODEL_PATH):
        with open(SARIMA_MODEL_PATH, "rb") as f:
            sarimax_payload = pickle.load(f)
    return metadata, prophet_model, sarimax_payload


try:
    model_metadata, prophet_model, sarimax_payload = charger_modeles(
        os.path.getmtime(BEST_MODEL_PATH),
        os.path.getmtime(PROPHET_MODEL_PATH),
        os.path.getmtime(SARIMA_MODEL_PATH) if os.path.exists(SARIMA_MODEL_PATH) else None,
    )
except FileNotFoundError:
    st.error("Modele non trouve. Executez d'abord `python run_ml.py`.")
    st.stop()

df_historique = charger_ventes_mensuelles()
if df_historique.empty:
    st.error("Aucune donnee disponible. Executez d'abord `python run_etl.py`.")
    st.stop()

best_model = model_metadata.get("best_model", "Prophet")
expected_test_year = 2017
forecast_start_year = int(model_metadata.get("forecast_start_year", 2018))
final_train_end_year = forecast_start_year - 1
df_modele_historique = df_historique[df_historique["annee"] <= final_train_end_year].copy()
df_reel_prevision = df_historique[df_historique["annee"] >= forecast_start_year].copy()

if df_modele_historique.empty:
    st.error("Aucune donnee historique disponible pour entrainer le modele final.")
    st.stop()

dernier_cours = float(df_modele_historique["cours_brent_moyen_usd"].iloc[-1])
derniere_date = df_modele_historique["date_mois"].max()

if model_metadata.get("test_year") != expected_test_year:
    st.warning(
        "Les artefacts ML charges semblent anciens. "
        "Relancez `python run_ml.py` apres installation des dependances pour recalculer "
        "l'evaluation sur 2017 et les modeles finaux 2015-2017."
    )

section_title("Modele retenu")
st.info(
    f"Modele utilise : **{best_model}**. "
    f"Evaluation sur {model_metadata.get('test_year', expected_test_year)}, "
    f"entrainement {model_metadata.get('train_period', '2015-2016')}. "
    f"Le modele final est ensuite re-entraine sur {model_metadata.get('final_train_period', '2015-2017')} "
    f"pour prevoir {forecast_start_year}."
)

if os.path.exists(COMPARISON_PATH):
    comparison = pd.read_csv(COMPARISON_PATH)
    styled_dataframe(comparison, hide_index=True)

section_title("Parametres")
c1, c2, c3 = st.columns([1.5, 2, 1.5])
with c1:
    horizon = st.slider("Horizon de prevision (mois)", 1, 12, 12)
with c2:
    scenario = st.radio(
        "Scenario cours du petrole",
        options=["stable", "hausse", "baisse"],
        format_func=lambda x: {
            "stable": "Stable - cours maintenu",
            "hausse": "Hausse +20%",
            "baisse": "Baisse -20%",
        }[x],
        horizontal=True,
    )
with c3:
    comparer = st.checkbox("Comparer les 3 scenarios", value=False)


def generer_prevision_prophet(h: int, sc: str, cours_val: float) -> pd.DataFrame:
    dates_futures = pd.date_range(
        start=derniere_date + pd.offsets.MonthBegin(1),
        periods=h,
        freq="MS",
    )
    facteurs = {
        "stable": np.ones(h),
        "hausse": np.linspace(1.0, 1.20, h),
        "baisse": np.linspace(1.0, 0.80, h),
    }
    cours_sc = cours_val * facteurs[sc]
    future = pd.DataFrame({"ds": dates_futures, "cours_brent": cours_sc})
    forecast = prophet_model.predict(future)
    forecast["cours_brent"] = cours_sc
    return forecast


def generer_prevision(h: int, sc: str, cours_val: float) -> pd.DataFrame:
    if best_model.upper() == "SARIMAX" and sarimax_payload is not None:
        return prevoir_sarimax(sarimax_payload, df_modele_historique, h, sc, cours_val)
    return generer_prevision_prophet(h, sc, cours_val)


forecast = generer_prevision(horizon, scenario, dernier_cours)

section_title("Projection des ventes")
COULEUR_SC = {"stable": "#168653", "hausse": CHART_COLORS[0], "baisse": "#B84A35"}

fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=df_modele_historique["date_mois"],
        y=df_modele_historique["total_quantite_m3"],
        name=f"Historique modele (2015-{final_train_end_year})",
        line=dict(color=CHART_COLORS[1], width=3.5),
        mode="lines+markers",
        marker=dict(size=5),
    )
)

if not df_reel_prevision.empty:
    fig.add_trace(
        go.Scatter(
            x=df_reel_prevision["date_mois"],
            y=df_reel_prevision["total_quantite_m3"],
            name=f"Reel {forecast_start_year}",
            line=dict(color="#9A958A", width=2.5, dash="dash"),
            mode="lines+markers",
            marker=dict(size=5),
        )
    )

if comparer:
    for sc in ["stable", "hausse", "baisse"]:
        fc = generer_prevision(horizon, sc, dernier_cours)
        fig.add_trace(
            go.Scatter(
                x=fc["ds"],
                y=fc["yhat"],
                name=f"Prevision {best_model} ({sc})",
                line=dict(color=COULEUR_SC[sc], width=3, dash="dot"),
                mode="lines+markers",
                marker=dict(size=5),
            )
        )
else:
    couleur = COULEUR_SC[scenario]
    rgb = tuple(int(couleur.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))
    fig.add_trace(
        go.Scatter(
            x=pd.concat([forecast["ds"], forecast["ds"][::-1]]),
            y=pd.concat([forecast["yhat_upper"], forecast["yhat_lower"][::-1]]),
            fill="toself",
            fillcolor=f"rgba({rgb[0]},{rgb[1]},{rgb[2]},0.12)",
            line=dict(color="rgba(0,0,0,0)"),
            name="Intervalle de confiance 95%",
            showlegend=True,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=forecast["ds"],
            y=forecast["yhat"],
            name=f"Prevision {best_model} ({scenario})",
            line=dict(color=couleur, width=3.5, dash="dot"),
            mode="lines+markers",
            marker=dict(size=5),
        )
    )

x_sep = str(derniere_date.date())
fig.add_shape(
    type="line",
    x0=x_sep,
    x1=x_sep,
    y0=0,
    y1=1,
    xref="x",
    yref="paper",
    line=dict(color="#9A958A", dash="dash"),
)
fig.add_annotation(
    x=x_sep,
    y=1.03,
    xref="x",
    yref="paper",
    text="Fin historique",
    showarrow=False,
    font=dict(color="#666257", size=11),
)
fig.update_layout(**agil_chart_layout(f"Prevision {best_model} sur {horizon} mois - Scenario : {scenario}", 530))
fig.update_layout(yaxis_title="Quantite (m3)")
st.plotly_chart(fig, use_container_width=True)

section_title("Resume de la prevision")
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Volume total prevu", formater_nombre(forecast["yhat"].sum()) + " m3")
with c2:
    st.metric("Borne basse (m3)", formater_nombre(forecast["yhat_lower"].sum()))
with c3:
    st.metric("Borne haute (m3)", formater_nombre(forecast["yhat_upper"].sum()))

section_title("Detail mensuel des previsions")
noms_mois_fr = {
    1: "Janvier",
    2: "Fevrier",
    3: "Mars",
    4: "Avril",
    5: "Mai",
    6: "Juin",
    7: "Juillet",
    8: "Aout",
    9: "Septembre",
    10: "Octobre",
    11: "Novembre",
    12: "Decembre",
}
df_tableau = pd.DataFrame(
    {
        "Mois": [noms_mois_fr[d.month] + " " + str(d.year) for d in forecast["ds"]],
        "Prevision (m3)": forecast["yhat"].round(1).values,
        "Borne basse (m3)": forecast["yhat_lower"].round(1).values,
        "Borne haute (m3)": forecast["yhat_upper"].round(1).values,
        "Cours Brent (USD)": forecast["cours_brent"].round(2).values,
    }
)
styled_dataframe(df_tableau, hide_index=True)

with st.expander("Comment fonctionne le modele ?"):
    st.markdown(
        """
        Le pipeline compare **Prophet** et **SARIMAX** sur une base identique :

        - entrainement de comparaison : 2015-2016 ;
        - test hors echantillon : 2017 ;
        - entrainement final : 2015-2017 ;
        - prevision : 2018 ;
        - selection : MAPE puis RMSE puis MAE les plus faibles.

        Prophet modelise tendance, saisonnalite et cours du Brent.
        SARIMAX modelise l'autocorrelation mensuelle, la saisonnalite et le cours du Brent comme variable exogene.
        """
    )
