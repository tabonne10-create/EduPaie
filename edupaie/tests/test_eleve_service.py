"""
Tests unitaires pour EleveService.
"""

import unittest
from unittest.mock import patch, MagicMock
from edupaie.services.eleve_service import EleveService
from edupaie.services.exceptions import ValidationError, ConfirmationRequise


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

    @patch('edupaie.services.eleve_service.transaction')
    @patch.object(EleveService, '__init__', lambda self: None)
    def test_modifier_eleve_baisse_total_du_avec_paiements_demande_confirmation(self, mock_transaction):
        """Teste que baisser le total_du avec paiements demande confirmation."""
        mock_conn = MagicMock()
        mock_transaction.return_value.__enter__.return_value = mock_conn

        service = EleveService()

        with patch('edupaie.services.eleve_service.EleveRepository') as mock_eleve_repo_class, \
             patch('edupaie.services.eleve_service.ClasseRepository') as mock_classe_repo_class, \
             patch('edupaie.database.repositories.paiement_repository.PaiementRepository') as mock_paiement_repo_class:

            mock_eleve_repo = MagicMock()
            mock_classe_repo = MagicMock()
            mock_paiement_repo = MagicMock()

            mock_eleve_repo_class.return_value = mock_eleve_repo
            mock_classe_repo_class.return_value = mock_classe_repo
            mock_paiement_repo_class.return_value = mock_paiement_repo

            # Mock élève existant avec total_du = 150000
            mock_eleve_repo.trouver_par_id.return_value = MagicMock(
                id=1,
                nom="Dupont",
                prenom="Jean",
                total_du=150000
            )
            mock_classe_repo.trouver_par_id.return_value = MagicMock(id=1)

            # Mock paiements existants
            mock_paiement = MagicMock()
            mock_paiement_repo.lister_par_eleve.return_value = [mock_paiement]

            with self.assertRaises(ConfirmationRequise) as context:
                service.modifier_eleve(1, "Dupont", "Jean", 1, "2025-2026", 100000)

            self.assertIn("baissez le total dû", str(context.exception))

    @patch('edupaie.services.eleve_service.transaction')
    @patch.object(EleveService, '__init__', lambda self: None)
    def test_modifier_eleve_baisse_total_du_avec_confirmation_acceptee(self, mock_transaction):
        """Teste que baisser le total_du avec confirmation est accepté."""
        mock_conn = MagicMock()
        mock_transaction.return_value.__enter__.return_value = mock_conn

        service = EleveService()

        with patch('edupaie.services.eleve_service.EleveRepository') as mock_eleve_repo_class, \
             patch('edupaie.services.eleve_service.ClasseRepository') as mock_classe_repo_class, \
             patch('edupaie.database.repositories.paiement_repository.PaiementRepository') as mock_paiement_repo_class:

            mock_eleve_repo = MagicMock()
            mock_classe_repo = MagicMock()
            mock_paiement_repo = MagicMock()

            mock_eleve_repo_class.return_value = mock_eleve_repo
            mock_classe_repo_class.return_value = mock_classe_repo
            mock_paiement_repo_class.return_value = mock_paiement_repo

            mock_eleve_repo.trouver_par_id.return_value = MagicMock(
                id=1,
                nom="Dupont",
                prenom="Jean",
                total_du=150000
            )
            mock_classe_repo.trouver_par_id.return_value = MagicMock(id=1)
            mock_paiement_repo.lister_par_eleve.return_value = [MagicMock()]
            mock_eleve_repo.trouver_par_id.return_value = MagicMock(
                id=1,
                nom="Dupont",
                prenom="Jean",
                total_du=100000
            )

            # Avec confirmation, doit réussir
            service.modifier_eleve(1, "Dupont", "Jean", 1, "2025-2026", 100000, confirmer=True)
            mock_eleve_repo.modifier.assert_called_once()

    @patch('edupaie.services.eleve_service.transaction')
    @patch.object(EleveService, '__init__', lambda self: None)
    def test_lister_eleves_filtre_par_statut(self, mock_transaction):
        """Teste le filtrage par statut."""
        mock_conn = MagicMock()
        mock_transaction.return_value.__enter__.return_value = mock_conn

        service = EleveService()

        with patch('edupaie.services.eleve_service.EleveRepository') as mock_eleve_repo_class:
            mock_eleve_repo = MagicMock()
            mock_eleve_repo_class.return_value = mock_eleve_repo

            from edupaie.models.eleve import Eleve
            from edupaie.models.eleve_avec_totaux import EleveAvecTotaux

            # Mock élèves
            mock_eleve1 = EleveAvecTotaux(
                eleve=Eleve(id=1, nom="Dupont", prenom="Jean", classe_id=1, annee_scolaire="2025-2026", total_du=150000),
                nom_classe="6ème A",
                total_paye=150000  # Soldé
            )

            mock_eleve2 = EleveAvecTotaux(
                eleve=Eleve(id=2, nom="Martin", prenom="Paul", classe_id=1, annee_scolaire="2025-2026", total_du=150000),
                nom_classe="6ème A",
                total_paye=50000  # Partiellement payé
            )

            mock_eleve3 = EleveAvecTotaux(
                eleve=Eleve(id=3, nom="Durand", prenom="Marie", classe_id=1, annee_scolaire="2025-2026", total_du=150000),
                nom_classe="6ème A",
                total_paye=0  # Non payé
            )

            mock_eleve_repo.lister_avec_totaux.return_value = [mock_eleve1, mock_eleve2, mock_eleve3]

            # Filtrer par "Soldé"
            result = service.lister_eleves(statut="Soldé")
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].total_paye, 150000)

            # Filtrer par "Partiellement payé"
            result = service.lister_eleves(statut="Partiellement payé")
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].total_paye, 50000)

            service.lister_eleves(classe_id=2, recherche="Martin")
            mock_eleve_repo.lister_avec_totaux.assert_called_with(
                recherche="Martin",
                classe_id=2,
            )

    @patch('edupaie.services.eleve_service.readonly_connection')
    @patch.object(EleveService, '__init__', lambda self: None)
    def test_fiche_retourne_toutes_les_informations(self, mock_readonly):
        """Teste que fiche() retourne toutes les informations de l'élève."""
        mock_conn = MagicMock()
        mock_readonly.return_value.__enter__.return_value = mock_conn

        service = EleveService()

        with patch('edupaie.services.eleve_service.EleveRepository') as mock_eleve_repo_class, \
             patch('edupaie.services.eleve_service.ClasseRepository') as mock_classe_repo_class, \
             patch('edupaie.database.repositories.paiement_repository.PaiementRepository') as mock_paiement_repo_class:

            mock_eleve_repo = MagicMock()
            mock_classe_repo = MagicMock()
            mock_paiement_repo = MagicMock()

            mock_eleve_repo_class.return_value = mock_eleve_repo
            mock_classe_repo_class.return_value = mock_classe_repo
            mock_paiement_repo_class.return_value = mock_paiement_repo

            from edupaie.models.eleve import Eleve
            from edupaie.models.eleve_avec_totaux import EleveAvecTotaux
            from edupaie.models.paiement import Paiement

            # Mock élève et total payé
            mock_eleve = Eleve(id=1, nom="Dupont", prenom="Jean", classe_id=1, annee_scolaire="2025-2026", total_du=150000)
            mock_eleve_repo.trouver_par_id.return_value = mock_eleve
            mock_eleve_repo.total_paye.return_value = 50000

            # Mock classe
            mock_classe = MagicMock(id=1, nom="6ème A")
            mock_classe_repo.trouver_par_id.return_value = mock_classe

            # Mock paiements
            mock_paiement = Paiement(
                id=1, eleve_id=1, montant=50000, date_paiement="2025-09-15",
                mode="especes", numero_recu="REC-2026-000001", solde_apres=100000, cree_le="2025-09-15 09:00:00"
            )
            mock_paiement_repo.lister_par_eleve.return_value = [mock_paiement]

            # Appeler fiche
            result = service.fiche(1)

            # Vérifier le résultat
            self.assertEqual(result["eleve"].id, 1)
            self.assertEqual(result["nom_classe"], "6ème A")
            self.assertEqual(result["total_du"], 150000)
            self.assertEqual(result["total_paye"], 50000)
            self.assertEqual(result["solde"], 100000)
            self.assertEqual(result["trop_percu"], 0)
            self.assertEqual(result["statut"], "Partiellement payé")
            self.assertEqual(len(result["paiements"]), 1)

    @patch('edupaie.services.eleve_service.readonly_connection')
    @patch.object(EleveService, '__init__', lambda self: None)
    def test_fiche_avec_trop_percu(self, mock_readonly):
        """Teste que fiche() détecte le trop-perçu."""
        mock_conn = MagicMock()
        mock_readonly.return_value.__enter__.return_value = mock_conn

        service = EleveService()

        with patch('edupaie.services.eleve_service.EleveRepository') as mock_eleve_repo_class, \
             patch('edupaie.services.eleve_service.ClasseRepository') as mock_classe_repo_class, \
             patch('edupaie.database.repositories.paiement_repository.PaiementRepository') as mock_paiement_repo_class:

            mock_eleve_repo = MagicMock()
            mock_classe_repo = MagicMock()
            mock_paiement_repo = MagicMock()

            mock_eleve_repo_class.return_value = mock_eleve_repo
            mock_classe_repo_class.return_value = mock_classe_repo
            mock_paiement_repo_class.return_value = mock_paiement_repo

            from edupaie.models.eleve import Eleve
            from edupaie.models.eleve_avec_totaux import EleveAvecTotaux

            # Mock élève avec trop-perçu
            mock_eleve = Eleve(id=1, nom="Dupont", prenom="Jean", classe_id=1, annee_scolaire="2025-2026", total_du=150000)
            mock_eleve_repo.trouver_par_id.return_value = mock_eleve
            mock_eleve_repo.total_paye.return_value = 180000  # Trop-perçu de 30000

            mock_classe_repo.trouver_par_id.return_value = MagicMock(id=1, nom="6ème A")
            mock_paiement_repo.lister_par_eleve.return_value = []

            result = service.fiche(1)

            self.assertEqual(result["solde"], 0)
            self.assertEqual(result["trop_percu"], 30000)
            self.assertEqual(result["statut"], "Soldé")

    @patch('edupaie.services.eleve_service.readonly_connection')
    @patch.object(EleveService, '__init__', lambda self: None)
    def test_fiche_eleve_inexistant(self, mock_readonly):
        """Teste que fiche() lève une ValidationError si l'élève n'existe pas."""
        mock_conn = MagicMock()
        mock_readonly.return_value.__enter__.return_value = mock_conn

        service = EleveService()

        with patch('edupaie.services.eleve_service.EleveRepository') as mock_eleve_repo_class:
            mock_eleve_repo = MagicMock()
            mock_eleve_repo_class.return_value = mock_eleve_repo
            mock_eleve_repo.trouver_par_id.return_value = None

            with self.assertRaises(ValidationError) as context:
                service.fiche(999)

            self.assertIn("Élève introuvable", str(context.exception))


if __name__ == "__main__":
    unittest.main()
