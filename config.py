"""Configuration centralisee du projet CBN Analytics."""

import os


# Connexion PostgreSQL
# 5433 : postgres/postgres pc sghir
# 5432 : root/root pc kbir
DB_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/cbn_analytics",
)

if DB_URL.startswith("postgres://"):
    DB_URL = DB_URL.replace("postgres://", "postgresql://", 1)


# Chemins fichiers
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_RAW = os.path.join(BASE_DIR, "data", "raw")
DATA_PROCESSED = os.path.join(BASE_DIR, "data", "processed")

FICHIER_VENTES_BRUT = os.path.join(DATA_RAW, "vente_car_2015_2018.xlsx")
FICHIER_GASOIL_CSV = os.path.join(DATA_PROCESSED, "ventes_gasoil.csv")
FICHIER_BRENT_CSV = os.path.join(DATA_PROCESSED, "cours_brent.csv")


# Parametres metier
CODPRD_GASOIL = 4
DATE_DEBUT = "2015-01-01"
DATE_FIN = "2018-12-31"
BRENT_TICKER = "BZ=F"


# Acces application
# Pour changer le code sans modifier le code source :
# PowerShell: $env:CBN_ACCESS_CODE="votre-code"
ACCESS_CODE = os.environ.get("CBN_ACCESS_CODE", "AGIL2026")


# Parametres ML
FREQ_AGREGATION = "MS"
HORIZON_DEFAUT = 6

# Comparaison Prophet vs SARIMAX.
# Protocole retenu :
# - entrainement de comparaison : 2015-2016
# - test hors echantillon : 2017
# - modele final : 2015-2017
# - prevision : 2018
TRAIN_END_YEAR = 2016
TEST_YEAR = 2017
EXCLUDED_EVAL_YEAR = None


"""DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "cbn_analytics",
    "user": "postgres",
    "password": "postgres",
    "client_encoding": "UTF-8",
}

DB_URL = (
    f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)"""
