"""
Service métier pour la gestion des élèves.

Ce module contient la logique métier liée aux élèves,
en utilisant EleveRepository et les fonctions de validation.
"""

from edupaie.database.repositories.eleve_repository import EleveRepository
from edupaie.database.repositories.classe_repository import ClasseRepository
from edupaie.database.transaction import transaction
from edupaie.services.validation import (
    valider_nom,
    valider_montant,
    valider_annee_scolaire
)
from edupaie.services.exceptions import ValidationError, ConfirmationRequise
from edupaie.models.eleve import Eleve
from edupaie.models.eleve_avec_totaux import EleveAvecTotaux


class EleveService:
    """Service métier pour la gestion des élèves."""

    def __init__(self):
        """Initialise le service."""
        pass

    def creer_eleve(
        self,
        nom: str,
        prenom: str,
        classe_id: int,
        annee_scolaire: str,
        total_du: int = 0
    ) -> Eleve:
        """
        Crée un nouvel élève.

        Args:
            nom: Nom de l'élève
            prenom: Prénom de l'élève
            classe_id: ID de la classe
            annee_scolaire: Année scolaire (ex: "2025-2026")
            total_du: Montant total dû (défaut: 0)

        Returns:
            Élève créé

        Raises:
            ValidationError: Si les données sont invalides
        """
        valider_nom(nom, "Nom")
        valider_nom(prenom, "Prénom")
        valider_montant(total_du, "Total dû")
        valider_annee_scolaire(annee_scolaire)

        with transaction() as conn:
            classe_repo = ClasseRepository(conn)
            eleve_repo = EleveRepository(conn)

            # Vérifier que la classe existe
            classe = classe_repo.trouver_par_id(classe_id)
            if classe is None:
                raise ValidationError("Classe introuvable")

            eleve = eleve_repo.creer(
                nom,
                prenom,
                classe_id,
                annee_scolaire,
                total_du
            )
            return eleve

    def modifier_eleve(
        self,
        eleve_id: int,
        nom: str,
        prenom: str,
        classe_id: int,
        annee_scolaire: str,
        total_du: int,
        confirmer: bool = False
    ) -> Eleve:
        """
        Modifie un élève.

        Args:
            eleve_id: ID de l'élève
            nom: Nouveau nom
            prenom: Nouveau prénom
            classe_id: Nouvelle classe
            annee_scolaire: Nouvelle année scolaire
            total_du: Nouveau total dû
            confirmer: Confirmation pour modification risquée

        Returns:
            Élève modifié

        Raises:
            ValidationError: Si les données sont invalides
            ConfirmationRequise: Si la baisse du total_du nécessite une confirmation
        """
        valider_nom(nom, "Nom")
        valider_nom(prenom, "Prénom")
        valider_montant(total_du, "Total dû")
        valider_annee_scolaire(annee_scolaire)

        with transaction() as conn:
            classe_repo = ClasseRepository(conn)
            eleve_repo = EleveRepository(conn)

            # Vérifier que l'élève existe
            eleve = eleve_repo.trouver_par_id(eleve_id)
            if eleve is None:
                raise ValidationError("Élève introuvable")

            # Vérifier que la classe existe
            classe = classe_repo.trouver_par_id(classe_id)
            if classe is None:
                raise ValidationError("Classe introuvable")

            # Règle métier : baisse du total_du avec paiements existants
            if total_du < eleve.total_du:
                # Vérifier s'il y a des paiements
                from edupaie.database.repositories.paiement_repository import PaiementRepository
                paiement_repo = PaiementRepository(conn)
                paiements = paiement_repo.lister_par_eleve(eleve_id)

                if paiements and not confirmer:
                    raise ConfirmationRequise(
                        f"Vous baissez le total dû de {eleve.total_du} à {total_du} "
                        f"alors que l'élève a déjà {len(paiements)} paiement(s). "
                        "Confirmez pour continuer."
                    )

            eleve_repo.modifier(
                eleve_id,
                nom,
                prenom,
                classe_id,
                annee_scolaire,
                total_du
            )
            return eleve_repo.trouver_par_id(eleve_id)

    def supprimer_eleve(self, eleve_id: int) -> None:
        """
        Supprime un élève (et ses paiements par CASCADE).

        Args:
            eleve_id: ID de l'élève

        Raises:
            ValidationError: Si l'élève n'existe pas
        """
        with transaction() as conn:
            eleve_repo = EleveRepository(conn)
            # Vérifier que l'élève existe
            eleve = eleve_repo.trouver_par_id(eleve_id)
            if eleve is None:
                raise ValidationError("Élève introuvable")

            eleve_repo.supprimer(eleve_id)

    def trouver_eleve(self, eleve_id: int) -> Eleve:
        """
        Trouve un élève par son ID.

        Args:
            eleve_id: ID de l'élève

        Returns:
            Élève trouvé

        Raises:
            ValidationError: Si l'élève n'existe pas
        """
        with transaction() as conn:
            eleve_repo = EleveRepository(conn)
            eleve = eleve_repo.trouver_par_id(eleve_id)
            if eleve is None:
                raise ValidationError("Élève introuvable")
            return eleve

    def lister_eleves(
        self,
        classe_id: int = None,
        recherche: str = None,
        statut: str = None
    ) -> list[EleveAvecTotaux]:
        """
        Liste les élèves avec leurs totaux de paiement.

        Args:
            classe_id: Filtre par classe (optionnel)
            recherche: Recherche par nom/prénom (optionnel)
            statut: Filtre par statut ("Soldé", "Partiellement payé", "Non payé") (optionnel)

        Returns:
            Liste des élèves avec totaux
        """
        with transaction() as conn:
            eleve_repo = EleveRepository(conn)
            eleves = eleve_repo.lister_avec_totaux(classe_id, recherche)

            # Filtrer par statut si demandé
            if statut:
                from edupaie.services.calculs import determiner_statut
                eleves_filtres = []
                for eleve in eleves:
                    statut_eleve = determiner_statut(eleve.eleve.total_du, eleve.total_paye)
                    if statut_eleve.value == statut:
                        eleves_filtres.append(eleve)
                return eleves_filtres

            return eleves

    def obtenir_statut_eleve(self, eleve_id: int) -> str:
        """
        Obtient le statut de paiement d'un élève.

        Args:
            eleve_id: ID de l'élève

        Returns:
            Statut ("Soldé", "Partiellement payé", "Non payé")

        Raises:
            ValidationError: Si l'élève n'existe pas
        """
        with transaction() as conn:
            eleve_repo = EleveRepository(conn)
            eleve = eleve_repo.lister_avec_totaux(
                filtre_eleve_id=eleve_id
            )
            if not eleve:
                raise ValidationError("Élève introuvable")

            eleve_avec_totaux = eleve[0]
            from edupaie.services.calculs import determiner_statut
            statut = determiner_statut(eleve_avec_totaux.eleve.total_du, eleve_avec_totaux.total_paye)
            return statut.value
