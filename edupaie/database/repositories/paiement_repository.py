"""
Repository pour la gestion des paiements.
"""

import sqlite3
from typing import List, Optional
from edupaie.models.paiement import Paiement
from edupaie.database.errors import PaiementRepositoryError


class PaiementRepository:
    """Repository pour accéder aux données des paiements."""
    
    def __init__(self, conn: sqlite3.Connection):
        """
        Initialise le repository avec une connexion.
        
        Args:
            conn: Connexion SQLite active
        """
        self.conn = conn
    
    def inserer(self, eleve_id: int, montant: int, date_paiement: str,
                mode: str, numero_recu: str, solde_apres: int) -> Paiement:
        """
        Insère un nouveau paiement.
        
        Note: numero_recu et solde_apres sont fournis par l'appelant (service).
        Le commit n'est pas fait ici, c'est l'appelant qui gère la transaction.
        
        Args:
            eleve_id: Identifiant de l'élève
            montant: Montant du paiement (en FCFA)
            date_paiement: Date du paiement (format ISO)
            mode: Mode de paiement
            numero_recu: Numéro de reçu unique
            solde_apres: Solde après paiement (en FCFA)
            
        Returns:
            Le paiement créé avec son ID
            
        Raises:
            PaiementRepositoryError: Si l'insertion échoue
        """
        try:
            cursor = self.conn.execute(
                "INSERT INTO paiements (eleve_id, montant, date_paiement, mode, "
                "numero_recu, solde_apres) VALUES (?, ?, ?, ?, ?, ?)",
                (eleve_id, montant, date_paiement, mode, numero_recu, solde_apres)
            )
            return Paiement(
                cursor.lastrowid, eleve_id, montant, date_paiement,
                mode, numero_recu, solde_apres, None  # cree_le sera rempli par la base
            )
        except sqlite3.IntegrityError as e:
            raise PaiementRepositoryError(
                f"Impossible d'insérer le paiement : {str(e)}"
            ) from e
    
    def lister_par_eleve(self, eleve_id: int) -> List[Paiement]:
        """
        Liste les paiements d'un élève, du plus ancien au plus récent.
        
        Tri par date_paiement, puis cree_le, puis id.
        
        Args:
            eleve_id: Identifiant de l'élève
            
        Returns:
            Liste des paiements triés chronologiquement
        """
        cursor = self.conn.execute(
            "SELECT id, eleve_id, montant, date_paiement, mode, "
            "numero_recu, solde_apres, cree_le "
            "FROM paiements WHERE eleve_id = ? "
            "ORDER BY date_paiement, cree_le, id",
            (eleve_id,)
        )
        return [
            Paiement(
                row['id'], row['eleve_id'], row['montant'],
                row['date_paiement'], row['mode'], row['numero_recu'],
                row['solde_apres'], row['cree_le']
            )
            for row in cursor.fetchall()
        ]
    
    def trouver_par_numero(self, numero_recu: str) -> Optional[Paiement]:
        """
        Trouve un paiement par son numéro de reçu.
        
        Args:
            numero_recu: Numéro de reçu
            
        Returns:
            Le paiement trouvé ou None
        """
        cursor = self.conn.execute(
            "SELECT id, eleve_id, montant, date_paiement, mode, "
            "numero_recu, solde_apres, cree_le "
            "FROM paiements WHERE numero_recu = ?",
            (numero_recu,)
        )
        row = cursor.fetchone()
        if row:
            return Paiement(
                row['id'], row['eleve_id'], row['montant'],
                row['date_paiement'], row['mode'], row['numero_recu'],
                row['solde_apres'], row['cree_le']
            )
        return None
    
    def trouver_par_id(self, paiement_id: int) -> Optional[Paiement]:
        """
        Trouve un paiement par son identifiant.
        
        Args:
            paiement_id: Identifiant du paiement
            
        Returns:
            Le paiement trouvé ou None
        """
        cursor = self.conn.execute(
            "SELECT id, eleve_id, montant, date_paiement, mode, "
            "numero_recu, solde_apres, cree_le "
            "FROM paiements WHERE id = ?",
            (paiement_id,)
        )
        row = cursor.fetchone()
        if row:
            return Paiement(
                row['id'], row['eleve_id'], row['montant'],
                row['date_paiement'], row['mode'], row['numero_recu'],
                row['solde_apres'], row['cree_le']
            )
        return None
