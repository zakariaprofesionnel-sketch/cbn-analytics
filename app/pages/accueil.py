"""Page Accueil - CBN Analytics AGIL."""

import os
import sys

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.ui import (
    AGIL_BLACK,
    AGIL_YELLOW,
    brand_header,
    card,
    process_card,
    render_navbar,
    section_title,
)
from utils import charger_stats_globales, formater_nombre


render_navbar("Accueil")
brand_header(
    "CBN Analytics",
    "Plateforme d'analyse et de prevision des ventes de carburant - AGIL Tunisie",
)

section_title("Indicateurs globaux 2015 - 2018")

stats = charger_stats_globales()

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Volume total (m3)", formater_nombre(stats["total_quantite"]))
with c2:
    st.metric("Chiffre d'affaires HT", formater_nombre(stats["total_montant"]) + " TND")
with c3:
    st.metric("Livraisons enregistrees", formater_nombre(stats["nb_livraisons"]))
with c4:
    st.metric("Periode couverte", "2015 - 2018")

st.markdown("---")

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
        "#9A958A",
    )

st.markdown("---")

section_title("Architecture du pipeline")

a1, a2, a3, a4 = st.columns(4)
with a1:
    process_card("01", "Sources", "Excel ventes + Yahoo Finance (Brent)")
with a2:
    process_card("02", "Pipeline ETL", "Extract, Transform, Load PostgreSQL")
with a3:
    process_card("03", "Modele ML", "Prophet + regresseur Brent")
with a4:
    process_card("04", "Dashboard", "KPIs + Previsions + Agent IA", highlight=True)

st.markdown("<br>", unsafe_allow_html=True)
st.caption("CBN Analytics v1.0 - Projet de Fin d'Etudes | Licence Business Intelligence | AGIL Tunisie")
