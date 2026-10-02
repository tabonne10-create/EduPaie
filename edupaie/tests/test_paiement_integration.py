from datetime import date
import pytest

from edupaie.database.connection import init_database
from edupaie.models.paiement import Paiement
from edupaie.services.classe_service import ClasseService
from edupaie.services.eleve_service import EleveService
from edupaie.services.paiement_service import PaiementService
from edupaie.services.auth_service import AuthService
from edupaie.services.exceptions import ValidationError
from edupaie.services.statistiques_service import StatistiquesService


def test_enregistrer_paiement_avec_une_vraie_base_sqlite(tmp_path, monkeypatch):
    database_path = tmp_path / "paiement-test.db"
    monkeypatch.setattr(
        "edupaie.database.connection.get_database_path",
        lambda: str(database_path),
    )
    init_database()

    classe = ClasseService().creer_classe("6e A")
    eleve = EleveService().creer_eleve(
        "Diallo",
        "Aminata",
        classe.id,
        "2026-2027",
        75000,
    )
    service = PaiementService(aujourdhui=lambda: date(2026, 10, 1))

    paiement = service.enregistrer_paiement(
        eleve.id,
        25000,
        "2026-10-01",
        "especes",
    )

    assert isinstance(paiement, Paiement)
    assert paiement.eleve_id == eleve.id
    assert paiement.montant == 25000
    assert paiement.numero_recu == "REC-2026-000001"
    assert paiement.solde_apres == 50000

    autre_eleve = EleveService().creer_eleve(
        "Sow",
        "Awa",
        classe.id,
        "2026-2027",
        40000,
    )
    autre_paiement = service.enregistrer_paiement(
        autre_eleve.id,
        10000,
        "2026-10-01",
        "cheque",
        "09:45:00",
        "Oumar Sow",
    )

    tous = service.lister_tous_paiements()
    resultat_recherche = service.lister_tous_paiements(recherche="REC-2026-000001")
    resultat_mode = service.lister_tous_paiements(recherche="Sow", mode="cheque")

    assert [ligne.paiement.id for ligne in tous] == [autre_paiement.id, paiement.id]
    assert len(resultat_recherche) == 1
    assert resultat_recherche[0].nom_eleve == "Diallo"
    assert resultat_recherche[0].prenom_eleve == "Aminata"
    assert resultat_recherche[0].nom_classe == "6e A"
    assert len(resultat_mode) == 1
    assert resultat_mode[0].paiement.numero_recu == "REC-2026-000002"
    assert resultat_mode[0].paiement.heure_paiement == "09:45:00"
    assert resultat_mode[0].paiement.nom_payeur == "Oumar Sow"


def test_annulation_garde_trace_et_recalcule_les_soldes(tmp_path, monkeypatch):
    database_path = tmp_path / "annulation-test.db"
    monkeypatch.setattr(
        "edupaie.database.connection.get_database_path",
        lambda: str(database_path),
    )
    init_database()

    classe = ClasseService().creer_classe("Terminale B")
    eleve = EleveService().creer_eleve(
        "Ba",
        "Mariam",
        classe.id,
        "2026-2027",
        60000,
    )
    paiements = PaiementService(aujourdhui=lambda: date(2026, 10, 1))
    auth = AuthService()
    session = auth.creer_premier_directeur(
        "Directeur EduPaie",
        "directeur",
        "mot-de-passe-long-123",
    )
    paiement = paiements.enregistrer_paiement(
        eleve.id,
        20000,
        "2026-10-01",
        "mobile_money",
        "10:15:00",
        "Fatou Ba",
    )

    with pytest.raises(ValidationError, match="motif"):
        paiements.annuler_paiement(paiement.id, session, " ")

    paiements.annuler_paiement(paiement.id, session, "Mauvais montant saisi")

    fiche = EleveService().fiche(eleve.id)
    stats = StatistiquesService().obtenir_statistiques_globales()
    historique = paiements.lister_paiements_eleve(eleve.id)
    registre = paiements.lister_tous_paiements()
    annule = next(ligne.paiement for ligne in registre if ligne.paiement.id == paiement.id)

    assert fiche["total_paye"] == 0
    assert fiche["solde"] == 60000
    assert len(fiche["paiements"]) == 1
    assert fiche["paiements"][0].est_annule
    assert fiche["paiements"][0].motif_annulation == "Mauvais montant saisi"
    assert historique == []
    assert stats["total_paye"] == 0
    assert stats["total_solde"] == 60000
    assert annule.est_annule
    assert annule.annule_par == session.id
