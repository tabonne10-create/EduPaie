"""
Gestion des transactions de base de données.

Ce module fournit un contexte pour exécuter des opérations
dans une transaction avec rollback automatique en cas d'erreur.
"""

from contextlib import contextmanager
from typing import Generator
import sqlite3

from edupaie.database.connection import get_connection


@contextmanager
def transaction() -> Generator[sqlite3.Connection, None, None]:
    """
    Contexte de transaction avec rollback automatique en cas d'erreur.

    Usage:
        with transaction() as conn:
            # Opérations sur conn
            # Tout échec entraîne un rollback automatique
            pass

    Yields:
        sqlite3.Connection: Connexion dans la transaction

    Raises:
        Exception: Toute exception déclenche un rollback
    """
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
