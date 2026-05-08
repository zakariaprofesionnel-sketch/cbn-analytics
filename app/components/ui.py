"""Composants UI partages - AGIL Analytics."""

import streamlit as st


AGIL_YELLOW = "#FFD100"
AGIL_DARK = "#262626"
AGIL_BLACK = "#1C1C1C"
AGIL_WHITE = "#FFFFFF"
AGIL_BG = "#F7F5EF"
AGIL_SURFACE = "#FFFFFF"
AGIL_SURFACE_SOFT = "#FBFAF5"
AGIL_BORDER = "#DDD7C8"
AGIL_BORDER_STRONG = "#C9C1AE"
AGIL_TEXT = "#202020"
AGIL_TEXT_MUTED = "#666257"
AGIL_SUCCESS = "#168653"
AGIL_DANGER = "#B84A35"
AGIL_BLUE = "#2F6F9F"

CHART_COLORS = [AGIL_YELLOW, AGIL_DARK, AGIL_BLUE, AGIL_SUCCESS, AGIL_DANGER, "#7B5FA8"]
CHART_LINE_WIDTH = 3.4

NAV_PAGES = [
    "Accueil",
    "Tableau de Bord",
    "Analyse",
    "Previsions",
    "Exploration",
    "Agent IA",
    "Chatbot",
]

PAGE_PATHS = {
    "Accueil": "pages/accueil.py",
    "Tableau de Bord": "pages/tableau_de_bord.py",
    "Analyse": "pages/analyse_historique.py",
    "Previsions": "pages/previsions.py",
    "Exploration": "pages/exploration.py",
    "Agent IA": "pages/agent_ia.py",
    "Chatbot": "pages/chatbot.py",
}

PAGE_ICONS = {
    "Accueil": "house-fill",
    "Tableau de Bord": "bar-chart-fill",
    "Analyse": "graph-up-arrow",
    "Previsions": "cpu-fill",
    "Exploration": "table",
    "Agent IA": "robot",
    "Chatbot": "chat-dots-fill",
}

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
    --agil-yellow: #FFD100;
    --agil-dark: #262626;
    --agil-text: #202020;
    --agil-muted: #666257;
    --agil-bg: #F7F5EF;
    --agil-surface: #FFFFFF;
    --agil-soft: #FBFAF5;
    --agil-border: #DDD7C8;
    --agil-border-strong: #C9C1AE;
    --agil-shadow: 0 14px 34px rgba(38, 38, 38, 0.08);
    --agil-radius: 14px;
}

html, body, [class*="css"], .stApp {
    font-family: 'Manrope', 'Segoe UI', Arial, sans-serif !important;
    font-size: 17px !important;
    color: var(--agil-text) !important;
}

p, span, div, label, h1, h2, h3, h4, h5, h6,
.stMarkdown, .stText, [class*="st-"] {
    color: var(--agil-text);
}

.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main {
    background:
        linear-gradient(180deg, rgba(255, 209, 0, 0.10) 0%, rgba(255, 209, 0, 0) 220px),
        var(--agil-bg) !important;
}

#MainMenu,
footer,
header,
.stDeployButton,
[data-testid="collapsedControl"],
section[data-testid="stSidebar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] {
    display: none !important;
    visibility: hidden !important;
}

.stApp > div:first-child,
[data-testid="stAppViewContainer"] > section {
    padding-top: 0 !important;
    margin-top: 0 !important;
}

[data-testid="stVerticalBlock"] > div:first-child,
[data-testid="stVerticalBlock"] > div:first-child > div,
.element-container:first-child {
    padding-top: 0 !important;
    margin-top: 0 !important;
}

.main .block-container {
    max-width: 1440px !important;
    padding: 0 2.4rem 3rem !important;
}

@media (max-width: 900px) {
    .main .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
}

.agil-nav-wrap {
    position: sticky;
    top: 0;
    z-index: 999;
    margin: 0 -2.4rem 1.8rem;
    padding: 0 2.4rem 0.7rem;
    background: rgba(247, 245, 239, 0.96);
    border-bottom: 1px solid rgba(201, 193, 174, 0.72);
    backdrop-filter: blur(12px);
}

