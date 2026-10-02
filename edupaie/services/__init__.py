"""
Services métier EduPaie.

Ce package contient les services implémentant la logique métier.
"""

from edupaie.services.eleve_service import EleveService
from edupaie.services.paiement_service import PaiementService
from edupaie.services.classe_service import ClasseService
from edupaie.services.parametre_service import ParametreService
from edupaie.services.auth_service import AuthService
from edupaie.services.statistiques_service import StatistiquesService

__all__ = [
    "EleveService",
    "PaiementService",
    "ClasseService",
    "ParametreService",
    "AuthService",
    "StatistiquesService",
]
