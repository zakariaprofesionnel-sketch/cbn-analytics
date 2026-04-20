"""Page 7 : Agent IA - Validation split 2015-2016 / test 2017."""

import os
import sys

import numpy as np
import pandas as pd
import streamlit as st
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import warnings

warnings.filterwarnings("ignore")

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(APP_DIR)
sys.path.insert(0, APP_DIR)
sys.path.insert(0, ROOT_DIR)

from agent.rules import generate_recommendations  # noqa: E402
from ml.forecast import charger_donnees_mensuelles, preparer_donnees_prophet  # noqa: E402

st.set_page_config(page_title="Agent IA — Split 2017", page_icon="🧪", layout="wide")
st.title("🧪 Agent IA — Validation split 2015‑2016 / test 2017")
st.caption("Même agent, même règles — mais modèle entraîné sur 2015-2016 et testé sur 2017.")


@st.cache_resource(show_spinner="Entraînement du modèle Prophet (2015-2016)...")
def _entrainer_et_evaluer_2017():
    """Entraîne sur 2015-2016, teste sur 2017. Résultat mis en cache."""
    df = charger_donnees_mensuelles()
    df_prophet = preparer_donnees_prophet(df)

    train = df_prophet[df_prophet["ds"].dt.year < 2017].copy()
    test  = df_prophet[df_prophet["ds"].dt.year == 2017].copy()

    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        seasonality_mode="multiplicative",
        changepoint_prior_scale=0.05,
        interval_width=0.95,
    )
    model.add_regressor("cours_brent", mode="multiplicative")
    model.fit(train)

    future_test = test[["ds", "cours_brent"]].copy()
    forecast    = model.predict(future_test)

    y_true = test["y"].values
    y_pred = forecast["yhat"].values

    mae  = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    r2   = r2_score(y_true, y_pred)

    predictions = pd.DataFrame({
        "date_mois":      test["ds"].dt.strftime("%Y-%m-%d"),
        "reel_m3":        y_true,
        "prediction_m3":  y_pred,
        "borne_basse_m3": forecast["yhat_lower"].values,
        "borne_haute_m3": forecast["yhat_upper"].values,
        "erreur_m3":      y_true - y_pred,
        "erreur_abs_m3":  np.abs(y_true - y_pred),
    })

    return {
        "metrics":     {"MAE": round(mae, 2), "RMSE": round(rmse, 2), "MAPE": round(mape, 2), "R2": round(r2, 4)},
        "predictions": predictions,
        "train_size":  len(train),
        "test_size":   len(test),
    }


def _build_context_2017(ml_results: dict, df_ventes: pd.DataFrame) -> dict:
    """Construit le contexte agent à partir des données 2017."""
    df = df_ventes.sort_values("date_mois").copy()
    df["date_mois"] = pd.to_datetime(df["date_mois"])

    latest    = df.iloc[-1]
    last_12   = df.tail(min(12, len(df)))
    latest_qty = float(latest["total_quantite_m3"])
    latest_brent = float(latest.get("cours_brent_moyen_usd", 0) or 0)

    trend_3m = 0.0
    if len(df) >= 4:
        prev_3 = float(df.iloc[-4]["total_quantite_m3"])
        trend_3m = ((latest_qty - prev_3) / prev_3 * 100.0) if prev_3 else 0.0

    pred = ml_results["predictions"]
    error_mae  = float(pred["erreur_abs_m3"].mean())
    error_rmse = float((pred["erreur_m3"] ** 2).mean() ** 0.5)

    return {
        "status": "ok",
        "signals": {
            "latest_date":          str(pd.to_datetime(latest["date_mois"]).date()),
            "latest_qty_m3":        latest_qty,
            "latest_brent_usd":     latest_brent,
            "mean_qty_last_12_m3":  float(last_12["total_quantite_m3"].mean()),
            "std_qty_last_12_m3":   float(last_12["total_quantite_m3"].std()),
            "qty_trend_3m_pct":     trend_3m,
            "mae_test_m3":          error_mae,
            "rmse_test_m3":         error_rmse,
        },
        "ml_results": ml_results,
    }


# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Paramètres")
    user_label = st.text_input("Utilisateur", value="analyste_cbn")
    if st.button("Générer recommandations", use_container_width=True):
        st.session_state["payload_2017"] = None  # force recalcul

if "payload_2017" not in st.session_state:
    st.session_state["payload_2017"] = None

if st.session_state["payload_2017"] is None:
    with st.spinner("Chargement des données..."):
        ml_results = _entrainer_et_evaluer_2017()
        df_ventes  = charger_donnees_mensuelles()
    context = _build_context_2017(ml_results, df_ventes)
    recs    = generate_recommendations(context)
    st.session_state["payload_2017"] = {"context": context, "recs": recs, "ml": ml_results}

payload = st.session_state["payload_2017"]
context = payload["context"]
recs    = payload["recs"]
ml      = payload["ml"]
signals = context["signals"]

# ─── Métriques du modèle ───────────────────────────────────────────────────────
st.markdown("### Métriques du modèle (train 2015-2016 / test 2017)")
m = ml["metrics"]
c1, c2, c3, c4 = st.columns(4)
c1.metric("MAE",  f"{m['MAE']:,.0f} m³")
c2.metric("RMSE", f"{m['RMSE']:,.0f} m³")
c3.metric("MAPE", f"{m['MAPE']:.1f}%")
c4.metric("R²",   f"{m['R2']:.4f}")

st.markdown("---")

# ─── Signaux ──────────────────────────────────────────────────────────────────
st.markdown("### Signaux détectés")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Dernier volume (m³)", f"{signals['latest_qty_m3']:,.0f}".replace(",", " "))
col2.metric("Brent (USD/baril)",   f"{signals['latest_brent_usd']:,.2f}")
col3.metric("Tendance 3 mois",     f"{signals['qty_trend_3m_pct']:,.1f}%")
col4.metric("MAE test (m³)",       f"{signals['mae_test_m3']:,.0f}".replace(",", " "))

st.markdown("---")

# ─── Recommandations ──────────────────────────────────────────────────────────
st.markdown("### Recommandations")
if not recs:
    st.info("Aucune recommandation générée.")
else:
    for rec in recs:
        with st.container(border=True):
            st.markdown(f"**Règle déclenchée** : `{rec.get('id', 'n/a')}`")
            st.markdown(f"**Action** : `{rec.get('type_action', 'n/a')}`")
            st.markdown(f"**Priorité** : `{rec.get('priority', 'n/a')}` | **Confiance** : `{rec.get('confidence', 0)}%`")
            st.write(f"**Raison** : {rec.get('reason', '-')}")
            st.write(f"**Impact estimé** : {rec.get('impact_estime', '-')}")
            st.write(f"**Proposition** : {rec.get('proposal', '-')}")

# ─── Comparatif réel vs prédit ────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Réel vs Prédit — 2017")
st.dataframe(
    ml["predictions"].style.format({
        "reel_m3":        "{:,.0f}",
        "prediction_m3":  "{:,.0f}",
        "borne_basse_m3": "{:,.0f}",
        "borne_haute_m3": "{:,.0f}",
        "erreur_m3":      "{:,.0f}",
        "erreur_abs_m3":  "{:,.0f}",
    }),
    use_container_width=True,
    hide_index=True,
)
