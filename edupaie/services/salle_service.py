"""Service de gestion des salles."""

from edupaie.database.connection import readonly_connection
from edupaie.database.repositories.salle_repository import SalleRepository
from edupaie.database.transaction import transaction
from edupaie.services.exceptions import ValidationError


class SalleService:
    def __init__(self):
        self.session = None

    def _verifier_permission(self):
        session = getattr(self, "session", None)
        if session is not None and not session.autorise("classes.manage"):
            raise ValidationError("Permission requise pour gérer les salles")

    def lister_salles(self, actives_seulement: bool = True):
        with readonly_connection() as conn:
            return SalleRepository(conn).lister(actives_seulement)

    def creer_salle(self, nom: str, capacite: int | None = None) -> int:
        self._verifier_permission()
        if not nom.strip():
            raise ValidationError("Le nom de la salle est obligatoire")
        if capacite is not None and capacite <= 0:
            raise ValidationError("La capacité doit être supérieure à zéro")
        with transaction() as conn:
            return SalleRepository(conn).creer(nom, capacite)

    def definir_active(self, salle_id: int, active: bool) -> None:
        self._verifier_permission()
        with transaction() as conn:
            SalleRepository(conn).definir_active(salle_id, active)
