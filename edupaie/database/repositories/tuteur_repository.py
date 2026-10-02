"""Repository des parents et tuteurs des élèves."""

import sqlite3


class TuteurRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def creer(self, nom: str, prenom: str, telephone: str, fonction: str) -> int:
        curseur = self.conn.execute(
            "INSERT INTO tuteurs (nom, prenom, telephone, fonction) VALUES (?, ?, ?, ?)",
            (nom.strip(), prenom.strip(), telephone.strip(), fonction.strip()),
        )
        return curseur.lastrowid

    def associer(self, eleve_id: int, tuteur_id: int, lien: str, principal: bool) -> None:
        self.conn.execute(
            "INSERT INTO eleve_tuteurs (eleve_id, tuteur_id, lien, principal) "
            "VALUES (?, ?, ?, ?) ON CONFLICT(eleve_id, tuteur_id) DO UPDATE SET "
            "lien = excluded.lien, principal = excluded.principal",
            (eleve_id, tuteur_id, lien.strip(), int(principal)),
        )

    def lister_par_eleve(self, eleve_id: int):
        return self.conn.execute(
            "SELECT t.id, t.nom, t.prenom, t.telephone, t.fonction, et.lien, et.principal "
            "FROM tuteurs t JOIN eleve_tuteurs et ON et.tuteur_id = t.id "
            "WHERE et.eleve_id = ? ORDER BY et.principal DESC, t.nom COLLATE NOCASE",
            (eleve_id,),
        ).fetchall()

    def lister_tous(self, recherche: str = ""):
        query = (
            "SELECT t.id, t.nom, t.prenom, t.telephone, t.fonction, "
            "COUNT(et.eleve_id) AS nombre_eleves "
            "FROM tuteurs t LEFT JOIN eleve_tuteurs et ON et.tuteur_id = t.id"
        )
        params = []
        if recherche.strip():
            motif = f"%{recherche.strip()}%"
            query += " WHERE t.nom LIKE ? OR t.prenom LIKE ? OR t.telephone LIKE ?"
            params.extend([motif, motif, motif])
        query += " GROUP BY t.id ORDER BY t.nom COLLATE NOCASE, t.prenom COLLATE NOCASE"
        return self.conn.execute(query, params).fetchall()