.agil-nav-inner {
    display: flex;
    align-items: stretch;
    gap: 0.75rem;
    width: 100%;
}

.agil-nav-inner > div:first-child {
    flex: 1 1 auto;
    min-width: 0;
}

.agil-nav-inner > div:last-child {
    flex: 0 0 auto;
    width: 158px;
}

.agil-nav-inner .stButton {
    height: 100% !important;
    display: block !important;
}

.agil-nav-inner .stButton > button {
    width: 100% !important;
    height: 52px !important;
    min-height: 52px !important;
    margin: 0 !important;
    padding: 0 1rem !important;
    border-radius: 13px !important;
    border: 1px solid #3A3A3A !important;
    background: #333333 !important;
    color: #FFFFFF !important;
    font-size: 0.92rem !important;
    font-weight: 800 !important;
    box-shadow: none !important;
}

.agil-nav-inner .stButton > button:hover {
    background: #1F1F1F !important;
    color: var(--agil-yellow) !important;
    transform: none !important;
}

.agil-nav-inner a,
.agil-nav-inner a span,
.agil-nav-inner a i,
.agil-nav-inner a svg {
    color: var(--agil-yellow) !important;
    fill: var(--agil-yellow) !important;
    stroke: var(--agil-yellow) !important;
}

.agil-nav-inner .nav-link-selected,
.agil-nav-inner .nav-link-selected *,
.agil-nav-inner .nav-link-selected i,
.agil-nav-inner .nav-link-selected svg,
.agil-nav-inner .nav-link-selected span,
.agil-nav-inner .nav-link-selected .icon,
.agil-nav-inner a.nav-link-selected,
.agil-nav-inner a.nav-link-selected *,
.nav-link-selected i,
.nav-link-selected svg {
    color: var(--agil-dark) !important;
    fill: var(--agil-dark) !important;
    stroke: var(--agil-dark) !important;
}

.agil-page-header {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
    padding: 0.8rem 0 1.35rem;
    border-bottom: 3px solid var(--agil-yellow);
    margin-bottom: 1.65rem;
}

.agil-page-header h1 {
    margin: 0 !important;
    padding: 0 !important;
    color: var(--agil-dark) !important;
    font-size: 2.55rem !important;
    font-weight: 800 !important;
    line-height: 1.12;
    letter-spacing: 0;
}

.agil-page-header .subtitle {
    margin: 0;
    color: var(--agil-muted) !important;
    font-size: 1.08rem;
    font-weight: 500;
}

.agil-section {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    margin: 1.95rem 0 0.85rem;
    padding: 0.38rem 0.75rem;
    border-left: 5px solid var(--agil-yellow);
    border-radius: 10px;
    background: rgba(255, 209, 0, 0.13);
    color: var(--agil-dark) !important;
    font-size: 0.92rem !important;
    font-weight: 800 !important;
    text-transform: uppercase;
    letter-spacing: 0.7px;
}

.agil-brand-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1.15rem 0 1.45rem;
    border-bottom: 3px solid var(--agil-yellow);
    margin-bottom: 1.8rem;
}

.agil-brand-logo {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 92px;
    height: 58px;
    background: var(--agil-yellow);
    border: 3px solid var(--agil-dark);
    border-radius: 12px;
    color: var(--agil-dark) !important;
    font-size: 1.45rem;
    font-weight: 900;
    line-height: 1;
}

.agil-brand-header h1 {
    margin: 0 !important;
    color: var(--agil-dark) !important;
    font-size: 2.15rem !important;
    font-weight: 850 !important;
    line-height: 1.12;
}

.agil-brand-header p {
    margin: 0.25rem 0 0;
    color: var(--agil-muted) !important;
    font-size: 1rem;
    font-weight: 500;
}

.agil-card,
.agil-process-card,
[data-testid="metric-container"],
[data-testid="stForm"],
[data-testid="stExpander"] {
    background: var(--agil-surface) !important;
    border: 1px solid var(--agil-border) !important;
    border-radius: var(--agil-radius) !important;
    box-shadow: var(--agil-shadow) !important;
}

[data-testid="metric-container"] {
    border-left: 6px solid var(--agil-yellow) !important;
    padding: 1.25rem 1.35rem !important;
}

