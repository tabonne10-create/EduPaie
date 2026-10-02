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
    ('annee_scolaire_courante', CASE
        WHEN CAST(strftime('%m', 'now') AS INTEGER) >= 9
        THEN strftime('%Y', 'now') || '-' || CAST(CAST(strftime('%Y', 'now') AS INTEGER) + 1 AS TEXT)
        ELSE CAST(CAST(strftime('%Y', 'now') AS INTEGER) - 1 AS TEXT) || '-' || strftime('%Y', 'now')
    END),
    ('logo_chemin', '');

-- Table des classes
CREATE TABLE IF NOT EXISTS classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL UNIQUE CHECK (length(trim(nom)) > 0),
    salle_id INTEGER,
    capacite INTEGER CHECK (capacite IS NULL OR capacite > 0),
    FOREIGN KEY (salle_id) REFERENCES salles(id) ON DELETE SET NULL
);

-- Comptes locaux et contrôle d'accès
CREATE TABLE IF NOT EXISTS utilisateurs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_complet TEXT NOT NULL CHECK (length(trim(nom_complet)) > 0),
    identifiant TEXT NOT NULL UNIQUE COLLATE NOCASE CHECK (length(trim(identifiant)) > 0),
    mot_de_passe_hash TEXT NOT NULL,
    actif INTEGER NOT NULL DEFAULT 1 CHECK (actif IN (0, 1)),
    cree_le TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    derniere_connexion TEXT
);

CREATE TABLE IF NOT EXISTS roles (
    code TEXT PRIMARY KEY,
    nom TEXT NOT NULL UNIQUE,
    systeme INTEGER NOT NULL DEFAULT 0 CHECK (systeme IN (0, 1))
);

CREATE TABLE IF NOT EXISTS permissions (
    code TEXT PRIMARY KEY,
    libelle TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS role_permissions (
    role_code TEXT NOT NULL,
    permission_code TEXT NOT NULL,
    PRIMARY KEY (role_code, permission_code),
    FOREIGN KEY (role_code) REFERENCES roles(code) ON DELETE CASCADE,
    FOREIGN KEY (permission_code) REFERENCES permissions(code) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS utilisateur_roles (
    utilisateur_id INTEGER NOT NULL,
    role_code TEXT NOT NULL,
    PRIMARY KEY (utilisateur_id, role_code),
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id) ON DELETE CASCADE,
    FOREIGN KEY (role_code) REFERENCES roles(code) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS utilisateur_classes (
    utilisateur_id INTEGER NOT NULL,
    classe_id INTEGER NOT NULL,
    PRIMARY KEY (utilisateur_id, classe_id),
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id) ON DELETE CASCADE,
    FOREIGN KEY (classe_id) REFERENCES classes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS fonctionnalites (
    code TEXT PRIMARY KEY,
    nom TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 0 CHECK (active IN (0, 1))
);

CREATE TABLE IF NOT EXISTS salles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL UNIQUE CHECK (length(trim(nom)) > 0),
    capacite INTEGER CHECK (capacite IS NULL OR capacite > 0),
    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1))
);

CREATE TABLE IF NOT EXISTS tuteurs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL CHECK (length(trim(nom)) > 0),
    prenom TEXT NOT NULL DEFAULT '',
    telephone TEXT NOT NULL DEFAULT '',
    fonction TEXT NOT NULL DEFAULT '',
    cree_le TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS eleve_tuteurs (
    eleve_id INTEGER NOT NULL,
    tuteur_id INTEGER NOT NULL,
    lien TEXT NOT NULL DEFAULT '',
    principal INTEGER NOT NULL DEFAULT 0 CHECK (principal IN (0, 1)),
    PRIMARY KEY (eleve_id, tuteur_id),
    FOREIGN KEY (eleve_id) REFERENCES eleves(id) ON DELETE CASCADE,
    FOREIGN KEY (tuteur_id) REFERENCES tuteurs(id) ON DELETE CASCADE
);

-- Table des élèves
CREATE TABLE IF NOT EXISTS eleves (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL CHECK (length(trim(nom)) > 0),
    prenom TEXT NOT NULL CHECK (length(trim(prenom)) > 0),
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
    date_paiement TEXT NOT NULL CHECK (date(date_paiement) IS NOT NULL AND date(date_paiement) = date_paiement),  -- Format ISO : AAAA-MM-JJ
    mode TEXT NOT NULL CHECK (mode IN ('especes', 'cheque', 'virement', 'mobile_money')),
    numero_recu TEXT NOT NULL UNIQUE,  -- Format : PREFIXE-AAAA-000001
    solde_apres INTEGER NOT NULL CHECK (solde_apres >= 0),
    cree_le TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- Date/heure de création (ISO, UTC)
    heure_paiement TEXT NOT NULL DEFAULT '00:00:00',
    nom_payeur TEXT NOT NULL DEFAULT '',
    annule_le TEXT,
    annule_par INTEGER,
    motif_annulation TEXT,
    FOREIGN KEY (eleve_id) REFERENCES eleves(id) ON DELETE CASCADE
);

-- Index pour optimiser les recherches par élève
CREATE INDEX IF NOT EXISTS idx_paiements_eleve ON paiements(eleve_id);

-- Table technique pour le compteur de reçus (par année civile)
CREATE TABLE IF NOT EXISTS compteur_recus (
    annee INTEGER PRIMARY KEY,
    dernier_numero INTEGER NOT NULL DEFAULT 0
);
