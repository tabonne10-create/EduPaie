"""
Tests unitaires pour les fonctions de formatage.
"""

import unittest
from edupaie.utils.format import formater_montant


class TestFormat(unittest.TestCase):
    """Tests des fonctions de formatage."""

    def test_formater_montant_simple(self):
        """Teste le formatage d'un montant simple."""
        self.assertEqual(formater_montant(150000, "FCFA"), "150 000 FCFA")

    def test_formater_montant_petit(self):
        """Teste le formatage d'un petit montant."""
        self.assertEqual(formater_montant(1000, "FCFA"), "1 000 FCFA")

    def test_formater_montant_zero(self):
        """Teste le formatage d'un montant nul."""
        self.assertEqual(formater_montant(0, "FCFA"), "0 FCFA")

    def test_formater_montant_grand(self):
        """Teste le formatage d'un grand montant."""
        self.assertEqual(
            formater_montant(1500000, "FCFA"),
            "1 500 000 FCFA"
        )

    def test_formater_montant_autre_devise(self):
        """Teste le formatage avec une autre devise."""
        self.assertEqual(formater_montant(150000, "EUR"), "150 000 EUR")


if __name__ == "__main__":
    unittest.main()
