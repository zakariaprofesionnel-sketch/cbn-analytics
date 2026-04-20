"""
ETL - Phase LOAD
=================
Responsabilités :
1. Créer la base de données si inexistante
2. Exécuter le schéma SQL (tables + vues)
3. Charger les dimensions (date, produit)
4. Charger les faits (ventes, cours Brent)
5. Vérifier l'intégrité des données chargées

Entrées  : DataFrames transformés + schéma SQL
Sorties  : Tables PostgreSQL peuplées
"""

import pandas as pd
import psycopg2
from psycopg2 import sql
from sqlalchemy import create_engine
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import *


def creer_base_si_inexistante():
    """
    Crée la base de données 'cbn_analytics' si elle n'existe pas.
    Se connecte d'abord à la base 'postgres' par défaut.
    """
    print("[LOAD] Vérification de la base de données...")
    
    conn = psycopg2.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        dbname='postgres'
    )
    conn.autocommit = True
    cur = conn.cursor()
    
    # Vérifier si la base existe
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_CONFIG['database'],))
    exists = cur.fetchone()
    
    if not exists:
        cur.execute(sql.SQL("CREATE DATABASE {}").format(
            sql.Identifier(DB_CONFIG['database'])
        ))
        print(f"[LOAD] ✓ Base '{DB_CONFIG['database']}' créée")
    else:
        print(f"[LOAD] ✓ Base '{DB_CONFIG['database']}' existe déjà")
    
    cur.close()
    conn.close()


def executer_schema():
    """
    Exécute le fichier schema.sql pour créer les tables et vues.
    """
    print("[LOAD] Exécution du schéma SQL...")
    
    schema_candidates = [
        os.path.join(BASE_DIR, "warehouse", "schema.sql"),
        os.path.join(BASE_DIR, "schema.sql"),
    ]
    schema_path = next((p for p in schema_candidates if os.path.exists(p)), None)
    if schema_path is None:
        raise FileNotFoundError(
            "schema.sql introuvable. Vérifiez `warehouse/schema.sql` ou `schema.sql` à la racine."
        )

    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(schema_sql)
    cur.close()
    conn.close()
    
    print("[LOAD] ✓ Tables et vues créées")


def charger_dim_date(df_date: pd.DataFrame):
    """
    Charge la dimension date dans PostgreSQL.
    Utilise SQLAlchemy + pandas pour l'insertion par batch.
    """
    print("[LOAD] Chargement dim_date...")
    
    engine = create_engine(DB_URL)
    df_date.to_sql('dim_date', engine, if_exists='append', index=False)
    
    print(f"[LOAD] ✓ {len(df_date)} jours chargés dans dim_date")
    engine.dispose()


def charger_dim_produit(df_produit: pd.DataFrame):
    """
    Charge la dimension produit dans PostgreSQL.
    """
    print("[LOAD] Chargement dim_produit...")
    
    engine = create_engine(DB_URL)
    df_produit.to_sql('dim_produit', engine, if_exists='append', index=False)
    
    print(f"[LOAD] ✓ {len(df_produit)} produits chargés dans dim_produit")
    engine.dispose()


def charger_dim_cours(df_cours: pd.DataFrame):
    """
    Charge les cours du Brent en liant chaque cours à son id_date.
    """
    print("[LOAD] Chargement dim_cours...")
    
    engine = create_engine(DB_URL)
    
    # Récupérer le mapping date → id_date
    df_dates = pd.read_sql("SELECT id_date, date_complete FROM dim_date", engine)
    df_dates['date_complete'] = pd.to_datetime(df_dates['date_complete'])
    
    # Joindre les cours avec les id_date
    df_cours['date'] = pd.to_datetime(df_cours['date'])
    df_merged = df_cours.merge(
        df_dates,
        left_on='date',
        right_on='date_complete',
        how='inner'
    )
    
    df_load = df_merged[['id_date', 'cours_brent_usd', 'variation_pct']].copy()
    df_load['source'] = 'Yahoo Finance'
    
    df_load.to_sql('dim_cours', engine, if_exists='append', index=False)
    
    print(f"[LOAD] ✓ {len(df_load)} jours de cours chargés dans dim_cours")
    engine.dispose()


def charger_fact_ventes(df_ventes: pd.DataFrame):
    """
    Charge les ventes gasoil en résolvant les clés étrangères (id_date, id_produit).
    """
    print("[LOAD] Chargement fact_ventes...")
    
    engine = create_engine(DB_URL)
    
    # Récupérer les mappings
    df_dates = pd.read_sql("SELECT id_date, date_complete FROM dim_date", engine)
    df_dates['date_complete'] = pd.to_datetime(df_dates['date_complete'])
    
    df_produits = pd.read_sql("SELECT id_produit, code_produit FROM dim_produit", engine)
    
    # Joindre id_date
    df_ventes['date_livraison'] = pd.to_datetime(df_ventes['date_livraison'])
    df = df_ventes.merge(
        df_dates,
        left_on='date_livraison',
        right_on='date_complete',
        how='left'
    )
    
    # Joindre id_produit
    df = df.merge(
        df_produits,
        on='code_produit',
        how='left'
    )
    
    # Préparer le DataFrame final
    df_load = df[[
        'id_date', 'id_produit', 'quantite_m3', 'montant_ht',
        'prix_unitaire', 'code_depot', 'num_compte', 'date_retour'
    ]].copy()
    
    # Charger par batch de 10000 lignes
    batch_size = 10000
    total = len(df_load)
    for i in range(0, total, batch_size):
        batch = df_load.iloc[i:i+batch_size]
        batch.to_sql('fact_ventes', engine, if_exists='append', index=False)
        print(f"[LOAD]   Batch {i//batch_size + 1} : {min(i+batch_size, total)}/{total} lignes")
    
    print(f"[LOAD] ✓ {total} ventes chargées dans fact_ventes")
    engine.dispose()


def verifier_chargement():
    """
    Vérifie l'intégrité des données chargées.
    """
    print("\n[LOAD] === VÉRIFICATION ===")
    
    engine = create_engine(DB_URL)
    
    tables = {
        'dim_date': 'SELECT COUNT(*) FROM dim_date',
        'dim_produit': 'SELECT COUNT(*) FROM dim_produit',
        'dim_cours': 'SELECT COUNT(*) FROM dim_cours',
        'fact_ventes': 'SELECT COUNT(*) FROM fact_ventes',
    }
    
    for table, query in tables.items():
        count = pd.read_sql(query, engine).iloc[0, 0]
        print(f"[LOAD]   {table}: {count} lignes")
    
    # Test de la vue agrégée
    print("\n[LOAD] === VUE MENSUELLE (aperçu) ===")
    df_vue = pd.read_sql("SELECT * FROM v_ventes_mensuelles_gasoil LIMIT 5", engine)
    print(df_vue.to_string(index=False))
    
    engine.dispose()
    print("\n[LOAD] ✓ Chargement terminé avec succès")


if __name__ == "__main__":
    creer_base_si_inexistante()
    executer_schema()
    verifier_chargement()
