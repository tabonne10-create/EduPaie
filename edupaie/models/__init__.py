"""
Modèles de données EduPaie.

Ce package contient les dataclasses représentant les entités métier.
"""

from edupaie.models.eleve import Eleve
from edupaie.models.classe import Classe
from edupaie.models.paiement import Paiement
from edupaie.models.eleve_avec_totaux import EleveAvecTotaux
from edupaie.models.paiement_liste import PaiementListe

__all__ = [
    "Eleve",
    "Classe",
    "Paiement",
    "EleveAvecTotaux",
    "PaiementListe",
]
