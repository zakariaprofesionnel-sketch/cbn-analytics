"""Configuration centralisée du projet CBN Analytics
==================================================
Ce fichier regroupe tous les paramètres du projet :
connexion PostgreSQL, chemins fichiers, paramètres ML.
"""

import os

# --------- CONNEXION POSTGRESQL ---------


#5433 postgress postgres pc sghir
#5432 root root pc kbir


DB_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/cbn_analytics",
)
# Railway fournit parfois "postgres://" — SQLAlchemy exige "postgresql://"
if DB_URL.startswith("postgres://"):
    DB_URL = DB_URL.replace("postgres://", "postgresql://", 1)

# ─────────────────────────────────────────────
# CHEMINS FICHIERS
# ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_RAW = os.path.join(BASE_DIR, "data", "raw")
DATA_PROCESSED = os.path.join(BASE_DIR, "data", "processed")

FICHIER_VENTES_BRUT = os.path.join(DATA_RAW, "vente_car_2015_2018.xlsx")
FICHIER_GASOIL_CSV = os.path.join(DATA_PROCESSED, "ventes_gasoil.csv")
FICHIER_BRENT_CSV = os.path.join(DATA_PROCESSED, "cours_brent.csv")

# ─────────────────────────────────────────────
# PARAMÈTRES MÉTIER
# ─────────────────────────────────────────────
# Code produit gasoil dans le fichier source
CODPRD_GASOIL = 4

# Plage de dates des données
DATE_DEBUT = "2015-01-01"
DATE_FIN = "2018-12-31"

# Ticker Yahoo Finance pour le Brent
BRENT_TICKER = "BZ=F"

# ─────────────────────────────────────────────
# PARAMÈTRES ML (PROPHET)
# ─────────────────────────────────────────────
# Fréquence d'agrégation pour le modèle
FREQ_AGREGATION = "MS"  # MS = Month Start

# Horizon de prévision par défaut (mois)
HORIZON_DEFAUT = 6

# Proportion train/test
TEST_YEAR = 2018  # Année réservée pour le test



"""DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "cbn_analytics",
    "user": "postgres",
    "password": "postgres",
    "client_encoding": "UTF-8",
}

# String de connexion pour SQLAlchemy
DB_URL = (
    f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)"""