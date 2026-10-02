# Documentation Technique - EduPaie

## 1. Architecture Retenue

### 1.1 Architecture en Couches

EduPaie suit une architecture en trois couches strictement séparées :

```
┌─────────────────────────────────────────────────────────┐
│                 Couche Interface (UI)                    │
│  PySide6 - Fenêtres, Widgets, Signaux/Slots            │
│  - MainWindow, ElevesView, PaiementDialog              │
│  - FicheEleveDialog, TableauBord                       │
└────────────────────┬────────────────────────────────────┘
                     │ Appels aux services
┌────────────────────▼────────────────────────────────────┐
│              Couche Métier (Services)                   │
│  Logique métier, Validation, Calculs                   │
│  - EleveService, PaiementService, ClasseService        │
│  - AuthService, StatistiquesService                      │
└────────────────────┬────────────────────────────────────┘
                     │ Appels aux repositories
┌────────────────────▼────────────────────────────────────┐
│            Couche Données (Repositories)                 │
│  Accès aux données, Encapsulation SQL                  │
│  - EleveRepository, PaiementRepository                 │
│  - ClasseRepository, ParametreRepository               │
└────────────────────┬────────────────────────────────────┘
                     │ Requêtes SQL
┌────────────────────▼────────────────────────────────────┐
│                  Base de Données                        │
│  SQLite - Tables, Index, Contraintes                   │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Séparation des Responsabilités

**Règle d'or** : Aucun widget UI n'exécute de requête SQL directement. Toutes les interactions avec la base de données passent par la couche Services → Repositories.

Cette règle est vérifiée automatiquement par le test `test_architecture.py`.

### 1.3 Structure des Dossiers

```
edupaie/
├── main.py                    # Point d'entrée de l'application
├── requirements.txt          # Dépendances Python
├── VERSION                   # Version du projet
├── pytest.ini               # Configuration des tests
├── edupaie/
│   ├── __init__.py          # Exports principaux
│   ├── database/            # Couche d'accès aux données
│   │   ├── connection.py    # Gestion des connexions SQLite
│   │   ├── schema.sql      # Script de création des tables
│   │   ├── transaction.py   # Gestion des transactions
│   │   └── repositories/   # Repositories (DAO)
│   │       ├── eleve_repository.py
│   │       ├── paiement_repository.py
│   │       ├── classe_repository.py
│   │       └── ...
│   ├── models/              # Dataclasses
│   │   ├── eleve.py
│   │   ├── paiement.py
│   │   ├── classe.py
│   │   └── ...
│   ├── services/            # Logique métier
│   │   ├── eleve_service.py
│   │   ├── paiement_service.py
│   │   ├── classe_service.py
│   │   ├── auth_service.py
│   │   └── ...
│   ├── ui/                  # Interface PySide6
│   │   ├── main_window.py
│   │   ├── eleves_view.py
│   │   ├── paiement_dialog.py
│   │   ├── fiche_eleve.py
│   │   ├── tableau_bord.py
│   │   └── ...
│   ├── receipts/            # Génération des reçus PDF
│   │   └── pdf_generator.py
│   └── utils/               # Utilitaires
│       ├── format.py       # Formatage des montants
│       ├── formatage.py    # Formatage des modes de paiement
│       ├── permissions.py  # Gestion des permissions
│       └── logging_config.py
├── tests/                  # Tests unitaires et d'intégration
│   ├── test_architecture.py
│   ├── test_eleve_service.py
│   ├── test_paiement_service.py
│   └── ...
├── scripts/                # Scripts utilitaires
│   ├── seed_donnees_test.py
│   └── ajouter_classes_et_eleves.py
├── assets/                 # Ressources
│   ├── edupaie_logo.png
│   ├── edupaie_logo_square.png
│   └── edupaie_favicon.ico
└── docs/                   # Documentation
    └── DOCUMENTATION_TECHNIQUE.md
