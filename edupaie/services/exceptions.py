"""
Exceptions personnalisées pour la couche service.
"""


class ValidationError(Exception):
    """Exception levée lorsqu'une donnée saisie est invalide."""
    pass


class RegleMetierError(Exception):
    """Exception levée lorsqu'une règle métier est violée."""
    pass


class ConfirmationRequise(Exception):
    """Exception levée lorsqu'une confirmation utilisateur est requise."""
    
    def __init__(self, message: str):
        """
        Initialise l'exception avec un message explicite.
        
        Args:
            message: Message à afficher à l'utilisateur
        """
        self.message = message
        super().__init__(message)