[data-testid="metric-container"] * {
    color: var(--agil-text) !important;
}

[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] * {
    color: var(--agil-muted) !important;
    font-size: 0.86rem !important;
    font-weight: 800 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.45px !important;
}

[data-testid="stMetricValue"],
[data-testid="stMetricValue"] * {
    color: var(--agil-dark) !important;
    font-size: 2rem !important;
    font-weight: 850 !important;
}

.agil-card {
    height: 100%;
    padding: 1.35rem 1.45rem;
    border-top: 5px solid var(--accent, var(--agil-yellow)) !important;
}

.agil-card h3 {
    margin: 0 0 0.45rem !important;
    color: var(--agil-dark) !important;
    font-size: 1.12rem !important;
    font-weight: 850 !important;
}

.agil-card p {
    margin: 0;
    color: var(--agil-muted) !important;
    font-size: 0.95rem;
    line-height: 1.58;
    font-weight: 500;
}

.agil-process-card {
    height: 100%;
    padding: 1.25rem;
    text-align: center;
}

.agil-process-card.is-highlight {
    background: var(--agil-yellow) !important;
    border-color: var(--agil-dark) !important;
}

.agil-step-number {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    margin-bottom: 0.7rem;
    border-radius: 50%;
    background: var(--agil-dark);
    color: var(--agil-yellow) !important;
    font-size: 1rem;
    font-weight: 900;
}

.agil-process-card.is-highlight .agil-step-number {
    background: var(--agil-surface);
    color: var(--agil-dark) !important;
}

.agil-process-card h3 {
    margin: 0 0 0.35rem !important;
    font-size: 1rem !important;
    font-weight: 850 !important;
}

.agil-process-card p {
    margin: 0;
    color: var(--agil-muted) !important;
    font-size: 0.88rem;
    line-height: 1.45;
}

.stButton {
    display: flex !important;
    justify-content: center !important;
}

.stButton > button,
.stDownloadButton > button,
.stFormSubmitButton > button {
    min-height: 46px !important;
    border: 1px solid #D0B900 !important;
    border-radius: 12px !important;
    background: var(--agil-yellow) !important;
    color: var(--agil-dark) !important;
    font-family: 'Manrope', 'Segoe UI', Arial, sans-serif !important;
    font-size: 0.98rem !important;
    font-weight: 800 !important;
    letter-spacing: 0 !important;
    box-shadow: 0 8px 18px rgba(38, 38, 38, 0.10) !important;
    transition: background 0.18s ease, box-shadow 0.18s ease, transform 0.18s ease !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover,
.stFormSubmitButton > button:hover {
    background: #E8BE00 !important;
    color: var(--agil-dark) !important;
    box-shadow: 0 12px 24px rgba(38, 38, 38, 0.16) !important;
    transform: translateY(-1px) !important;
}

input,
textarea,
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea,
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stChatInput"] textarea {
    min-height: 44px;
    background: var(--agil-surface) !important;
    color: var(--agil-text) !important;
    border: 1px solid var(--agil-border-strong) !important;
    border-radius: 12px !important;
    font-family: 'Manrope', 'Segoe UI', Arial, sans-serif !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    caret-color: var(--agil-dark) !important;
}

input:focus,
textarea:focus,
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus,
[data-testid="stTextArea"] textarea:focus,
[data-testid="stChatInput"] textarea:focus {
    border-color: var(--agil-yellow) !important;
    box-shadow: 0 0 0 4px rgba(255, 209, 0, 0.24) !important;
}

input::placeholder,
textarea::placeholder {
    color: #9A958A !important;
    opacity: 1 !important;
}

[data-baseweb="select"] > div {
    min-height: 46px;
    background: var(--agil-surface) !important;
    border: 1px solid var(--agil-border-strong) !important;
    border-radius: 12px !important;
    color: var(--agil-text) !important;
    box-shadow: none !important;
}

[data-baseweb="select"] > div:hover,
[data-baseweb="select"] > div:focus-within {
    border-color: var(--agil-yellow) !important;
    box-shadow: 0 0 0 4px rgba(255, 209, 0, 0.18) !important;
}

