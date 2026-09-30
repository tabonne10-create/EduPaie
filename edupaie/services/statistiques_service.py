"""
Service métier pour les statistiques globales.

Ce module contient la logique métier liée aux statistiques,
en utilisant StatistiquesRepository.
"""

from edupaie.database.repositories.statistiques_repository import StatistiquesRepository
from edupaie.database.transaction import transaction
from edupaie.services.calculs import determiner_statut


class StatistiquesService:
    """Service métier pour les statistiques."""

    def __init__(self):
        """Initialise le service."""
        pass

    def obtenir_statistiques_globales(self) -> dict:
        """
        Obtient les statistiques globales de l'établissement.

        Returns:
            Dictionnaire avec les statistiques :
            - total_eleves: nombre total d'élèves
            - total_du: montant total dû
            - total_paye: montant total payé
            - total_solde: montant total restant à payer
            - eleves_soldes: nombre d'élèves soldés
            - eleves_partiellement_payes: nombre d'élèves partiellement payés
            - eleves_non_payes: nombre d'élèves non payés
        """
        with transaction() as conn:
            repo = StatistiquesRepository(conn)
            stats = repo.totaux_globaux()

            # Calculer les statuts
            from edupaie.database.repositories.eleve_repository import EleveRepository
            eleve_repo = EleveRepository(conn)
            eleves = eleve_repo.lister_avec_totaux()

            eleves_soldes = 0
            eleves_partiellement_payes = 0
            eleves_non_payes = 0

            for eleve in eleves:
                statut = determiner_statut(eleve.eleve.total_du, eleve.total_paye)
                if statut.value == "Soldé":
                    eleves_soldes += 1
                elif statut.value == "Partiellement payé":
                    eleves_partiellement_payes += 1
                else:
                    eleves_non_payes += 1

            total_du = int(stats["total_du"])
            total_paye = int(stats["total_encaisse"])
            total_solde = total_du - total_paye
            if total_solde < 0:
                total_solde = 0  # Borné à 0 en cas de trop-perçu

            return {
                "total_eleves": int(stats["nombre_eleves"]),
                "total_du": total_du,
                "total_paye": total_paye,
                "total_solde": total_solde,
                "eleves_soldes": eleves_soldes,
                "eleves_partiellement_payes": eleves_partiellement_payes,
                "eleves_non_payes": eleves_non_payes
            }

    def obtenir_statistiques_par_classe(self, classe_id: int) -> dict:
        """
        Obtient les statistiques pour une classe spécifique.

        Args:
            classe_id: ID de la classe

        Returns:
            Dictionnaire avec les statistiques de la classe
        """
        with transaction() as conn:
            from edupaie.database.repositories.eleve_repository import EleveRepository
            eleve_repo = EleveRepository(conn)

            eleves = eleve_repo.lister_avec_totaux(classe_id=classe_id)

            total_du = sum(e.eleve.total_du for e in eleves)
            total_paye = sum(e.total_paye for e in eleves)
            total_solde = sum(e.eleve.total_du - e.total_paye for e in eleves)

            eleves_soldes = 0
            eleves_partiellement_payes = 0
            eleves_non_payes = 0

            for eleve in eleves:
                statut = determiner_statut(eleve.eleve.total_du, eleve.total_paye)
                if statut.value == "Soldé":
                    eleves_soldes += 1
                elif statut.value == "Partiellement payé":
                    eleves_partiellement_payes += 1
                else:
                    eleves_non_payes += 1

            return {
                "total_eleves": len(eleves),
                "total_du": total_du,
                "total_paye": total_paye,
                "total_solde": total_solde,
                "eleves_soldes": eleves_soldes,
                "eleves_partiellement_payes": eleves_partiellement_payes,
                "eleves_non_payes": eleves_non_payes
            }
