"""Repository des salles de l'établissement."""

import sqlite3


class SalleRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def lister(self, actives_seulement: bool = True):
        query = "SELECT id, nom, capacite, active FROM salles"
        if actives_seulement:
            query += " WHERE active = 1"
        query += " ORDER BY nom COLLATE NOCASE"
        return self.conn.execute(query).fetchall()

    def creer(self, nom: str, capacite: int | None) -> int:
        cursor = self.conn.execute(
            "INSERT INTO salles (nom, capacite) VALUES (?, ?)",
            (nom.strip(), capacite),
        )
        return cursor.lastrowid

    def definir_active(self, salle_id: int, active: bool) -> None:
        self.conn.execute(
            "UPDATE salles SET active = ? WHERE id = ?",
            (int(active), salle_id),
        )
