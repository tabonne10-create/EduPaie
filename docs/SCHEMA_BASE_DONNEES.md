# Schéma de la Base de Données - EduPaie

## 1. Diagramme Entité-Association (Mermaid)

```mermaid
erDiagram
    %% Tables principales
    CLASSES ||--o{ ELEVES : "contient"
    ELEVES ||--o{ PAIEMENTS : "effectue"
    PARAMETRES ||--|| : "configuration"
    UTILISATEURS ||--o{ UTILISATEUR_ROLES : "a"
    ROLES ||--o{ UTILISATEUR_ROLES : "attribué à"
    ROLES ||--o{ ROLE_PERMISSIONS : "possède"
    PERMISSIONS ||--o{ ROLE_PERMISSIONS : "accordée"
    UTILISATEURS ||--o{ UTILISATEUR_CLASSES : "accède à"
    CLASSES ||--o{ UTILISATEUR_CLASSES : "affectée à"
    SALLES ||--o{ CLASSES : "héberge"
    TUTEURS ||--o{ ELEVE_TUTEURS : "est tuteur de"
    ELEVES ||--o{ ELEVE_TUTEURS : "a pour tuteur"
    FONCTIONNALITES ||--|| : "configuration"
    COMPTEUR_RECUS ||--|| : "numérotation"

    %% Table CLASSES
    CLASSES {
        int id PK
        string nom UK
        int salle_id FK
        int capacite
    }

    %% Table ELEVES
    ELEVES {
        int id PK
        string nom
        string prenom
        int classe_id FK
        string annee_scolaire
        int total_du
    }

    %% Table PAIEMENTS
    PAIEMENTS {
        int id PK
        int eleve_id FK
        int montant
        string date_paiement
        string mode
        string numero_recu UK
        int solde_apres
        string cree_le
        string heure_paiement
        string nom_payeur
        string annule_le
        int annule_par FK
        string motif_annulation
    }

    %% Table PARAMETRES
    PARAMETRES {
        string cle PK
        string valeur
    }

    %% Table UTILISATEURS
    UTILISATEURS {
        int id PK
        string nom_complet
        string identifiant UK
        string mot_de_passe_hash
        int actif
        string cree_le
        string derniere_connexion
    }

    %% Table ROLES
    ROLES {
        string code PK
        string nom UK
        int systeme
    }

    %% Table PERMISSIONS
    PERMISSIONS {
        string code PK
        string libelle
    }

    %% Table UTILISATEUR_ROLES
    UTILISATEUR_ROLES {
        int utilisateur_id PK,FK
        string role_code PK,FK
    }

    %% Table ROLE_PERMISSIONS
    ROLE_PERMISSIONS {
        string role_code PK,FK
        string permission_code PK,FK
    }

    %% Table UTILISATEUR_CLASSES
    UTILISATEUR_CLASSES {
        int utilisateur_id PK,FK
        int classe_id PK,FK
    }

    %% Table SALLES
    SALLES {
        int id PK
        string nom UK
        int capacite
        int active
    }

    %% Table TUTEURS
    TUTEURS {
        int id PK
        string nom
        string prenom
        string telephone
        string fonction
        string cree_le
    }

    %% Table ELEVE_TUTEURS
    ELEVE_TUTEURS {
        int eleve_id PK,FK
        int tuteur_id PK,FK
        string lien
        int principal
    }

    %% Table FONCTIONNALITES
    FONCTIONNALITES {
        string code PK
        string nom
        int active
    }

    %% Table COMPTEUR_RECUS
    COMPTEUR_RECUS {
        int annee PK
        int dernier_numero
    }
```

## 2. Description des Tables

### 2.1 Tables Principales (Cœur du métier)

#### `classes`
- **Description** : Liste des classes de l'établissement
- **Clé primaire** : `id` (auto-incrément)
- **Contraintes** :
  - `nom` UNIQUE : pas de doublon de nom de classe
  - `salle_id` FK → `salles(id)` avec ON DELETE SET NULL
  - `capacite` CHECK : doit être NULL ou > 0

#### `eleves`
- **Description** : Liste des élèves inscrits
- **Clé primaire** : `id` (auto-incrément)
- **Contraintes** :
  - `nom` CHECK : non vide après trim
  - `prenom` CHECK : non vide après trim
  - `classe_id` FK → `classes(id)` avec ON DELETE RESTRICT
  - `total_du` CHECK : ≥ 0
- **Index** : `idx_eleves_classe` sur `classe_id`

#### `paiements`
- **Description** : Historique des paiements effectués
- **Clé primaire** : `id` (auto-incrément)
- **Contraintes** :
  - `eleve_id` FK → `eleves(id)` avec ON DELETE CASCADE
  - `montant` CHECK : > 0
  - `date_paiement` CHECK : date valide (format ISO YYYY-MM-DD)
  - `mode` CHECK : IN ('especes', 'cheque', 'virement', 'mobile_money')
  - `numero_recu` UNIQUE : numéro de reçu unique
  - `solde_apres` CHECK : ≥ 0
- **Index** : `idx_paiements_eleve` sur `eleve_id`

