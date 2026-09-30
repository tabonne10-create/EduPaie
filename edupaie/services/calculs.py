"""
Fonctions de calcul pour la logique métier.

Ce module contient des fonctions pures (sans accès à la base)
faciles à tester.
"""

from enum import Enum


class Statut(Enum):
    """Statuts de paiement d'un élève."""
    SOLDE = "Soldé"
    PARTIELLEMENT_PAYE = "Partiellement payé"
    NON_PAYE = "Non payé"


def calculer_solde(total_du: int, total_paye: int) -> int:
    """
    Calcule le solde restant (borné à 0).
    
    Args:
        total_du: Montant total dû
        total_paye: Montant total payé
        
    Returns:
        Solde restant (jamais négatif)
    """
    return max(0, total_du - total_paye)


def calculer_trop_percu(total_du: int, total_paye: int) -> int:
    """
    Calcule le trop-perçu.
    
    Args:
        total_du: Montant total dû
        total_paye: Montant total payé
        
    Returns:
        Trop-perçu (0 si pas de trop-perçu)
    """
    return max(0, total_paye - total_du)


def determiner_statut(total_du: int, total_paye: int) -> Statut:
    """
    Détermine le statut de paiement d'un élève.
    
    Règles :
    - solde == 0 (y compris total_du == 0) -> Soldé
    - total_paye == 0 et total_du > 0 -> Non payé
    - sinon -> Partiellement payé
    
    Args:
        total_du: Montant total dû
        total_paye: Montant total payé
        
    Returns:
        Statut de paiement
    """
    solde = calculer_solde(total_du, total_paye)
    
    if solde == 0:
        return Statut.SOLDE
    elif total_paye == 0 and total_du > 0:
        return Statut.NON_PAYE
    else:
        return Statut.PARTIELLEMENT_PAYE


def formater_numero_recu(prefixe: str, annee: int, numero: int) -> str:
    """
    Formate un numéro de reçu.
    
    Args:
        prefixe: Préfixe (ex: "REC")
        annee: Année civile
        numero: Numéro séquentiel
        
    Returns:
        Numéro de reçu formaté (ex: "REC-2026-000001")
    """
    return f"{prefixe}-{annee:04d}-{numero:06d}"
