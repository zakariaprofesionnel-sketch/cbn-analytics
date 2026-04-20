"""
ETL - Phase TRANSFORM
======================
Responsabilités :
1. Filtrer les ventes gasoil uniquement (CODPRD == 4)
2. Nettoyer : supprimer négatifs, zéros, aberrants
3. Calculer le prix unitaire
4. Préparer les tables de dimensions (date, produit)
5. Appliquer forward-fill sur le cours Brent (week-ends/jours fériés)
6. Calculer la variation % du cours

Entrées  : DataFrames bruts (ventes + Brent)
Sorties  : DataFrames nettoyés prêts pour le chargement
"""

import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import *


def transform_ventes(df_brut: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie et filtre les ventes pour ne garder que le gasoil valide.
    
    Règles de nettoyage :
    - Garder uniquement CODPRD == 4 (gasoil)
    - Supprimer les quantités <= 0 (retours, corrections, erreurs)
    - Supprimer les montants <= 0
    - Calculer le prix unitaire (MNTHT / QTEPRD)
    - Détecter les valeurs aberrantes via IQR sur le prix unitaire
    """
    print("[TRANSFORM] Nettoyage des ventes...")
    
    df = df_brut.copy()
    n_initial = len(df)
    
    # 1. Filtrer gasoil uniquement
    df = df[df['CODPRD'] == CODPRD_GASOIL].copy()
    n_gasoil = len(df)
    print(f"[TRANSFORM]   Filtre gasoil : {n_initial} → {n_gasoil} lignes")
    
    # 2. Supprimer quantités <= 0
    df = df[df['QTEPRD'] > 0].copy()
    n_positif = len(df)
    print(f"[TRANSFORM]   Filtre QTEPRD > 0 : {n_gasoil} → {n_positif} lignes (-{n_gasoil - n_positif})")
    
    # 3. Supprimer montants <= 0
    df = df[df['MNTHT'] > 0].copy()
    n_mnt = len(df)
    print(f"[TRANSFORM]   Filtre MNTHT > 0 : {n_positif} → {n_mnt} lignes (-{n_positif - n_mnt})")
    
    # 4. Calculer le prix unitaire
    df['prix_unitaire'] = df['MNTHT'] / df['QTEPRD']
    
    # 5. Détection des aberrants via IQR sur le prix unitaire
    Q1 = df['prix_unitaire'].quantile(0.01)
    Q3 = df['prix_unitaire'].quantile(0.99)
    df = df[(df['prix_unitaire'] >= Q1) & (df['prix_unitaire'] <= Q3)].copy()
    n_final = len(df)
    print(f"[TRANSFORM]   Filtre aberrants prix (P1-P99) : {n_mnt} → {n_final} lignes (-{n_mnt - n_final})")
    
    # 6. Renommer les colonnes pour le warehouse
    df = df.rename(columns={
        'DATLIV': 'date_livraison',
        'DATRET': 'date_retour',
        'CODPRD': 'code_produit',
        'LIBPRD1': 'libelle_produit',
        'TYPPRD': 'type_produit',
        'CATPRD': 'categorie',
        'QTEPRD': 'quantite_m3',
        'MNTHT': 'montant_ht',
        'CODDPO': 'code_depot',
        'NUMCPT': 'num_compte',
    })
    
    print(f"[TRANSFORM] ✓ {n_final} ventes gasoil nettoyées")
    
    return df


def transform_cours_brent(df_brent: pd.DataFrame) -> pd.DataFrame:
    """
    Complète et enrichit les cours du Brent.
    
    Étapes :
    - Créer un index journalier complet (y compris week-ends)
    - Forward-fill : chaque jour prend le dernier cours connu
    - Calculer la variation en % jour/jour
    """
    print("[TRANSFORM] Traitement cours Brent...")
    
    df = df_brent.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date').sort_index()
    
    # Créer un index journalier complet
    idx_complet = pd.date_range(start=DATE_DEBUT, end=DATE_FIN, freq='D')
    df = df.reindex(idx_complet)
    
    # Forward-fill : le cours du vendredi s'applique au week-end
    jours_manquants = df['cours_brent_usd'].isna().sum()
    df['cours_brent_usd'] = df['cours_brent_usd'].ffill()
    # Backward-fill pour les tout premiers jours si nécessaire
    df['cours_brent_usd'] = df['cours_brent_usd'].bfill()
    
    # Variation en pourcentage
    df['variation_pct'] = df['cours_brent_usd'].pct_change() * 100
    df['variation_pct'] = df['variation_pct'].fillna(0)
    
    df = df.reset_index().rename(columns={'index': 'date'})
    
    print(f"[TRANSFORM] ✓ {len(df)} jours (forward-fill appliqué sur {jours_manquants} jours manquants)")
    
    return df


def generer_dim_date() -> pd.DataFrame:
    """
    Génère la dimension date : un enregistrement par jour de 2015 à 2018.
    Inclut : mois, trimestre, jour de semaine, nom du jour, est_weekend.
    """
    print("[TRANSFORM] Génération dim_date...")
    
    noms_mois = {
        1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril',
        5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août',
        9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
    }
    noms_jours = {
        0: 'Lundi', 1: 'Mardi', 2: 'Mercredi', 3: 'Jeudi',
        4: 'Vendredi', 5: 'Samedi', 6: 'Dimanche'
    }
    
    dates = pd.date_range(start=DATE_DEBUT, end=DATE_FIN, freq='D')
    
    df = pd.DataFrame({
        'date_complete': dates,
        'jour': dates.day,
        'mois': dates.month,
        'nom_mois': [noms_mois[d.month] for d in dates],
        'annee': dates.year,
        'trimestre': dates.quarter,
        'jour_semaine': dates.dayofweek,
        'nom_jour': [noms_jours[d.dayofweek] for d in dates],
        'est_weekend': dates.dayofweek >= 5,
    })
    
    print(f"[TRANSFORM] ✓ {len(df)} jours générés ({dates[0].date()} → {dates[-1].date()})")
    
    return df


def generer_dim_produit(df_ventes: pd.DataFrame) -> pd.DataFrame:
    """
    Extrait les produits uniques du fichier source pour la dimension produit.
    """
    print("[TRANSFORM] Génération dim_produit...")
    
    # On prend tous les produits du fichier original (pas seulement gasoil)
    df_prod = df_ventes[['CODPRD', 'LIBPRD1', 'TYPPRD', 'CATPRD']].drop_duplicates()
    df_prod = df_prod.rename(columns={
        'CODPRD': 'code_produit',
        'LIBPRD1': 'libelle',
        'TYPPRD': 'type_produit',
        'CATPRD': 'categorie',
    })
    # Prendre une seule catégorie par produit (la plus fréquente)
    df_prod = df_prod.drop_duplicates(subset=['code_produit'], keep='first')
    
    print(f"[TRANSFORM] ✓ {len(df_prod)} produits")
    
    return df_prod


if __name__ == "__main__":
    # Test standalone
    from extract import extract_ventes, extract_cours_brent
    
    df_brut = extract_ventes()
    df_gasoil = transform_ventes(df_brut)
    print(df_gasoil.head())
