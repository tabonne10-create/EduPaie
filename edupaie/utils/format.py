"""
Fonctions de formatage pour l'affichage.
"""


def formater_montant(montant: int, devise: str) -> str:
    """
    Formate un montant avec séparateur de milliers.
    
    Args:
        montant: Montant en FCFA (entier)
        devise: Devise (ex: "FCFA")
        
    Returns:
        Montant formaté (ex: "150 000 FCFA")
    """
    # Formatage avec séparateur de milliers (espace)
    montant_formate = f"{montant:,}".replace(",", " ")
    return f"{montant_formate} {devise}"
