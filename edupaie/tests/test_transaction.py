"""
Tests unitaires pour la gestion des transactions.
"""

import unittest
import os
import tempfile
import sqlite3
from unittest.mock import patch
from edupaie.database.transaction import transaction


class TestTransaction(unittest.TestCase):
    """Tests du contexte de transaction."""

    def setUp(self):
        """Prépare une base de données temporaire pour les tests."""
        # Utiliser un répertoire temporaire dans le projet
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
        conn.close()

    def tearDown(self):
        """Nettoie la base de données temporaire."""
        try:
            os.unlink(self.temp_db_path)
        except:
            pass

    def _get_temp_connection(self):
        """Retourne une connexion à la base temporaire avec les mêmes paramètres que get_connection."""
        conn = sqlite3.connect(self.temp_db_path, isolation_level=None, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    @patch('edupaie.database.transaction.get_connection')
    def test_transaction_commit(self, mock_get_connection):
        """Teste qu'une transaction réussie est commitée."""
        mock_get_connection.return_value = self._get_temp_connection()

        with transaction() as conn:
            conn.execute("INSERT INTO test_table (valeur) VALUES (?)", ("test",))

        # Vérifier que la donnée est persistée
        conn = self._get_temp_connection()
        result = conn.execute("SELECT valeur FROM test_table").fetchone()
        conn.close()
        self.assertEqual(result[0], "test")

    @patch('edupaie.database.transaction.get_connection')
    def test_transaction_rollback_on_error(self, mock_get_connection):
        """Teste qu'une erreur entraîne un rollback."""
        mock_get_connection.return_value = self._get_temp_connection()

        # Insérer une donnée avant
        conn = self._get_temp_connection()
        conn.execute("INSERT INTO test_table (valeur) VALUES (?)", ("before",))
        conn.commit()
        conn.close()

        # Tenter une transaction qui échoue
        with self.assertRaises(ValueError):
            with transaction() as conn:
                conn.execute("INSERT INTO test_table (valeur) VALUES (?)", ("during",))
                raise ValueError("Test error")

        # Vérifier que "during" n'est pas dans la base
        conn = self._get_temp_connection()
        rows = conn.execute("SELECT valeur FROM test_table").fetchall()
        conn.close()
        valeurs = [row[0] for row in rows]
        self.assertEqual(valeurs, ["before"])
        self.assertNotIn("during", valeurs)

    @patch('edupaie.database.transaction.get_connection')
    def test_transaction_multiple_operations(self, mock_get_connection):
        """Teste plusieurs opérations dans une même transaction."""
        mock_get_connection.return_value = self._get_temp_connection()

        with transaction() as conn:
            conn.execute("INSERT INTO test_table (valeur) VALUES (?)", ("test1",))
            conn.execute("INSERT INTO test_table (valeur) VALUES (?)", ("test2",))
            conn.execute("INSERT INTO test_table (valeur) VALUES (?)", ("test3",))

        # Vérifier que toutes les données sont persistées
        conn = self._get_temp_connection()
        rows = conn.execute("SELECT valeur FROM test_table ORDER BY valeur").fetchall()
        conn.close()
        valeurs = [row[0] for row in rows]
        self.assertEqual(valeurs, ["test1", "test2", "test3"])

    @patch('edupaie.database.transaction.get_connection')
    def test_transaction_verrou(self, mock_get_connection):
        """Teste qu'une seconde transaction avec un timeout court lève sqlite3.OperationalError."""
        mock_get_connection.return_value = self._get_temp_connection()

        # Ouvrir une transaction et la laisser ouverte
        conn1 = self._get_temp_connection()
        conn1.execute("BEGIN IMMEDIATE")

        # Tenter une seconde transaction avec un timeout très court
        try:
            conn2 = sqlite3.connect(self.temp_db_path, isolation_level=None, timeout=0.1)
            conn2.row_factory = sqlite3.Row
            conn2.execute("BEGIN IMMEDIATE")
            self.fail("La seconde transaction aurait dû lever sqlite3.OperationalError")
        except sqlite3.OperationalError as e:
            self.assertIn("locked", str(e).lower())
        finally:
            conn1.execute("ROLLBACK")
            conn1.close()
            if 'conn2' in locals():
                conn2.close()


if __name__ == "__main__":
    unittest.main()
