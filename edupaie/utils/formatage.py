"""
Utilitaires de formatage et de conversion.

Ce module contient des fonctions utilitaires pour formater
et convertir des données pour l'affichage.
"""


def get_mode_libelle(mode: str) -> str:
    """
    Retourne le libellé accentué du mode de paiement.

    Args:
        mode: Code du mode (especes, cheque, virement, mobile_money)

    Returns:
        Libellé accentué
    """
    libelles = {
        "especes": "Espèces",
        "cheque": "Chèque",
        "virement": "Virement",
        "mobile_money": "Mobile Money"
    }
    return libelles.get(mode, mode)
