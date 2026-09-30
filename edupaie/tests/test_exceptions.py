"""
Tests unitaires pour les exceptions personnalisées.
"""

import unittest
from edupaie.services.exceptions import (
    ValidationError,
    RegleMetierError,
    ConfirmationRequise
)


class TestExceptions(unittest.TestCase):
    """Tests des exceptions personnalisées."""

    def test_validation_error(self):
        """Teste que ValidationError peut être levée et capturée."""
        with self.assertRaises(ValidationError):
            raise ValidationError("Donnée invalide")

    def test_validation_error_message(self):
        """Teste le message de ValidationError."""
        try:
            raise ValidationError("Test message")
        except ValidationError as e:
            self.assertEqual(str(e), "Test message")

    def test_regle_metier_error(self):
        """Teste que RegleMetierError peut être levée et capturée."""
        with self.assertRaises(RegleMetierError):
            raise RegleMetierError("Règle violée")

    def test_regle_metier_error_message(self):
        """Teste le message de RegleMetierError."""
        try:
            raise RegleMetierError("Test message")
        except RegleMetierError as e:
            self.assertEqual(str(e), "Test message")

    def test_confirmation_requise(self):
        """Teste que ConfirmationRequise peut être levée et capturée."""
        with self.assertRaises(ConfirmationRequise):
            raise ConfirmationRequise("Confirmer l'action")

    def test_confirmation_requise_message(self):
        """Teste le message de ConfirmationRequise."""
        exc = ConfirmationRequise("Confirmer la suppression")
        self.assertEqual(exc.message, "Confirmer la suppression")
        self.assertEqual(str(exc), "Confirmer la suppression")


if __name__ == "__main__":
    unittest.main()