[data-baseweb="tag"] {
    background: var(--agil-yellow) !important;
    border: 1px solid #D0B900 !important;
    border-radius: 999px !important;
    color: var(--agil-dark) !important;
    font-weight: 800 !important;
    box-shadow: none !important;
}

[data-baseweb="tag"] *,
[data-baseweb="tag"] span,
[data-baseweb="tag"] div,
[data-baseweb="tag"] [role="button"],
[data-baseweb="tag"] svg {
    background: transparent !important;
    background-color: transparent !important;
    color: var(--agil-dark) !important;
    fill: var(--agil-dark) !important;
    stroke: var(--agil-dark) !important;
}

[data-testid="stMultiSelect"] [data-baseweb="tag"],
[data-testid="stMultiSelect"] [data-baseweb="tag"] > div,
[data-testid="stMultiSelect"] [data-baseweb="tag"] > span {
    background: var(--agil-yellow) !important;
    background-color: var(--agil-yellow) !important;
    color: var(--agil-dark) !important;
}

[role="listbox"],
[data-baseweb="popover"] {
    background: var(--agil-surface) !important;
    border: 1px solid var(--agil-border) !important;
    border-radius: 14px !important;
    box-shadow: 0 18px 42px rgba(38, 38, 38, 0.16) !important;
}

[role="option"] {
    color: var(--agil-text) !important;
    background: var(--agil-surface) !important;
}

[role="option"]:hover,
[aria-selected="true"] {
    background: rgba(255, 209, 0, 0.22) !important;
    color: var(--agil-dark) !important;
}

[data-testid="stRadio"] label,
[data-testid="stCheckbox"] label,
[data-testid="stMultiSelect"] label,
[data-testid="stSelectbox"] label,
[data-testid="stSlider"] label,
[data-testid="stDateInput"] label {
    color: var(--agil-dark) !important;
    font-weight: 800 !important;
}

[data-testid="stRadio"] div[role="radiogroup"] {
    gap: 0.55rem;
}

[data-testid="stRadio"] label,
[data-testid="stCheckbox"] label {
    background: var(--agil-surface) !important;
    border: 1px solid var(--agil-border) !important;
    border-radius: 999px !important;
    padding: 0.45rem 0.72rem !important;
}

[data-testid="stRadio"] label:has(input:checked),
[data-testid="stCheckbox"] label:has(input:checked) {
    background: rgba(255, 209, 0, 0.30) !important;
    border-color: #D0B900 !important;
}

[data-testid="stSlider"] [role="slider"] {
    background: var(--agil-yellow) !important;
    border: 2px solid var(--agil-dark) !important;
}

[data-testid="stSlider"] > div > div > div > div {
    background: var(--agil-yellow) !important;
}

[data-testid="stForm"] {
    padding: 1.45rem !important;
}

.stAlert {
    border-radius: 14px !important;
    border: 1px solid var(--agil-border) !important;
    box-shadow: 0 8px 22px rgba(38, 38, 38, 0.06) !important;
}

[data-testid="stExpander"] {
    overflow: hidden !important;
}

.streamlit-expanderHeader,
.streamlit-expanderHeader * {
    color: var(--agil-dark) !important;
    font-weight: 800 !important;
}

hr {
    border: none !important;
    border-top: 1px solid var(--agil-border) !important;
    margin: 1.7rem 0 !important;
}

[data-testid="stPlotlyChart"] {
    overflow: hidden;
    background: var(--agil-surface) !important;
    border: 1px solid var(--agil-border) !important;
    border-radius: 16px !important;
    box-shadow: var(--agil-shadow) !important;
}

[data-testid="stDataFrame"],
[data-testid="stDataFrame"] > div {
    overflow: hidden !important;
    background: var(--agil-surface) !important;
    border: 1px solid var(--agil-border) !important;
    border-radius: 16px !important;
    box-shadow: var(--agil-shadow) !important;
    color-scheme: light !important;
    --gdg-bg-cell: #FFFFFF !important;
    --gdg-bg-cell-medium: #FBFAF5 !important;
    --gdg-bg-header: #F2E9C7 !important;
    --gdg-bg-header-has-focus: #E8DDAF !important;
    --gdg-text-dark: #202020 !important;
    --gdg-text-medium: #4D4A42 !important;
    --gdg-text-light: #666257 !important;
    --gdg-accent-color: #262626 !important;
    --gdg-accent-light: rgba(255, 209, 0, 0.24) !important;
    --gdg-border-color: #DDD7C8 !important;
}

