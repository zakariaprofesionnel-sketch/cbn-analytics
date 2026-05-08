"""Page Agent IA CBN - Recommandations semi-automatiques."""
import streamlit as st
import pandas as pd
import pickle
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.ui import render_navbar, page_header, section_title, styled_dataframe, CHART_COLORS, AGIL_YELLOW, AGIL_BLACK
from agent.decision_agent import run_decision_agent
from agent.executor import record_decision, load_decision_history

render_navbar("Agent IA")
page_header("Agent IA CBN", "Recommandations semi-automatiques - l'agent propose, l'utilisateur valide")


def _charger_metriques() -> dict:
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    path = os.path.join(root, "ml", "metriques.pkl")
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    return {}


# ── Session state ─────────────────────────────────────────────────────────────
if "agent_payload" not in st.session_state:
    st.session_state["agent_payload"] = None
if "agent_feedback" not in st.session_state:
    st.session_state["agent_feedback"] = ""

# ── Controles ─────────────────────────────────────────────────────────────────
section_title("Parametres")

c1, c2, c3 = st.columns([2, 2, 1.5])
with c1:
    user_label = st.text_input("Identifiant utilisateur", value="analyste_cbn")
with c2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Generer les recommandations", use_container_width=True):
        payload = run_decision_agent()
        payload["ml_metrics"] = _charger_metriques()
        st.session_state["agent_payload"] = payload
        st.session_state["agent_feedback"] = ""

payload = st.session_state["agent_payload"]

if payload is None:
    st.info("Cliquez sur 'Generer les recommandations' pour lancer l'analyse.")
    st.stop()

if payload.get("status") != "ok":
    st.warning(payload.get("message", "Contexte indisponible."))
    st.stop()

signals = payload.get("signals", {})
recs    = payload.get("recommendations", [])

# ── Metriques ML ──────────────────────────────────────────────────────────────
section_title("Metriques du modele retenu (train 2015-2016 / test 2017)")

ml = payload.get("ml_metrics", {})
best_model = ml.get("best_model", "Prophet")
best_metrics = ml.get(best_model, ml)
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric(f"MAE ({best_model})", f"{best_metrics.get('MAE', 0):,.0f} m3".replace(",", " "))
with c2:
    st.metric("RMSE", f"{best_metrics.get('RMSE', 0):,.0f} m3".replace(",", " "))
with c3:
    st.metric("MAPE", f"{best_metrics.get('MAPE', 0):.1f}%")
with c4:
    st.metric("R2", f"{best_metrics.get('R2', 0):.4f}")

st.markdown("---")

# ── Signaux detectes ──────────────────────────────────────────────────────────
section_title("Signaux detectes")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Dernier volume (m3)", f"{signals.get('latest_qty_m3', 0):,.0f}".replace(",", " "))
with c2:
    st.metric("Brent (USD/baril)", f"{signals.get('latest_brent_usd', 0):,.2f}")
with c3:
    st.metric("Tendance 3 mois", f"{signals.get('qty_trend_3m_pct', 0):,.1f}%")
with c4:
    st.metric("MAE test (m3)", f"{signals.get('mae_test_m3', 0):,.0f}".replace(",", " "))

st.markdown("---")

# ── Recommandations ───────────────────────────────────────────────────────────
section_title("Recommandations")

PRIORITY_COLOR = {"haute": "#CC4400", "moyenne": AGIL_YELLOW, "faible": "#00A651"}

if not recs:
    st.info("Aucune recommandation disponible pour le moment.")
else:
    for rec in recs:
        priority = rec.get("priority", "faible")
        border_color = PRIORITY_COLOR.get(priority, AGIL_BLACK)

        st.markdown(
            f"""
            <div style="background:#FFFFFF;border:1px solid #DDD7C8;
            border-left:6px solid {border_color};border-radius:16px;
            padding:1.25rem 1.45rem;margin-bottom:1rem;
            box-shadow:0 14px 34px rgba(38,38,38,0.08);">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;
                margin-bottom:0.6rem;">
                    <span style="font-weight:850;font-size:0.98rem;color:#262626;
                    font-family:Manrope,Segoe UI,Arial,sans-serif;">{rec.get('type_action', 'N/A')}</span>
                    <div style="display:flex;gap:0.5rem;">
                        <span style="background:{border_color};color:{'#F0F0F0' if priority == 'haute' else '#1C1C1C'};
                        font-size:0.75rem;font-weight:850;padding:4px 11px;border-radius:999px;
                        font-family:Manrope,Segoe UI,Arial,sans-serif;text-transform:uppercase;">
                            {priority}
                        </span>
                        <span style="background:#F2E9C7;color:#262626;
                        font-size:0.75rem;font-weight:750;padding:4px 11px;border-radius:999px;
                        font-family:Manrope,Segoe UI,Arial,sans-serif;">
                            {rec.get('confidence', 0)}% confiance
                        </span>
                    </div>
                </div>
                <p style="font-size:0.94rem;color:#444;margin:0 0 0.45rem 0;
                font-family:Manrope,Segoe UI,Arial,sans-serif;line-height:1.55;"><strong>Raison :</strong> {rec.get('reason', '-')}</p>
                <p style="font-size:0.94rem;color:#444;margin:0 0 0.45rem 0;
                font-family:Manrope,Segoe UI,Arial,sans-serif;line-height:1.55;"><strong>Impact estime :</strong> {rec.get('impact_estime', '-')}</p>
                <p style="font-size:0.94rem;color:#444;margin:0;
                font-family:Manrope,Segoe UI,Arial,sans-serif;line-height:1.55;"><strong>Proposition :</strong> {rec.get('proposal', '-')}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        a_col, r_col, _ = st.columns([1, 1, 3])
        with a_col:
            if st.button("Valider", key=f"approve_{rec['id']}", use_container_width=True):
                res = record_decision(rec, decision="validated", user_label=user_label)
                st.session_state["agent_feedback"] = (
                    f"Recommandation {rec['id']} validee (log : {res['stored_in']})."
                )
                st.rerun()
        with r_col:
            if st.button("Rejeter", key=f"reject_{rec['id']}", use_container_width=True):
                res = record_decision(rec, decision="rejected", user_label=user_label)
                st.session_state["agent_feedback"] = (
                    f"Recommandation {rec['id']} rejetee (log : {res['stored_in']})."
                )
                st.rerun()

if st.session_state["agent_feedback"]:
    st.success(st.session_state["agent_feedback"])

# ── Historique ────────────────────────────────────────────────────────────────
st.markdown("---")
section_title("Historique des decisions")

df_hist = load_decision_history(limit=200)
if isinstance(df_hist, pd.DataFrame) and not df_hist.empty:
    styled_dataframe(df_hist, hide_index=True)
else:
    st.info("Aucun historique disponible pour le moment.")
