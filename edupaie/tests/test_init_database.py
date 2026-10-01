"""
Tests d'initialisation de la base de données.

Ce module vérifie que la base est correctement initialisée
quand elle est absente ou vide, et qu'elle n'est pas modifiée
quand elle contient déjà des données.
"""

import os
import tempfile
import shutil

from edupaie.database.connection import init_database, get_connection
from edupaie.utils.paths import get_database_path


def test_base_vide_est_initialisee():
    """Vérifie qu'une base vide (fichier de 0 octet) est correctement initialisée."""
    # Sauvegarder le chemin original
    original_db_path = get_database_path()

    # Créer un fichier vide temporaire
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db_path = os.path.join(tmpdir, 'test_edupaie.db')

        # Créer un fichier vide
        with open(test_db_path, 'w') as f:
            pass  # Fichier vide

        # Patch temporairement get_database_path
        import edupaie.database.connection as conn_module
        original_get_db_path = conn_module.get_database_path
        conn_module.get_database_path = lambda: test_db_path

        try:
            # Initialiser
            init_database()

            # Vérifier que la table classes existe
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='classes'"
            )
            result = cursor.fetchone()
            conn.close()

            assert result is not None, "La table 'classes' devrait exister après initialisation"
        finally:
            # Restaurer la fonction originale
            conn_module.get_database_path = original_get_db_path


def test_base_existante_pas_modifiee():
    """Vérifie qu'une base déjà remplie n'est pas modifiée."""
    # Sauvegarder le chemin original
    original_db_path = get_database_path()

    with tempfile.TemporaryDirectory() as tmpdir:
        test_db_path = os.path.join(tmpdir, 'test_edupaie.db')

        # Patch temporairement get_database_path
        import edupaie.database.connection as conn_module
        original_get_db_path = conn_module.get_database_path
        conn_module.get_database_path = lambda: test_db_path

        try:
            # Créer une base avec des données
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE classes (id INTEGER PRIMARY KEY, nom TEXT NOT NULL)")
            cursor.execute("INSERT INTO classes (nom) VALUES ('TestClass')")
            conn.commit()
            conn.close()

            # Récupérer l'ID avant réinitialisation
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM classes WHERE nom = 'TestClass'")
            original_id = cursor.fetchone()[0]
            conn.close()

            # Initialiser (ne devrait rien changer)
            init_database()

            # Vérifier que les données sont toujours là
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM classes WHERE nom = 'TestClass'")
            result = cursor.fetchone()
            conn.close()

            assert result is not None, "Les données existantes ne devraient pas être supprimées"
            assert result[0] == original_id, "L'ID ne devrait pas changer"
        finally:
            # Restaurer la fonction originale
            conn_module.get_database_path = original_get_db_path
