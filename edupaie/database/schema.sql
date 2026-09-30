-- Schéma de la base de données EduPaie
-- Une base par établissement

-- Table des paramètres de l'établissement (clé/valeur)
-- Permet d'ajouter des paramètres sans modifier le schéma
CREATE TABLE IF NOT EXISTS parametres (
    cle TEXT PRIMARY KEY,
    valeur TEXT NOT NULL
);

-- Insertion des paramètres par défaut
INSERT OR IGNORE INTO parametres (cle, valeur) VALUES
    ('nom_etablissement', 'Mon Établissement'),
    ('sigle', ''),
    ('adresse', ''),
    ('telephone', ''),
    ('email', ''),
    ('devise', 'FCFA'),
    ('prefixe_recu', 'REC'),
    ('annee_scolaire_courante', '2025-2026'),
    ('logo_chemin', '');

-- Table des classes
CREATE TABLE IF NOT EXISTS classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL UNIQUE
);

-- Table des élèves
CREATE TABLE IF NOT EXISTS eleves (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    classe_id INTEGER NOT NULL,
    annee_scolaire TEXT NOT NULL,
    total_du INTEGER NOT NULL DEFAULT 0 CHECK (total_du >= 0),
    FOREIGN KEY (classe_id) REFERENCES classes(id) ON DELETE RESTRICT
);

-- Index pour optimiser les recherches par classe
CREATE INDEX IF NOT EXISTS idx_eleves_classe ON eleves(classe_id);

-- Table des paiements
CREATE TABLE IF NOT EXISTS paiements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    eleve_id INTEGER NOT NULL,
    montant INTEGER NOT NULL CHECK (montant > 0),
    date_paiement TEXT NOT NULL,  -- Format ISO : AAAA-MM-JJ
    mode TEXT NOT NULL CHECK (mode IN ('especes', 'cheque', 'virement', 'mobile_money')),
    numero_recu TEXT NOT NULL UNIQUE,  -- Format : PREFIXE-AAAA-000001
    solde_apres INTEGER NOT NULL,
    cree_le TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- Date/heure de création (ISO)
    FOREIGN KEY (eleve_id) REFERENCES eleves(id) ON DELETE CASCADE
);

-- Index pour optimiser les recherches par élève
CREATE INDEX IF NOT EXISTS idx_paiements_eleve ON paiements(eleve_id);

-- Table technique pour le compteur de reçus (par année civile)
CREATE TABLE IF NOT EXISTS compteur_recus (
    annee INTEGER PRIMARY KEY,
    dernier_numero INTEGER NOT NULL DEFAULT 0
);
