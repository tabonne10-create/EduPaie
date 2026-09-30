"""
Modèle de données pour un élève.
"""

from dataclasses import dataclass


@dataclass
class Eleve:
    """Représente un élève."""
    
    id: int
    nom: str
    prenom: str
    classe_id: int
    annee_scolaire: str
    total_du: int  # Montant en FCFA (entier)
