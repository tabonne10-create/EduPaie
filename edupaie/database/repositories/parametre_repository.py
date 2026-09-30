"""
Repository pour la gestion des paramètres de l'établissement.
"""

import sqlite3
from typing import Optional, Dict
from edupaie.database.errors import ParametreRepositoryError


class ParametreRepository:
    """Repository pour accéder aux paramètres."""
    
    def __init__(self, conn: sqlite3.Connection):
        """
        Initialise le repository avec une connexion.
        
        Args:
            conn: Connexion SQLite active
        """
        self.conn = conn
    
    def lire(self, cle: str) -> Optional[str]:
        """
        Lit un paramètre par sa clé.
        
        Args:
            cle: Clé du paramètre
            
        Returns:
            Valeur du paramètre ou None si inexistant
        """
        cursor = self.conn.execute(
            "SELECT valeur FROM parametres WHERE cle = ?",
            (cle,)
        )
        row = cursor.fetchone()
        if row:
            return row['valeur']
        return None
    
    def lire_tous(self) -> Dict[str, str]:
        """
        Lit tous les paramètres.
        
        Returns:
            Dictionnaire clé -> valeur
        """
        cursor = self.conn.execute("SELECT cle, valeur FROM parametres")
        return {row['cle']: row['valeur'] for row in cursor.fetchall()}
    
    def ecrire(self, cle: str, valeur: str) -> None:
        """
        Écrit ou met à jour un paramètre.
        
        Note: Le commit n'est pas fait ici, c'est l'appelant qui gère la transaction.
        
        Args:
            cle: Clé du paramètre
            valeur: Valeur du paramètre
            
        Raises:
            ParametreRepositoryError: Si l'écriture échoue
        """
        try:
            self.conn.execute(
                "INSERT INTO parametres (cle, valeur) VALUES (?, ?) "
                "ON CONFLICT(cle) DO UPDATE SET valeur = excluded.valeur",
                (cle, valeur)
            )
        except sqlite3.Error as e:
            raise ParametreRepositoryError(
                f"Impossible d'écrire le paramètre '{cle}' : {str(e)}"
            ) from e
