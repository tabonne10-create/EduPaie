"""
Tests unitaires pour les fonctions de calcul.
"""

import unittest
from edupaie.services.calculs import (
    calculer_solde,
    calculer_trop_percu,
    determiner_statut,
    formater_numero_recu,
    Statut
)


class TestCalculs(unittest.TestCase):
    """Tests des fonctions de calcul."""

    def test_calculer_solde_normal(self):
        """Teste le calcul du solde dans un cas normal."""
        self.assertEqual(calculer_solde(100000, 50000), 50000)

    def test_calculer_solde_solde_nul(self):
        """Teste le calcul du solde quand tout est payé."""
        self.assertEqual(calculer_solde(100000, 100000), 0)

    def test_calculer_solde_trop_percu(self):
        """Teste que le solde est borné à 0 même en cas de trop-perçu."""
        self.assertEqual(calculer_solde(100000, 150000), 0)

    def test_calculer_solde_zero_du(self):
        """Teste le solde quand rien n'est dû."""
        self.assertEqual(calculer_solde(0, 0), 0)

    def test_calculer_trop_percu_normal(self):
        """Teste le calcul du trop-perçu dans un cas normal."""
        self.assertEqual(calculer_trop_percu(100000, 150000), 50000)

    def test_calculer_trop_percu_aucun(self):
        """Teste que le trop-perçu est 0 quand tout est normal."""
        self.assertEqual(calculer_trop_percu(100000, 100000), 0)

    def test_calculer_trop_percu_solde_restant(self):
        """Teste que le trop-perçu est 0 quand il reste un solde."""
        self.assertEqual(calculer_trop_percu(100000, 50000), 0)

    def test_determiner_statut_solde(self):
        """Teste le statut Soldé quand tout est payé."""
        self.assertEqual(determiner_statut(100000, 100000), Statut.SOLDE)

    def test_determiner_statut_solde_zero_du(self):
        """Teste le statut Soldé quand total_du == 0."""
        self.assertEqual(determiner_statut(0, 0), Statut.SOLDE)

    def test_determiner_statut_non_paye(self):
        """Teste le statut Non payé quand rien n'est payé."""
        self.assertEqual(determiner_statut(100000, 0), Statut.NON_PAYE)

    def test_determiner_statut_partiellement_paye(self):
        """Teste le statut Partiellement payé."""
        self.assertEqual(determiner_statut(100000, 50000), Statut.PARTIELLEMENT_PAYE)

    def test_determiner_statut_trop_percu(self):
        """Teste le statut Soldé en cas de trop-perçu."""
        self.assertEqual(determiner_statut(100000, 150000), Statut.SOLDE)

    def test_formater_numero_recu(self):
        """Teste le formatage d'un numéro de reçu."""
        self.assertEqual(
            formater_numero_recu("REC", 2026, 1),
            "REC-2026-000001"
        )

    def test_formater_numero_recu_grand_numero(self):
        """Teste le formatage avec un grand numéro."""
        self.assertEqual(
            formater_numero_recu("REC", 2026, 123456),
            "REC-2026-123456"
        )


if __name__ == "__main__":
    unittest.main()
