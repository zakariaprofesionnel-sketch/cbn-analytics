"""Page Previsions IA — Modele Prophet"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import pickle
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.ui import render_navbar, page_header, section_title, agil_chart_layout, CHART_COLORS
from utils import charger_ventes_mensuelles, formater_nombre
from config import BASE_DIR

render_navbar("Previsions")
page_header("Previsions IA", "Modele Prophet — projection des ventes de gasoil avec scenarios Brent")

# ── Chargement modele ────────────────────────────────────────────────────────
MODEL_PATH = os.path.join(BASE_DIR, "ml", "prophet_model.pkl")

@st.cache_resource
def charger_modele():
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)

try:
    model = charger_modele()
except FileNotFoundError:
    st.error("Modele non trouve. Executez d'abord `python run_ml.py`.")
    st.stop()

df_historique = charger_ventes_mensuelles()
if df_historique.empty:
    st.error("Aucune donnee disponible. Executez d'abord `python run_etl.py`.")
    st.stop()

# ── Parametres de prevision ──────────────────────────────────────────────────
section_title("Parametres")

c1, c2, c3 = st.columns([1.5, 2, 1.5])
with c1:
    horizon = st.slider("Horizon de prevision (mois)", 1, 12, 6)
with c2:
    scenario = st.radio(
        "Scenario cours du petrole",
        options=["stable", "hausse", "baisse"],
        format_func=lambda x: {
            "stable": "Stable — cours maintenu",
            "hausse": "Hausse +20%",
            "baisse": "Baisse -20%",
        }[x],
        horizontal=True,
    )
with c3:
    comparer = st.checkbox("Comparer les 3 scenarios", value=False)

# ── Generation des previsions ────────────────────────────────────────────────
dernier_cours   = float(df_historique["cours_brent_moyen_usd"].iloc[-1])
derniere_date   = df_historique["date_mois"].max()

def generer_prevision(h: int, sc: str, cours_val: float) -> pd.DataFrame:
    dates_futures = pd.date_range(
        start=derniere_date + pd.offsets.MonthBegin(1),
        periods=h, freq="MS",
    )
    facteurs = {
        "stable": np.ones(h),
        "hausse": np.linspace(1.0, 1.20, h),
        "baisse": np.linspace(1.0, 0.80, h),
    }
    cours_sc = cours_val * facteurs[sc]
    future = pd.DataFrame({"ds": dates_futures, "cours_brent": cours_sc})
    forecast = model.predict(future)
    forecast["cours_brent"] = cours_sc
    return forecast

forecast = generer_prevision(horizon, scenario, dernier_cours)

# ── Graphique principal ──────────────────────────────────────────────────────
section_title("Projection des ventes")

COULEUR_SC = {"stable": "#00A651", "hausse": CHART_COLORS[0], "baisse": "#CC4400"}

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_historique["date_mois"],
    y=df_historique["total_quantite_m3"],
    name="Historique",
    line=dict(color=CHART_COLORS[1], width=3.5),
    mode="lines+markers",
    marker=dict(size=5),
))

if comparer:
    for sc in ["stable", "hausse", "baisse"]:
        fc = generer_prevision(horizon, sc, dernier_cours)
        noms = {"stable": "Prevision (stable)", "hausse": "Prevision (hausse)", "baisse": "Prevision (baisse)"}
        fig.add_trace(go.Scatter(
            x=fc["ds"], y=fc["yhat"],
            name=noms[sc],
            line=dict(color=COULEUR_SC[sc], width=3, dash="dot"),
            mode="lines+markers",
            marker=dict(size=5),
        ))
else:
    couleur = COULEUR_SC[scenario]
    rgb = tuple(int(couleur.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
    fig.add_trace(go.Scatter(
        x=pd.concat([forecast["ds"], forecast["ds"][::-1]]),
        y=pd.concat([forecast["yhat_upper"], forecast["yhat_lower"][::-1]]),
        fill="toself",
        fillcolor=f"rgba({rgb[0]},{rgb[1]},{rgb[2]},0.12)",
        line=dict(color="rgba(0,0,0,0)"),
        name="Intervalle de confiance 95%",
        showlegend=True,
    ))
    fig.add_trace(go.Scatter(
        x=forecast["ds"], y=forecast["yhat"],
        name=f"Prevision ({scenario})",
        line=dict(color=couleur, width=3.5, dash="dot"),
        mode="lines+markers",
        marker=dict(size=5),
    ))

x_sep = str(derniere_date.date())
fig.add_shape(
    type="line", x0=x_sep, x1=x_sep, y0=0, y1=1,
    xref="x", yref="paper", line=dict(color="#AAAAAA", dash="dash"),
)
fig.add_annotation(
    x=x_sep, y=1.03, xref="x", yref="paper",
    text="Fin historique", showarrow=False,
    font=dict(color="#AAAAAA", size=11),
)
fig.update_layout(**agil_chart_layout(f"Prevision sur {horizon} mois — Scenario : {scenario}", 530))
fig.update_layout(yaxis_title="Quantite (m3)")
st.plotly_chart(fig, use_container_width=True)

# ── KPIs prevision ───────────────────────────────────────────────────────────
section_title("Resume de la prevision")

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Volume total prevu", formater_nombre(forecast["yhat"].sum()) + " m3")
with c2:
    st.metric("Borne basse (m3)", formater_nombre(forecast["yhat_lower"].sum()))
with c3:
    st.metric("Borne haute (m3)", formater_nombre(forecast["yhat_upper"].sum()))

# ── Tableau détail ───────────────────────────────────────────────────────────
section_title("Detail mensuel des previsions")

noms_mois_fr = {
    1:"Janvier", 2:"Fevrier", 3:"Mars", 4:"Avril",
    5:"Mai", 6:"Juin", 7:"Juillet", 8:"Aout",
    9:"Septembre", 10:"Octobre", 11:"Novembre", 12:"Decembre",
}
df_tableau = pd.DataFrame({
    "Mois":             [noms_mois_fr[d.month] + " " + str(d.year) for d in forecast["ds"]],
    "Prevision (m3)":   forecast["yhat"].round(1).values,
    "Borne basse (m3)": forecast["yhat_lower"].round(1).values,
    "Borne haute (m3)": forecast["yhat_upper"].round(1).values,
    "Cours Brent (USD)":forecast["cours_brent"].round(2).values,
})
st.dataframe(df_tableau, use_container_width=True, hide_index=True)

# ── Explication modele ───────────────────────────────────────────────────────
with st.expander("Comment fonctionne le modele ?"):
    st.markdown("""
    **Prophet** (Meta/Facebook) decompose la serie temporelle en :
    - **Tendance** : evolution de fond des ventes
    - **Saisonnalite** : variations cycliques annuelles
    - **Regresseur externe** : cours du Brent comme variable explicative

    **Formule** : `y(t) = tendance(t) + saisonnalite(t) + B × cours_brent(t) + erreur(t)`

    **Scenarios de cours** :
    - *Stable* : dernier cours observe maintenu
    - *Hausse +20%* : augmentation progressive
    - *Baisse -20%* : diminution progressive

    L'intervalle de confiance a 95% indique la fourchette probable de la valeur reelle.
    """)
