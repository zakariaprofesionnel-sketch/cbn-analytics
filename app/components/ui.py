"""Composants UI partagés — AGIL Analytics"""
import streamlit as st

# ── Palette AGIL ────────────────────────────────────────────────────────────
AGIL_YELLOW  = "#FFD100"
AGIL_BLACK   = "#1C1C1C"
AGIL_WHITE   = "#FFFFFF"
AGIL_GRAY    = "#F4F4F4"
AGIL_BORDER  = "#E8E8E8"
AGIL_TEXT_MUTED = "#6B6B6B"

# ── Couleurs graphiques ──────────────────────────────────────────────────────
CHART_COLORS = ["#FFD100", "#1C1C1C", "#0066CC", "#00A651", "#CC4400", "#7B2D8B"]
CHART_LINE_WIDTH = 3.5   # épaisseur standard des lignes de graphique

# ── Pages & chemins ─────────────────────────────────────────────────────────
NAV_PAGES = [
    "Accueil",
    "Tableau de Bord",
    "Analyse",
    "Previsions",
    "Exploration",
    "Agent IA",
    "Chatbot",
    "Connexion",
]

PAGE_PATHS = {
    "Accueil":         "pages/accueil.py",
    "Tableau de Bord": "pages/tableau_de_bord.py",
    "Analyse":         "pages/analyse_historique.py",
    "Previsions":      "pages/previsions.py",
    "Exploration":     "pages/exploration.py",
    "Agent IA":        "pages/agent_ia.py",
    "Chatbot":         "pages/chatbot.py",
    "Connexion":       "pages/login.py",
}

PAGE_ICONS = {
    "Accueil":         "house-fill",
    "Tableau de Bord": "bar-chart-fill",
    "Analyse":         "graph-up-arrow",
    "Previsions":      "cpu-fill",
    "Exploration":     "table",
    "Agent IA":        "robot",
    "Chatbot":         "chat-dots-fill",
    "Connexion":       "person-circle",
}

# ── CSS global ──────────────────────────────────────────────────────────────
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif !important;
    font-size: 18px !important;
    color: #2C2C2C !important;
}

/* Couleur de texte forcée partout — aucun texte blanc sur fond clair */
p, span, div, label, h1, h2, h3, h4, h5, h6,
.stMarkdown, .stText, [class*="st-"] {
    color: #2C2C2C;
}

/* Fond blanc cassé */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main {
    background-color: #F8F7F4 !important;
}

/* Masquer l'interface Streamlit par défaut */
#MainMenu                        { visibility: hidden !important; }
footer                           { visibility: hidden !important; }
header                           { visibility: hidden !important; }
.stDeployButton                  { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }
[data-testid="stDecoration"]     { display: none !important; }
[data-testid="stStatusWidget"]   { display: none !important; }

/* Supprimer tout espace au-dessus de la navbar */
.stApp > div:first-child         { padding-top: 0 !important; margin-top: 0 !important; }
[data-testid="stAppViewContainer"] > section { padding-top: 0 !important; }
.main .block-container {
    padding-top: 0 !important;
    padding-left: 2.5rem !important;
    padding-right: 2.5rem !important;
    max-width: 1400px !important;
}
/* Option-menu doit coller au top */
div[data-testid="stVerticalBlock"] > div:first-child {
    margin-top: 0 !important;
    padding-top: 0 !important;
}

/* En-tête de page */
.agil-page-header {
    padding: 1.6rem 0 1rem 0;
    border-bottom: 3px solid #FFD100;
    margin-bottom: 2rem;
}
.agil-page-header h1 {
    font-size: 2.3rem !important;
    font-weight: 700 !important;
    color: #1C1C1C !important;
    margin: 0 !important;
    padding: 0 !important;
    letter-spacing: -0.4px;
    line-height: 1.2;
}
.agil-page-header .subtitle {
    font-size: 1.1rem;
    color: #555555;
    margin: 0.4rem 0 0 0;
    font-weight: 400;
}

/* Titres de section */
.agil-section {
    font-size: 0.9rem !important;
    font-weight: 700 !important;
    color: #555555 !important;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin: 2rem 0 0.75rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #E8E8E8;
}