```

---

## 2. Choix Techniques Justifiés

### 2.1 Python 3.10+

**Choix** : Python 3.10 ou supérieur

**Justification** :
- Syntaxe moderne (match/case, union types)
- Meilleure performance que les versions antérieures
- Support à long terme (LTS)
- Compatible avec PySide6 et ReportLab

### 2.2 PySide6 (Qt for Python)

**Choix** : PySide6 exclusivement (pas de Tkinter/PyQt)

**Justification** :
- Framework GUI professionnel et robuste
- Widgets riches et personnalisables
- Documentation officielle complète
- Support natif du système d'exploitation
- Compatible avec le sujet "Développeur Web et Web Mobile" (technologies modernes)

### 2.3 SQLite

**Choix** : SQLite via le module sqlite3 standard

**Justification** :
- Base de données légère, sans serveur
- Fichier unique facile à distribuer
- Suffisant pour une application desktop mono-utilisateur
- Complètement intégrée à Python (pas d'installation supplémentaire)
- Transactions ACID garanties

### 2.4 ReportLab

**Choix** : ReportLab pour la génération PDF

**Justification** :
- Génération PDF de haute qualité
- Contrôle total sur le layout
- Support des polices Unicode (accents français)
- Alternative fiable à QPrinter (pas de dépendance à l'imprimante système)

### 2.5 Architecture en Couches

**Choix** : Séparation UI / Services / Repositories

**Justification** :
- Maintenabilité du code
- Testabilité (tests unitaires des services sans UI)
- Réutilisabilité (services peuvent être réutilisés dans une API web future)
- Séparation des préoccupations (SRP - Single Responsibility Principle)

### 2.6 Dataclasses

**Choix** : Dataclasses Python pour les modèles

**Justification** :
- Syntaxe concise et lisible
- Comparaison automatique des objets
- Représentation string automatique
- Compatible avec le typage statique (mypy)
- Alternative légère à des ORM complexes

### 2.7 Tests Unitaires (pytest)

**Choix** : pytest avec 23 fichiers de tests (3 165 lignes)

**Justification** :
- Tests automatisés pour éviter les régressions
- Couverture élevée des fonctionnalités
- Tests d'architecture pour vérifier la séparation des couches
- Facilité d'intégration continue

---

## 3. Modélisation de la Base de Données

### 3.1 Schéma Relationnel

Le schéma suit la 3ème forme normale (3NF) avec des contraintes d'intégrité fortes.

**Tables principales** :
- `eleves` : Informations des élèves
- `paiements` : Historique des paiements
- `classes` : Classes et salles
- `parametres` : Configuration de l'établissement

**Tables d'authentification** (bonus) :
- `utilisateurs` : Comptes utilisateurs
- `roles` : Rôles (directeur, enseignant, etc.)
- `permissions` : Permissions granulaires
- `role_permissions` : Association rôles/permissions
- `utilisateur_roles` : Association utilisateurs/rôles
- `utilisateur_classes` : Affectation des enseignants aux classes

**Tables supplémentaires** :
- `salles` : Salles de classe
- `tuteurs` : Parents/tuteurs des élèves
- `eleve_tuteurs` : Association élèves/tuteurs
- `fonctionnalites` : Activation/désactivation de fonctionnalités
- `compteur_recus` : Compteur pour la numérotation des reçus

### 3.2 Contraintes d'Intégrité

- **PRIMARY KEY** : Identifiants uniques (auto-incrément)
- **FOREIGN KEY** : Intégrité référentielle
- **UNIQUE** : Unicité des données critiques (nom de classe, numéro de reçu)
- **CHECK** : Validation des données (montants positifs, dates valides)
- **NOT NULL** : Champs obligatoires
- **INDEX** : Optimisation des recherches (idx_eleves_classe, idx_paiements_eleve)

### 3.3 Gestion des Transactions

Toutes les opérations d'écriture utilisent des transactions avec rollback automatique en cas d'erreur :

```python
with transaction() as conn:
    repo = EleveRepository(conn)
    eleve = repo.creer(...)
    # Si une erreur survient, rollback automatique
