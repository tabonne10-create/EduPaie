"""Service métier des parents et tuteurs."""

from edupaie.database.repositories.eleve_repository import EleveRepository
from edupaie.database.repositories.tuteur_repository import TuteurRepository
from edupaie.database.transaction import transaction
from edupaie.database.connection import readonly_connection
from edupaie.services.exceptions import ValidationError
from edupaie.services.validation import valider_telephone


class TuteurService:
    def __init__(self):
        self.session = None

    @staticmethod
    def _autoriser(session):
        if session is None or not session.autorise("guardians.manage"):
            raise ValidationError("Permission requise pour gérer les parents et tuteurs")

    def creer_et_associer(
        self, eleve_id: int, nom: str, prenom: str, telephone: str,
        fonction: str, lien: str, session, principal: bool = False,
    ) -> int:
        self._autoriser(session)
        if not nom.strip():
            raise ValidationError("Le nom du parent ou tuteur est obligatoire")
        valider_telephone(telephone)
        with transaction() as conn:
            if EleveRepository(conn).trouver_par_id(eleve_id) is None:
                raise ValidationError("Élève introuvable")
            repo = TuteurRepository(conn)
            tuteur_id = repo.creer(nom, prenom, telephone, fonction)
            repo.associer(eleve_id, tuteur_id, lien, principal)
            return tuteur_id

    def lister_par_eleve(self, eleve_id: int, session):
        self._autoriser(session)
        with readonly_connection() as conn:
            if EleveRepository(conn).trouver_par_id(eleve_id) is None:
                raise ValidationError("Élève introuvable")
            return TuteurRepository(conn).lister_par_eleve(eleve_id)

    def lister_tous(self, recherche: str, session):
        self._autoriser(session)
        with readonly_connection() as conn:
            return TuteurRepository(conn).lister_tous(recherche)