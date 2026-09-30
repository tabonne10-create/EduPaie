"""
Fonctions de validation des données saisies.

Ce module contient des fonctions pures qui valident les données
et lèvent ValidationError en cas d'erreur.
"""

from edupaie.services.exceptions import ValidationError


def valider_nom(nom: str, champ: str = "nom") -> None:
    """
    Valide qu'un nom n'est pas vide.

    Args:
        nom: Nom à valider
        champ: Nom du champ pour le message d'erreur

    Raises:
        ValidationError: Si le nom est vide ou ne contient que des espaces
    """
    if not nom or not nom.strip():
        raise ValidationError(f"{champ} ne peut pas être vide")


def valider_montant(montant: int, champ: str = "montant") -> None:
    """
    Valide qu'un montant est positif.

    Args:
        montant: Montant à valider
        champ: Nom du champ pour le message d'erreur

    Raises:
        ValidationError: Si le montant est négatif
    """
    if montant < 0:
        raise ValidationError(f"{champ} ne peut pas être négatif")


def valider_montant_positif(montant: int, champ: str = "montant") -> None:
    """
    Valide qu'un montant est strictement positif.

    Args:
        montant: Montant à valider
        champ: Nom du champ pour le message d'erreur

    Raises:
        ValidationError: Si le montant est inférieur ou égal à 0
    """
    if montant <= 0:
        raise ValidationError(f"{champ} doit être strictement positif")


def valider_annee_scolaire(annee: str) -> None:
    """
    Valide le format d'une année scolaire (ex: "2025-2026").

    Args:
        annee: Année scolaire à valider

    Raises:
        ValidationError: Si le format est invalide
    """
    if not annee or "-" not in annee:
        raise ValidationError("L'année scolaire doit être au format AAAA-AAAA")

    parties = annee.split("-")
    if len(parties) != 2:
        raise ValidationError("L'année scolaire doit être au format AAAA-AAAA")

    try:
        annee_debut = int(parties[0])
        annee_fin = int(parties[1])
    except ValueError:
        raise ValidationError("L'année scolaire doit contenir des années valides")

    if annee_fin != annee_debut + 1:
        raise ValidationError("L'année scolaire doit couvrir deux années consécutives")

    if annee_debut < 2000 or annee_debut > 2100:
        raise ValidationError("L'année scolaire doit être entre 2000-2001 et 2099-2100")


def valider_date(date_str: str) -> None:
    """
    Valide le format d'une date (YYYY-MM-DD).

    Args:
        date_str: Date à valider

    Raises:
        ValidationError: Si le format est invalide
    """
    if not date_str:
        raise ValidationError("La date ne peut pas être vide")

    if len(date_str) != 10 or date_str[4] != "-" or date_str[7] != "-":
        raise ValidationError("La date doit être au format AAAA-MM-JJ")

    try:
        annee = int(date_str[0:4])
        mois = int(date_str[5:7])
        jour = int(date_str[8:10])

        if mois < 1 or mois > 12:
            raise ValidationError("Le mois doit être entre 01 et 12")

        if jour < 1 or jour > 31:
            raise ValidationError("Le jour doit être entre 01 et 31")

        # Validation basique des jours par mois
        if mois in [4, 6, 9, 11] and jour > 30:
            raise ValidationError("Ce mois n'a que 30 jours")

        if mois == 2:
            # Année bissextile simple
            est_bissextile = (annee % 4 == 0 and annee % 100 != 0) or (annee % 400 == 0)
            if jour > 29 or (jour == 29 and not est_bissextile):
                raise ValidationError("Février n'a que 28 ou 29 jours (année bissextile)")

    except ValueError:
        raise ValidationError("La date doit contenir des nombres valides")


def valider_mode_paiement(mode: str) -> None:
    """
    Valide qu'un mode de paiement est autorisé.

    Args:
        mode: Mode de paiement à valider

    Raises:
        ValidationError: Si le mode n'est pas autorisé
    """
    modes_autorises = ["especes", "cheque", "virement", "mobile_money"]
    if mode not in modes_autorises:
        raise ValidationError(f"Mode de paiement invalide. Modes autorisés : {', '.join(modes_autorises)}")


def valider_telephone(telephone: str) -> None:
    """
    Valide un numéro de téléphone (format basique).

    Args:
        telephone: Numéro de téléphone à valider

    Raises:
        ValidationError: Si le format est invalide
    """
    if not telephone:
        return  # Téléphone optionnel

    # Nettoyer : espaces, tirets, points
    telephone_nettoye = telephone.replace(" ", "").replace("-", "").replace(".", "")

    if not telephone_nettoye.isdigit():
        raise ValidationError("Le numéro de téléphone ne doit contenir que des chiffres")

    if len(telephone_nettoye) < 8 or len(telephone_nettoye) > 15:
        raise ValidationError("Le numéro de téléphone doit contenir entre 8 et 15 chiffres")


def valider_email(email: str) -> None:
    """
    Valide un email (format basique).

    Args:
        email: Email à valider

    Raises:
        ValidationError: Si le format est invalide
    """
    if not email:
        return  # Email optionnel

    if "@" not in email or "." not in email.split("@")[-1]:
        raise ValidationError("L'email doit être au format utilisateur@domaine.ext")

    if email.startswith("@") or email.endswith("@"):
        raise ValidationError("L'email ne peut pas commencer ou finir par @")


def valider_numero_recu(numero: str) -> None:
    """
    Valide le format d'un numéro de reçu (PREFIXE-AAAA-XXXXXX).

    Args:
        numero: Numéro de reçu à valider

    Raises:
        ValidationError: Si le format est invalide
    """
    if not numero:
        raise ValidationError("Le numéro de reçu ne peut pas être vide")

    parties = numero.split("-")
    if len(parties) != 3:
        raise ValidationError("Le numéro de reçu doit être au format PREFIXE-AAAA-XXXXXX")

    prefixe, annee_str, numero_str = parties

    if not prefixe or not prefixe.isalpha():
        raise ValidationError("Le préfixe doit être composé de lettres")

    try:
        annee = int(annee_str)
        if annee < 2000 or annee > 2100:
            raise ValidationError("L'année doit être entre 2000 et 2100")
    except ValueError:
        raise ValidationError("L'année doit être un nombre valide")

    if len(numero_str) != 6 or not numero_str.isdigit():
        raise ValidationError("Le numéro séquentiel doit être sur 6 chiffres")
