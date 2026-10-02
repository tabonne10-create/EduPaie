"""
Repository pour la gestion des élèves.
"""

import sqlite3
from typing import List, Optional
from edupaie.models.eleve import Eleve
from edupaie.models.eleve_avec_totaux import EleveAvecTotaux
from edupaie.database.errors import EleveRepositoryError


class EleveRepository:
    """Repository pour accéder aux données des élèves."""
    
    def __init__(self, conn: sqlite3.Connection):
        """
        Initialise le repository avec une connexion.
        
        Args:
            conn: Connexion SQLite active
        """
        self.conn = conn
    
    def creer(self, nom: str, prenom: str, classe_id: int, 
              annee_scolaire: str, total_du: int) -> Eleve:
        """
        Crée un nouvel élève.
        
        Note: Le commit n'est pas fait ici, c'est l'appelant qui gère la transaction.
        
        Args:
            nom: Nom de l'élève
            prenom: Prénom de l'élève
            classe_id: Identifiant de la classe
            annee_scolaire: Année scolaire (ex: "2025-2026")
            total_du: Montant total dû (en FCFA)
            
        Returns:
            L'élève créé avec son ID
            
        Raises:
            EleveRepositoryError: Si la création échoue
        """
        try:
            cursor = self.conn.execute(
                "INSERT INTO eleves (nom, prenom, classe_id, annee_scolaire, total_du) "
                "VALUES (?, ?, ?, ?, ?)",
                (nom, prenom, classe_id, annee_scolaire, total_du)
            )
            return Eleve(
                cursor.lastrowid, nom, prenom, classe_id, annee_scolaire, total_du
            )
        except sqlite3.IntegrityError as e:
            raise EleveRepositoryError(
                f"Impossible de créer l'élève : {str(e)}"
            ) from e
    
    def modifier(self, eleve_id: int, nom: str, prenom: str, 
                 classe_id: int, annee_scolaire: str, total_du: int) -> None:
        """
        Modifie un élève.
        
        Note: Le commit n'est pas fait ici, c'est l'appelant qui gère la transaction.
        
        Args:
            eleve_id: Identifiant de l'élève
            nom: Nouveau nom
            prenom: Nouveau prénom
            classe_id: Nouvelle classe
            annee_scolaire: Nouvelle année scolaire
            total_du: Nouveau total dû
            
        Raises:
            EleveRepositoryError: Si la modification échoue
        """
        try:
            cursor = self.conn.execute(
                "UPDATE eleves SET nom = ?, prenom = ?, classe_id = ?, "
                "annee_scolaire = ?, total_du = ? WHERE id = ?",
                (nom, prenom, classe_id, annee_scolaire, total_du, eleve_id)
            )
            if cursor.rowcount == 0:
                raise EleveRepositoryError(f"Élève {eleve_id} introuvable")
        except sqlite3.IntegrityError as e:
            raise EleveRepositoryError(
                f"Impossible de modifier l'élève : {str(e)}"
            ) from e
    
    def supprimer(self, eleve_id: int) -> None:
        """
        Supprime un élève (et ses paiements par CASCADE).
        
        Note: Le commit n'est pas fait ici, c'est l'appelant qui gère la transaction.
        
        Args:
            eleve_id: Identifiant de l'élève
            
        Raises:
            EleveRepositoryError: Si la suppression échoue
        """
        cursor = self.conn.execute(
            "DELETE FROM eleves WHERE id = ?",
            (eleve_id,)
        )
        if cursor.rowcount == 0:
            raise EleveRepositoryError(f"Élève {eleve_id} introuvable")
    
    def trouver_par_id(self, eleve_id: int) -> Optional[Eleve]:
        """
        Trouve un élève par son identifiant.
        
        Args:
            eleve_id: Identifiant de l'élève
            
        Returns:
            L'élève trouvé ou None
        """
        cursor = self.conn.execute(
            "SELECT id, nom, prenom, classe_id, annee_scolaire, total_du "
            "FROM eleves WHERE id = ?",
            (eleve_id,)
        )
        row = cursor.fetchone()
        if row:
            return Eleve(
                row['id'], row['nom'], row['prenom'], row['classe_id'],
                row['annee_scolaire'], row['total_du']
            )
        return None
    
    def lister_avec_totaux(self, recherche: Optional[str] = None,
                          classe_id: Optional[int] = None,
                          annee_scolaire: Optional[str] = None) -> List[EleveAvecTotaux]:
        """
        Liste les élèves avec leurs totaux de paiement.
        
        Une seule requête avec JOIN sur classes et LEFT JOIN + SUM sur paiements.
        Les élèves sans paiement ont total_paye = 0 grâce à COALESCE.
        
        Args:
            recherche: Filtre sur nom ou prénom (LIKE)
            classe_id: Filtre sur classe
            annee_scolaire: Filtre sur année scolaire
            
        Returns:
            Liste des élèves avec totaux, triés par nom
        """
        query = """
            SELECT e.id, e.nom, e.prenom, e.classe_id, e.annee_scolaire, e.total_du,
                   c.nom as nom_classe,
                   COALESCE(SUM(CASE WHEN p.annule_le IS NULL THEN p.montant ELSE 0 END), 0) as total_paye
            FROM eleves e
            JOIN classes c ON e.classe_id = c.id
            LEFT JOIN paiements p ON e.id = p.eleve_id
        """
        params = []
        
        # Filtres
        conditions = []
        if recherche:
            conditions.append("(e.nom LIKE ? OR e.prenom LIKE ?)")
            params.extend([f"%{recherche}%", f"%{recherche}%"])
        if classe_id:
            conditions.append("e.classe_id = ?")
            params.append(classe_id)
        if annee_scolaire:
            conditions.append("e.annee_scolaire = ?")
            params.append(annee_scolaire)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " GROUP BY e.id ORDER BY e.nom"
        
        cursor = self.conn.execute(query, params)
        resultats = []
        for row in cursor.fetchall():
            eleve = Eleve(
                row['id'], row['nom'], row['prenom'], row['classe_id'],
                row['annee_scolaire'], row['total_du']
            )
            resultats.append(EleveAvecTotaux(
                eleve, row['nom_classe'], row['total_paye']
            ))
        
        return resultats
    
    def compter_paiements(self, eleve_id: int) -> int:
        """
        Compte le nombre de paiements d'un élève.
        
        Args:
            eleve_id: Identifiant de l'élève
            
        Returns:
            Nombre de paiements
        """
        cursor = self.conn.execute(
            "SELECT COUNT(*) as count FROM paiements WHERE eleve_id = ?",
            (eleve_id,)
        )
        return cursor.fetchone()['count']
    
    def total_paye(self, eleve_id: int) -> int:
        """
        Calcule le total payé par un élève.
        
        Args:
            eleve_id: Identifiant de l'élève
            
        Returns:
            Total payé (en FCFA)
        """
        cursor = self.conn.execute(
            "SELECT COALESCE(SUM(montant), 0) as total FROM paiements "
            "WHERE eleve_id = ? AND annule_le IS NULL",
            (eleve_id,)
        )
        return cursor.fetchone()['total']
