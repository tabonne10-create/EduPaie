"""
Modèle de données pour un élève avec ses totaux de paiement.
"""

from dataclasses import dataclass
from edupaie.models.eleve import Eleve


@dataclass
class EleveAvecTotaux:
    """Représente un élève avec ses totaux de paiement."""
    
    eleve: Eleve
    nom_classe: str
    total_paye: int  # Somme des paiements (en FCFA)
