import os
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from edupaie.ui.tableau_bord import TableauBord


_app = QApplication.instance() or QApplication([])


class FakeStatistiquesService:
    def __init__(self):
        self.refreshes = 0

    def obtenir_statistiques_globales(self):
        self.refreshes += 1
        return {
            "total_eleves": 11 + self.refreshes,
            "total_du": 120000,
            "total_paye": 85000,
            "total_solde": 35000,
            "eleves_soldes": 5,
            "eleves_partiellement_payes": 4,
            "eleves_non_payes": 3,
        }

    def obtenir_statistiques_par_classe(self, classe_id):
        return {
            "total_eleves": 7 if classe_id == 1 else 6,
            "total_du": 70000 if classe_id == 1 else 50000,
            "total_paye": 50000 if classe_id == 1 else 35000,
            "total_solde": 20000 if classe_id == 1 else 15000,
        }


class FakeClasseService:
    def lister_classes(self):
        return [SimpleNamespace(id=1, nom="6e A"), SimpleNamespace(id=2, nom="5e B")]


class FakeParametreService:
    def lire_parametre(self, cle):
        return "FCFA"


def test_tableau_bord_affiche_et_actualise_les_indicateurs():
    statistiques = FakeStatistiquesService()
    dashboard = TableauBord({
        "statistiques": statistiques,
        "classe": FakeClasseService(),
        "parametre": FakeParametreService(),
    })

    assert dashboard.metric_values["total_eleves"].text() == "12"
    assert dashboard.metric_values["total_solde"].text() == "35 000 FCFA"
    assert dashboard.status_values["eleves_soldes"].text() == "5"
    assert dashboard.collection_progress.value() == 71
    assert dashboard.collection_percent.text() == "71 %"
    assert dashboard.table.rowCount() == 2
    assert dashboard.table.item(0, 0).text() == "6e A"
    assert dashboard.table.item(0, 4).text() == "20 000 FCFA"
    assert dashboard.class_count_label.text() == "2 classes"
    assert dashboard.actualisation_label.text().startswith("Actualisé à ")

    dashboard.actualiser()

    assert dashboard.metric_values["total_eleves"].text() == "13"
    assert statistiques.refreshes == 2
