"""
Repository pour la gestion des classes.
"""

import sqlite3
from typing import List, Optional
from edupaie.models.classe import Classe
from edupaie.database.errors import ClasseRepositoryError


class ClasseRepository:
    """Repository pour accéder aux données des classes."""
    
    def __init__(self, conn: sqlite3.Connection):
        """
        Initialise le repository avec une connexion.
        
        Args:
            conn: Connexion SQLite active
        """
        self.conn = conn
    
    def lister(self) -> List[Classe]:
        """
        Liste toutes les classes.
        
        Returns:
            Liste des classes triées par nom
        """
        cursor = self.conn.execute(
            "SELECT id, nom FROM classes ORDER BY nom"
        )
        return [Classe(row['id'], row['nom']) for row in cursor.fetchall()]
    
    def trouver_par_id(self, classe_id: int) -> Optional[Classe]:
        """
        Trouve une classe par son identifiant.
        
        Args:
            classe_id: Identifiant de la classe
            
        Returns:
            La classe trouvée ou None
        """
        cursor = self.conn.execute(
            "SELECT id, nom FROM classes WHERE id = ?",
            (classe_id,)
        )
        row = cursor.fetchone()
        if row:
            return Classe(row['id'], row['nom'])
        return None
    
    def creer(self, nom: str) -> Classe:
        """
        Crée une nouvelle classe.
        
        Note: Le commit n'est pas fait ici, c'est l'appelant qui gère la transaction.
        
        Args:
            nom: Nom de la classe
            
        Returns:
            La classe créée avec son ID
            
        Raises:
            ClasseRepositoryError: Si la création échoue (ex: nom en double)
        """
        try:
            cursor = self.conn.execute(
                "INSERT INTO classes (nom) VALUES (?)",
                (nom,)
            )
            return Classe(cursor.lastrowid, nom)
        except sqlite3.IntegrityError as e:
            raise ClasseRepositoryError(
                f"Impossible de créer la classe '{nom}' : nom déjà existant"
            ) from e
    
    def modifier(self, classe_id: int, nom: str) -> None:
        """
        Modifie le nom d'une classe.
        
        Note: Le commit n'est pas fait ici, c'est l'appelant qui gère la transaction.
        
        Args:
            classe_id: Identifiant de la classe
            nom: Nouveau nom
            
        Raises:
            ClasseRepositoryError: Si la modification échoue
        """
        try:
            self.conn.execute(
                "UPDATE classes SET nom = ? WHERE id = ?",
                (nom, classe_id)
            )
        except sqlite3.IntegrityError as e:
            raise ClasseRepositoryError(
                f"Impossible de modifier la classe : nom '{nom}' déjà existant"
            ) from e
    
    def supprimer(self, classe_id: int) -> None:
        """
        Supprime une classe.
        
        Note: Le commit n'est pas fait ici, c'est l'appelant qui gère la transaction.
        
        Args:
            classe_id: Identifiant de la classe
            
        Raises:
            ClasseRepositoryError: Si la suppression échoue (ex: des élèves sont inscrits)
        """
        try:
            cursor = self.conn.execute(
                "DELETE FROM classes WHERE id = ?",
                (classe_id,)
            )
            if cursor.rowcount == 0:
                raise ClasseRepositoryError(
                    f"Classe {classe_id} introuvable"
                )
        except sqlite3.IntegrityError as e:
            raise ClasseRepositoryError(
                f"Impossible de supprimer la classe : des élèves y sont inscrits"
            ) from e
    
    def compter_eleves(self, classe_id: int) -> int:
        """
        Compte le nombre d'élèves dans une classe.
        
        Args:
            classe_id: Identifiant de la classe
            
        Returns:
            Nombre d'élèves
        """
        cursor = self.conn.execute(
            "SELECT COUNT(*) as count FROM eleves WHERE classe_id = ?",
            (classe_id,)
        )
        return cursor.fetchone()['count']
