"""
Tests unitaires pour PaiementService.
"""

import unittest
from edupaie.services.paiement_service import PaiementService
from edupaie.services.exceptions import ValidationError


class TestPaiementService(unittest.TestCase):
    """Tests du service de gestion des paiements."""

    def test_enregistrer_paiement_montant_invalide(self):
        """Teste qu'un montant invalide lève une ValidationError."""
        service = PaiementService.__new__(PaiementService)

        with self.assertRaises(ValidationError) as context:
            service.enregistrer_paiement(1, 0, "2025-01-15", "especes")
        self.assertIn("strictement positif", str(context.exception))

    def test_enregistrer_paiement_date_invalide(self):
        """Teste qu'une date invalide lève une ValidationError."""
        service = PaiementService.__new__(PaiementService)

        with self.assertRaises(ValidationError) as context:
            service.enregistrer_paiement(1, 50000, "15/01/2025", "especes")
        self.assertIn("AAAA-MM-JJ", str(context.exception))

    def test_enregistrer_paiement_mode_invalide(self):
        """Teste qu'un mode invalide lève une ValidationError."""
        service = PaiementService.__new__(PaiementService)

        with self.assertRaises(ValidationError) as context:
            service.enregistrer_paiement(1, 50000, "2025-01-15", "carte")
        self.assertIn("Modes autorisés", str(context.exception))


if __name__ == "__main__":
    unittest.main()
