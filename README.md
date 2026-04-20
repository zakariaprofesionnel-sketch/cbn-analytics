# CBN Analytics - SNDP Tunisie

Application BI + ML pour analyser et prevoir les ventes de gasoil, avec un agent IA d'aide a la decision.

---

## 1) Version simple (lecture rapide)

Le projet fait 4 choses:

1. lit les donnees de ventes + cours Brent,
2. charge les donnees dans PostgreSQL,
3. entraine un modele de prevision (Prophet),
4. affiche un dashboard Streamlit avec une page Agent IA CBN.

Objectif metier: aider le pilotage CBN (Carburant/Bilan Negatif) avec des indicateurs clairs et des recommandations.

### Lancer rapidement

```cmd
cd "C:\Users\zakbe\Desktop\projet pc sghir"
.\.venv\Scripts\activate.bat
python run_etl.py
python run_ml.py
streamlit run app/app.py
```

---

## 2) Version detaillee (pour comprendre le pourquoi et le comment)
 
Cette section explique la logique technique, dans l'ordre reel d'execution.

### 2.1 Pourquoi cette architecture

On a choisi une architecture ETL + Data Warehouse + Dashboard pour separer clairement:

- **l'acquisition des donnees** (source externe + fichier interne),
- **la qualite des donnees** (nettoyage centralise),
- **la decision** (KPI, previsions, recommandations).

Ce decoupage rend le projet plus robuste, plus explicable, et plus simple a maintenir.

### 2.2 Comment les donnees circulent

1. **Extract**
   - lecture de l'Excel des ventes,
   - telechargement du Brent via Yahoo Finance (ou fallback CSV).
2. **Transform**
   - filtrage du gasoil,
   - suppression des valeurs invalides,
   - calculs utiles (prix unitaire, variation Brent),
   - generation des dimensions (date, produit).
3. **Load**
   - chargement dans PostgreSQL (schema etoile),
   - creation de la vue mensuelle `v_ventes_mensuelles_gasoil`.
4. **ML**
   - entrainement Prophet sur historique,
   - evaluation sur periode test,
   - sauvegarde des metriques et du comparatif reel/predit.
5. **Dashboard**
   - visualisation des KPI,
   - analyse historique,
   - previsions,
   - agent IA d'aide a la decision.

### 2.3 Pourquoi Prophet

Prophet est adapte ici parce que:

- serie temporelle metier avec saisonnalite annuelle,
- peu de tuning necessaire (bon pour un projet applicatif),
- ajout facile d'un regresseur externe (`cours_brent`),
- production d'intervalles de confiance utiles en decision.

### 2.4 Pourquoi un agent IA semi-automatique

Le projet ne dispose pas d'un acces direct aux stocks entreprise. Donc:

- on ne fait pas d'automatisation risquee,
- on fait un **assistant** qui propose et justifie,
- l'utilisateur garde la validation finale.

Ce choix est plus realiste en contexte industriel et plus defendable en soutenance.

---

## 3) Structure du projet (coherente avec le flux)

```text
projet/
├── data/
│   ├── raw/                          # Sources brutes (Excel)
│   └── processed/                    # Sorties CSV (fallbacks, logs)
├── etl/
│   ├── extract.py
│   ├── transform.py
│   └── load.py
├── warehouse/
│   └── schema.sql
├── ml/
│   ├── forecast.py
│   ├── prophet_model.pkl
│   ├── metriques.pkl
│   └── predictions_test.csv
├── app/
│   ├── app.py
│   ├── utils.py
│   ├── agent/
│   │   ├── context.py
│   │   ├── rules.py
│   │   ├── decision_agent.py
│   │   └── executor.py
│   └── pages/
├── config.py
├── run_etl.py
├── run_ml.py
└── requirements.txt
```

---

## 4) Installation complete

### 4.1 Prerequis

- Python 3.10+ (3.11/3.12 recommande)
- PostgreSQL actif
- fichier `data/raw/vente_car_2015_2018.xlsx`
- internet (ou fallback Brent deja present)

### 4.2 Environnement Python (recommande)

