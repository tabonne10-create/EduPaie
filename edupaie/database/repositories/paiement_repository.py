"""Repository pour la gestion et l'audit des paiements."""

import sqlite3
from typing import List, Optional

from edupaie.database.errors import PaiementRepositoryError
from edupaie.models.paiement import Paiement
from edupaie.models.paiement_liste import PaiementListe


class PaiementRepository:
    """Accès aux données de paiements, y compris leur annulation auditée."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    @staticmethod
    def _paiement(row) -> Paiement:
        return Paiement(
            row["id"], row["eleve_id"], row["montant"], row["date_paiement"],
            row["mode"], row["numero_recu"], row["solde_apres"], row["cree_le"],
            row["heure_paiement"], row["nom_payeur"], row["annule_le"],
            row["annule_par"], row["motif_annulation"],
        )

    def inserer(
        self,
        eleve_id: int,
        montant: int,
        date_paiement: str,
        mode: str,
        numero_recu: str,
        solde_apres: int,
        heure_paiement: str = "00:00:00",
        nom_payeur: str = "",
    ) -> Paiement:
        try:
            cursor = self.conn.execute(
                "INSERT INTO paiements (eleve_id, montant, date_paiement, mode, "
                "numero_recu, solde_apres, heure_paiement, nom_payeur) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (eleve_id, montant, date_paiement, mode, numero_recu, solde_apres,
                 heure_paiement, nom_payeur.strip()),
            )
            return Paiement(
                cursor.lastrowid, eleve_id, montant, date_paiement, mode,
                numero_recu, solde_apres, None, heure_paiement, nom_payeur.strip(),
            )
        except sqlite3.IntegrityError as erreur:
            raise PaiementRepositoryError(
                f"Impossible d'insérer le paiement : {erreur}"
            ) from erreur

    def lister_par_eleve(
        self, eleve_id: int, inclure_annules: bool = False
    ) -> List[Paiement]:
        query = (
            "SELECT id, eleve_id, montant, date_paiement, mode, numero_recu, "
            "solde_apres, cree_le, heure_paiement, nom_payeur, annule_le, "
            "annule_par, motif_annulation FROM paiements WHERE eleve_id = ?"
        )
        if not inclure_annules:
            query += " AND annule_le IS NULL"
        query += " ORDER BY date_paiement, heure_paiement, cree_le, id"
        rows = self.conn.execute(query, (eleve_id,)).fetchall()
        return [self._paiement(row) for row in rows]

    def lister_tous(
        self,
        recherche: Optional[str] = None,
        mode: Optional[str] = None,
    ) -> List[PaiementListe]:
        query = (
            "SELECT p.id, p.eleve_id, p.montant, p.date_paiement, p.mode, "
            "p.numero_recu, p.solde_apres, p.cree_le, p.heure_paiement, "
            "p.nom_payeur, p.annule_le, p.annule_par, p.motif_annulation, "
            "e.nom AS nom_eleve, e.prenom AS prenom_eleve, c.nom AS nom_classe "
            "FROM paiements p JOIN eleves e ON e.id = p.eleve_id "
            "JOIN classes c ON c.id = e.classe_id"
        )
        conditions = []
        params = []
        if recherche:
            motif = f"%{recherche.strip()}%"
            conditions.append(
                "(p.numero_recu LIKE ? OR e.nom LIKE ? OR e.prenom LIKE ? "
                "OR c.nom LIKE ? OR p.nom_payeur LIKE ?)"
            )
            params.extend([motif] * 5)
        if mode:
            conditions.append("p.mode = ?")
            params.append(mode)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += (
            " ORDER BY p.date_paiement DESC, p.heure_paiement DESC, "
            "p.cree_le DESC, p.id DESC"
        )

        lignes = []
        for row in self.conn.execute(query, params).fetchall():
            lignes.append(PaiementListe(
                paiement=self._paiement(row),
                nom_eleve=row["nom_eleve"],
                prenom_eleve=row["prenom_eleve"],
                nom_classe=row["nom_classe"],
            ))
        return lignes

    def trouver_par_numero(self, numero_recu: str) -> Optional[Paiement]:
        row = self.conn.execute(
            "SELECT id, eleve_id, montant, date_paiement, mode, numero_recu, "
            "solde_apres, cree_le, heure_paiement, nom_payeur, annule_le, "
            "annule_par, motif_annulation FROM paiements WHERE numero_recu = ?",
            (numero_recu,),
        ).fetchone()
        return self._paiement(row) if row else None

    def trouver_par_id(self, paiement_id: int) -> Optional[Paiement]:
        row = self.conn.execute(
            "SELECT id, eleve_id, montant, date_paiement, mode, numero_recu, "
            "solde_apres, cree_le, heure_paiement, nom_payeur, annule_le, "
            "annule_par, motif_annulation FROM paiements WHERE id = ?",
            (paiement_id,),
        ).fetchone()
        return self._paiement(row) if row else None

    def annuler(self, paiement_id: int, utilisateur_id: int, motif: str) -> None:
        curseur = self.conn.execute(
            "UPDATE paiements SET annule_le = CURRENT_TIMESTAMP, annule_par = ?, "
            "motif_annulation = ? WHERE id = ? AND annule_le IS NULL",
            (utilisateur_id, motif.strip(), paiement_id),
        )
        if curseur.rowcount == 0:
            raise PaiementRepositoryError("Paiement introuvable ou déjà annulé")

    def recalculer_soldes_actifs(self, eleve_id: int, total_du: int) -> None:
        solde = total_du
        paiements = self.lister_par_eleve(eleve_id)
        for paiement in paiements:
            solde = max(0, solde - paiement.montant)
            self.conn.execute(
                "UPDATE paiements SET solde_apres = ? WHERE id = ?",
                (solde, paiement.id),
            )
