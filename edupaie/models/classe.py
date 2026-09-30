"""
Modèle de données pour une classe.
"""

from dataclasses import dataclass


@dataclass
class Classe:
    """Représente une classe d'élèves."""
    
    id: int
    nom: str