```cmd
cd "C:\Users\zakbe\Desktop\projet pc sghir"
python -m venv .venv
.\.venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4.3 Configuration DB

Verifier `config.py`:

```python
DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "cbn_analytics",
    "user": "postgres",
    "password": "postgres",
    "client_encoding": "UTF-8",
}
```

Pourquoi: toute l'application (ETL, ML, app) depend de cette config unique.

---

## 5) Execution (ordre obligatoire)

```cmd
python run_etl.py
python run_ml.py
streamlit run app/app.py
```

Pourquoi cet ordre:

- le dashboard depend des tables ETL,
- la page previsions depend des artefacts ML,
- l'agent IA depend des signaux ETL + ML.

---

## 6) Pages du dashboard et utilite

- **Accueil**: contexte general.
- **Tableau de Bord**: KPI metier de base.
- **Analyse Historique**: relation ventes vs Brent.
- **Previsions IA**: projection + comparaison reel/predit.
- **Exploration**: verification detaillee des donnees.
- **Methodologie**: justification technique.
- **Agent IA CBN**: recommandations semi-automatiques.
- **Chatbot Donnees**: questions en langage naturel sur les ventes de gasoil.

---

## 7) Agent IA CBN: ce qu'il fait exactement

### 7.1 Comment il decide

1. `context.py` construit les signaux (volume, tendance, Brent, MAE).
2. `rules.py` transforme ces signaux en recommandations lisibles.
3. `decision_agent.py` orchestre et renvoie la liste finale.
4. `executor.py` enregistre la decision utilisateur.

### 7.2 Pourquoi SQL + CSV

On enregistre:

- en **SQL** pour integrer le suivi dans le SI data,
- en **CSV** comme backup de securite.

Donc meme si la DB est indisponible, l'historique n'est pas perdu.

### 7.3 Comment l'utiliser

1. Ouvrir la page **Agent IA CBN**.
2. Cliquer **Generer recommandations**.
3. Lire raison, impact, priorite, confiance.
4. Cliquer **Valider** ou **Rejeter**.
5. Verifier l'historique.

---

## 8) Choix techniques importants (et raison)

- **Import Streamlit pages via `from utils import ...`**
  - evite les erreurs de package selon mode de lancement.
- **Plotly API moderne**
  - suppression des proprietes depreciees pour compatibilite versions recentes.
- **Garde-fous sur donnees vides**
  - pas de crash, message utilisateur clair.
- **Fallback schema SQL**
  - compatibilite si `schema.sql` est en racine ou dans `warehouse/`.
- **Versioning deps dans `requirements.txt`**
  - reduit les ecarts entre PCs.

---

## 9) Depannage rapide

- **`No module named ...`**
  - verifier venv active, puis `pip install -r requirements.txt`.
- **Erreur DB connection refused**
  - verifier service PostgreSQL + `config.py`.
- **Erreur `statsmodels`**
  - `pip install statsmodels`.
- **Erreur `schema.sql` introuvable**
  - verifier `warehouse/schema.sql` ou racine.
- **Pas d'ecriture en base pour agent**
  - verifier droits SQL `CREATE/INSERT/SELECT`,
  - sinon verifier backup CSV `data/processed/agent_decisions_log.csv`.

---

## 9b) Chatbot Donnees: ce qu'il fait exactement

### 9b.1 Principe

Le chatbot permet a l'utilisateur de poser des questions en francais sur les donnees de ventes
de gasoil et d'obtenir des reponses calculees automatiquement a partir des CSV.

Il est entierement code en Python (sans LLM externe, sans API), base sur:
- detection de mots-cles pour identifier l'intention de la question,
- extraction d'entites (annee, depot) depuis le texte brut,
- requetes pandas sur `ventes_gasoil.csv` et `cours_brent.csv`,
- formatage de la reponse en francais.

### 9b.2 Architecture

```text
app/chatbot/
├── intent_detector.py   # detecte l'intention (meilleure_vente, tendance, comparaison...)
├── entity_extractor.py  # extrait annee, depot depuis le texte
└── query_engine.py      # execute la requete pandas et formate la reponse
```

La page Streamlit (`app/pages/8_Chatbot.py`) appelle ces trois modules en sequence.

### 9b.3 Intentions reconnues

| Intention | Mots-cles detectes | Exemple de question |
|---|---|---|
| meilleure_vente | meilleur, maximum, record, top | "Quel mois a eu les meilleures ventes ?" |
| tendance | tendance, evolution, progression, baisse, hausse | "Quelle est la tendance en 2017 ?" |
| comparaison | compare, difference, entre, vs | "Compare 2015 et 2018" |
| moyenne | moyenne, moyen, en moyenne | "Quelle est la vente moyenne par mois ?" |
| depot | depot, station, site | "Quel depot vend le plus ?" |
| correlation | brent, correlation, lien, petrole | "Y a-t-il un lien avec le Brent ?" |
| total | total, cumul, somme, combien | "Quel est le total des ventes en 2016 ?" |

### 9b.4 Limites

- Fonctionne uniquement sur les donnees disponibles dans les CSV (2015-2018).
- Ne comprend pas les questions hors du domaine ventes/Brent.
- Questions tres complexes ou ambigues retournent un message d'aide.

---

## 10) Limites actuelles et suite logique

Limites:

- pas d'acces direct aux stocks entreprise,
- agent base sur signaux ventes + Brent + qualite prevision.

Suite logique:

1. brancher des donnees stock reelles,
2. ajouter des regles metier plus fines par depot/segment,
3. ajouter un workflow de validation par role utilisateur.

---

## 11) Notes

- Unites: quantites en m3, Brent en USD/baril.
- Projet academique avec structure proche d'un usage professionnel.
