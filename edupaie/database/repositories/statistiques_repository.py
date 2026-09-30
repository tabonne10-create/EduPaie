"""
Repository pour les statistiques globales (tableau de bord).
"""

import sqlite3
from typing import Dict


class StatistiquesRepository:
    """Repository pour accéder aux statistiques globales."""
    
    def __init__(self, conn: sqlite3.Connection):
        """
        Initialise le repository avec une connexion.
        
        Args:
            conn: Connexion SQLite active
        """
        self.conn = conn
    
    def totaux_globaux(self) -> Dict[str, int]:
        """
        Calcule les totaux globaux pour le tableau de bord.
        
        Returns:
            Dictionnaire avec:
            - nombre_eleves: nombre total d'élèves
            - total_du: somme des totaux dus
            - total_encaisse: somme des paiements
        """
        query = """
            SELECT 
                COUNT(DISTINCT e.id) as nombre_eleves,
                COALESCE(SUM(e.total_du), 0) as total_du,
                COALESCE(SUM(p.montant), 0) as total_encaisse
            FROM eleves e
            LEFT JOIN paiements p ON e.id = p.eleve_id
        """
        cursor = self.conn.execute(query)
        row = cursor.fetchone()
        
        return {
            'nombre_eleves': row['nombre_eleves'],
            'total_du': row['total_du'],
            'total_encaisse': row['total_encaisse']
        }
