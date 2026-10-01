"""
Service métier pour la gestion des paiements.

Ce module contient la logique métier liée aux paiements,
en utilisant PaiementRepository, CompteurRecusRepository et les fonctions de validation.
"""

from datetime import date
from typing import Callable, Optional
from edupaie.database.repositories.paiement_repository import PaiementRepository
from edupaie.database.repositories.eleve_repository import EleveRepository
from edupaie.database.repositories.compteur_recus_repository import CompteurRecusRepository
from edupaie.database.repositories.parametre_repository import ParametreRepository
from edupaie.database.transaction import transaction
from edupaie.database.connection import readonly_connection
from edupaie.services.validation import (
    valider_montant_positif,
    valider_date,
    valider_mode_paiement
)
from edupaie.services.exceptions import ValidationError, RegleMetierError
from edupaie.models.paiement import Paiement
from edupaie.services.calculs import calculer_solde, formater_numero_recu


class PaiementService:
    """Service métier pour la gestion des paiements."""

    def __init__(self, aujourdhui: Optional[Callable[[], date]] = None):
        """
        Initialise le service.

        Args:
            aujourdhui: Fonction retournant la date du jour (pour tests). Par défaut date.today().
        """
        self.aujourdhui = aujourdhui or date.today

    def enregistrer_paiement(
        self,
        eleve_id: int,
        montant: int,
        date_paiement: str,
        mode: str
    ) -> Paiement:
        """
        Enregistre un nouveau paiement.

        Args:
            eleve_id: ID de l'élève
            montant: Montant payé
            date_paiement: Date du paiement (YYYY-MM-DD)
            mode: Mode de paiement (especes, cheque, virement, mobile_money)

        Returns:
            Paiement enregistré

        Raises:
            ValidationError: Si les données sont invalides
            RegleMetierError: Si les règles métier sont violées
        """
        valider_montant_positif(montant, "Montant")
        valider_date(date_paiement)
        valider_mode_paiement(mode)

        with transaction() as conn:
            eleve_repo = EleveRepository(conn)
            paiement_repo = PaiementRepository(conn)
            compteur_repo = CompteurRecusRepository(conn)
            parametre_repo = ParametreRepository(conn)

            # Vérifier que l'élève existe
            eleve = eleve_repo.trouver_par_id(eleve_id)
            if eleve is None:
                raise ValidationError("Élève introuvable")

            # Calculer le total déjà payé
            paiements_existants = paiement_repo.lister_par_eleve(eleve_id)
            total_deja_paye = sum(p.montant for p in paiements_existants)

            # Calculer le nouveau solde
            nouveau_solde = calculer_solde(eleve.total_du, total_deja_paye + montant)

            # Règle métier : on ne peut pas payer plus que ce qui est dû
            # (sauf tolérance autorisée, mais ici on refuse le trop-perçu)
            if total_deja_paye + montant > eleve.total_du:
                from edupaie.utils.format import formater_montant
                devise = parametre_repo.lire("devise")
                if not devise:
                    devise = "FCFA"
                solde_restant = eleve.total_du - total_deja_paye
                raise RegleMetierError(
                    f"Le paiement excède le montant dû. "
                    f"Reste à payer : {formater_montant(solde_restant, devise)}"
                )

            # Générer le numéro de reçu (année basée sur la date du jour)
            annee_courante = self.aujourdhui().year
            prefixe = parametre_repo.lire("prefixe_recu")
            if not prefixe:
                prefixe = "REC"

            numero = compteur_repo.incrementer(annee_courante)
            numero_recu = formater_numero_recu(prefixe, annee_courante, numero)

            # Insérer le paiement
            paiement = paiement_repo.inserer(
                eleve_id,
                montant,
                date_paiement,
                mode,
                numero_recu,
                nouveau_solde
            )

            return paiement

    def lister_paiements_eleve(self, eleve_id: int) -> list[Paiement]:
        """
        Liste les paiements d'un élève par ordre chronologique.

        Args:
            eleve_id: ID de l'élève

        Returns:
            Liste des paiements

        Raises:
            ValidationError: Si l'élève n'existe pas
        """
        with readonly_connection() as conn:
            eleve_repo = EleveRepository(conn)
            paiement_repo = PaiementRepository(conn)

            # Vérifier que l'élève existe
            eleve = eleve_repo.trouver_par_id(eleve_id)
            if eleve is None:
                raise ValidationError("Élève introuvable")

            return paiement_repo.lister_par_eleve(eleve_id)

    def trouver_paiement(self, paiement_id: int) -> Paiement:
        """
        Trouve un paiement par son ID.

        Args:
            paiement_id: ID du paiement

        Returns:
            Paiement trouvé

        Raises:
            ValidationError: Si le paiement n'existe pas
        """
        with readonly_connection() as conn:
            paiement_repo = PaiementRepository(conn)
            paiement = paiement_repo.trouver_par_id(paiement_id)
            if paiement is None:
                raise ValidationError("Paiement introuvable")
            return paiement

    def annuler_paiement(self, paiement_id: int) -> None:
        """
        Annule un paiement (suppression).

        Args:
            paiement_id: ID du paiement

        Raises:
            ValidationError: Si le paiement n'existe pas
            RegleMetierError: Si l'annulation violerait une règle métier
        """
        with transaction() as conn:
            paiement_repo = PaiementRepository(conn)
            # Vérifier que le paiement existe
            paiement = paiement_repo.trouver_par_id(paiement_id)
            if paiement is None:
                raise ValidationError("Paiement introuvable")

            # Règle métier : vérifier que l'annulation est acceptable
            # (par exemple, pas d'annulation après un certain délai)
            # Pour l'instant, on autorise toujours

            paiement_repo.supprimer(paiement_id)
