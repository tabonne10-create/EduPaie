"""
Tests unitaires pour PaiementService.
"""

import unittest
from unittest.mock import patch, MagicMock
from edupaie.services.paiement_service import PaiementService
from edupaie.services.exceptions import ValidationError, RegleMetierError
from edupaie.models.paiement import Paiement
from edupaie.models.eleve import Eleve


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

    @patch('edupaie.services.paiement_service.transaction')
    @patch.object(PaiementService, '__init__', lambda self: None)
    def test_paiement_depasse_solde_refuse_sans_ecriture(self, mock_transaction):
        """Teste qu'un paiement dépassant le solde est refusé sans écriture."""
        mock_conn = MagicMock()
        mock_transaction.return_value.__enter__.return_value = mock_conn

        service = PaiementService()

        with patch('edupaie.services.paiement_service.EleveRepository') as mock_eleve_repo_class, \
             patch('edupaie.services.paiement_service.PaiementRepository') as mock_paiement_repo_class, \
             patch('edupaie.services.paiement_service.CompteurRecusRepository') as mock_compteur_repo_class, \
             patch('edupaie.services.paiement_service.ParametreRepository') as mock_parametre_repo_class:

            mock_eleve_repo = MagicMock()
            mock_paiement_repo = MagicMock()
            mock_compteur_repo = MagicMock()
            mock_parametre_repo = MagicMock()

            mock_eleve_repo_class.return_value = mock_eleve_repo
            mock_paiement_repo_class.return_value = mock_paiement_repo
            mock_compteur_repo_class.return_value = mock_compteur_repo
            mock_parametre_repo_class.return_value = mock_parametre_repo

            # Mock élève avec total_du = 150000
            mock_eleve_repo.trouver_par_id.return_value = Eleve(
                id=1,
                nom="Dupont",
                prenom="Jean",
                classe_id=1,
                annee_scolaire="2025-2026",
                total_du=150000
            )

            # Mock paiements existants (déjà 100000 payés)
            mock_paiement = MagicMock()
            mock_paiement.montant = 100000
            mock_paiement_repo.lister_par_eleve.return_value = [mock_paiement]

            with self.assertRaises(RegleMetierError) as context:
                service.enregistrer_paiement(1, 60000, "2025-01-15", "especes")

            self.assertIn("excède le montant dû", str(context.exception))
            # Vérifier que l'insertion n'a pas été appelée
            mock_paiement_repo.inserer.assert_not_called()

    @patch('edupaie.services.paiement_service.transaction')
    @patch.object(PaiementService, '__init__', lambda self: None)
    def test_paiement_egal_solde_accepte(self, mock_transaction):
        """Teste qu'un paiement égal au solde restant est accepté."""
        mock_conn = MagicMock()
        mock_transaction.return_value.__enter__.return_value = mock_conn

        service = PaiementService()

        with patch('edupaie.services.paiement_service.EleveRepository') as mock_eleve_repo_class, \
             patch('edupaie.services.paiement_service.PaiementRepository') as mock_paiement_repo_class, \
             patch('edupaie.services.paiement_service.CompteurRecusRepository') as mock_compteur_repo_class, \
             patch('edupaie.services.paiement_service.ParametreRepository') as mock_parametre_repo_class:

            mock_eleve_repo = MagicMock()
            mock_paiement_repo = MagicMock()
            mock_compteur_repo = MagicMock()
            mock_parametre_repo = MagicMock()

            mock_eleve_repo_class.return_value = mock_eleve_repo
            mock_paiement_repo_class.return_value = mock_paiement_repo
            mock_compteur_repo_class.return_value = mock_compteur_repo
            mock_parametre_repo_class.return_value = mock_parametre_repo

            # Mock élève avec total_du = 150000
            mock_eleve_repo.trouver_par_id.return_value = Eleve(
                id=1,
                nom="Dupont",
                prenom="Jean",
                classe_id=1,
                annee_scolaire="2025-2026",
                total_du=150000
            )

            # Mock paiements existants (déjà 100000 payés)
            mock_paiement = MagicMock()
            mock_paiement.montant = 100000
            mock_paiement_repo.lister_par_eleve.return_value = [mock_paiement]

            # Mock insertion
            mock_paiement_repo.inserer.return_value = 1
            mock_paiement_repo.trouver_par_id.return_value = MagicMock(
                id=1,
                montant=50000,
                numero_recu="REC-2025-000001"
            )

            # Mock compteur
            mock_compteur_repo.incrementer.return_value = 1
            mock_parametre_repo.lire.return_value = "REC"

            # Doit réussir (50000 == solde restant)
            result = service.enregistrer_paiement(1, 50000, "2025-01-15", "especes")

            self.assertIsNotNone(result)
            mock_paiement_repo.inserer.assert_called_once()

    @patch('edupaie.services.paiement_service.transaction')
    @patch.object(PaiementService, '__init__', lambda self: None)
    def test_numerotation_recus_sequentielle(self, mock_transaction):
        """Teste que les numéros de reçus sont séquentiels (000001, 000002)."""
        mock_conn = MagicMock()
        mock_transaction.return_value.__enter__.return_value = mock_conn

        service = PaiementService()

        with patch('edupaie.services.paiement_service.EleveRepository') as mock_eleve_repo_class, \
             patch('edupaie.services.paiement_service.PaiementRepository') as mock_paiement_repo_class, \
             patch('edupaie.services.paiement_service.CompteurRecusRepository') as mock_compteur_repo_class, \
             patch('edupaie.services.paiement_service.ParametreRepository') as mock_parametre_repo_class:

            mock_eleve_repo = MagicMock()
            mock_paiement_repo = MagicMock()
            mock_compteur_repo = MagicMock()
            mock_parametre_repo = MagicMock()

            mock_eleve_repo_class.return_value = mock_eleve_repo
            mock_paiement_repo_class.return_value = mock_paiement_repo
            mock_compteur_repo_class.return_value = mock_compteur_repo
            mock_parametre_repo_class.return_value = mock_parametre_repo

            mock_eleve_repo.trouver_par_id.return_value = Eleve(
                id=1,
                nom="Dupont",
                prenom="Jean",
                classe_id=1,
                annee_scolaire="2025-2026",
                total_du=150000
            )
            mock_paiement_repo.lister_par_eleve.return_value = []
            mock_parametre_repo.lire.return_value = "REC"

            # Premier paiement : compteur retourne 1
            mock_compteur_repo.incrementer.return_value = 1
            mock_paiement_repo.inserer.return_value = 1
            mock_paiement_repo.trouver_par_id.return_value = MagicMock(
                numero_recu="REC-2025-000001"
            )

            result1 = service.enregistrer_paiement(1, 50000, "2025-01-15", "especes")
            self.assertEqual(result1.numero_recu, "REC-2025-000001")

            # Deuxième paiement : compteur retourne 2
            mock_compteur_repo.incrementer.return_value = 2
            mock_paiement_repo.inserer.return_value = 2
            mock_paiement_repo.trouver_par_id.return_value = MagicMock(
                numero_recu="REC-2025-000002"
            )

            result2 = service.enregistrer_paiement(1, 50000, "2025-01-16", "especes")
            self.assertEqual(result2.numero_recu, "REC-2025-000002")

    @patch('edupaie.services.paiement_service.transaction')
    @patch.object(PaiementService, '__init__', lambda self: None)
    def test_prefixe_modifiable(self, mock_transaction):
        """Teste que le préfixe des reçus est modifiable."""
        mock_conn = MagicMock()
        mock_transaction.return_value.__enter__.return_value = mock_conn

        service = PaiementService()

        with patch('edupaie.services.paiement_service.EleveRepository') as mock_eleve_repo_class, \
             patch('edupaie.services.paiement_service.PaiementRepository') as mock_paiement_repo_class, \
             patch('edupaie.services.paiement_service.CompteurRecusRepository') as mock_compteur_repo_class, \
             patch('edupaie.services.paiement_service.ParametreRepository') as mock_parametre_repo_class:

            mock_eleve_repo = MagicMock()
            mock_paiement_repo = MagicMock()
            mock_compteur_repo = MagicMock()
            mock_parametre_repo = MagicMock()

            mock_eleve_repo_class.return_value = mock_eleve_repo
            mock_paiement_repo_class.return_value = mock_paiement_repo
            mock_compteur_repo_class.return_value = mock_compteur_repo
            mock_parametre_repo_class.return_value = mock_parametre_repo

            mock_eleve_repo.trouver_par_id.return_value = Eleve(
                id=1,
                nom="Dupont",
                prenom="Jean",
                classe_id=1,
                annee_scolaire="2025-2026",
                total_du=150000
            )
            mock_paiement_repo.lister_par_eleve.return_value = []
            mock_compteur_repo.incrementer.return_value = 1
            mock_paiement_repo.inserer.return_value = 1
            mock_paiement_repo.trouver_par_id.return_value = MagicMock(
                numero_recu="FAC-2025-000001"
            )

            # Préfixe modifié en "FAC"
            mock_parametre_repo.lire.return_value = "FAC"

            result = service.enregistrer_paiement(1, 50000, "2025-01-15", "especes")
            self.assertEqual(result.numero_recu, "FAC-2025-000001")

    @patch('edupaie.services.paiement_service.transaction')
    @patch.object(PaiementService, '__init__', lambda self: None)
    def test_changement_annee_reinitialise_compteur(self, mock_transaction):
        """Teste que le changement d'année réinitialise le compteur."""
        mock_conn = MagicMock()
        mock_transaction.return_value.__enter__.return_value = mock_conn

        service = PaiementService()

        with patch('edupaie.services.paiement_service.EleveRepository') as mock_eleve_repo_class, \
             patch('edupaie.services.paiement_service.PaiementRepository') as mock_paiement_repo_class, \
             patch('edupaie.services.paiement_service.CompteurRecusRepository') as mock_compteur_repo_class, \
             patch('edupaie.services.paiement_service.ParametreRepository') as mock_parametre_repo_class:

            mock_eleve_repo = MagicMock()
            mock_paiement_repo = MagicMock()
            mock_compteur_repo = MagicMock()
            mock_parametre_repo = MagicMock()

            mock_eleve_repo_class.return_value = mock_eleve_repo
            mock_paiement_repo_class.return_value = mock_paiement_repo
            mock_compteur_repo_class.return_value = mock_compteur_repo
            mock_parametre_repo_class.return_value = mock_parametre_repo

            mock_eleve_repo.trouver_par_id.return_value = Eleve(
                id=1,
                nom="Dupont",
                prenom="Jean",
                classe_id=1,
                annee_scolaire="2025-2026",
                total_du=150000
            )
            mock_paiement_repo.lister_par_eleve.return_value = []
            mock_parametre_repo.lire.return_value = "REC"
            mock_paiement_repo.inserer.return_value = 1
            mock_paiement_repo.trouver_par_id.return_value = MagicMock(
                numero_recu="REC-2025-000001"
            )

            # Paiement en 2025 : compteur 1
            mock_compteur_repo.incrementer.return_value = 1
            result1 = service.enregistrer_paiement(1, 50000, "2025-12-31", "especes")
            self.assertEqual(result1.numero_recu, "REC-2025-000001")

            # Paiement en 2026 : compteur réinitialisé à 1
            mock_compteur_repo.incrementer.return_value = 1
            mock_paiement_repo.trouver_par_id.return_value = MagicMock(
                numero_recu="REC-2026-000001"
            )

            result2 = service.enregistrer_paiement(1, 50000, "2026-01-01", "especes")
            self.assertEqual(result2.numero_recu, "REC-2026-000001")


if __name__ == "__main__":
    unittest.main()
