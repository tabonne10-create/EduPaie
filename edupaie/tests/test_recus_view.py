import os
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from edupaie.models.paiement import Paiement
from edupaie.models.paiement_liste import PaiementListe
from edupaie.ui.recus_view import RecusView


_app = QApplication.instance() or QApplication([])


class FakePaiementService:
    def __init__(self):
        self.args = None
        self.lignes = [
            PaiementListe(
                Paiement(7, 3, 25000, "2026-10-01", "especes", "REC-2026-000007", 50000, None),
                "Diallo",
                "Aminata",
                "6e A",
            )
        ]

    def lister_tous_paiements(self, recherche=None, mode=None):
        self.args = (recherche, mode)
        return self.lignes


class FakeParametreService:
    def lire_parametre(self, cle):
        return "FCFA"


def test_registre_recherche_selectionne_et_exporte_le_recu(monkeypatch):
    paiement_service = FakePaiementService()
    services = {"paiement": paiement_service, "parametre": FakeParametreService()}
    exports = []
    monkeypatch.setattr(
        "edupaie.ui.recus_view.proposer_export_recu",
        lambda parent, services, paiement, eleve_id: exports.append((paiement, eleve_id)),
    )

    view = RecusView(services)

    assert view.table.rowCount() == 1
    assert view.count_label.text() == "1 reçu"
    assert view.table.item(0, 2).text() == "REC-2026-000007"
    assert view.table.item(0, 3).text() == "Aminata Diallo"
    assert not view.btn_exporter.isEnabled()

    view.recherche_input.setText("Aminata")
    view.mode_combo.setCurrentIndex(1)
    assert paiement_service.args == ("Aminata", "especes")

    view.table.selectRow(0)
    assert view.btn_exporter.isEnabled()
    view.btn_exporter.click()
    assert exports == [(paiement_service.lignes[0].paiement, 3)]