[data-testid="stDataFrame"] * {
    color: var(--agil-text) !important;
}

[data-testid="stDataFrame"] div {
    background-color: var(--agil-surface) !important;
}

[data-testid="stDataFrame"] canvas {
    background-color: transparent !important;
}

[data-testid="stDataFrame"] [role="columnheader"],
[data-testid="stDataFrame"] thead,
[data-testid="stDataFrame"] th {
    background: #F2E9C7 !important;
    color: var(--agil-dark) !important;
    font-weight: 850 !important;
}

[data-testid="stTable"],
[data-testid="stTable"] table {
    background: var(--agil-surface) !important;
    color: var(--agil-text) !important;
    border-radius: 16px !important;
    overflow: hidden !important;
}

[data-testid="stTable"] th {
    background: #F2E9C7 !important;
    color: var(--agil-dark) !important;
}

.agil-table-wrap {
    width: 100%;
    overflow-x: auto;
    margin: 0.35rem 0 1rem;
    background: var(--agil-surface);
    border: 1px solid var(--agil-border);
    border-radius: 16px;
    box-shadow: var(--agil-shadow);
}

.agil-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    color: var(--agil-text);
    font-family: 'Manrope', 'Segoe UI', Arial, sans-serif;
    font-size: 0.94rem;
}

.agil-table thead th {
    position: sticky;
    top: 0;
    z-index: 1;
    background: #F2E9C7;
    color: var(--agil-dark);
    border-bottom: 1px solid var(--agil-border-strong);
    font-weight: 850;
    text-align: left;
    white-space: nowrap;
}

.agil-table th,
.agil-table td {
    padding: 0.76rem 0.9rem;
    border-bottom: 1px solid #ECE6D8;
    color: var(--agil-text);
    background: var(--agil-surface);
    vertical-align: middle;
}

.agil-table tbody tr:nth-child(even) td {
    background: var(--agil-soft);
}

.agil-table tbody tr:hover td {
    background: rgba(255, 209, 0, 0.16);
}

.agil-table tbody tr:last-child td {
    border-bottom: none;
}

[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] * {
    color: var(--agil-muted) !important;
    font-size: 0.88rem !important;
}

[data-testid="stChatMessage"] {
    background: var(--agil-surface) !important;
    border: 1px solid var(--agil-border) !important;
    border-radius: 16px !important;
    box-shadow: 0 8px 22px rgba(38, 38, 38, 0.06) !important;
}

[data-testid="stMarkdownContainer"] *,
[data-testid="stText"] *,
.stMarkdown p,
.stMarkdown span,
.stMarkdown li,
.element-container p,
.element-container span {
    color: var(--agil-text) !important;
}

[data-testid="stHeading"],
[data-testid="stHeading"] * {
    color: var(--agil-dark) !important;
}

