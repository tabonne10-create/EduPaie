"""
Tests unitaires pour ClasseService.
"""

import unittest
from edupaie.services.classe_service import ClasseService
from edupaie.services.exceptions import ValidationError, ConfirmationRequise


class TestClasseService(unittest.TestCase):
    """Tests du service de gestion des classes."""

    def test_creer_classe_nom_vide(self):
        """Teste qu'un nom vide lève une ValidationError."""
        service = ClasseService.__new__(ClasseService)

        with self.assertRaises(ValidationError) as context:
            service.creer_classe("")
        self.assertIn("ne peut pas être vide", str(context.exception))

    def test_creer_classe_nom_espaces(self):
        """Teste qu'un nom avec seulement des espaces lève une ValidationError."""
        service = ClasseService.__new__(ClasseService)

        with self.assertRaises(ValidationError) as context:
            service.creer_classe("   ")
        self.assertIn("ne peut pas être vide", str(context.exception))


if __name__ == "__main__":
    unittest.main()
