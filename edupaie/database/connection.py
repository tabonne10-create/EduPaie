"""
Gestion de la connexion à la base de données SQLite.

Ce module fournit une fonction pour obtenir une connexion à la base edupaie.db
avec les configurations nécessaires (foreign_keys activés, row_factory).
"""

import sys
import sqlite3
import os
from datetime import date
from contextlib import contextmanager
from typing import Generator
from edupaie.utils.paths import get_database_path


PERMISSIONS_PAR_DEFAUT = {
    "dashboard.view": "Consulter le tableau de bord",
    "students.view": "Consulter les élèves",
    "students.manage": "Ajouter et modifier les élèves",
    "classes.view": "Consulter les classes",
    "classes.manage": "Gérer les classes et les salles",
    "payments.view": "Consulter les paiements",
    "payments.register": "Enregistrer un paiement",
    "payments.cancel": "Annuler un paiement avec motif",
    "receipts.view": "Consulter le registre des reçus",
    "receipts.export": "Exporter les reçus PDF",
    "guardians.manage": "Gérer les parents et tuteurs",
    "users.manage": "Gérer les utilisateurs et leurs rôles",
    "permissions.manage": "Attribuer les permissions aux rôles",
    "features.manage": "Activer ou désactiver les fonctionnalités",
    "settings.manage": "Modifier les paramètres de l'établissement",
}

ROLES_PAR_DEFAUT = {
    "directeur": ("Directeur", set(PERMISSIONS_PAR_DEFAUT)),
    "comptable": ("Comptable", {
        "dashboard.view", "students.view", "classes.view", "payments.view",
        "payments.register", "payments.cancel", "receipts.view", "receipts.export",
    }),
    "secretaire": ("Secrétaire", {
        "dashboard.view", "students.view", "students.manage", "classes.view",
        "payments.view", "payments.register", "payments.cancel", "receipts.view",
        "receipts.export", "guardians.manage",
    }),
    "enseignant": ("Enseignant", {
        "dashboard.view", "students.view", "classes.view",
    }),
}

FONCTIONNALITES_PAR_DEFAUT = {
    "dashboard": ("Tableau de bord", 1),
    "students": ("Gestion des élèves", 1),
    "classes": ("Gestion des classes", 1),
    "payments": ("Paiements", 1),
    "receipts": ("Reçus PDF", 1),
    "guardians": ("Parents et tuteurs", 1),
    "rooms": ("Gestion des salles", 1),
    "advanced_reports": ("Rapports avancés", 0),
}


def _initialiser_extensions(conn: sqlite3.Connection) -> None:
    """Migre une base existante de façon idempotente, sans supprimer ses données."""
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'"
    ).fetchall()
    tables_existantes = {row[0] for row in tables}
    if "classes" not in tables_existantes:
        return

    colonnes_a_ajouter = {
        "classes": {
            "salle_id": "INTEGER REFERENCES salles(id) ON DELETE SET NULL",
            "capacite": "INTEGER CHECK (capacite IS NULL OR capacite > 0)",
        },
        "paiements": {
            "heure_paiement": "TEXT NOT NULL DEFAULT '00:00:00'",
            "nom_payeur": "TEXT NOT NULL DEFAULT ''",
            "annule_le": "TEXT",
            "annule_par": "INTEGER",
            "motif_annulation": "TEXT",
        },
    }
    for table, definitions in colonnes_a_ajouter.items():
        colonnes_existantes = {
            row[1] for row in conn.execute(f"PRAGMA table_info({table})")
        }
        for colonne, definition in definitions.items():
            if colonne not in colonnes_existantes:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {colonne} {definition}")

    version = conn.execute("PRAGMA user_version").fetchone()[0]
    if version < 1:
        for code, libelle in PERMISSIONS_PAR_DEFAUT.items():
            conn.execute(
                "INSERT OR IGNORE INTO permissions (code, libelle) VALUES (?, ?)",
                (code, libelle),
            )
        for code, (nom, permissions) in ROLES_PAR_DEFAUT.items():
            conn.execute(
                "INSERT OR IGNORE INTO roles (code, nom, systeme) VALUES (?, ?, 1)",
                (code, nom),
            )
            conn.executemany(
                "INSERT OR IGNORE INTO role_permissions (role_code, permission_code) VALUES (?, ?)",
                [(code, permission) for permission in permissions],
            )
        for code, (nom, active) in FONCTIONNALITES_PAR_DEFAUT.items():
            conn.execute(
                "INSERT OR IGNORE INTO fonctionnalites (code, nom, active) VALUES (?, ?, ?)",
                (code, nom, active),
            )
        conn.execute("PRAGMA user_version = 1")


