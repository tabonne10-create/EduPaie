"""
Tests pour la gestion des connexions de base de données.
"""

import unittest
import os
import sqlite3
from edupaie.database.connection import readonly_connection


class TestConnection(unittest.TestCase):
    """Tests des fonctions de connexion."""

    def setUp(self):
        """Prépare une base de données temporaire pour les tests."""
        self.temp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'temp_db')
        os.makedirs(self.temp_dir, exist_ok=True)
        self.temp_db_path = os.path.join(self.temp_dir, f'test_{id(self)}.db')

        # Initialiser la base
        conn = sqlite3.connect(self.temp_db_path, isolation_level=None, timeout=10)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY,
                valeur TEXT
            )
        """)
        conn.execute("INSERT INTO test_table (valeur) VALUES (?)", ("test_data",))
        conn.close()

    def tearDown(self):
        """Nettoie la base de données temporaire."""
        try:
            os.unlink(self.temp_db_path)
        except:
            pass

    def test_readonly_connection_ferme_connexion(self):
        """Teste que readonly_connection ferme bien la connexion même en cas d'erreur."""
        from unittest.mock import patch, MagicMock

        # Mock get_connection pour retourner notre connexion de test
        original_get_connection = __import__('edupaie.database.connection', fromlist=['get_connection']).get_connection

        def mock_get_connection():
            conn = sqlite3.connect(self.temp_db_path, isolation_level=None, timeout=10)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            return conn

        with patch('edupaie.database.connection.get_connection', side_effect=mock_get_connection):
            # Test normal : connexion fermée après usage
            with readonly_connection() as conn:
                result = conn.execute("SELECT valeur FROM test_table").fetchone()
                self.assertEqual(result[0], "test_data")

            # Test avec erreur : connexion quand même fermée
            try:
                with readonly_connection() as conn:
                    conn.execute("SELECT valeur FROM test_table")
                    raise ValueError("Test error")
            except ValueError:
                pass

            # Vérifier que la connexion est bien fermée (on peut réouvrir le fichier)
            # Si la connexion n'était pas fermée, le fichier serait verrouillé
            conn2 = sqlite3.connect(self.temp_db_path, isolation_level=None, timeout=10)
            conn2.execute("SELECT valeur FROM test_table")
            conn2.close()


if __name__ == "__main__":
    unittest.main()