/* Cards métriques */
[data-testid="metric-container"] {
    background: #FFFFFF !important;
    border: 1px solid #E2E2DF !important;
    border-left: 5px solid #FFD100 !important;
    border-radius: 16px !important;
    padding: 1.3rem 1.5rem !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05) !important;
    transition: box-shadow 0.2s ease;
}
[data-testid="metric-container"]:hover {
    box-shadow: 0 6px 20px rgba(0,0,0,0.09) !important;
}
[data-testid="metric-container"] *,
[data-testid="metric-container"] label,
[data-testid="metric-container"] p,
[data-testid="metric-container"] span,
[data-testid="metric-container"] div {
    color: #2C2C2C !important;
}
[data-testid="metric-container"] label,
[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] * {
    font-size: 0.88rem !important;
    font-weight: 700 !important;
    color: #555555 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"],
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] * {
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: #1C1C1C !important;
}
[data-testid="stMetricDelta"],
[data-testid="stMetricDelta"] * {
    color: #2C2C2C !important;
}

/* Boutons principaux */
.stButton {
    display: flex !important;
    justify-content: center !important;
}
.stButton > button[kind="primary"],
.stButton > button {
    background-color: #FFD100 !important;
    color: #1C1C1C !important;
    border: none !important;
    border-radius: 14px !important;
    font-weight: 700 !important;
    font-size: 1.05rem !important;
    padding: 0.65rem 2rem !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.2px;
    font-family: 'Inter', sans-serif !important;
    min-width: 120px;
}
.stButton > button:hover {
    background-color: #E5BA00 !important;
    box-shadow: 0 4px 16px rgba(255,209,0,0.45) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* Séparateurs */
hr {
    border: none !important;
    border-top: 1px solid #E8E8E8 !important;
    margin: 1.5rem 0 !important;
}

/* DataFrames */
[data-testid="stDataFrame"] {
    border-radius: 16px !important;
    overflow: hidden !important;
    border: 1px solid #E2E2DF !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
}

/* Charts Plotly */
[data-testid="stPlotlyChart"] {
    border-radius: 16px;
    border: 1px solid #E2E2DF;
    overflow: hidden;
    background: white;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

/* Inputs — texte toujours visible */
input, textarea, [data-baseweb="input"] input,
[data-baseweb="textarea"] textarea,
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stChatInput"] textarea {
    background-color: #FFFFFF !important;
    color: #1C1C1C !important;
    border-radius: 12px !important;
    border-color: #E2E2DF !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1.05rem !important;
    padding: 0.6rem 1rem !important;
    caret-color: #1C1C1C !important;
}
input:focus, textarea:focus,
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus,
[data-testid="stTextArea"] textarea:focus,
[data-testid="stChatInput"] textarea:focus {
    border-color: #FFD100 !important;
    box-shadow: 0 0 0 3px rgba(255,209,0,0.2) !important;
}
input::placeholder, textarea::placeholder {
    color: #AAAAAA !important;
    opacity: 1 !important;
}

/* Expander */
.streamlit-expanderHeader {
    font-weight: 600 !important;
    font-size: 1.05rem !important;
    color: #2C2C2C !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stExpander"] {
    border-radius: 14px !important;
    border-color: #E2E2DF !important;
    overflow: hidden !important;
}

/* Alertes */
.stAlert {
    border-radius: 14px !important;
    font-size: 1rem !important;
}

/* Slider */
[data-testid="stSlider"] > div > div > div {
    background-color: #FFD100 !important;
}

/* Selectbox / Multiselect */
[data-baseweb="select"] > div {
    border-radius: 12px !important;
    border-color: #E2E2DF !important;
    font-size: 1rem !important;
    color: #2C2C2C !important;
}

/* Conteneur general des widgets — arrondi */
[data-testid="stForm"] {
    border-radius: 18px !important;
    border-color: #E2E2DF !important;
    padding: 1.5rem !important;
    background: #FFFFFF !important;
}

/* Navbar option-menu override */
.nav-container {
    margin-bottom: 0 !important;
}

/* Force texte sombre sur tous les composants Streamlit */
[data-testid="stMarkdownContainer"] *,
[data-testid="stText"] *,
[data-testid="stCaption"] *,
.stMarkdown p,
.stMarkdown span,
.stMarkdown li,
.element-container p,
.element-container span {
    color: #2C2C2C !important;
}

/* Titres Streamlit natifs */
[data-testid="stHeading"],
[data-testid="stHeading"] * {
    color: #1C1C1C !important;
}

/* Caption */
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] * {
    color: #666666 !important;
    font-size: 0.85rem !important;
}
</style>
"""


def inject_css() -> None:
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def render_navbar(current_page: str = "Accueil") -> None:
    from streamlit_option_menu import option_menu

    # Pages affichées dans la navbar (sans Connexion)
    nav_items = [p for p in NAV_PAGES if p != "Connexion"]
    idx = nav_items.index(current_page) if current_page in nav_items else 0
    icons = [PAGE_ICONS[p] for p in nav_items]

    # Ligne navbar + bouton deconnexion
    nav_col, logout_col = st.columns([9, 1])

    with nav_col:
        selected = option_menu(
            menu_title=None,
            options=nav_items,
            icons=icons,
            default_index=idx,
            orientation="horizontal",
            styles={
                "container": {
                    "padding": "0 !important",
                    "background-color": "#1C1C1C",
                    "border-radius": "0",
                    "margin": "0 !important",
                },
                "icon": {
                    "color": "#FFD100",
                    "font-size": "16px",
                },
                "nav-link": {
                    "font-family": "Inter, sans-serif",
                    "font-size": "16px",
                    "font-weight": "500",
                    "color": "#DDDDDD",
                    "padding": "14px 18px",
                    "border-radius": "0",
                    "--hover-color": "#2D2D2D",
                },
                "nav-link-selected": {
                    "background-color": "#FFD100",
                    "color": "#1C1C1C",
                    "font-weight": "700",
                },
            },
        )

    with logout_col:
        st.markdown(
            """<div style="background:#1C1C1C;height:52px;display:flex;
            align-items:center;justify-content:center;">""",
            unsafe_allow_html=True,
        )
        if st.button("Deconnexion", key="logout_btn"):
            st.session_state.clear()
            st.switch_page("pages/login.py")
        st.markdown("</div>", unsafe_allow_html=True)

    # Navigation
    if selected != current_page:
        st.switch_page(PAGE_PATHS[selected])


