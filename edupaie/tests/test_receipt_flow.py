import os
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox

from edupaie.models.paiement import Paiement
from edupaie.ui.fiche_eleve import FicheEleveDialog
from edupaie.ui.paiement_dialog import PaiementDialog


_app = QApplication.instance() or QApplication([])


class FakeEleveService:
    def fiche(self, eleve_id):
        return {
            "eleve": SimpleNamespace(
                id=eleve_id,
                nom="Diallo",
                prenom="Aminata",
                annee_scolaire="2026-2027",
            ),
            "nom_classe": "Terminale A",
            "total_du": 75000,
            "total_paye": 0,
            "solde": 75000,
            "trop_percu": 0,
            "statut": "Non payé",
            "paiements": [],
        }


class FakePaiementService:
    def enregistrer_paiement(self, eleve_id, montant, date_paiement, mode):
        return Paiement(
            id=12,
            eleve_id=eleve_id,
            montant=montant,
            date_paiement=date_paiement,
            mode=mode,
            numero_recu="REC-2026-000012",
            solde_apres=75000 - montant,
            cree_le="2026-10-01 10:00:00",
        )


class FakeParametreService:
    def lire_parametre(self, cle):
        return "FCFA"

    def lire_tous_les_parametres(self):
        return {
            "nom_etablissement": "École de Démonstration",
            "devise": "FCFA",
        }


def test_paiement_propose_et_genere_le_recu_pdf(tmp_path, monkeypatch):
    services = {
        "eleve": FakeEleveService(),
        "paiement": FakePaiementService(),
        "parametre": FakeParametreService(),
    }
    chemin_pdf = tmp_path / "recu.pdf"
    dialog = PaiementDialog(services, 4)
    dialog.montant_input.setText("25000")

    monkeypatch.setattr(
        QMessageBox,
        "information",
        staticmethod(lambda *args, **kwargs: QMessageBox.StandardButton.Ok),
    )
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        staticmethod(lambda *args, **kwargs: (str(chemin_pdf), "Fichier PDF (*.pdf)")),
    )
    monkeypatch.setattr(
        "edupaie.ui.recu_export.QDesktopServices.openUrl",
        lambda url: True,
    )

    dialog._on_accept()

    assert dialog.result() == dialog.DialogCode.Accepted
    assert dialog.paiement_enregistre.numero_recu == "REC-2026-000012"
    assert chemin_pdf.is_file()
    assert chemin_pdf.read_bytes().startswith(b"%PDF-")


def test_fiche_eleve_echoue_proprement_si_le_chargement_echoue(monkeypatch):
    services = {"eleve": SimpleNamespace(
        fiche=lambda eleve_id: (_ for _ in ()).throw(
            TypeError("lister_avec_totaux() got an unexpected keyword argument 'eleve_id'")
        )
    )}
    erreurs = []
    monkeypatch.setattr(
        QMessageBox,
        "critical",
        staticmethod(lambda *args, **kwargs: erreurs.append(args[2])),
    )

    dialog = FicheEleveDialog(services, 4)

    assert dialog._fiche_chargee is False
    assert dialog.exec() == int(dialog.DialogCode.Rejected)
    assert not hasattr(dialog, "fiche")
    assert len(erreurs) == 1