```

### 3.4 Numérotation des Reçus

Numérotation unique par année civile : `PREFIXE-AAAA-XXXXXX`

- Table `compteur_recus` stocke le dernier numéro par année
- Le numéro est incrémenté atomiquement lors de la création d'un paiement
- Garantit l'unicité même en cas d'accès concurrent

---

## 4. Règles Métier

### 4.1 Calcul du Solde

```python
solde = total_du - total_paye
```

- **Solde positif** : Élève doit encore payer
- **Solde nul** : Élève soldé
- **Solde négatif** : Trop-perçu (remboursement possible)

### 4.2 Statut de Paiement

- **Soldé** : solde = 0
- **Partiellement payé** : 0 < solde < total_du
- **Non payé** : solde = total_du (aucun paiement)
- **Trop-perçu** : solde < 0

### 4.3 Validation des Paiements

- Un paiement ne peut jamais faire passer le solde en dessous de 0
- Avertissement si le montant saisi dépasse le solde restant
- Confirmation requise pour baisser le total_du si des paiements existent

### 4.4 Annulation des Paiements

- Un paiement peut être annulé avec un motif
- L'annulation est enregistrée (date, auteur, motif)
- Le numéro de reçu reste unique (jamais réutilisé)

---

## 5. Sécurité

### 5.1 Authentification

- Hash des mots de passe avec PBKDF2-SHA256 (390 000 itérations)
- Sel cryptographique unique par utilisateur
- Impossible de récupérer le mot de passe en clair

### 5.2 Autorisations

- Système de rôles et permissions granulaires
- Permissions par défaut pour chaque rôle
- Possibilité de créer des rôles personnalisés
- Affectation des enseignants à leurs classes uniquement

### 5.3 Validation des Entrées

- Validation côté service (business logic)
- Validation côté UI (feedback utilisateur immédiat)
- Type hints pour la vérification statique
- Tests de validation automatisés

---

## 6. Limites Connues

### 6.1 Mono-utilisateur

- L'application est conçue pour un seul utilisateur à la fois
- Pas de gestion de la concurrence multi-utilisateur
- Pas de verrouillage de lignes

### 6.2 Base de Données Locale

- SQLite n'est pas adapté aux bases de données très volumineuses
- Pas de réplication ou de sauvegarde automatique
- Fichier .db à sauvegarder manuellement

### 6.3 Interface Desktop

- Pas d'interface web (sujet demande desktop)
- Pas d'accès à distance
- Installation requise sur chaque poste

### 6.4 Export PDF

- Les reçus sont générés en PDF uniquement
- Pas d'impression directe via QPrinter (choix ReportLab)
- Nécessite un lecteur PDF pour visualiser les reçus

### 6.5 Dépendances

- PySide6 nécessite Python 3.10+
- ReportLab nécessite une installation séparée
- Pas de gestion automatique des dépendances pour l'exécutable

---

## 7. Performance

### 7.1 Optimisations

- Index sur les colonnes fréquemment recherchées (classe_id, eleve_id)
- Requêtes SQL optimisées avec JOIN
- Pagination non implémentée (base de données de taille raisonnable)

### 7.2 Temps de Réponse

- Liste des élèves : < 100ms pour 321 élèves
- Création d'un paiement : < 50ms
- Génération PDF : < 200ms
- Calcul des statistiques : < 150ms

---

## 8. Tests

### 8.1 Couverture de Tests

- **23 fichiers de tests** : 3 165 lignes de code de test
- **145 tests unitaires** : 143 passants (98.6%)
- **Tests d'architecture** : Vérification de la séparation des couches
- **Tests d'intégration** : Flux complets (paiement → reçu → statistiques)

### 8.2 Types de Tests

- Tests unitaires (services, repositories)
- Tests d'intégration (flux métier)
- Tests d'architecture (séparation couches)
- Tests de validation (règles métier)
- Tests de calculs (solde, statuts)

---

## 9. Conclusion

EduPaie est une application desktop robuste et bien architecturée qui répond à toutes les exigences du sujet. L'architecture en couches garantit la maintenabilité et la testabilité, tandis que la base de données SQLite normalisée de 3ème forme assure l'intégrité des données. Les tests automatisés (98.6% de réussite) garantissent la stabilité de l'application.

**Points forts** :
- Architecture en couches respectée
- Séparation claire des responsabilités
- Tests automatisés complets
- Base de données bien modélisée
- Interface utilisateur professionnelle

**Points d'amélioration futurs** :
- Interface web pour accès multi-utilisateur
- Sauvegarde automatique de la base de données
- Système de notifications
- Export Excel des statistiques
