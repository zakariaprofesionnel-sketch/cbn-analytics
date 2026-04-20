"""Page Accueil — CBN Analytics AGIL"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.ui import render_navbar, page_header, section_title, card, AGIL_YELLOW, AGIL_BLACK
from utils import charger_stats_globales, formater_nombre

render_navbar("Accueil")

# ── Logo AGIL + titre ────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="display:flex;align-items:center;gap:1rem;padding:1.5rem 0 0.5rem 0;
    border-bottom:3px solid #FFD100;margin-bottom:2rem;">
        <div style="background:#1C1C1C;color:#FFD100;font-size:1.4rem;font-weight:900;
        padding:0.5rem 0.9rem;border-radius:8px;letter-spacing:1px;font-family:Inter,sans-serif;">
            AGIL
        </div>
        <div>
            <h1 style="font-size:1.75rem;font-weight:700;color:#1C1C1C;margin:0;
            font-family:Inter,sans-serif;letter-spacing:-0.3px;">
                CBN Analytics
            </h1>
            <p style="font-size:0.875rem;color:#6B6B6B;margin:0.2rem 0 0 0;
            font-family:Inter,sans-serif;">
                Plateforme d'analyse et de prevision des ventes de carburant — AGIL Tunisie
            </p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── KPIs globaux ─────────────────────────────────────────────────────────────
section_title("Indicateurs globaux 2015 — 2018")

stats = charger_stats_globales()

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Volume total (m3)", formater_nombre(stats["total_quantite"]))
with c2:
    st.metric("Chiffre d'affaires HT", formater_nombre(stats["total_montant"]) + " TND")
with c3:
    st.metric("Livraisons enregistrees", formater_nombre(stats["nb_livraisons"]))
with c4:
    st.metric("Periode couverte", "2015 — 2018")

st.markdown("---")

# ── Modules ──────────────────────────────────────────────────────────────────
section_title("Modules disponibles")

col1, col2, col3 = st.columns(3)
with col1:
    card(
        "Tableau de Bord",
        "KPIs synthetiques, evolution mensuelle et comparaison annuelle des ventes de gasoil.",
        AGIL_YELLOW,
    )
with col2:
    card(
        "Analyse Historique",
        "Correlation ventes vs cours du Brent, analyse trimestrielle et taux de variation.",
        AGIL_YELLOW,
    )
with col3:
    card(
        "Previsions IA",
        "Modele Prophet avec 3 scenarios de cours du Brent et intervalles de confiance a 95%.",
        AGIL_YELLOW,
    )

col1, col2, col3 = st.columns(3)
with col1:
    card(
        "Exploration",
        "Acces aux donnees brutes, statistiques descriptives et decomposition saisonniere.",
        AGIL_BLACK,
    )
with col2:
    card(
        "Agent IA CBN",
        "Recommandations semi-automatiques basees sur les signaux de ventes et de prevision.",
        AGIL_BLACK,
    )
with col3:
    card(
        "Chatbot Donnees",
        "Interrogez les donnees en langage naturel. Disponible dans la prochaine version.",
        "#AAAAAA",
    )

st.markdown("---")

# ── Architecture ─────────────────────────────────────────────────────────────
section_title("Architecture du pipeline")

a1, a2, a3, a4 = st.columns(4)

with a1:
    st.markdown(
        """
        <div style="text-align:center;padding:1.2rem;background:#FAFAFA;
        border:1px solid #E8E8E8;border-radius:10px;">
            <div style="font-size:1.5rem;margin-bottom:0.5rem;">01</div>
            <div style="font-weight:700;font-size:0.85rem;color:#1C1C1C;
            font-family:Inter,sans-serif;">Sources</div>
            <div style="font-size:0.75rem;color:#6B6B6B;margin-top:0.3rem;
            font-family:Inter,sans-serif;">Excel ventes + Yahoo Finance (Brent)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with a2:
    st.markdown(
        """
        <div style="text-align:center;padding:1.2rem;background:#FAFAFA;
        border:1px solid #E8E8E8;border-radius:10px;">
            <div style="font-size:1.5rem;margin-bottom:0.5rem;">02</div>
            <div style="font-weight:700;font-size:0.85rem;color:#1C1C1C;
            font-family:Inter,sans-serif;">Pipeline ETL</div>
            <div style="font-size:0.75rem;color:#6B6B6B;margin-top:0.3rem;
            font-family:Inter,sans-serif;">Extract → Transform → Load PostgreSQL</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with a3:
    st.markdown(
        """
        <div style="text-align:center;padding:1.2rem;background:#FAFAFA;
        border:1px solid #E8E8E8;border-radius:10px;">
            <div style="font-size:1.5rem;margin-bottom:0.5rem;">03</div>
            <div style="font-weight:700;font-size:0.85rem;color:#1C1C1C;
            font-family:Inter,sans-serif;">Modele ML</div>
            <div style="font-size:0.75rem;color:#6B6B6B;margin-top:0.3rem;
            font-family:Inter,sans-serif;">Prophet + regresseur Brent</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with a4:
    st.markdown(
        """
        <div style="text-align:center;padding:1.2rem;background:#FFD100;
        border:1px solid #E8E8E8;border-radius:10px;">
            <div style="font-size:1.5rem;margin-bottom:0.5rem;">04</div>
            <div style="font-weight:700;font-size:0.85rem;color:#1C1C1C;
            font-family:Inter,sans-serif;">Dashboard</div>
            <div style="font-size:0.75rem;color:#1C1C1C;margin-top:0.3rem;
            font-family:Inter,sans-serif;">KPIs + Previsions + Agent IA</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)
st.caption("CBN Analytics v1.0 — Projet de Fin d'Etudes | Licence Business Intelligence | AGIL Tunisie")
