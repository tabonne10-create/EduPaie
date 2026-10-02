"""
Utilitaires pour la gestion des permissions et des rôles.

Ce module contient des fonctions utilitaires pour vérifier
et filtrer les données selon les permissions de l'utilisateur.
"""


def est_enseignant(session) -> bool:
    """
    Vérifie si l'utilisateur a le rôle enseignant.

    Args:
        session: Session utilisateur (optionnelle)

    Returns:
        True si l'utilisateur est enseignant, False sinon
    """
    return session is not None and "enseignant" in session.roles


def filtrer_par_classes_autorisees(items, session, classe_getter):
    """
    Filtre une liste d'éléments selon les classes autorisées de l'enseignant.

    Args:
        items: Liste d'éléments à filtrer
        session: Session utilisateur
        classe_getter: Fonction pour extraire l'ID de classe d'un élément

    Returns:
        Liste filtrée des éléments
    """
    if not est_enseignant(session):
        return items

    classes_autorisees = session.classes
    return [item for item in items if classe_getter(item) in classes_autorisees]

