"""
Tests unitaires pour les fonctions de validation.
"""

import unittest
from edupaie.services.validation import (
    valider_nom,
    valider_montant,
    valider_montant_positif,
    valider_montant_chaine,
    valider_annee_scolaire,
    valider_date,
    valider_mode_paiement,
    valider_telephone,
    valider_email,
    valider_numero_recu
)
from edupaie.services.exceptions import ValidationError


class TestValidation(unittest.TestCase):
    """Tests des fonctions de validation."""

    def test_valider_nom_valide(self):
        """Teste qu'un nom valide passe."""
        valider_nom("Dupont")
        valider_nom("Jean-Pierre")

    def test_valider_nom_vide(self):
        """Teste qu'un nom vide lève une erreur."""
        with self.assertRaises(ValidationError) as context:
            valider_nom("")
        self.assertIn("ne peut pas être vide", str(context.exception))

    def test_valider_nom_espaces(self):
        """Teste qu'un nom avec seulement des espaces lève une erreur."""
        with self.assertRaises(ValidationError) as context:
            valider_nom("   ")
        self.assertIn("ne peut pas être vide", str(context.exception))

    def test_valider_montant_valide(self):
        """Teste qu'un montant valide passe."""
        valider_montant(0)
        valider_montant(1000)

    def test_valider_montant_negatif(self):
        """Teste qu'un montant négatif lève une erreur."""
        with self.assertRaises(ValidationError) as context:
            valider_montant(-100)
        self.assertIn("ne peut pas être négatif", str(context.exception))

    def test_valider_montant_positif_valide(self):
        """Teste qu'un montant strictement positif valide passe."""
        valider_montant_positif(1)
        valider_montant_positif(1000)

    def test_valider_montant_positif_zero(self):
        """Teste qu'un montant zéro lève une erreur."""
        with self.assertRaises(ValidationError) as context:
            valider_montant_positif(0)
        self.assertIn("strictement positif", str(context.exception))

    def test_valider_montant_positif_negatif(self):
        """Teste qu'un montant négatif lève une erreur."""
        with self.assertRaises(ValidationError) as context:
            valider_montant_positif(-100)
        self.assertIn("strictement positif", str(context.exception))

    def test_valider_annee_scolaire_valide(self):
        """Teste qu'une année scolaire valide passe."""
        valider_annee_scolaire("2025-2026")
        valider_annee_scolaire("2000-2001")

    def test_valider_annee_scolaire_format_invalide(self):
        """Teste qu'un format invalide lève une erreur."""
        with self.assertRaises(ValidationError) as context:
            valider_annee_scolaire("2025")
        self.assertIn("AAAA-AAAA", str(context.exception))

    def test_valider_annee_scolaire_non_consecutive(self):
        """Teste que des années non consécutives lèvent une erreur."""
        with self.assertRaises(ValidationError) as context:
            valider_annee_scolaire("2025-2027")
        self.assertIn("consécutives", str(context.exception))

    def test_valider_annee_scolaire_hors_limites(self):
        """Teste qu'une année hors limites lève une erreur."""
        with self.assertRaises(ValidationError) as context:
            valider_annee_scolaire("1999-2000")
        self.assertIn("2000-2001", str(context.exception))

    def test_valider_date_valide(self):
        """Teste qu'une date valide passe."""
        valider_date("2025-01-15")
        valider_date("2024-12-31")

    def test_valider_date_future(self):
        """Teste qu'une date future est refusée."""
        from datetime import datetime, timedelta
        date_future = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        with self.assertRaises(ValidationError) as context:
            valider_date(date_future)
        self.assertIn("futur", str(context.exception))

    def test_valider_date_vide(self):
        """Teste qu'une date vide lève une erreur."""
        with self.assertRaises(ValidationError) as context:
            valider_date("")
        self.assertIn("ne peut pas être vide", str(context.exception))

    def test_valider_date_format_invalide(self):
        """Teste qu'un format invalide lève une erreur."""
        with self.assertRaises(ValidationError) as context:
            valider_date("15/01/2025")
        self.assertIn("AAAA-MM-JJ", str(context.exception))

    def test_valider_date_mois_invalide(self):
        """Teste qu'un mois invalide lève une erreur."""
        with self.assertRaises(ValidationError) as context:
            valider_date("2025-13-01")
        self.assertIn("entre 01 et 12", str(context.exception))

    def test_valider_date_jour_invalide(self):
        """Teste qu'un jour invalide lève une erreur."""
        with self.assertRaises(ValidationError) as context:
            valider_date("2025-01-32")
        self.assertIn("entre 01 et 31", str(context.exception))

    def test_valider_date_30_jours(self):
        """Teste la validation des mois à 30 jours."""
        with self.assertRaises(ValidationError) as context:
            valider_date("2025-04-31")
        self.assertIn("30 jours", str(context.exception))

    def test_valider_date_fevrier_normal(self):
        """Teste février en année non bissextile."""
        with self.assertRaises(ValidationError) as context:
            valider_date("2025-02-29")
        self.assertIn("28 ou 29 jours", str(context.exception))

    def test_valider_date_fevrier_bissextile(self):
        """Teste février en année bissextile."""
        valider_date("2024-02-29")  # 2024 est bissextile

    def test_valider_mode_paiement_valide(self):
        """Teste qu'un mode de paiement valide passe."""
        valider_mode_paiement("especes")
        valider_mode_paiement("cheque")
        valider_mode_paiement("virement")
        valider_mode_paiement("mobile_money")

    def test_valider_mode_paiement_invalide(self):
        """Teste qu'un mode invalide lève une erreur."""
        with self.assertRaises(ValidationError) as context:
            valider_mode_paiement("carte")
        self.assertIn("Modes autorisés", str(context.exception))

    def test_valider_telephone_valide(self):
        """Teste qu'un téléphone valide passe."""
        valider_telephone("0123456789")
        valider_telephone("01 23 45 67 89")
        valider_telephone("")

    def test_valider_telephone_invalide(self):
        """Teste qu'un téléphone avec lettres lève une erreur."""
        with self.assertRaises(ValidationError) as context:
            valider_telephone("abc123")
        self.assertIn("chiffres", str(context.exception))

    def test_valider_telephone_trop_court(self):
        """Teste qu'un téléphone trop court lève une erreur."""
        with self.assertRaises(ValidationError) as context:
            valider_telephone("1234567")
        self.assertIn("entre 8 et 15", str(context.exception))

    def test_valider_telephone_trop_long(self):
        """Teste qu'un téléphone trop long lève une erreur."""
        with self.assertRaises(ValidationError) as context:
            valider_telephone("1234567890123456")
        self.assertIn("entre 8 et 15", str(context.exception))

    def test_valider_email_valide(self):
        """Teste qu'un email valide passe."""
        valider_email("test@example.com")
        valider_email("")

    def test_valider_email_sans_arobase(self):
        """Teste qu'un email sans @ lève une erreur."""
        with self.assertRaises(ValidationError) as context:
            valider_email("testexample.com")
        self.assertIn("@", str(context.exception))

    def test_valider_email_sans_point(self):
        """Teste qu'un email sans point lève une erreur."""
        with self.assertRaises(ValidationError) as context:
            valider_email("test@example")
        self.assertIn(".", str(context.exception))

    def test_valider_email_commence_arobase(self):
        """Teste qu'un email commençant par @ lève une erreur."""
        with self.assertRaises(ValidationError) as context:
            valider_email("@example.com")
        self.assertIn("@", str(context.exception))

    def test_valider_numero_recu_valide(self):
        """Teste qu'un numéro de reçu valide passe."""
        valider_numero_recu("REC-2025-000001")
        valider_numero_recu("FAC-2026-123456")

    def test_valider_montant_chaine_valide(self):
        """Teste qu'un montant chaîne valide passe."""
        self.assertEqual(valider_montant_chaine("150000"), 150000)
        self.assertEqual(valider_montant_chaine("150 000"), 150000)

    def test_valider_montant_chaine_abc(self):
        """Teste qu'un montant avec lettres lève une erreur."""
        with self.assertRaises(ValidationError) as context:
            valider_montant_chaine("abc")
        self.assertIn("nombre valide", str(context.exception))

    def test_valider_montant_chaine_negatif(self):
        """Teste qu'un montant négatif lève une erreur."""
        with self.assertRaises(ValidationError) as context:
            valider_montant_chaine("-5")
        self.assertIn("strictement positif", str(context.exception))

    def test_valider_montant_chaine_zero(self):
        """Teste qu'un montant zéro lève une erreur."""
        with self.assertRaises(ValidationError) as context:
            valider_montant_chaine("0")
        self.assertIn("strictement positif", str(context.exception))

    def test_valider_montant_chaine_virgule(self):
        """Teste qu'un montant avec virgule est refusé."""
        with self.assertRaises(ValidationError) as context:
            valider_montant_chaine("12,5")
        self.assertIn("décimales", str(context.exception))

    def test_valider_montant_chaine_point(self):
        """Teste qu'un montant avec point décimal est refusé."""
        with self.assertRaises(ValidationError) as context:
            valider_montant_chaine("12.5")
        self.assertIn("décimales", str(context.exception))

    def test_valider_numero_recu_vide(self):
        """Teste qu'un numéro vide lève une erreur."""
        with self.assertRaises(ValidationError) as context:
            valider_numero_recu("")
        self.assertIn("ne peut pas être vide", str(context.exception))

    def test_valider_numero_recu_format_invalide(self):
        """Teste qu'un format invalide lève une erreur."""
        with self.assertRaises(ValidationError) as context:
            valider_numero_recu("REC2025000001")
        self.assertIn("PREFIXE-AAAA-XXXXXX", str(context.exception))

    def test_valider_numero_recu_prefixe_invalide(self):
        """Teste qu'un préfixe invalide lève une erreur."""
        with self.assertRaises(ValidationError) as context:
            valider_numero_recu("123-2025-000001")
        self.assertIn("lettres", str(context.exception))

    def test_valider_numero_recu_chiffres_insuffisants(self):
        """Teste qu'un numéro sur moins de 6 chiffres lève une erreur."""
        with self.assertRaises(ValidationError) as context:
            valider_numero_recu("REC-2025-00001")
        self.assertIn("6 chiffres", str(context.exception))


if __name__ == "__main__":
    unittest.main()
