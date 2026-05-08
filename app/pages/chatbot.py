"""Page Chatbot - Assistant CBN Analytics bilingue, sans API externe."""

import os
import sys

import streamlit as st


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.ui import render_navbar, page_header  # noqa: E402
from chatbot.entity_extractor import extract_depot, extract_month, extract_year  # noqa: E402
from chatbot.intent_detector import detect_intent, detect_language  # noqa: E402
from chatbot.query_engine import repondre  # noqa: E402


render_navbar("Chatbot")
page_header("Assistant CBN", "Posez vos questions en francais ou en anglais sur les ventes de gasoil")

if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = [
        {
            "role": "assistant",
            "content": (
                "Bonjour ! Je suis l'assistant CBN Analytics.\n\n"
                "Je peux repondre a vos questions sur les **ventes de gasoil** "
                "(2015-2018) : volumes, prix, depots, tendances, cours du Brent.\n\n"
                "I also understand English. Type **aide** or **help** to see examples."
            ),
        }
    ]

for msg in st.session_state["chat_messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Posez votre question ici... / Ask your question here...")

if prompt:
    st.session_state["chat_messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    lang = detect_language(prompt)
    intent = detect_intent(prompt)
    year = extract_year(prompt)
    month = extract_month(prompt)
    depot = extract_depot(prompt)
    answer = repondre(intent, year=year, month=month, depot=depot, lang=lang)

    st.session_state["chat_messages"].append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer)

st.markdown("---")
col, _ = st.columns([1, 4])
with col:
    if st.button("Effacer la conversation", use_container_width=True):
        st.session_state["chat_messages"] = [
            {
                "role": "assistant",
                "content": (
                    "Conversation effacee. Comment puis-je vous aider ?\n\n"
                    "Tapez **aide** ou **help** pour voir ce que je sais faire."
                ),
            }
        ]
        st.rerun()
