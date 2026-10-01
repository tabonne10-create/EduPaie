"""
Gestion de la connexion à la base de données SQLite.

Ce module fournit une fonction pour obtenir une connexion à la base edupaie.db
avec les configurations nécessaires (foreign_keys activés, row_factory).
"""

import sys
import sqlite3
import os
from contextlib import contextmanager
from typing import Generator
from edupaie.utils.paths import get_database_path


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
        return

    # Créer la base et exécuter le schéma
    conn = get_connection()

    # Chemin vers schema.sql
    if getattr(sys, 'frozen', False):
        # Mode packagé PyInstaller : schema.sql est dans sys._MEIPASS
        base_dir = sys._MEIPASS
        schema_path = os.path.join(base_dir, 'schema.sql')
    else:
        # Mode développement
        schema_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'database',
            'schema.sql'
        )

    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    conn.executescript(schema_sql)
    conn.commit()
    conn.close()