def page_header(title: str, subtitle: str = "") -> None:
    sub_html = f'<p class="subtitle">{subtitle}</p>' if subtitle else ""
    st.markdown(
        f'<div class="agil-page-header"><h1>{title}</h1>{sub_html}</div>',
        unsafe_allow_html=True,
    )


def section_title(text: str) -> None:
    st.markdown(f'<p class="agil-section">{text}</p>', unsafe_allow_html=True)


def card(title: str, body: str, accent: str = AGIL_YELLOW) -> None:
    st.markdown(
        f"""
        <div style="background:#fff;border:1px solid #E8E8E8;border-top:4px solid {accent};
        border-radius:10px;padding:1.4rem 1.5rem;box-shadow:0 2px 10px rgba(0,0,0,0.04);
        margin-bottom:0.5rem;">
        <h3 style="font-size:1.14rem;font-weight:700;color:#1C1C1C;margin:0 0 0.4rem 0;
        font-family:Inter,sans-serif;">{title}</h3>
        <p style="font-size:0.99rem;color:#6B6B6B;margin:0;line-height:1.5;
        font-family:Inter,sans-serif;">{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def agil_chart_layout(title: str = "", height: int = 450) -> dict:
    return dict(
        title=dict(
            text=title,
            font=dict(size=16, color="#1C1C1C", family="Inter"),
            x=0,
            pad=dict(l=0, t=4),
        ),
        font=dict(family="Inter, sans-serif", size=14, color="#1C1C1C"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=56, r=28, t=54 if title else 28, b=48),
        xaxis=dict(
            showgrid=False,
            linecolor="#E8E8E8",
            tickfont=dict(size=13, color="#6B6B6B"),
        ),
        yaxis=dict(
            gridcolor="#F0F0F0",
            linecolor="#E8E8E8",
            tickfont=dict(size=13, color="#6B6B6B"),
        ),
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=13),
            bgcolor="rgba(0,0,0,0)",
        ),
        height=height,
    )
