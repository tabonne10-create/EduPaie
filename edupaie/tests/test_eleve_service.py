"""
Tests unitaires pour EleveService.
"""

import unittest
from edupaie.services.eleve_service import EleveService
from edupaie.services.exceptions import ValidationError


class TestEleveService(unittest.TestCase):
    """Tests du service de gestion des élèves."""

    def test_creer_eleve_nom_vide(self):
        """Teste qu'un nom vide lève une ValidationError."""
        service = EleveService.__new__(EleveService)

        with self.assertRaises(ValidationError) as context:
            service.creer_eleve("", "Jean", 1, "2025-2026")
        self.assertIn("Nom", str(context.exception))

    def test_creer_eleve_prenom_vide(self):
        """Teste qu'un prénom vide lève une ValidationError."""
        service = EleveService.__new__(EleveService)

        with self.assertRaises(ValidationError) as context:
            service.creer_eleve("Dupont", "", 1, "2025-2026")
        self.assertIn("Prénom", str(context.exception))

    def test_creer_eleve_montant_negatif(self):
        """Teste qu'un montant négatif lève une ValidationError."""
        service = EleveService.__new__(EleveService)

        with self.assertRaises(ValidationError) as context:
            service.creer_eleve("Dupont", "Jean", 1, "2025-2026", -1000)
        self.assertIn("Total dû", str(context.exception))

    def test_creer_eleve_annee_invalide(self):
        """Teste qu'une année scolaire invalide lève une ValidationError."""
        service = EleveService.__new__(EleveService)

        with self.assertRaises(ValidationError) as context:
            service.creer_eleve("Dupont", "Jean", 1, "2025")
        self.assertIn("AAAA-AAAA", str(context.exception))


if __name__ == "__main__":
    unittest.main()
