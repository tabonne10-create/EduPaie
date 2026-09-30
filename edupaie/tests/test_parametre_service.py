"""
Tests unitaires pour ParametreService.
"""

import unittest
from edupaie.services.parametre_service import ParametreService
from edupaie.services.exceptions import ValidationError


class TestParametreService(unittest.TestCase):
    """Tests du service de gestion des paramètres."""

    def test_lire_parametre_nom_vide(self):
        """Teste qu'un nom vide lève une ValidationError."""
        service = ParametreService.__new__(ParametreService)

        with self.assertRaises(ValidationError) as context:
            service.ecrire_parametre("nom_etablissement", "")
        self.assertIn("ne peut pas être vide", str(context.exception))

    def test_ecrire_parametre_telephone_invalide(self):
        """Teste qu'un téléphone invalide lève une ValidationError."""
        service = ParametreService.__new__(ParametreService)

        with self.assertRaises(ValidationError) as context:
            service.ecrire_parametre("telephone", "abc")
        self.assertIn("chiffres", str(context.exception))

    def test_ecrire_parametre_email_invalide(self):
        """Teste qu'un email invalide lève une ValidationError."""
        service = ParametreService.__new__(ParametreService)

        with self.assertRaises(ValidationError) as context:
            service.ecrire_parametre("email", "invalid")
        self.assertIn("@", str(context.exception))

    def test_mettre_a_jour_paiements_devise_vide(self):
        """Teste qu'une devise vide lève une ValidationError."""
        service = ParametreService.__new__(ParametreService)

        with self.assertRaises(ValidationError) as context:
            service.mettre_a_jour_paiements("", "REC")
        self.assertIn("ne peut pas être vide", str(context.exception))

    def test_mettre_a_jour_paiements_prefixe_invalide(self):
        """Teste qu'un préfixe invalide lève une ValidationError."""
        service = ParametreService.__new__(ParametreService)

        with self.assertRaises(ValidationError) as context:
            service.mettre_a_jour_paiements("FCFA", "123")
        self.assertIn("lettres", str(context.exception))


if __name__ == "__main__":
    unittest.main()
