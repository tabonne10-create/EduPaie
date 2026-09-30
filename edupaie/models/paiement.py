"""
Modèle de données pour un paiement.
"""

from dataclasses import dataclass


@dataclass
class Paiement:
    """Représente un paiement."""
    
    id: int
    eleve_id: int
    montant: int  # Montant en FCFA (entier)
    date_paiement: str  # Format ISO : AAAA-MM-JJ
    mode: str  # 'especes', 'cheque', 'virement', 'mobile_money'
    numero_recu: str  # Format : PREFIXE-AAAA-000001
    solde_apres: int  # Solde figé au moment du paiement (en FCFA)
    cree_le: str  # Date/heure de création (ISO, UTC)
