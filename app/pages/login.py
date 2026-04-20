"""Page Connexion — CBN Analytics AGIL"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── Comptes autorisés (email → {password, nom}) ─────────────────────────────
USERS = {
    "admin@agil.com.tn":    {"password": "admin123",    "nom": "Administrateur"},
    "analyste@agil.com.tn": {"password": "analyste123", "nom": "Analyste CBN"},
}

# ── Si déjà connecté, rediriger directement ──────────────────────────────────
if st.session_state.get("authenticated", False):
    st.switch_page("pages/accueil.py")

# ── Page sans navbar (page publique) ────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)

_, center, _ = st.columns([1, 1.3, 1])

with center:

    # Logo + titre
    st.markdown(
        """
        <div style="text-align:center;margin-bottom:2rem;">
            <div style="display:inline-block;background:#1C1C1C;color:#FFD100;
            font-size:1.5rem;font-weight:900;padding:0.55rem 1.1rem;border-radius:12px;
            letter-spacing:2px;font-family:Inter,sans-serif;margin-bottom:1rem;">
                AGIL
            </div>
            <h2 style="font-size:1.7rem;font-weight:700;color:#1C1C1C;margin:0;
            font-family:Inter,sans-serif;">Connexion</h2>
            <p style="font-size:1rem;color:#555555;margin:0.4rem 0 0 0;
            font-family:Inter,sans-serif;">CBN Analytics — Acces securise</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("login_form", clear_on_submit=False):
        email = st.text_input(
            "Adresse email",
            placeholder="exemple@agil.com.tn",
        )
        password = st.text_input(
            "Mot de passe",
            type="password",
            placeholder="••••••••",
        )
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Se connecter", use_container_width=True)

    # ── Validation ────────────────────────────────────────────────────────────
    if submitted:
        if not email or not password:
            st.warning("Veuillez renseigner votre email et votre mot de passe.")
        elif email in USERS and USERS[email]["password"] == password:
            st.session_state["authenticated"] = True
            st.session_state["user_email"]    = email
            st.session_state["user_nom"]      = USERS[email]["nom"]
            st.switch_page("pages/accueil.py")
        else:
            st.error("Email ou mot de passe incorrect.")

    st.markdown(
        """
        <p style="text-align:center;font-size:0.88rem;color:#888888;margin-top:1.5rem;
        font-family:Inter,sans-serif;">
            CBN Analytics v1.0 — AGIL Tunisie<br>
            Acces reserve au personnel autorise
        </p>
        """,
        unsafe_allow_html=True,
    )
