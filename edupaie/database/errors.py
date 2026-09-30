"""
Exceptions personnalisées pour la couche repository.
"""


class RepositoryError(Exception):
    """Exception de base pour les erreurs de repository."""
    pass


class ClasseRepositoryError(RepositoryError):
    """Erreur spécifique au repository de classes."""
    pass


class EleveRepositoryError(RepositoryError):
    """Erreur spécifique au repository d'élèves."""
    pass


class PaiementRepositoryError(RepositoryError):
    """Erreur spécifique au repository de paiements."""
    pass


class ParametreRepositoryError(RepositoryError):
    """Erreur spécifique au repository de paramètres."""
    pass