def get_connection():
    """
    Ouvre une connexion à la base de données edupaie.db.

    La connexion est configurée avec :
    - isolation_level=None : autocommit côté Python (BEGIN explicite requis)
    - timeout=10 : attente de 10 secondes si la base est verrouillée
    - PRAGMA foreign_keys = ON : active les clés étrangères
    - row_factory = sqlite3.Row : permet d'accéder aux colonnes par nom

    Returns:
        sqlite3.Connection: Connexion à la base de données
    """
    db_path = get_database_path()
    conn = sqlite3.connect(db_path, isolation_level=None, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def readonly_connection() -> Generator[sqlite3.Connection, None, None]:
    """
    Contexte pour une connexion en lecture seule avec fermeture garantie.

    Usage:
        with readonly_connection() as conn:
            # Opérations de lecture sur conn
            pass

    Yields:
        sqlite3.Connection: Connexion pour lecture

    Note:
        La connexion est fermée automatiquement dans le finally,
        même en cas d'erreur.
    """
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def init_database():
    """
    Initialise la base de données si elle n'existe pas ou si elle est vide.

    Lit le fichier schema.sql et exécute les commandes SQL pour créer
    les tables et insérer les données par défaut.

    Note packaging PyInstaller :
    - En développement : schema.sql est dans edupaie/database/
    - En packaging : schema.sql est dans sys._MEIPASS (dossier temporaire PyInstaller)
    - Le fichier sera inclus via --add-data dans le spec file PyInstaller
    """
    db_path = get_database_path()

    # Vérifier si la base doit être initialisée
    needs_init = False

    if not os.path.exists(db_path):
        # Fichier inexistant
        needs_init = True
    else:
        # Fichier existe : vérifier s'il contient des tables
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='classes'"
        )
        result = cursor.fetchone()
        conn.close()

        if result is None:
            # Table 'classes' n'existe pas
            needs_init = True

    if not needs_init:
        aujourdhui = date.today()
        debut_annee = aujourdhui.year if aujourdhui.month >= 9 else aujourdhui.year - 1
        annee_courante = f"{debut_annee}-{debut_annee + 1}"
        conn = get_connection()
    else:
        conn = get_connection()

    # Charger le schéma pour initialiser les bases neuves ou créer les nouvelles tables.
    if getattr(sys, 'frozen', False):
        # Mode packagé PyInstaller : schema.sql est dans sys._MEIPASS/edupaie/database/
        base_dir = sys._MEIPASS
        schema_path = os.path.join(base_dir, 'edupaie', 'database', 'schema.sql')
    else:
        # Mode développement
        schema_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'database',
            'schema.sql'
        )

    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    try:
        conn.executescript(schema_sql)
        if not needs_init:
            aujourdhui = date.today()
            debut_annee = aujourdhui.year if aujourdhui.month >= 9 else aujourdhui.year - 1
            annee_courante = f"{debut_annee}-{debut_annee + 1}"
            conn.execute(
                "UPDATE parametres SET valeur = ? "
                "WHERE cle = 'annee_scolaire_courante' AND valeur = '2025-2026'"
            , (annee_courante,))
        _initialiser_extensions(conn)
        conn.commit()
    finally:
        conn.close()
