from datetime import date

from edupaie.database.connection import init_database
from edupaie.models.paiement import Paiement
from edupaie.services.classe_service import ClasseService
from edupaie.services.eleve_service import EleveService
from edupaie.services.paiement_service import PaiementService


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
