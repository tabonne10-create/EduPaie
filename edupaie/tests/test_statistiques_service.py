"""
Tests unitaires pour StatistiquesService.
"""

import unittest
import os
import tempfile
import sqlite3
from unittest.mock import patch
from edupaie.services.statistiques_service import StatistiquesService
from edupaie.database.repositories.classe_repository import ClasseRepository
from edupaie.database.repositories.eleve_repository import EleveRepository
from edupaie.database.repositories.paiement_repository import PaiementRepository


class TestStatistiquesService(unittest.TestCase):
    """Tests du service de statistiques."""

    def setUp(self):
        """Crée une base de données temporaire pour chaque test."""
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        self.conn = sqlite3.connect(self.db_path, timeout=10)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")

        # Exécuter le schéma
        schema_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'database',
            'schema.sql'
        )
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        self.conn.executescript(schema_sql)
        self.conn.commit()

    def tearDown(self):
        """Ferme la connexion et supprime la base temporaire."""
        self.conn.close()
        os.close(self.db_fd)
        os.unlink(self.db_path)

    @patch('edupaie.database.transaction.get_connection')
    def test_statistiques_avec_trop_percu(self, mock_get_connection):
        """Teste que StatistiquesService gère correctement le trop-perçu."""
        mock_get_connection.return_value = self.conn

        # Créer des données de test
        classe_repo = ClasseRepository(self.conn)
        eleve_repo = EleveRepository(self.conn)
        paiement_repo = PaiementRepository(self.conn)

        classe = classe_repo.creer("6ème A")
        self.conn.commit()

        # Élève 1 : trop-perçu
        eleve1 = eleve_repo.creer("Dupont", "Jean", classe.id, "2025-2026", 150000)
        self.conn.commit()
        paiement_repo.inserer(eleve1.id, 200000, "2025-09-30", "especes", "REC-2025-000001", 0)
        self.conn.commit()

        # Élève 2 : soldé exact
        eleve2 = eleve_repo.creer("Martin", "Paul", classe.id, "2025-2026", 150000)
        self.conn.commit()
        paiement_repo.inserer(eleve2.id, 150000, "2025-09-30", "especes", "REC-2025-000002", 0)
        self.conn.commit()

        # Tester le service
        service = StatistiquesService()
        result = service.obtenir_statistiques_globales()

        # Vérifier que le solde est borné à 0 (pas négatif malgré le trop-perçu)
        self.assertEqual(result["total_solde"], 0)
        self.assertEqual(result["total_paye"], 350000)
        self.assertEqual(result["total_du"], 300000)
        self.assertEqual(result["total_eleves"], 2)


if __name__ == "__main__":
    unittest.main()
