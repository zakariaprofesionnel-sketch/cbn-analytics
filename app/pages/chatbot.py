"""Page Chatbot — Assistant CBN Analytics (rule-based, sans API externe)"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.ui import render_navbar, page_header, inject_css
from chatbot.intent_detector import detect_intent
from chatbot.entity_extractor import extract_year, extract_month, extract_depot
from chatbot.query_engine import repondre

render_navbar("Chatbot")
page_header("Assistant CBN", "Posez vos questions sur les données de ventes de gasoil")

# ── Initialisation historique ────────────────────────────────────────────────
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = [
        {
            "role": "assistant",
            "content": (
                "Bonjour ! Je suis l'assistant CBN Analytics.\n\n"
                "Je peux répondre à vos questions sur les **ventes de gasoil** "
                "(2015–2018) : volumes, prix, dépôts, tendances, cours du Brent…\n\n"
                "Tapez **aide** pour voir la liste complète."
            ),
        }
    ]

# ── Affichage de l'historique ────────────────────────────────────────────────
for msg in st.session_state["chat_messages"]:
    with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])

# ── Saisie utilisateur ───────────────────────────────────────────────────────
prompt = st.chat_input("Posez votre question ici…")

if prompt:
    # Afficher le message utilisateur
    st.session_state["chat_messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Traitement
    intent = detect_intent(prompt)
    year   = extract_year(prompt)
    month  = extract_month(prompt)
    depot  = extract_depot(prompt)
    answer = repondre(intent, year=year, month=month, depot=depot)

    # Afficher la réponse
    st.session_state["chat_messages"].append({"role": "assistant", "content": answer})
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(answer)

# ── Bouton reset ─────────────────────────────────────────────────────────────
st.markdown("---")
col, _ = st.columns([1, 4])
with col:
    if st.button("Effacer la conversation", use_container_width=True):
        st.session_state["chat_messages"] = [
            {
                "role": "assistant",
                "content": (
                    "Conversation effacée. Comment puis-je vous aider ?\n\n"
                    "Tapez **aide** pour voir ce que je sais faire."
                ),
            }
        ]
        st.rerun()
