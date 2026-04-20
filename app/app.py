"""CBN Analytics — AGIL Tunisie | Routeur principal"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from components.ui import inject_css

st.set_page_config(
    page_title="CBN Analytics — AGIL Tunisie",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()

pg = st.navigation(
    [
        st.Page("pages/login.py",               title="Connexion",       url_path="connexion"),
        st.Page("pages/accueil.py",             title="Accueil",         url_path="accueil"),
        st.Page("pages/tableau_de_bord.py",     title="Tableau de Bord", url_path="tableau-de-bord"),
        st.Page("pages/analyse_historique.py",  title="Analyse",         url_path="analyse"),
        st.Page("pages/previsions.py",          title="Previsions",      url_path="previsions"),
        st.Page("pages/exploration.py",         title="Exploration",     url_path="exploration"),
        st.Page("pages/agent_ia.py",            title="Agent IA",        url_path="agent-ia"),
        st.Page("pages/chatbot.py",             title="Chatbot",         url_path="chatbot"),
    ],
    position="hidden",
)

# Garde d'authentification : toutes les pages sauf Connexion exigent une session active
if not st.session_state.get("authenticated", False) and pg.title != "Connexion":
    st.switch_page("pages/login.py")

pg.run()
