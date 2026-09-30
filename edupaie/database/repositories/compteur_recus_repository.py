"""
Repository pour la gestion du compteur de reçus.
"""

import sqlite3
from edupaie.database.errors import RepositoryError


class CompteurRecusRepository:
    """Repository pour accéder au compteur de reçus."""
    
    def __init__(self, conn: sqlite3.Connection):
        """
        Initialise le repository avec une connexion.
        
        Args:
            conn: Connexion SQLite active
        """
        self.conn = conn
    
    def lire_dernier(self, annee: int) -> int:
        """
        Lit le dernier numéro de reçu pour une année.
        
        Args:
            annee: Année civile
            
        Returns:
            Dernier numéro utilisé (0 si aucun pour cette année)
        """
        cursor = self.conn.execute(
            "SELECT dernier_numero FROM compteur_recus WHERE annee = ?",
            (annee,)
        )
        row = cursor.fetchone()
        if row:
            return row['dernier_numero']
        return 0
    
    def incrementer(self, annee: int) -> int:
        """
        Incrémente le compteur pour une année et retourne le nouveau numéro.
        
        Utilise INSERT OR IGNORE pour créer l'entrée si elle n'existe pas,
        puis UPDATE pour incrémenter.
        
        Note: La transaction n'est pas gérée ici (c'est l'appelant qui la gère).
        
        Args:
            annee: Année civile
            
        Returns:
            Nouveau numéro après incrémentation
        """
        # Insérer si n'existe pas (idempotent)
        self.conn.execute(
            "INSERT OR IGNORE INTO compteur_recus (annee, dernier_numero) "
            "VALUES (?, 0)",
            (annee,)
        )
        
        # Incrémenter
        cursor = self.conn.execute(
            "UPDATE compteur_recus SET dernier_numero = dernier_numero + 1 "
            "WHERE annee = ?",
            (annee,)
        )
        
        # Lire la nouvelle valeur
        cursor = self.conn.execute(
            "SELECT dernier_numero FROM compteur_recus WHERE annee = ?",
            (annee,)
        )
        return cursor.fetchone()['dernier_numero']