#### `parametres`
- **Description** : Configuration de l'établissement (clé/valeur)
- **Clé primaire** : `cle`
- **Exemples** : nom_etablissement, devise, prefixe_recu, annee_scolaire_courante

### 2.2 Tables d'Authentification et Autorisations

#### `utilisateurs`
- **Description** : Comptes utilisateurs de l'application
- **Clé primaire** : `id` (auto-incrément)
- **Contraintes** :
  - `nom_complet` CHECK : non vide après trim
  - `identifiant` UNIQUE COLLATE NOCASE : insensible à la casse
  - `mot_de_passe_hash` : hash PBKDF2-SHA256
  - `actif` CHECK : IN (0, 1)

#### `roles`
- **Description** : Rôles utilisateurs (directeur, comptable, etc.)
- **Clé primaire** : `code`
- **Contraintes** :
  - `nom` UNIQUE
  - `systeme` CHECK : IN (0, 1) (rôles système immuables)

#### `permissions`
- **Description** : Permissions granulaires (payments.register, etc.)
- **Clé primaire** : `code`

#### `utilisateur_roles` (Table d'association)
- **Description** : Association utilisateurs ↔ rôles (N:M)
- **Clé primaire** : (`utilisateur_id`, `role_code`)
- **Contraintes** : CASCADE sur suppression

#### `role_permissions` (Table d'association)
- **Description** : Association rôles ↔ permissions (N:M)
- **Clé primaire** : (`role_code`, `permission_code`)
- **Contraintes** : CASCADE sur suppression

#### `utilisateur_classes` (Table d'association)
- **Description** : Affectation des enseignants à leurs classes
- **Clé primaire** : (`utilisateur_id`, `classe_id`)
- **Contraintes** : CASCADE sur suppression

### 2.3 Tables Supplémentaires

#### `salles`
- **Description** : Salles de classe
- **Clé primaire** : `id` (auto-incrément)
- **Contraintes** :
  - `nom` UNIQUE
  - `capacite` CHECK : NULL ou > 0
  - `active` CHECK : IN (0, 1)

#### `tuteurs`
- **Description** : Parents/tuteurs des élèves
- **Clé primaire** : `id` (auto-incrément)
- **Contraintes** :
  - `nom` CHECK : non vide après trim

#### `eleve_tuteurs` (Table d'association)
- **Description** : Association élèves ↔ tuteurs (N:M)
- **Clé primaire** : (`eleve_id`, `tuteur_id`)
- **Contraintes** :
  - `principal` CHECK : IN (0, 1)
  - CASCADE sur suppression

#### `fonctionnalites`
- **Description** : Activation/désactivation de fonctionnalités
- **Clé primaire** : `code`
- **Contraintes** : `active` CHECK : IN (0, 1)

#### `compteur_recus`
- **Description** : Compteur pour numérotation des reçus par année
- **Clé primaire** : `annee`
- **Usage** : Garantit l'unicité des numéros de reçu (PREFIXE-AAAA-XXXXXX)

## 3. Relations Principales

### 3.1 Relation Élève ↔ Paiements (1:N)
- Un élève peut avoir plusieurs paiements
- Un paiement appartient à un seul élève
- Contrainte : CASCADE DELETE (supprimer élève → supprimer ses paiements)

### 3.2 Relation Classe ↔ Élèves (1:N)
- Une classe peut avoir plusieurs élèves
- Un élève appartient à une seule classe
- Contrainte : RESTRICT DELETE (ne peut pas supprimer une classe avec des élèves)

### 3.3 Relation Utilisateur ↔ Rôles (N:M)
- Un utilisateur peut avoir plusieurs rôles
- Un rôle peut être attribué à plusieurs utilisateurs

### 3.4 Relation Rôle ↔ Permissions (N:M)
- Un rôle peut avoir plusieurs permissions
- Une permission peut être attribuée à plusieurs rôles

## 4. Contraintes d'Intégrité

### 4.1 Contraintes de clé
- **PRIMARY KEY** : Identifiants uniques (auto-incrément ou naturel)
- **FOREIGN KEY** : Intégrité référentielle entre tables
- **UNIQUE** : Unicité des données critiques (nom classe, numéro reçu, identifiant)

### 4.2 Contraintes de domaine
- **CHECK** : Validation des données
  - Montants positifs
  - Dates valides
  - Modes de paiement valides
  - Actif/inactif (0 ou 1)

### 4.3 Contraintes de non-nullité
- **NOT NULL** : Champs obligatoires (nom, prénom, identifiant, etc.)

## 5. Normalisation

Le schéma respecte la **3ème Forme Normale (3NF)** :
- **1NF** : Tous les attributs sont atomiques
- **2NF** : Pas de dépendances partielles de clé
- **3NF** : Pas de dépendances transitives de clé

## 6. Index pour Optimisation

- `idx_eleves_classe` : accélère les recherches par classe
- `idx_paiements_eleve` : accélère l'historique des paiements d'un élève

## 7. Transactions

Toutes les opérations d'écriture utilisent des transactions ACID :
- **Atomicité** : tout ou rien
- **Cohérence** : contraintes respectées
- **Isolation** : opérations isolées
- **Durabilité** : écritures persistantes

Rollback automatique en cas d'erreur.
