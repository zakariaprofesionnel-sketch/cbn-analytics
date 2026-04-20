"""Page 6: Agent IA CBN - aide a la decision semi-automatique."""

import os
import sys
import pickle

import pandas as pd
import streamlit as st

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(APP_DIR)
sys.path.insert(0, APP_DIR)
sys.path.insert(0, ROOT_DIR)

from agent.decision_agent import run_decision_agent  # noqa: E402
from agent.executor import record_decision, load_decision_history  # noqa: E402


def _load_metriques() -> dict:
    path = os.path.join(ROOT_DIR, "ml", "metriques.pkl")
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    return {}


st.set_page_config(page_title="Agent IA CBN", page_icon="🧠", layout="wide")
st.title("🧠 Agent IA CBN - Aide a la decision")
st.caption("Mode semi-automatique: l'agent propose, l'utilisateur valide ou rejette.")

if "agent_payload" not in st.session_state:
    st.session_state["agent_payload"] = None
if "agent_feedback" not in st.session_state:
    st.session_state["agent_feedback"] = ""

with st.sidebar:
    st.markdown("### Parametres")
    user_label = st.text_input("Utilisateur", value="analyste_cbn")
    if st.button("Generer recommandations", use_container_width=True):
        payload = run_decision_agent()
        payload["ml_metrics"] = _load_metriques()
        st.session_state["agent_payload"] = payload
        st.session_state["agent_feedback"] = ""

payload = st.session_state["agent_payload"]
if payload is None:
    st.info("Cliquez sur 'Generer recommandations' pour lancer l'agent.")
    st.stop()

if payload.get("status") != "ok":
    st.warning(payload.get("message", "Contexte indisponible."))
    st.stop()

signals = payload.get("signals", {})
recs = payload.get("recommendations", [])

st.markdown("### Métriques du modèle (train 2015-2017 / test 2018)")
m_col1, m_col2, m_col3, m_col4 = st.columns(4)
ml_metrics = payload.get("ml_metrics", {})
m_col1.metric("MAE",  f"{ml_metrics.get('MAE', 0):,.0f} m³")
m_col2.metric("RMSE", f"{ml_metrics.get('RMSE', 0):,.0f} m³")
m_col3.metric("MAPE", f"{ml_metrics.get('MAPE', 0):.1f}%")
m_col4.metric("R²",   f"{ml_metrics.get('R2', 0):.4f}")

st.markdown("---")
st.markdown("### Signaux detectes")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Dernier volume (m3)", f"{signals.get('latest_qty_m3', 0):,.0f}".replace(",", " "))
with col2:
    st.metric("Brent (USD/baril)", f"{signals.get('latest_brent_usd', 0):,.2f}")
with col3:
    st.metric("Tendance 3 mois", f"{signals.get('qty_trend_3m_pct', 0):,.1f}%")
with col4:
    st.metric("MAE test (m3)", f"{signals.get('mae_test_m3', 0):,.0f}".replace(",", " "))

st.markdown("---")
st.markdown("### Recommandations")
if not recs:
    st.info("Aucune recommandation disponible.")
else:
    for rec in recs:
        with st.container(border=True):
            st.markdown(f"**Règle déclenchée** : `{rec.get('id', 'n/a')}`")
            st.markdown(f"**Action**: `{rec.get('type_action', 'n/a')}`")
            st.markdown(f"**Priorite**: `{rec.get('priority', 'n/a')}` | **Confiance**: `{rec.get('confidence', 0)}%`")
            st.write(f"**Raison**: {rec.get('reason', '-')}")
            st.write(f"**Impact estime**: {rec.get('impact_estime', '-')}")
            st.write(f"**Proposition**: {rec.get('proposal', '-')}")
            if rec.get("llm_note"):
                st.caption(rec["llm_note"])

            a_col, r_col = st.columns(2)
            with a_col:
                if st.button("Valider", key=f"approve_{rec['id']}", use_container_width=True):
                    res = record_decision(rec, decision="validated", user_label=user_label)
                    st.session_state["agent_feedback"] = (
                        f"Recommendation {rec['id']} validee (log: {res['stored_in']})."
                    )
                    st.rerun()
            with r_col:
                if st.button("Rejeter", key=f"reject_{rec['id']}", use_container_width=True):
                    res = record_decision(rec, decision="rejected", user_label=user_label)
                    st.session_state["agent_feedback"] = (
                        f"Recommendation {rec['id']} rejetee (log: {res['stored_in']})."
                    )
                    st.rerun()

if st.session_state["agent_feedback"]:
    st.success(st.session_state["agent_feedback"])

st.markdown("---")
st.markdown("### Historique des decisions")
df_hist = load_decision_history(limit=200)
if isinstance(df_hist, pd.DataFrame) and not df_hist.empty:
    st.dataframe(df_hist, use_container_width=True, hide_index=True)
else:
    st.info("Aucun historique disponible pour le moment.")

