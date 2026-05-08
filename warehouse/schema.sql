-- ============================================================
-- SCHÉMA DATA WAREHOUSE - CBN Analytics (SNDP)
-- ============================================================
-- Architecture : Schéma en étoile
-- Base : PostgreSQL
-- 
-- Tables :
--   - dim_date       : Dimension temporelle
--   - dim_produit    : Dimension produit (carburants)
--   - dim_cours      : Table de faits secondaire (cours Brent)
--   - fact_ventes    : Table de faits principale (ventes gasoil)
-- ============================================================

-- Création de la base de données (à exécuter séparément dans pgAdmin)
-- CREATE DATABASE cbn_analytics;

-- ────────────────────────────────────────────
-- DIMENSION : DATE
-- ────────────────────────────────────────────
-- Chaque ligne = un jour calendaire de 2015 à 2018
-- Permet des analyses par mois, trimestre, année, jour de semaine.

DROP TABLE IF EXISTS fact_ventes CASCADE;
DROP TABLE IF EXISTS dim_cours CASCADE;
DROP TABLE IF EXISTS dim_produit CASCADE;
DROP TABLE IF EXISTS dim_date CASCADE;

CREATE TABLE dim_date (
    id_date         SERIAL PRIMARY KEY,
    date_complete   DATE NOT NULL UNIQUE,
    jour            INTEGER NOT NULL,       -- 1-31
    mois            INTEGER NOT NULL,       -- 1-12
    nom_mois        VARCHAR(20) NOT NULL,   -- 'Janvier', 'Février'...
    annee           INTEGER NOT NULL,       -- 2015, 2016...
    trimestre       INTEGER NOT NULL,       -- 1-4
    jour_semaine    INTEGER NOT NULL,       -- 0=Lundi, 6=Dimanche
    nom_jour        VARCHAR(20) NOT NULL,   -- 'Lundi', 'Mardi'...
    est_weekend     BOOLEAN NOT NULL        -- True si samedi/dimanche
);

-- Index pour les requêtes fréquentes
CREATE INDEX idx_dim_date_annee ON dim_date(annee);
CREATE INDEX idx_dim_date_mois ON dim_date(annee, mois);

-- ────────────────────────────────────────────
-- DIMENSION : PRODUIT
-- ────────────────────────────────────────────
-- Référentiel produits. Même si on filtre sur gasoil,
-- on conserve tous les produits pour l'extensibilité.

CREATE TABLE dim_produit (
    id_produit      SERIAL PRIMARY KEY,
    code_produit    INTEGER NOT NULL UNIQUE,  -- CODPRD du fichier source
    libelle         VARCHAR(50) NOT NULL,     -- LIBPRD1 (ex: 'GASOIL')
    type_produit    VARCHAR(10) NOT NULL,     -- TYPPRD (ex: 'C')
    categorie       VARCHAR(50) NOT NULL      -- CATPRD (ex: 'CARBURANT')
);

-- ────────────────────────────────────────────
-- TABLE DE FAITS SECONDAIRE : COURS DU PÉTROLE
-- ────────────────────────────────────────────
-- Cours Brent journalier (source: Yahoo Finance)
-- Liée à dim_date par la date (pas par FK directe sur fact_ventes)
-- Note : le Brent n'est coté que les jours ouvrés boursiers.
-- On applique un forward-fill pour les week-ends/jours fériés.

CREATE TABLE dim_cours (
    id_cours        SERIAL PRIMARY KEY,
    id_date         INTEGER NOT NULL REFERENCES dim_date(id_date),
    cours_brent_usd NUMERIC(10, 4) NOT NULL,  -- Prix spot en USD/baril
    cours_brent_tnd NUMERIC(10, 4),            -- Converti en TND (optionnel)
    variation_pct   NUMERIC(8, 4),             -- Variation % jour/jour
    source          VARCHAR(30) DEFAULT 'Yahoo Finance'
);

CREATE INDEX idx_dim_cours_date ON dim_cours(id_date);

-- ────────────────────────────────────────────
-- TABLE DE FAITS PRINCIPALE : VENTES
-- ────────────────────────────────────────────
-- Granularité : une ligne = une livraison individuelle
-- Mesures : quantité (m³), montant HT (TND)
-- Attributs dégénérés : code_depot, num_compte (pas de dimension dédiée)

CREATE TABLE fact_ventes (
    id_vente        SERIAL PRIMARY KEY,
    id_date         INTEGER NOT NULL REFERENCES dim_date(id_date),
    id_produit      INTEGER NOT NULL REFERENCES dim_produit(id_produit),
    quantite_m3     NUMERIC(12, 3) NOT NULL,   -- Quantité en m³
    montant_ht      NUMERIC(14, 3) NOT NULL,   -- Montant HT en TND
    prix_unitaire   NUMERIC(10, 3),            -- MNTHT / QTEPRD (TND/m³)
    code_depot      INTEGER,                   -- CODDPO (attribut dégénéré)
    num_compte      INTEGER,                   -- NUMCPT (attribut dégénéré)
    date_retour     DATE                       -- DATRET
);

CREATE INDEX idx_fact_ventes_date ON fact_ventes(id_date);
CREATE INDEX idx_fact_ventes_produit ON fact_ventes(id_produit);
CREATE INDEX idx_fact_ventes_date_produit ON fact_ventes(id_date, id_produit);

-- ────────────────────────────────────────────
-- VUE AGRÉGÉE : VENTES MENSUELLES GASOIL
-- ────────────────────────────────────────────
-- Vue matérialisée pour le dashboard et le modèle ML
-- Agrège les ventes gasoil au niveau mensuel avec le cours Brent moyen

CREATE OR REPLACE VIEW v_ventes_mensuelles_gasoil AS
SELECT
    d.annee,
    d.mois,
    d.nom_mois,
    DATE_TRUNC('month', d.date_complete)::DATE AS date_mois,
    COUNT(f.id_vente)                           AS nb_livraisons,
    SUM(f.quantite_m3)                          AS total_quantite_m3,
    SUM(f.montant_ht)                           AS total_montant_ht,
    AVG(f.prix_unitaire)                        AS prix_unitaire_moyen,
    AVG(c.cours_brent_usd)                      AS cours_brent_moyen_usd
FROM fact_ventes f
JOIN dim_date d ON f.id_date = d.id_date
JOIN dim_produit p ON f.id_produit = p.id_produit
LEFT JOIN dim_cours c ON f.id_date = c.id_date
WHERE p.code_produit = 4  -- GASOIL uniquement
GROUP BY d.annee, d.mois, d.nom_mois, DATE_TRUNC('month', d.date_complete)
ORDER BY date_mois;
