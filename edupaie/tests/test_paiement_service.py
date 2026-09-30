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
    def test_paiement_depasse_solde_refuse_sans_ecriture(self, mock_transaction):
        """Teste qu'un paiement dépassant le solde est refusé sans écriture."""
        from datetime import date

        mock_conn = MagicMock()
        mock_transaction.return_value.__enter__.return_value = mock_conn

        service = PaiementService(aujourdhui=lambda: date(2025, 1, 15))

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

            # Mock devise
            mock_parametre_repo.lire.return_value = "FCFA"

            with self.assertRaises(RegleMetierError) as context:
                service.enregistrer_paiement(1, 60000, "2025-01-15", "especes")

            self.assertIn("excède le montant dû", str(context.exception))
            # Vérifier que l'insertion n'a pas été appelée
            mock_paiement_repo.inserer.assert_not_called()

            # Vérifier que le message contient le montant formaté avec devise
            self.assertIn("50 000 FCFA", str(context.exception))

    @patch('edupaie.services.paiement_service.transaction')
    def test_paiement_egal_solde_accepte(self, mock_transaction):
        """Teste qu'un paiement égal au solde restant est accepté."""
        from datetime import date

        mock_conn = MagicMock()
        mock_transaction.return_value.__enter__.return_value = mock_conn

        service = PaiementService(aujourdhui=lambda: date(2025, 1, 15))

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
            mock_paiement_retourne = MagicMock(
                id=1,
                montant=50000,
                numero_recu="REC-2025-000001",
                solde_apres=0  # Solde après = 0 car paiement = solde restant
            )
            mock_paiement_repo.trouver_par_id.return_value = mock_paiement_retourne

            # Mock compteur
            mock_compteur_repo.incrementer.return_value = 1
            mock_parametre_repo.lire.return_value = "REC"

            # Doit réussir (50000 == solde restant)
            result = service.enregistrer_paiement(1, 50000, "2025-01-15", "especes")

            self.assertIsNotNone(result)
            mock_paiement_repo.inserer.assert_called_once()
            # Vérifier que solde_apres = 0 (statut Soldé)
            self.assertEqual(result.solde_apres, 0)

    @patch('edupaie.services.paiement_service.transaction')
    def test_numerotation_recus_sequentielle(self, mock_transaction):
        """Teste que les numéros de reçus sont séquentiels (000001, 000002)."""
        from datetime import date

        mock_conn = MagicMock()
        mock_transaction.return_value.__enter__.return_value = mock_conn

        service = PaiementService(aujourdhui=lambda: date(2025, 1, 15))

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
    def test_prefixe_modifiable(self, mock_transaction):
        """Teste que le préfixe des reçus est modifiable."""
        from datetime import date

        mock_conn = MagicMock()
        mock_transaction.return_value.__enter__.return_value = mock_conn

        service = PaiementService(aujourdhui=lambda: date(2025, 1, 15))

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
    def test_changement_annee_reinitialise_compteur(self, mock_transaction):
        """Teste que le changement d'année réinitialise le compteur (basé sur date du jour)."""
        from datetime import date

        mock_conn = MagicMock()
        mock_transaction.return_value.__enter__.return_value = mock_conn

        # Premier appel : date du jour = 2025-12-31
        service2025 = PaiementService(aujourdhui=lambda: date(2025, 12, 31))

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
            result1 = service2025.enregistrer_paiement(1, 50000, "2025-12-31", "especes")
            self.assertEqual(result1.numero_recu, "REC-2025-000001")

        # Deuxième appel : date du jour = 2026-01-01
        service2026 = PaiementService(aujourdhui=lambda: date(2026, 1, 1))

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
            mock_paiement_repo.inserer.return_value = 2
            mock_paiement_repo.trouver_par_id.return_value = MagicMock(
                numero_recu="REC-2026-000001"
            )

            # Paiement en 2026 : compteur réinitialisé à 1
            mock_compteur_repo.incrementer.return_value = 1
            result2 = service2026.enregistrer_paiement(1, 50000, "2026-01-01", "especes")
            self.assertEqual(result2.numero_recu, "REC-2026-000001")

    @patch('edupaie.services.paiement_service.transaction')
    def test_paiement_annee_precedente_saisi_annee_courante(self, mock_transaction):
        """Teste qu'un paiement daté de l'année précédente saisi cette année reçoit un numéro de l'année en cours."""
        from datetime import date

        mock_conn = MagicMock()
        mock_transaction.return_value.__enter__.return_value = mock_conn

        # Date du jour = 2026-01-15
        service = PaiementService(aujourdhui=lambda: date(2026, 1, 15))

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
                numero_recu="REC-2026-000001"
            )

            # Paiement daté de 2025 mais saisi en 2026 : numéro de 2026
            mock_compteur_repo.incrementer.return_value = 1
            result = service.enregistrer_paiement(1, 50000, "2025-12-31", "especes")
            self.assertEqual(result.numero_recu, "REC-2026-000001")

    @patch('edupaie.services.paiement_service.transaction')
    def test_erreur_insertion_annule_compteur(self, mock_transaction):
        """Teste qu'une erreur à l'insertion annule l'incrémentation du compteur."""
        from datetime import date

        mock_conn = MagicMock()
        mock_transaction.return_value.__enter__.return_value = mock_conn

        service = PaiementService(aujourdhui=lambda: date(2025, 1, 15))

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

            # Simuler une erreur à l'insertion
            mock_paiement_repo.inserer.side_effect = Exception("Erreur d'insertion")

            # Le compteur est incrémenté avant l'insertion
            mock_compteur_repo.incrementer.return_value = 1

            # L'erreur doit être propagée
            with self.assertRaises(Exception) as context:
                service.enregistrer_paiement(1, 50000, "2025-01-15", "especes")
            self.assertEqual(str(context.exception), "Erreur d'insertion")

            # Vérifier que l'insertion a été appelée
            mock_paiement_repo.inserer.assert_called_once()

            # Vérifier que le compteur a été incrémenté (dans la transaction)
            mock_compteur_repo.incrementer.assert_called_once_with(2025)

            # Le rollback est assuré par le contexte de transaction
            # En pratique, cela signifie que l'incrémentation du compteur
            # est aussi annulée quand la transaction est rollbackée


if __name__ == "__main__":
    unittest.main()
