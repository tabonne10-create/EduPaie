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
        # Utiliser un répertoire temporaire dans le projet
        self.temp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'temp_db')
        os.makedirs(self.temp_dir, exist_ok=True)
        self.db_path = os.path.join(self.temp_dir, f'test_{id(self)}.db')
        self.conn = sqlite3.connect(self.db_path, isolation_level=None, timeout=10)
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

    def tearDown(self):
        """Ferme la connexion et supprime la base temporaire."""
        self.conn.close()
        try:
            os.unlink(self.db_path)
        except:
            pass

    @patch('edupaie.database.transaction.get_connection')
    def test_statistiques_avec_trop_percu(self, mock_get_connection):
        """Teste que StatistiquesService gère correctement le trop-perçu."""
        mock_get_connection.return_value = self.conn

        # Créer des données de test
        classe_repo = ClasseRepository(self.conn)
        eleve_repo = EleveRepository(self.conn)
        paiement_repo = PaiementRepository(self.conn)

        classe = classe_repo.creer("6ème A")


        # Élève 1 : trop-perçu
        eleve1 = eleve_repo.creer("Dupont", "Jean", classe.id, "2025-2026", 150000)

        paiement_repo.inserer(eleve1.id, 200000, "2025-09-30", "especes", "REC-2025-000001", 0)
        paiement_repo.inserer(eleve1.id, 10000, "2025-10-01", "especes", "REC-2025-000003", 0)


        # Élève 2 : soldé exact
        eleve2 = eleve_repo.creer("Martin", "Paul", classe.id, "2025-2026", 150000)

        paiement_repo.inserer(eleve2.id, 150000, "2025-09-30", "especes", "REC-2025-000002", 0)

        # Élève 3 : aucun paiement, sa dette ne doit pas être compensée par le trop-perçu d'un autre.
        eleve3 = eleve_repo.creer("Sow", "Awa", classe.id, "2025-2026", 50000)


        # Tester le service
        service = StatistiquesService()
        result = service.obtenir_statistiques_globales()

        # Vérifier que le solde est borné à 0 (pas négatif malgré le trop-perçu)
        self.assertEqual(result["total_solde"], 50000)
        self.assertEqual(result["total_paye"], 360000)
        self.assertEqual(result["total_du"], 350000)
        self.assertEqual(result["total_eleves"], 3)


if __name__ == "__main__":
    unittest.main()
