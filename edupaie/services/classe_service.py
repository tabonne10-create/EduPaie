"""
Service métier pour la gestion des classes.

Ce module contient la logique métier liée aux classes,
en utilisant ClasseRepository et les fonctions de validation.
"""

from edupaie.database.repositories.classe_repository import ClasseRepository
from edupaie.database.transaction import transaction
from edupaie.services.validation import valider_nom
from edupaie.services.exceptions import ValidationError, RegleMetierError, ConfirmationRequise
from edupaie.models.classe import Classe


class ClasseService:
    """Service métier pour la gestion des classes."""

    def __init__(self):
        """Initialise le service."""
        pass

    def creer_classe(self, nom: str) -> Classe:
        """
        Crée une nouvelle classe.

        Args:
            nom: Nom de la classe

        Returns:
            Classe créée

        Raises:
            ValidationError: Si le nom est invalide
        """
        valider_nom(nom, "Nom de la classe")

        with transaction() as conn:
            repo = ClasseRepository(conn)
            classe = repo.creer(nom)
            return classe

    def modifier_classe(self, classe_id: int, nouveau_nom: str) -> Classe:
        """
        Modifie le nom d'une classe.

        Args:
            classe_id: ID de la classe
            nouveau_nom: Nouveau nom

        Returns:
            Classe modifiée

        Raises:
            ValidationError: Si le nom est invalide
        """
        valider_nom(nouveau_nom, "Nom de la classe")

        with transaction() as conn:
            repo = ClasseRepository(conn)
            repo.modifier(classe_id, nouveau_nom)
            return repo.trouver_par_id(classe_id)

    def supprimer_classe(self, classe_id: int, confirmer: bool = False) -> None:
        """
        Supprime une classe.

        Args:
            classe_id: ID de la classe
            confirmer: Confirmation de suppression

        Raises:
            ConfirmationRequise: Si confirmer est False et la classe a des élèves
            RegleMetierError: Si la classe a des élèves et confirmation refusée
        """
        with transaction() as conn:
            repo = ClasseRepository(conn)
            # Vérifier si la classe a des élèves
            nb_eleves = repo.compter_eleves(classe_id)

            if nb_eleves > 0:
                if not confirmer:
                    raise ConfirmationRequise(
                        f"La classe contient {nb_eleves} élève(s). "
                        "Confirmez la suppression pour continuer."
                    )
                # La suppression échouera à cause de la contrainte FK RESTRICT
                # Le repository lèvera une erreur qu'on laissera remonter

            repo.supprimer(classe_id)

    def lister_classes(self) -> list[Classe]:
        """
        Liste toutes les classes.

        Returns:
            Liste des classes
        """
        with transaction() as conn:
            repo = ClasseRepository(conn)
            return repo.lister()

    def trouver_classe(self, classe_id: int) -> Classe:
        """
        Trouve une classe par son ID.

        Args:
            classe_id: ID de la classe

        Returns:
            Classe trouvée

        Raises:
            ValidationError: Si la classe n'existe pas
        """
        with transaction() as conn:
            repo = ClasseRepository(conn)
            classe = repo.trouver_par_id(classe_id)
            if classe is None:
                raise ValidationError("Classe introuvable")
            return classe

    def compter_eleves(self, classe_id: int) -> int:
        """
        Compte le nombre d'élèves dans une classe.

        Args:
            classe_id: ID de la classe

        Returns:
            Nombre d'élèves
        """
        with transaction() as conn:
            repo = ClasseRepository(conn)
            return repo.compter_eleves(classe_id)