@media (max-width: 900px) {
    .agil-nav-wrap {
        margin-left: -1rem;
        margin-right: -1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .agil-nav-inner {
        flex-direction: column;
    }

    .agil-nav-inner > div:last-child {
        width: 100%;
    }

    .agil-page-header h1 {
        font-size: 2rem !important;
    }

    .agil-brand-header {
        align-items: flex-start;
        flex-direction: column;
    }
}
</style>
"""


def inject_css() -> None:
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def render_navbar(current_page: str = "Accueil") -> None:
    from streamlit_option_menu import option_menu

    nav_items = NAV_PAGES
    idx = nav_items.index(current_page) if current_page in nav_items else 0
    icons = [PAGE_ICONS[p] for p in nav_items]

    st.markdown('<div class="agil-nav-wrap"><div class="agil-nav-inner">', unsafe_allow_html=True)
    nav_col, logout_col = st.columns([8.5, 1.25], gap="small")

    with nav_col:
        selected = option_menu(
            menu_title=None,
            options=nav_items,
            icons=icons,
            default_index=idx,
            orientation="horizontal",
            styles={
                "container": {
                    "height": "52px",
                    "padding": "4px",
                    "background-color": "#262626",
                    "border-radius": "14px",
                    "box-shadow": "0 14px 32px rgba(38,38,38,0.13)",
                    "margin": "0",
                    "display": "flex",
                    "align-items": "center",
                },
                "icon": {
                    "color": "#FFD100",
                    "font-size": "15px",
                },
                "nav-link": {
                    "height": "44px",
                    "display": "flex",
                    "align-items": "center",
                    "justify-content": "center",
                    "gap": "6px",
                    "font-family": "Manrope, Segoe UI, Arial, sans-serif",
                    "font-size": "14px",
                    "font-weight": "700",
                    "color": "#FFD100",
                    "padding": "0 13px",
                    "border-radius": "11px",
                    "margin": "0 1px",
                    "--hover-color": "#3A3A3A",
                    "white-space": "nowrap",
                },
                "nav-link-selected": {
                    "background-color": "#FFD100",
                    "color": "#262626",
                    "font-weight": "900",
                },
            },
        )

    with logout_col:
        if st.button("Deconnexion", key="logout_btn", use_container_width=True):
            st.session_state.clear()
            st.switch_page("pages/login.py")

    st.markdown("</div></div>", unsafe_allow_html=True)

    if selected != current_page:
        st.switch_page(PAGE_PATHS[selected])


def page_header(title: str, subtitle: str = "") -> None:
    sub_html = f'<p class="subtitle">{subtitle}</p>' if subtitle else ""
    st.markdown(
        f'<div class="agil-page-header"><h1>{title}</h1>{sub_html}</div>',
        unsafe_allow_html=True,
    )


def brand_header(title: str, subtitle: str = "") -> None:
    st.markdown(
        f"""
        <div class="agil-brand-header">
            <div class="agil-brand-logo">AGIL</div>
            <div>
                <h1>{title}</h1>
                <p>{subtitle}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(text: str) -> None:
    st.markdown(f'<p class="agil-section">{text}</p>', unsafe_allow_html=True)


def card(title: str, body: str, accent: str = AGIL_YELLOW) -> None:
    st.markdown(
        f"""
        <div class="agil-card" style="--accent:{accent};">
            <h3>{title}</h3>
            <p>{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def process_card(step: str, title: str, body: str, highlight: bool = False) -> None:
    highlight_class = " is-highlight" if highlight else ""
    st.markdown(
        f"""
        <div class="agil-process-card{highlight_class}">
            <div class="agil-step-number">{step}</div>
            <h3>{title}</h3>
            <p>{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def styled_dataframe(df, hide_index: bool = True) -> None:
    """Affiche un DataFrame avec un tableau HTML clair et stable."""
    display_df = df.copy()
    for column in display_df.columns:
        if hasattr(display_df[column], "dt"):
            try:
                display_df[column] = display_df[column].dt.strftime("%Y-%m-%d")
            except (AttributeError, ValueError):
                pass

    html = display_df.to_html(
        index=not hide_index,
        classes="agil-table",
        border=0,
        escape=True,
    )
    st.markdown(f'<div class="agil-table-wrap">{html}</div>', unsafe_allow_html=True)


def agil_chart_layout(title: str = "", height: int = 450) -> dict:
    return dict(
        title=dict(
            text=title,
            font=dict(size=17, color=AGIL_DARK, family="Manrope"),
            x=0,
            pad=dict(l=0, t=6),
        ),
        font=dict(family="Manrope, Segoe UI, Arial, sans-serif", size=14, color=AGIL_TEXT),
        plot_bgcolor=AGIL_SURFACE,
        paper_bgcolor=AGIL_SURFACE,
        margin=dict(l=60, r=32, t=58 if title else 30, b=50),
        xaxis=dict(
            showgrid=False,
            linecolor=AGIL_BORDER,
            tickfont=dict(size=13, color=AGIL_TEXT_MUTED),
        ),
        yaxis=dict(
            gridcolor="#EEE9DA",
            linecolor=AGIL_BORDER,
            tickfont=dict(size=13, color=AGIL_TEXT_MUTED),
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
