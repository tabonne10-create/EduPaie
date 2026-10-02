"""
EduPaie - Système de gestion scolaire.

Ce package contient tous les modules de l'application EduPaie.
"""

__version__ = "1.0.0"

# Exports principaux
from edupaie.models.eleve import Eleve
from edupaie.models.classe import Classe
from edupaie.models.paiement import Paiement

__all__ = [
    "__version__",
    "Eleve",
    "Classe",
    "Paiement",
]
