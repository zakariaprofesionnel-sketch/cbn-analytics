"""
Page 5 : Méthodologie
=======================
Documentation technique pour la soutenance :
- Architecture Data Warehouse
- Pipeline ETL
- Modèle de prévision Prophet
"""

import streamlit as st

st.set_page_config(page_title="Méthodologie", page_icon="📖", layout="wide")
st.title("📖 Méthodologie")
st.markdown("*Documentation technique — Projet de Fin d'Études*")

# ─────────────────────────────────────────────
# 1. ARCHITECTURE DATA WAREHOUSE
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("## 1. Architecture Data Warehouse")

st.markdown("""
Le Data Warehouse suit un **schéma en étoile** (star schema), le modèle le plus courant 
en Business Intelligence. Il se compose d'une **table de faits** centrale entourée de 
**tables de dimensions** descriptives.
""")

st.markdown("### Schéma")

st.code("""
                    ┌──────────────┐
                    │  dim_produit │
                    │──────────────│
                    │ id_produit   │
                    │ code_produit │
                    │ libelle      │
                    │ type_produit │
                    │ categorie    │
                    └──────┬───────┘
                           │
┌──────────────┐    ┌──────┴───────┐    ┌──────────────────┐
│   dim_date   │    │ fact_ventes  │    │    dim_cours      │
│──────────────│    │──────────────│    │──────────────────│
│ id_date      ├────┤ id_vente     │    │ id_cours         │
│ date_complete│    │ id_date (FK) │    │ id_date (FK)     │
│ jour         │    │ id_produit   │    │ cours_brent_usd  │
│ mois         │    │ quantite_m3  │    │ variation_pct    │
│ annee        │    │ montant_ht   │    │ source           │
│ trimestre    │    │ prix_unitaire│    └──────────────────┘
│ nom_mois     │    │ code_depot   │
│ nom_jour     │    │ num_compte   │
│ est_weekend  │    └──────────────┘
└──────────────┘
""", language=None)

st.markdown("""
**Choix de conception :**
- **`dim_cours`** est une table de faits secondaire, pas une dimension classique.
  Le cours du Brent est une mesure externe indexée par le temps, pas un attribut descriptif d'une vente.
- **`code_depot`** et **`num_compte`** sont des attributs dégénérés dans `fact_ventes` 
  (pas de dimension dédiée car un seul dépôt).
- La **vue `v_ventes_mensuelles_gasoil`** pré-agrège les données pour le dashboard et le modèle ML.
""")

# ─────────────────────────────────────────────
# 2. PIPELINE ETL
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("## 2. Pipeline ETL")

st.markdown("### Vue d'ensemble")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 📥 Extract
    **Sources :**
    - Fichier Excel des ventes CBN (108 542 lignes)
    - API Yahoo Finance (cours Brent 2015-2018)
    
    **Outils :** pandas, yfinance
    """)

with col2:
    st.markdown("""
    ### ⚙️ Transform
    **Traitements :**
    - Filtrage gasoil (CODPRD = 4)
    - Suppression négatifs/zéros (146 lignes)
    - Calcul prix unitaire
    - Forward-fill cours Brent (week-ends)
    - Génération des dimensions
    """)

with col3:
    st.markdown("""
    ### 📤 Load
    **Cible :** PostgreSQL
    - Création automatique de la base
    - Chargement par batch (10 000 lignes)
    - Vérification d'intégrité
    """)

st.markdown("### Données nettoyées")

st.markdown("""
| Indicateur | Valeur |
|---|---|
| Lignes brutes | 108 542 |
| Lignes gasoil | 98 127 (90,4%) |
| Lignes supprimées (négatifs + zéros) | ~146 |
| Lignes chargées | ~97 981 |
| Période | 01/01/2015 → 31/12/2018 |
| Mois complets | 48 |
""")

# ─────────────────────────────────────────────
# 3. MODÈLE DE PRÉVISION
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("## 3. Modèle de Prévision — Prophet")

st.markdown("""
### Pourquoi Prophet ?

**Prophet** (Meta/Facebook, 2017) est un modèle de prévision de séries temporelles 
conçu pour les données métier. Il a été choisi pour ce projet car :

1. **Adapté aux données métier** : gère la saisonnalité, les tendances et les jours fériés
2. **Simple d'utilisation** : API `fit()` / `predict()`, pas de tuning complexe
3. **Régresseurs externes** : permet d'intégrer le cours du pétrole
4. **Intervalles de confiance** : produit automatiquement des bandes d'incertitude
5. **Robuste** : gère les données manquantes sans pré-traitement
""")

st.markdown("""
### Formulation mathématique

Le modèle décompose la série temporelle :

> **y(t) = g(t) + s(t) + β · x(t) + ε(t)**

Où :
- **g(t)** = tendance (croissance linéaire ou logistique avec points de changement)
- **s(t)** = saisonnalité annuelle (séries de Fourier)
- **β · x(t)** = effet du régresseur externe (cours du Brent)
- **ε(t)** = terme d'erreur

La saisonnalité est en mode **multiplicatif** : l'effet saisonnier est proportionnel 
au niveau de la série (une hausse de 10% en été représente plus de volume si la tendance est haute).
""")

st.markdown("""
### Protocole d'évaluation

| Aspect | Détail |
|---|---|
| **Données train** | 2015-2017 (36 mois) |
| **Données test** | 2018 (12 mois) |
| **Granularité** | Mensuelle (48 points) |
| **Régresseur** | Cours Brent moyen mensuel (USD/baril) |
| **Intervalle de confiance** | 95% |

### Métriques utilisées

- **MAE** (Mean Absolute Error) : erreur moyenne en m³ — interprétable directement
- **RMSE** (Root Mean Square Error) : pénalise les grosses erreurs
- **MAPE** (Mean Absolute Percentage Error) : erreur en % — le plus parlant
- **R²** (Coefficient de détermination) : 1.0 = prédiction parfaite, 0 = modèle naïf
""")

st.markdown("""
### Approche par scénarios

Pour prédire les ventes futures, le modèle a besoin du cours futur du Brent 
(qu'on ne connaît pas). Solution : **3 scénarios** basés sur le dernier cours observé :

- **Stable** : le cours reste constant
- **Hausse +20%** : augmentation linéaire sur l'horizon
- **Baisse -20%** : diminution linéaire sur l'horizon

Cette approche est plus réaliste qu'une prédiction unique et permet au décideur 
d'anticiper différentes situations de marché.
""")

# ─────────────────────────────────────────────
# 4. STACK TECHNOLOGIQUE
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("## 4. Stack Technologique")

st.markdown("""
| Composant | Technologie | Rôle |
|---|---|---|
| Langage | Python 3.10+ | Manipulation données, ML, dashboard |
| Base de données | PostgreSQL 18 | Data Warehouse (schéma étoile) |
| ETL | pandas, psycopg2, SQLAlchemy | Extract-Transform-Load |
| Données externes | yfinance | Cours du Brent (Yahoo Finance) |
| Visualisation | Plotly + Streamlit | Dashboard interactif |
| Machine Learning | Prophet + scikit-learn | Prévision + évaluation |
| Administration DB | pgAdmin | Interface graphique PostgreSQL |
""")

st.markdown("---")
st.caption("CBN Analytics — Projet de Fin d'Études — Licence Business Intelligence")
