"""
Page 3 : Prévisions IA — Modèle Prophet
==========================================
Interface de prévision interactive :
- Horizon configurable (1-12 mois)
- 3 scénarios de cours du pétrole
- Graphique avec intervalle de confiance
- Métriques de performance du modèle
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import pickle
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils import charger_ventes_mensuelles, formater_nombre
from config import BASE_DIR

st.set_page_config(page_title="Prévisions IA", page_icon="🤖", layout="wide")
st.title("🤖 Prévisions IA — Modèle Prophet")

# ─────────────────────────────────────────────
# CHARGER LE MODÈLE ET LES DONNÉES
# ─────────────────────────────────────────────
MODEL_PATH = os.path.join(BASE_DIR, "ml", "prophet_model.pkl")
METRICS_PATH = os.path.join(BASE_DIR, "ml", "metriques.pkl")
PREDICTIONS_TEST_PATH = os.path.join(BASE_DIR, "ml", "predictions_test.csv")

@st.cache_resource
def charger_modele():
    """Charge le modèle Prophet sauvegardé."""
    with open(MODEL_PATH, 'rb') as f:
        return pickle.load(f)

@st.cache_data
def charger_metriques():
    """Charge les métriques sauvegardées."""
    if os.path.exists(METRICS_PATH):
        with open(METRICS_PATH, 'rb') as f:
            return pickle.load(f)
    return None

@st.cache_data
def charger_predictions_test():
    """Charge le comparatif réel vs prédit sur la période de test."""
    if not os.path.exists(PREDICTIONS_TEST_PATH):
        return pd.DataFrame()
    df = pd.read_csv(PREDICTIONS_TEST_PATH)
    df["date_mois"] = pd.to_datetime(df["date_mois"])
    return df

try:
    model = charger_modele()
except FileNotFoundError:
    st.error("⚠️ Modèle non trouvé. Exécutez d'abord `python run_ml.py` pour entraîner le modèle.")
    st.stop()

df_historique = charger_ventes_mensuelles()
if df_historique.empty:
    st.error("⚠️ Aucune donnée disponible depuis la base. Exécutez d'abord `python run_etl.py`.")
    st.stop()

# ─────────────────────────────────────────────
# PARAMÈTRES DE PRÉVISION (sidebar)
# ─────────────────────────────────────────────
st.sidebar.header("⚙️ Paramètres de prévision")

horizon = st.sidebar.slider(
    "Horizon de prévision (mois)",
    min_value=1,
    max_value=12,
    value=6,
    help="Nombre de mois à prévoir après décembre 2018"
)

scenario = st.sidebar.radio(
    "Scénario cours du pétrole",
    options=['stable', 'hausse', 'baisse'],
    format_func=lambda x: {
        'stable': '➡️ Stable (cours maintenu)',
        'hausse': '📈 Hausse (+20%)',
        'baisse': '📉 Baisse (-20%)',
    }[x],
    help="Impact du cours Brent sur les prévisions"
)

afficher_tous_scenarios = st.sidebar.checkbox(
    "Comparer les 3 scénarios", value=False
)

# ─────────────────────────────────────────────
# GÉNÉRER LES PRÉVISIONS
# ─────────────────────────────────────────────
dernier_cours = float(df_historique['cours_brent_moyen_usd'].iloc[-1])
derniere_date = df_historique['date_mois'].max()

def generer_prevision(horizon_mois, scenario_cours, dernier_cours_val):
    """Génère les prévisions Prophet avec scénario de cours."""
    dates_futures = pd.date_range(
        start=derniere_date + pd.offsets.MonthBegin(1),
        periods=horizon_mois,
        freq='MS'
    )
    
    facteurs = {
        'stable': np.ones(horizon_mois),
        'hausse': np.linspace(1.0, 1.20, horizon_mois),
        'baisse': np.linspace(1.0, 0.80, horizon_mois),
    }
    
    cours_scenario = dernier_cours_val * facteurs[scenario_cours]
    
    future = pd.DataFrame({
        'ds': dates_futures,
        'cours_brent': cours_scenario,
    })
    
    forecast = model.predict(future)
    forecast['cours_brent'] = cours_scenario
    
    return forecast

# Prévision principale
forecast = generer_prevision(horizon, scenario, dernier_cours)

# ─────────────────────────────────────────────
# GRAPHIQUE PRINCIPAL
# ─────────────────────────────────────────────
st.markdown("### Prévision des ventes de gasoil")

fig = go.Figure()

# Historique
fig.add_trace(go.Scatter(
    x=df_historique['date_mois'],
    y=df_historique['total_quantite_m3'],
    name='Historique',
    line=dict(color='#2196F3', width=2.5),
    mode='lines+markers',
))

if afficher_tous_scenarios:
    # Afficher les 3 scénarios
    couleurs = {'stable': '#4CAF50', 'hausse': '#FF9800', 'baisse': '#F44336'}
    noms = {'stable': 'Prévision (stable)', 'hausse': 'Prévision (hausse)', 'baisse': 'Prévision (baisse)'}
    
    for sc in ['stable', 'hausse', 'baisse']:
        fc = generer_prevision(horizon, sc, dernier_cours)
        fig.add_trace(go.Scatter(
            x=fc['ds'], y=fc['yhat'],
            name=noms[sc],
            line=dict(color=couleurs[sc], width=2, dash='dot'),
            mode='lines+markers',
        ))
else:
    # Scénario unique avec intervalle de confiance
    couleur_scenario = {'stable': '#4CAF50', 'hausse': '#FF9800', 'baisse': '#F44336'}[scenario]
    
    # Bande de confiance
    fig.add_trace(go.Scatter(
        x=pd.concat([forecast['ds'], forecast['ds'][::-1]]),
        y=pd.concat([forecast['yhat_upper'], forecast['yhat_lower'][::-1]]),
        fill='toself',
        fillcolor=f'rgba({",".join(str(int(couleur_scenario[i:i+2], 16)) for i in (1, 3, 5))}, 0.15)',
        line=dict(color='rgba(0,0,0,0)'),
        name='Intervalle de confiance (95%)',
        showlegend=True,
    ))
    
    # Ligne de prévision
    fig.add_trace(go.Scatter(
        x=forecast['ds'], y=forecast['yhat'],
        name=f'Prévision ({scenario})',
        line=dict(color=couleur_scenario, width=2.5, dash='dot'),
        mode='lines+markers',
    ))

# Ligne de séparation historique/prévision
x_sep = str(derniere_date.date())
fig.add_shape(
    type="line",
    x0=x_sep, x1=x_sep,
    y0=0, y1=1,
    xref="x", yref="paper",
    line=dict(color="gray", dash="dash"),
)
fig.add_annotation(
    x=x_sep, y=1.02,
    xref="x", yref="paper",
    text="Fin historique",
    showarrow=False,
    font=dict(color="gray"),
)
fig.update_layout(
    title=f"Prévision sur {horizon} mois — Scénario : {scenario}",
    xaxis_title='', yaxis_title='Quantité (m³)',
    hovermode='x unified',
    legend=dict(orientation='h', yanchor='bottom', y=1.02),
    height=550,
)

st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# COMPARATIF RÉEL VS PRÉDIT (TEST)
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📊 Comparaison Réel vs Prédit (période de test)")

df_test_pred = charger_predictions_test()
if not df_test_pred.empty:
    fig_compare = go.Figure()
    fig_compare.add_trace(go.Scatter(
        x=df_test_pred["date_mois"],
        y=df_test_pred["reel_m3"],
        name="Réel",
        mode="lines+markers",
        line=dict(color="#2196F3", width=2.5),
    ))
    fig_compare.add_trace(go.Scatter(
        x=df_test_pred["date_mois"],
        y=df_test_pred["prediction_m3"],
        name="Prédit",
        mode="lines+markers",
        line=dict(color="#FF9800", width=2.5, dash="dot"),
    ))
    fig_compare.update_layout(
        title="Ventes réelles vs prédictions (test 2018)",
        xaxis_title="",
        yaxis_title="Quantité (m³)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=460,
    )
    st.plotly_chart(fig_compare, use_container_width=True)

    fig_error = go.Figure()
    fig_error.add_trace(go.Bar(
        x=df_test_pred["date_mois"],
        y=df_test_pred["erreur_m3"],
        name="Erreur (Réel - Prédit)",
        marker_color="#9C27B0",
        opacity=0.8,
    ))
    fig_error.update_layout(
        title="Erreur de prédiction mensuelle",
        xaxis_title="",
        yaxis_title="Erreur (m³)",
        hovermode="x unified",
        height=320,
    )
    st.plotly_chart(fig_error, use_container_width=True)
else:
    st.info(
        "Comparatif indisponible. Lancez `python run_ml.py` pour générer "
        "`ml/predictions_test.csv`."
    )

# ─────────────────────────────────────────────
# TABLEAU DES PRÉVISIONS
# ─────────────────────────────────────────────
st.markdown("### Détail des prévisions")

noms_mois_fr = {1:'Janvier', 2:'Février', 3:'Mars', 4:'Avril',
                5:'Mai', 6:'Juin', 7:'Juillet', 8:'Août',
                9:'Septembre', 10:'Octobre', 11:'Novembre', 12:'Décembre'}

df_tableau = pd.DataFrame({
    'Mois': [noms_mois_fr[d.month] + ' ' + str(d.year) for d in forecast['ds']],
    'Prévision (m³)': forecast['yhat'].round(1).values,
    'Borne basse (m³)': forecast['yhat_lower'].round(1).values,
    'Borne haute (m³)': forecast['yhat_upper'].round(1).values,
    'Cours Brent (USD)': forecast['cours_brent'].round(2).values,
})

st.dataframe(df_tableau, use_container_width=True, hide_index=True)

# Total
col1, col2 = st.columns(2)
with col1:
    st.metric(
        "Volume total prévu",
        f"{formater_nombre(forecast['yhat'].sum())} m³"
    )
with col2:
    st.metric(
        "Intervalle",
        f"{formater_nombre(forecast['yhat_lower'].sum())} — {formater_nombre(forecast['yhat_upper'].sum())} m³"
    )

# ─────────────────────────────────────────────
# MÉTRIQUES DU MODÈLE
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📐 Performance du modèle (évaluation sur 2018)")

metriques = charger_metriques()

if metriques:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("MAE", f"{metriques['MAE']:,.2f} m³",
                   help="Erreur Absolue Moyenne — en moyenne, le modèle se trompe de cette quantité")
    with col2:
        st.metric("RMSE", f"{metriques['RMSE']:,.2f} m³",
                   help="Racine de l'Erreur Quadratique Moyenne — pénalise les grosses erreurs")
    with col3:
        st.metric("MAPE", f"{metriques['MAPE']:.2f}%",
                   help="Erreur en Pourcentage Absolu Moyen — le % d'erreur typique")
    with col4:
        st.metric("R²", f"{metriques['R2']:.4f}",
                   help="Coefficient de détermination — 1.0 = prédiction parfaite")
else:
    st.info("Les métriques seront disponibles après l'exécution de `python run_ml.py`")

# ─────────────────────────────────────────────
# EXPLICATION PÉDAGOGIQUE
# ─────────────────────────────────────────────
with st.expander("ℹ️ Comment fonctionne le modèle ?"):
    st.markdown("""
    **Prophet** (développé par Meta/Facebook) décompose la série temporelle en :
    
    - **Tendance** : l'évolution de fond des ventes (croissance ou décroissance)
    - **Saisonnalité** : les variations cycliques (été vs hiver, etc.)
    - **Régresseur externe** : le cours du Brent, qui influence le volume vendu
    
    **Formule** : `y(t) = tendance(t) + saisonnalité(t) + β × cours_brent(t) + ε(t)`
    
    **Scénarios de cours** :
    - *Stable* : le dernier cours observé est maintenu
    - *Hausse +20%* : augmentation progressive sur l'horizon
    - *Baisse -20%* : diminution progressive sur l'horizon
    
    L'**intervalle de confiance à 95%** signifie que la valeur réelle a 95% de chances 
    de se situer dans cette fourchette.
    """)
