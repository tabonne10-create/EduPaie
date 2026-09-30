"""
Service métier pour la gestion des paramètres de l'établissement.

Ce module contient la logique métier liée aux paramètres,
en utilisant ParametreRepository et les fonctions de validation.
"""

from edupaie.database.repositories.parametre_repository import ParametreRepository
from edupaie.database.transaction import transaction
from edupaie.services.validation import valider_nom, valider_telephone, valider_email
from edupaie.services.exceptions import ValidationError


class ParametreService:
    """Service métier pour la gestion des paramètres."""

    def __init__(self):
        """Initialise le service."""
        pass

    def lire_parametre(self, cle: str) -> str:
        """
        Lit un paramètre.

        Args:
            cle: Clé du paramètre

        Returns:
            Valeur du paramètre

        Raises:
            ValidationError: Si le paramètre n'existe pas
        """
        with transaction() as conn:
            repo = ParametreRepository(conn)
            valeur = repo.lire(cle)
            if valeur is None:
                raise ValidationError(f"Paramètre '{cle}' introuvable")
            return valeur

    def ecrire_parametre(self, cle: str, valeur: str) -> None:
        """
        Écrit un paramètre.

        Args:
            cle: Clé du paramètre
            valeur: Valeur du paramètre

        Raises:
            ValidationError: Si les données sont invalides
        """
        # Validation spécifique selon la clé
        if cle == "nom_etablissement":
            valider_nom(valeur, "Nom de l'établissement")
        elif cle == "telephone":
            valider_telephone(valeur)
        elif cle == "email":
            valider_email(valeur)

        with transaction() as conn:
            repo = ParametreRepository(conn)
            repo.ecrire(cle, valeur)

    def lire_tous_les_parametres(self) -> dict[str, str]:
        """
        Lit tous les paramètres.

        Returns:
            Dictionnaire des paramètres
        """
        with transaction() as conn:
            repo = ParametreRepository(conn)
            return repo.lire_tous()

    def mettre_a_jour_etablissement(
        self,
        nom: str,
        sigle: str,
        adresse: str,
        telephone: str,
        email: str
    ) -> None:
        """
        Met à jour les informations de l'établissement.

        Args:
            nom: Nom de l'établissement
            sigle: Sigle
            adresse: Adresse
            telephone: Téléphone
            email: Email

        Raises:
            ValidationError: Si les données sont invalides
        """
        valider_nom(nom, "Nom de l'établissement")
        valider_telephone(telephone)
        valider_email(email)

        with transaction() as conn:
            repo = ParametreRepository(conn)
            repo.ecrire("nom_etablissement", nom)
            repo.ecrire("sigle", sigle)
            repo.ecrire("adresse", adresse)
            repo.ecrire("telephone", telephone)
            repo.ecrire("email", email)

    def mettre_a_jour_paiements(
        self,
        devise: str,
        prefixe_recu: str
    ) -> None:
        """
        Met à jour les paramètres de paiement.

        Args:
            devise: Devise
            prefixe_recu: Préfixe des reçus

        Raises:
            ValidationError: Si les données sont invalides
        """
        if not devise or not devise.strip():
            raise ValidationError("La devise ne peut pas être vide")

        if not prefixe_recu or not prefixe_recu.isalpha():
            raise ValidationError("Le préfixe doit être composé de lettres")

        with transaction() as conn:
            repo = ParametreRepository(conn)
            repo.ecrire("devise", devise)
            repo.ecrire("prefixe_recu", prefixe_recu)
