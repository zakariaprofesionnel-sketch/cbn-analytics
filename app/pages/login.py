"""Page Connexion - acces par code unique."""

import os
import sys

import streamlit as st


ACCESS_CODE = os.environ.get("CBN_ACCESS_CODE", "AGIL2026")


if st.session_state.get("authenticated", False):
    st.switch_page("pages/accueil.py")


st.markdown(
    """
    <style>
    .main .block-container {
        max-width: 720px !important;
        padding: 4.5rem 2rem 2rem !important;
    }

    [data-testid="stAppViewContainer"] {
        background:
            linear-gradient(135deg, rgba(255, 209, 0, 0.18) 0%, rgba(255, 255, 255, 0) 36%),
            linear-gradient(180deg, #FBFAF4 0%, #F1F0EA 100%) !important;
    }

    .login-shell {
        width: 100%;
        margin: 0 auto;
        text-align: center;
    }

    .agil-logo {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 190px;
        height: 96px;
        margin: 0 auto 1.35rem;
        background: #FFD100;
        color: #2D2D2D !important;
        border: 4px solid #2D2D2D;
        border-radius: 8px;
        font-family: Manrope, Segoe UI, Arial, sans-serif;
        font-size: 3.1rem;
        font-weight: 900;
        letter-spacing: 0;
        line-height: 1;
        box-shadow: 0 18px 45px rgba(28, 28, 28, 0.16);
    }

    .login-title {
        margin: 0;
        color: #1C1C1C !important;
        font-family: Manrope, Segoe UI, Arial, sans-serif;
        font-size: 2.85rem !important;
        font-weight: 850;
        line-height: 1.08;
    }

    .login-subtitle {
        margin: 0.75rem 0 2rem;
        color: #4E4E4E !important;
        font-family: Manrope, Segoe UI, Arial, sans-serif;
        font-size: 1.2rem;
        font-weight: 500;
    }

    [data-testid="stForm"] {
        max-width: 520px;
        margin: 0 auto;
        padding: 2.2rem 2.25rem 2.35rem !important;
        border: 1px solid #DDD8C8 !important;
        border-top: 8px solid #FFD100 !important;
        border-radius: 8px !important;
        background: rgba(255, 255, 255, 0.96) !important;
        box-shadow: 0 22px 55px rgba(28, 28, 28, 0.13) !important;
    }

    [data-testid="stTextInput"] label,
    [data-testid="stTextInput"] label p {
        color: #1C1C1C !important;
        font-size: 1.15rem !important;
        font-weight: 800 !important;
    }

    [data-testid="stTextInput"] input {
        height: 54px !important;
        min-height: 54px !important;
        line-height: 1.3 !important;
        padding: 0.65rem 3rem 0.65rem 1rem !important;
        box-sizing: border-box !important;
        border: 2px solid #D7D1BF !important;
        border-radius: 8px !important;
        font-size: 1.08rem !important;
        font-weight: 700 !important;
    }

    [data-testid="stTextInput"] div[data-baseweb="input"] {
        min-height: 54px !important;
        height: 54px !important;
        align-items: center !important;
        overflow: visible !important;
    }

    [data-testid="stTextInput"] button {
        height: 38px !important;
        min-height: 38px !important;
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        align-self: center !important;
    }

    [data-testid="stTextInput"] input:focus {
        border-color: #FFD100 !important;
        box-shadow: 0 0 0 4px rgba(255, 209, 0, 0.26) !important;
    }

    .stFormSubmitButton > button {
        min-height: 60px;
        margin-top: 0.35rem;
        background: #FFD100 !important;
        color: #1C1C1C !important;
        border: 2px solid #1C1C1C !important;
        border-radius: 8px !important;
        font-size: 1.18rem !important;
        font-weight: 900 !important;
        box-shadow: 0 12px 24px rgba(28, 28, 28, 0.13) !important;
    }

    .login-footer {
        margin-top: 1.65rem;
        color: #676767 !important;
        font-family: Manrope, Segoe UI, Arial, sans-serif;
        font-size: 0.98rem;
        font-weight: 600;
        line-height: 1.55;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    """
    <div class="login-shell">
        <div class="agil-logo">AGIL</div>
        <h1 class="login-title">Connexion</h1>
        <p class="login-subtitle">Entrez le code d'acces pour ouvrir CBN Analytics</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.form("access_form", clear_on_submit=False):
    access_code = st.text_input(
        "Code d'acces",
        type="password",
        placeholder="Code d'acces",
    )
    st.markdown("<br>", unsafe_allow_html=True)
    submitted = st.form_submit_button("Acceder au site", use_container_width=True)

if submitted:
    if not access_code:
        st.warning("Veuillez saisir le code d'acces.")
    elif access_code == ACCESS_CODE:
        st.session_state["authenticated"] = True
        st.switch_page("pages/accueil.py")
    else:
        st.error("Code d'acces incorrect.")

st.markdown(
    """
    <p class="login-footer">
        CBN Analytics v1.0 - AGIL Tunisie<br>
        Acces reserve aux personnes autorisees
    </p>
    """,
    unsafe_allow_html=True,
)
